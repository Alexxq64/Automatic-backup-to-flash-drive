import os
import shutil
import psutil
from win32gui import GetOpenFileNameW
from backup_manager import BackupManager  # Предполагается, что ваш BackupManager уже существует


def get_flash_drive():
    """Определяет первую подключенную флешку."""
    partitions = psutil.disk_partitions()
    for partition in partitions:
        if 'removable' in partition.opts.lower():
            return partition.device
    return None


def auto_backup():
    """Основная логика автоматического резервирования."""
    flash_drive_path = get_flash_drive()
    if not flash_drive_path:
        print("Флешка не обнаружена. Завершение работы.")
        return

    flash_drive_backup = os.path.join(flash_drive_path, "backup_info.txt")
    local_backup = "backup_info.txt"

    backup_manager = BackupManager()

    if not backup_manager.check_backup_info_exists():
        print("Локальный файл резервирования отсутствует. Копируем с флешки...")
        shutil.copy2(flash_drive_backup, local_backup)
        print("Файл резервирования успешно скопирован с флешки.")
    else:
        print("Локальный файл резервирования найден. Используем его.")

    entries = backup_manager.read_backup_info()
    changes = []
    for entry in entries:
        source_file = entry['From']
        target_file = os.path.join(flash_drive_path, entry['To'], entry['Name'])

        if not os.path.exists(source_file):
            changes.append((entry, "Пропущен (файл отсутствует)"))
            continue

        if os.path.exists(target_file):
            source_modified = os.path.getmtime(source_file)
            target_modified = os.path.getmtime(target_file)
            if source_modified > target_modified:
                changes.append((entry, "Обновить"))
            else:
                changes.append((entry, "Актуален"))
        else:
            changes.append((entry, "Добавить"))

    if not changes:
        print("Все файлы актуальны. Резервирование не требуется.")
        return

    while True:
        print("\nСписок файлов:")
        for idx, (entry, status) in enumerate(changes, start=1):
            print(f"{idx}. {entry['Name']} - {status}")

        print("\nМеню:")
        print("1 <N> <N>... - Обновить выбранные файлы (укажите номера через пробел).")
        print("* - Обновить все файлы.")
        print("+ - Добавить новый файл.")
        print("- - Удалить файл из списка резервирования.")
        print("0 - Завершить программу.")

        user_input = input("Выберите действие: ").strip()
        if user_input == "0":
            print("Завершение программы.")
            break
        elif user_input.startswith("1"):
            try:
                file_indices = list(map(int, user_input.split()[1:]))
                update_selected_files(file_indices, changes, backup_manager, flash_drive_path)
            except ValueError:
                print("Неверный ввод. Попробуйте снова.")
        elif user_input == "*":
            update_all_files(changes, backup_manager, flash_drive_path)
        elif user_input == "+":
            add_new_file(backup_manager)
            changes = refresh_changes(backup_manager, flash_drive_path)
        elif user_input == "-":
            remove_file_from_backup(backup_manager)
            changes = refresh_changes(backup_manager, flash_drive_path)
        else:
            print("Неверный ввод. Попробуйте снова.")


def update_selected_files(file_indices, changes, backup_manager, flash_drive_path):
    """Обновление выбранных файлов."""
    for idx in file_indices:
        if idx < 1 or idx > len(changes):
            print(f"Файл с номером {idx} отсутствует в списке.")
            continue
        entry, status = changes[idx - 1]
        if status in ("Добавить", "Обновить"):
            copy_file(entry, backup_manager, flash_drive_path)
    print("Выбранные файлы обновлены.")


def update_all_files(changes, backup_manager, flash_drive_path):
    """Обновление всех файлов."""
    for entry, status in changes:
        if status in ("Добавить", "Обновить"):
            copy_file(entry, backup_manager, flash_drive_path)
    print("Все файлы обновлены.")


def copy_file(entry, backup_manager, flash_drive_path):
    """Копирование файла на флешку."""
    source_file = entry['From']
    target_file = os.path.join(flash_drive_path, entry['To'], entry['Name'])
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    shutil.copy2(source_file, target_file)
    print(f"Файл {entry['Name']} скопирован на флешку.")


import win32gui
import win32con
import os


def add_new_file(backup_manager):
    """Добавление нового файла в резервирование."""

    # Перемещение текущего окна на передний план
    current_window = win32gui.GetForegroundWindow()

    # Попытка показать окно на переднем плане
    win32gui.ShowWindow(current_window, win32con.SW_RESTORE)  # Восстановление окна, если оно свернуто
    win32gui.SetForegroundWindow(current_window)  # Переводим на передний план

    # Конфигурация диалога выбора файла
    options = {
        "Filter": "All Files\0*.*\0",
        "Title": "Выберите файл для резервирования",
        "File": "",
    }

    try:
        result = win32gui.GetOpenFileNameW(**options)
        if not result:
            print("Файл не выбран.")
            return

        # Обработка возвращенного результата (может быть строка или кортеж)
        if isinstance(result, tuple):
            file_path = result[0]  # Путь к файлу в первом элементе кортежа
        else:
            file_path = result  # Если результат уже строка
    except Exception as e:
        print(f"Ошибка при выборе файла: {e}")
        return

    if not file_path:
        print("Файл не выбран.")
        return

    # Создание нового элемента резервирования
    entry = {
        "Name": os.path.basename(file_path),
        "From": file_path,
        "Modified": os.path.getmtime(file_path),
        "To": "/",
        "Backup": "never",
        "Size": os.path.getsize(file_path),
        "Hash": backup_manager.calculate_file_hash(file_path),
    }
    if backup_manager.add_new_entry(entry):
        print(f"Файл {entry['Name']} добавлен в резервирование.")
    else:
        print(f"Ошибка при добавлении файла {entry['Name']} в резервирование.")


def remove_file_from_backup(backup_manager):
    """Удаление файла из резервирования."""
    entries = backup_manager.read_backup_info()
    print("\nФайлы в резервировании:")
    for idx, entry in enumerate(entries, start=1):
        print(f"{idx}. {entry['Name']}")

    try:
        file_index = int(input("Введите номер файла для удаления: ").strip())
        if 1 <= file_index <= len(entries):
            removed_entry = entries.pop(file_index - 1)
            backup_manager.write_backup_info(entries)
            print(f"Файл {removed_entry['Name']} удален из резервирования.")
        else:
            print("Неверный номер. Попробуйте снова.")
    except ValueError:
        print("Неверный ввод. Попробуйте снова.")


def refresh_changes(backup_manager, flash_drive_path):
    """Обновить список изменений после добавления или удаления."""
    entries = backup_manager.read_backup_info()
    changes = []
    for entry in entries:
        source_file = entry['From']
        target_file = os.path.join(flash_drive_path, entry['To'], entry['Name'])

        if not os.path.exists(source_file):
            changes.append((entry, "Пропущен (файл отсутствует)"))
            continue

        if os.path.exists(target_file):
            source_modified = os.path.getmtime(source_file)
            target_modified = os.path.getmtime(target_file)
            if source_modified > target_modified:
                changes.append((entry, "Обновить"))
            else:
                changes.append((entry, "Актуален"))
        else:
            changes.append((entry, "Добавить"))
    return changes


if __name__ == "__main__":
    auto_backup()
