import os
import hashlib
from datetime import datetime
import psutil



def calculate_file_hash(file_path):
    """Вычисление хэша файла для проверки актуальности."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def read_metadata(metadata_path):
    """Чтение метаданных из файла metadata.txt."""
    metadata = []
    with open(metadata_path, "r") as file:
        entry = {}
        for line in file:
            line = line.strip()
            if line == "----------------------------------------":  # Разделитель записей
                if entry:
                    metadata.append(entry)
                entry = {}
            elif ": " in line:  # Ключ-значение
                key, value = line.split(": ", 1)
                entry[key] = value
            else:
                print(f"Предупреждение: строка пропущена из-за некорректного формата: '{line}'")
        if entry:  # Добавляем последнюю запись
            metadata.append(entry)
    return metadata


def check_files_on_flash_drive(metadata, flash_drive_path):
    """Проверяет наличие файлов на флешке и их актуальность."""
    for index, entry in enumerate(metadata, 1):
        file_path_on_flash = os.path.join(flash_drive_path, entry.get("To", ""))
        if os.path.exists(file_path_on_flash):
            # Проверка актуальности файла
            local_hash = entry.get("Hash")
            flash_hash = calculate_file_hash(file_path_on_flash)
            if local_hash == flash_hash:
                status = "актуален"
            else:
                status = "неактуален"
        else:
            status = "отсутствует"

        # Вывод статуса
        print(f"[{index}] {entry['Name']} — {status}")


def update_files(metadata, flash_drive_path, choices, metadata_file):
    """Обновляет файлы на флешке в соответствии с выбором и обновляет метаданные."""
    updated_metadata = []  # Для хранения обновлённых записей

    for entry in reversed(metadata):  # Обрабатываем список с конца
        if entry["Name"] == "metadata.txt":
            # Обновляем metadata.txt
            entry["Modified"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            entry["To"] = "metadata.txt"
            entry["Backup"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            entry["Size"] = f"{os.path.getsize(metadata_file)} bytes"
            entry["Hash"] = calculate_file_hash(metadata_file)
            print(f"Файл {entry['Name']} обновлён.")
        elif str(metadata.index(entry) + 1) in choices or "*" in choices:
            file_path_local = entry.get("From")
            # Формируем путь к файлу на флешке
            relative_path = entry["To"] if entry["To"] != "null" else entry["Name"]
            file_path_on_flash = os.path.join(flash_drive_path, relative_path)

            if not file_path_local or not os.path.exists(file_path_local):
                print(f"Пропущен файл {entry['Name']} (локальный файл отсутствует).")
                updated_metadata.append(entry)  # Сохраняем запись без изменений
                continue

            # Копирование файла
            os.makedirs(os.path.dirname(file_path_on_flash), exist_ok=True)
            with open(file_path_local, "rb") as src, open(file_path_on_flash, "wb") as dst:
                dst.write(src.read())

            # Обновляем метаданные
            entry["To"] = relative_path
            entry["Backup"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            entry["Hash"] = calculate_file_hash(file_path_local)
            entry["Size"] = f"{os.path.getsize(file_path_local)} bytes"

            print(f"Файл {entry['Name']} обновлён.")
        else:
            print(f"Файл {entry['Name']} пропущен.")

        updated_metadata.insert(0, entry)  # Добавляем обработанные записи в начало списка

    return updated_metadata


def save_metadata(metadata_file, metadata):
    """Перезаписывает файл metadata.txt с обновлёнными данными."""
    with open(metadata_file, "w") as file:
        for entry in metadata:
            for key, value in entry.items():
                file.write(f"{key}: {value}\n")
            file.write("----------------------------------------\n")


def get_flash_drive():
    """Находит подключенную флешку (съёмный диск)."""
    partitions = psutil.disk_partitions()
    for partition in partitions:
        if "removable" in partition.opts:
            return partition.mountpoint  # Возвращаем путь к флешке
    return None


def main():
    # Определяем путь к файлу metadata.txt в папке программы
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Путь к папке, где находится скрипт
    metadata_file = os.path.join(base_dir, "metadata.txt")

    if not os.path.exists(metadata_file):
        print("Файл metadata.txt отсутствует!")
        # TODO: предложить создать ? получится для любой флешки ? нет. Наличие метафайла - признак резервного хранилища
        return

    # Чтение метаданных
    metadata = read_metadata(metadata_file)

    # Поиск флешки
    flash_drive_path = get_flash_drive()
    # if not flash_drive_path:
    #     print("Флешка не найдена!")
    #     return

    # Проверка файлов на флешке
    print("\nПроверка файлов:")
    check_files_on_flash_drive(metadata, flash_drive_path)

    # Запрос выбора файлов для обновления
    choices = input(
        "\nВведите номера файлов для замены через запятую, '*' для всех, '-' для пропуска: "
    ).strip().split(",")
    # TODO: + добавить новый файл на резервирование(+) + удалить файл из списка (-) + поменять (-) на (0)
    # TODO: зациклить до (0), (-) или списка цифр
    if "-" in choices:
        print("Операция отменена.")
        return

    # Обновление файлов на флешке
    update_files(metadata, flash_drive_path, choices, metadata_file)


if __name__ == "__main__":
    main()
