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