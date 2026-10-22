from .utils import load_table_data


ALLOWED_TYPES = ("int", "str", "bool")


def create_table(metadata, table_name, columns):

    if table_name in metadata:
        raise ValueError(f'Ошибка: Таблица "{table_name}" уже существует.')

    table_columns = {}

    for column in columns:
        try:
            name, data_type = column.split(":")
        except ValueError:
            raise ValueError(f"Некорректное значение: {column}. Попробуйте снова.")

        if (data_type not in ALLOWED_TYPES or not name
                or name in table_columns or (name == "ID" and data_type != "int")):
            raise ValueError(f"Некорректное значение: {column}. Попробуйте снова.")

        table_columns[name] = data_type

    table_columns = {"ID": "int", **table_columns}

    metadata[table_name] = table_columns

    columns_desc = ", ".join(f"{name}:{data_type}" for name, data_type in table_columns.items())
    print(f"Таблица '{table_name}' успешно создана со столбцами: {columns_desc}")

    return metadata


def drop_table(metadata, table_name):

    if table_name not in metadata:
        raise ValueError(f'Ошибка: Таблица "{table_name}" не существует.')

    del metadata[table_name]

    print(f'Таблица "{table_name}" успешно удалена.')

    return metadata


def insert(metadata, table_name, values):

    if table_name not in metadata:
        raise ValueError(f'Ошибка: Таблица "{table_name}" не существует.')

    columns = {
        name: data_type
        for name, data_type in metadata[table_name].items()
        if name != "ID"
    }

    if len(values) != len(columns):
        raise ValueError("Некорректное количество значений.")

    types = {"int": int, "str": str, "bool": bool}

    for value, data_type in zip(values, columns.values()):
        if type(value) != types[data_type]:
            raise ValueError(f"Некорректное значение: {value}. Попробуйте снова.")

    data = load_table_data(table_name)

    new_id = max((row["ID"] for row in data), default=0) + 1

    new_row = {"ID": new_id, **dict(zip(columns, values))}
    data.append(new_row)

    return data


def select(table_data, where_clause=None):

    if where_clause is None:
        return table_data

    return [
        row for row in table_data
        if all(row.get(key) == value for key, value in where_clause.items())
    ]


def update(table_data, set_clause, where_clause):

    for row in table_data:
        if all(row.get(key) == value for key, value in where_clause.items()):
            row.update(set_clause)

    return table_data


def delete(table_data, where_clause):

    return [
        row for row in table_data
        if not all(row.get(key) == value for key, value in where_clause.items())
    ]