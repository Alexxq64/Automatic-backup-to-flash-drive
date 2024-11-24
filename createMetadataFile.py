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

def get_default_metadata_path():
    """Возвращает путь для файла метаданных по умолчанию."""
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    return os.path.join(desktop, "filesToBackUp.txt")

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

def add_source_file():
    """
    Добавляет новый файл-источник в файл метаданных.
    Если файл метаданных ещё не существует, создаёт его.
    """
    # Выбор или создание файла метаданных
    metadata_file = filedialog.asksaveasfilename(
        title="Создать или выбрать файл метаданных",
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt")],
        initialfile=os.path.basename(get_default_metadata_path()),
        initialdir=os.path.dirname(get_default_metadata_path())
    )
    if not metadata_file:
        print("Операция отменена.")
        return

    # Проверка, является ли файл метаданных новым
    is_new_metadata_file = not os.path.exists(metadata_file)

    # Если файл метаданных новый, то инициализируем параметры для первой записи
    if is_new_metadata_file:
        creation_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        initial_modified = "null"
        initial_backup = "null"
        initial_to = "null"
        file_name = os.path.basename(metadata_file)
        file_size = 0
        file_hash = hashlib.md5(b"").hexdigest()
    else:
        # Для добавления новых файлов в уже существующий файл
        initial_modified = "null"  # В первой записи для нового файла будет "null"
        initial_backup = "null"  # Для первого добавления резервного копирования
        initial_to = "null"  # Путь назначения пока не установлен

        # Выбор файла для добавления в метаданные
        source_file = choose_file("Выберите файл для резервного копирования")
        if not source_file:
            print("Файл не выбран. Операция отменена.")
            return

        # Сбор данных о выбранном файле
        file_name = os.path.basename(source_file)
        file_size = os.path.getsize(source_file)
        file_hash = calculate_file_hash(source_file)
        initial_modified = datetime.datetime.fromtimestamp(os.path.getmtime(source_file)).strftime('%Y-%m-%d %H:%M:%S')

    # Открытие файла метаданных для записи
    with open(metadata_file, "a" if not is_new_metadata_file else "w") as meta_file:
        # Вызов записи метаданных с нужными параметрами
        write_metadata_entry(
            meta_file=meta_file,
            name=file_name,
            from_path=source_file if not is_new_metadata_file else metadata_file,
            modified=initial_modified,
            to_path=initial_to,
            backup_date=initial_backup,
            size=file_size,
            file_hash=file_hash
        )

    print(f"Запись для файла {file_name} добавлена в файл метаданных.")
