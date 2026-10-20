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