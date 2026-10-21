import shlex
from .core import create_table, drop_table
from .utils import load_metadata, save_metadata


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
   
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n") 


def run():

    print_help()

    while True:
        metadata = load_metadata(METADATA_FILE_NAME)
        user_input = input("Введите команду: ")

        if not user_input.strip():
            continue

        args = shlex.split(user_input)
        command, *params = args

        try:
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

                case "help":
                    print_help()

                case "exit":
                    break

                case _:
                    print(f"Функции {command} нет. Попробуйте снова.")

        except ValueError as error:
            print(error)