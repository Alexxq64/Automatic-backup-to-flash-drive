import os
import hashlib
import datetime
from tkinter import filedialog, Tk

# Инициализация Tkinter (без создания окна)
Tk().withdraw()

def calculate_file_hash(file_path):
    """Рассчитывает MD5-хеш файла."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def choose_folder(prompt="Choose a folder"):
    """Открывает диалог выбора папки."""
    return filedialog.askdirectory(title=prompt)

def choose_file(prompt="Choose a file"):
    """Открывает диалог выбора файла."""
    return filedialog.askopenfilename(title=prompt)

# def get_default_metadata_path():
#     """Возвращает путь для файла метаданных по умолчанию."""
#     desktop = os.path.join(os.path.expanduser("~"), "Desktop")
#     return os.path.join(desktop, "filesToBackUp.txt")
#
def write_metadata_entry(meta_file, name, from_path, modified, to_path="null", backup_date="null", size=0, file_hash=""):
    """Записывает одну запись метаданных в файл."""
    meta_file.write(f"Name: {name}\n")
    meta_file.write(f"From: {from_path}\n")
    meta_file.write(f"Modified: {modified}\n")
    meta_file.write(f"To: {to_path}\n")
    meta_file.write(f"Backup: {backup_date}\n")
    meta_file.write(f"Size: {size} bytes\n")
    meta_file.write(f"Hash: {file_hash}\n")
    meta_file.write("-" * 40 + "\n")

import os
import hashlib
from datetime import datetime
from setSystemPath import set_environment_variable_to_program_path

import os
import hashlib
from datetime import datetime

METADATA_FILENAME = "metadata.txt"
ENV_VAR_NAME = "AUTOMATIC_BACKUP_TO_FLASH_DRIVE"


def add_source_file():
    """
    Создаёт файл метаданных в папке программы при первом запуске.
    Устанавливает переменную среды AUTOMATIC_BACKUP_TO_FLASH_DRIVE с путём к этой папке.
    Добавляет данные о новом файле в метаданные.
    """
    # Определяем путь к папке программы
    program_path = os.getcwd()  # Текущая рабочая директория (папка программы)
    metadata_file = os.path.join(program_path, METADATA_FILENAME)

    # Проверяем, существует ли файл метаданных
    is_new_metadata_file = not os.path.exists(metadata_file)

    # Параметры для записи в файл метаданных
    if is_new_metadata_file:
        print(f"Файл метаданных не найден. Создаём новый: {metadata_file}")
        # Устанавливаем переменную среды только если файл метаданных был создан
        set_environment_variable_to_program_path()

        # Данные для записи самого метаданных
        file_name = METADATA_FILENAME
        from_path = metadata_file
        modified_time = "null"
        to_path = "null"
        backup_date = "null"
        file_size = 0
        file_hash = hashlib.md5(b"").hexdigest()

        # Создание записи о самом файле метаданных
        first_entry = True
    else:
        # Если файл метаданных уже существует, то будем добавлять новый файл
        print(f"Файл метаданных найден: {metadata_file}")

        # Выбор нового файла для добавления в метаданные
        source_file = choose_file("Выберите файл для резервного копирования")
        if not source_file:
            print("Файл не выбран. Операция отменена.")
            return

        # Данные для записи нового файла
        file_name = os.path.basename(source_file)
        from_path = source_file
        modified_time = datetime.fromtimestamp(os.path.getmtime(source_file)).strftime('%Y-%m-%d %H:%M:%S')
        to_path = "null"
        backup_date = "null"
        file_size = os.path.getsize(source_file)
        file_hash = calculate_file_hash(source_file)

        first_entry = False

    # Открытие файла метаданных и запись
    with open(metadata_file, "a" if not first_entry else "w") as meta_file:
        write_metadata_entry(
            meta_file=meta_file,
            name=file_name,
            from_path=from_path,
            modified=modified_time,
            to_path=to_path,
            backup_date=backup_date,
            size=file_size,
            file_hash=file_hash
        )

    print(f"Запись для файла {file_name} добавлена в файл метаданных.")


add_source_file()
