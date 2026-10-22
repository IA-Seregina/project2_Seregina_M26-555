import shlex
import re
from prettytable import PrettyTable
from .core import create_table, drop_table, insert, select, update, delete
from .utils import load_metadata, save_metadata, load_table_data, save_table_data


METADATA_FILE_NAME = "db_meta.json"

def welcome():
    print("Первая попытка запустить проект!")
    print("\n***")

    while True:
        print("<command> exit - выйти из программы")
        print("<command> help - справочная информация")

        command = input("Введите команду: ")

        if command == "exit":
            break
        elif command == "help":
            continue
        else:
            print("Команда не найдена.")


def print_help():
    """Prints the help message for the current mode."""

    print("\n***Операции с данными***")
    print("\nФункции:")
    print("<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - создать запись.")
    print("<command> select from <имя_таблицы> where <столбец> = <значение> - прочитать записи по условию.")
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print("<command> update <имя_таблицы> set <столбец1> = <новое_значение1> where <столбец_условия> = <значение_условия> - обновить запись.")
    print("<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись.")
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")
    print("<command> exit - выход из программы")
    print("<command> help- справочная информация\n")


def parse_clause(clause):
    column, value = clause.split("=")
    value = value.strip()

    if value.startswith(('"', "'")) and value.endswith(('"', "'")):
        value = value[1:-1]
    elif value.lower() in ("true", "false"):
        value = value.lower() == "true"
    else:
        try:
            value = int(value)
        except ValueError:
            raise ValueError(f"Некорректное значение: {value}. Попробуйте снова.") from None

    return {column.strip(): value}


def run():

    print_help()

    while True:
        metadata = load_metadata(METADATA_FILE_NAME)
        user_input = input("Введите команду: ")

        if not user_input.strip():
            continue

        try:
            args = shlex.split(user_input)
            command, *params = args

            match command:
                case "create_table":
                    metadata = create_table(metadata, params[0], params[1:])
                    save_metadata(METADATA_FILE_NAME, metadata)

                case "drop_table":
                    metadata = drop_table(metadata, params[0])
                    save_metadata(METADATA_FILE_NAME, metadata)

                case "list_tables":
                    for table_name in metadata:
                        print(f"- {table_name}")

                case "insert":
                    parts = re.fullmatch(
                        r"insert into (\w+) values\s*\((.*)\)",
                        user_input.strip()
                    )

                    if not parts:
                        raise ValueError("Некорректная команда insert.")

                    table_name, values_text = parts.groups()

                    lexer = shlex.shlex(values_text, posix=False)
                    lexer.whitespace = ","
                    lexer.whitespace_split = True

                    values = []
                    for value in lexer:
                        value = value.strip()

                        if value.startswith(('"', "'")) and value.endswith(('"', "'")):
                            values.append(value[1:-1])
                        elif value.lower() in ("true", "false"):
                            values.append(value.lower() == "true")
                        else:
                            values.append(int(value))

                    table_data = insert(metadata, table_name, values)
                    save_table_data(table_name, table_data)

                    print(
                        f'Запись с ID={table_data[-1]["ID"]} '
                        f'успешно добавлена в таблицу "{table_name}".'
                    )

                case "select":
                    parts = re.fullmatch(
                        r"select from (\w+)(?: where (.+))?",
                        user_input.strip()
                    )

                    if not parts:
                        raise ValueError("Некорректная команда select.")

                    table_name, condition = parts.groups()

                    if table_name not in metadata:
                        raise ValueError(f'Таблица "{table_name}" не существует.')

                    where_clause = parse_clause(condition) if condition else None

                    table_data = load_table_data(table_name)
                    result = select(table_data, where_clause)

                    table = PrettyTable()
                    table.field_names = list(metadata[table_name])

                    for row in result:
                        table.add_row([row[column] for column in table.field_names])

                    print(table)

                case "update":
                    parts = re.fullmatch(
                        r"update (\w+) set (.+?) where (.+)",
                        user_input.strip()
                    )

                    if not parts:
                        raise ValueError("Некорректная команда update.")

                    table_name, set_text, where_text = parts.groups()

                    if table_name not in metadata:
                        raise ValueError(f'Таблица "{table_name}" не существует.')

                    set_clause = parse_clause(set_text)
                    where_clause = parse_clause(where_text)

                    column, value = next(iter(set_clause.items()))
                    types = {"int": int, "str": str, "bool": bool}

                    if (
                        column not in metadata[table_name]
                        or column == "ID"
                        or type(value) is not types[metadata[table_name][column]]
                    ):
                        raise ValueError(
                            f"Некорректное значение: {column}. Попробуйте снова."
                        )

                    table_data = load_table_data(table_name)
                    matched = select(table_data, where_clause)

                    table_data = update(table_data, set_clause, where_clause)
                    save_table_data(table_name, table_data)

                    for row in matched:
                        print(
                            f'Запись с ID={row["ID"]} в таблице '
                            f'"{table_name}" успешно обновлена.'
                        )

                case "delete":
                    parts = re.fullmatch(
                        r"delete from (\w+) where (.+)",
                        user_input.strip()
                    )

                    if not parts:
                        raise ValueError("Некорректная команда delete.")

                    table_name, condition = parts.groups()

                    if table_name not in metadata:
                        raise ValueError(f'Таблица "{table_name}" не существует.')

                    where_clause = parse_clause(condition)

                    table_data = load_table_data(table_name)
                    matched = select(table_data, where_clause)

                    table_data = delete(table_data, where_clause)
                    save_table_data(table_name, table_data)

                    for row in matched:
                        print(
                            f'Запись с ID={row["ID"]} успешно удалена '
                            f'из таблицы "{table_name}".'
                        )

                case "info":
                    table_name = params[0]

                    if table_name not in metadata:
                        raise ValueError(f'Таблица "{table_name}" не существует.')

                    columns = ", ".join(
                        f"{name}:{data_type}"
                        for name, data_type in metadata[table_name].items()
                    )

                    table_data = load_table_data(table_name)

                    print(f"Таблица: {table_name}")
                    print(f"Столбцы: {columns}")
                    print(f"Количество записей: {len(table_data)}")

                case "help":
                    print_help()

                case "exit":
                    break

                case _:
                    print(f"Функции {command} нет. Попробуйте снова.")

        except (ValueError, IndexError) as error:
            print(error)