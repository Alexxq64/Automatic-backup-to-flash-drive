import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def add_file_to_list_with_dialog(file_list_path):
    """
    Выводит стандартное окно выбора файла, получает его путь и добавляет в список file_list.txt.
    Все пути нормализуются для единого формата.

    :param file_list_path: Путь к файлу списка.
    """
    # Убедимся, что файл существует, если нет — создадим его
    if not os.path.exists(file_list_path):
        with open(file_list_path, "w") as file:
            pass

    # Скрываем главное окно Tkinter
    Tk().withdraw()

    # Открываем стандартное окно выбора файла
    selected_file = askopenfilename(title="Выберите файл для добавления")

    # Проверяем, был ли выбран файл
    if not selected_file:
        print("Файл не выбран.")
        return

    # Нормализуем путь (приводим к стандарту Windows с обратными слэшами)
    normalized_file = os.path.normpath(selected_file)

    # Считываем текущие записи
    with open(file_list_path, "r") as file:
        existing_files = {line.strip() for line in file}

    # Добавляем файл, если его нет в списке
    if normalized_file in existing_files:
        print(f"Файл уже в списке: {normalized_file}")
    else:
        with open(file_list_path, "a") as file:
            file.write(normalized_file + "\n")  # Добавляем новую строку для каждого файла
        print(f"Файл добавлен в список: {normalized_file}")

# Пример использования
file_list_path = r"C:\Users\User\Desktop\Work\file_list.txt"  # Укажите путь к вашему file_list.txt
add_file_to_list_with_dialog(file_list_path)
