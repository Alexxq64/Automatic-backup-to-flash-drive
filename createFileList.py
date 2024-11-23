import os


def create_file_with_its_path(folder_path, file_name):
    """
    Создает файл в указанной папке и записывает в него полный путь к самому файлу.

    :param folder_path: Путь к папке, где нужно создать файл.
    :param file_name: Имя файла, который нужно создать.
    """
    # Полный путь к файлу
    file_path = os.path.join(folder_path, file_name)

    # Убедимся, что папка существует
    os.makedirs(folder_path, exist_ok=True)

    # Запишем в файл его собственный путь
    with open(file_path, "w") as file:
        file.write(file_path)

    print(f"Файл создан и записан: {file_path}")


# Пример использования
create_file_with_its_path(r"C:\Users\User\Desktop\Work", "file_list.txt")
