import os
import datetime
import winreg  # Для работы с реестром Windows
from backup_manager import BackupManager


def set_environment_variable_to_program_path():
    """Установка переменной среды с путем к программе."""
    program_folder = os.path.dirname(os.path.abspath(__file__))
    env_var_name = "AUTOMATIC_BACKUP_TO_FLASH_DRIVE"

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Environment",
                            0,
                            winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, env_var_name, 0, winreg.REG_SZ, program_folder)
        os.system(f"setx {env_var_name} \"{program_folder}\" > nul 2>&1")
        print(f"Переменная окружения {env_var_name} установлена: {program_folder}")
    except Exception as e:
        print(f"Ошибка при установке переменной окружения: {e}")


def create_initial_backup_info():
    """Первоначальная настройка файла резервирования."""
    backup_manager = BackupManager()

    if backup_manager.check_backup_info_exists():
        print("Файл резервирования уже существует.")
        return

    print("Создаем файл резервирования...")
    backup_manager.create_initial_backup_info()

    # Добавляем запись о самом файле резервирования
    backup_file_path = os.path.abspath(backup_manager.backup_file)
    entry = {
        "Name": os.path.basename(backup_file_path),
        "From": backup_file_path,
        "Modified": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "To": "/",
        "Backup": "never",
        "Size": os.path.getsize(backup_file_path),
        "Hash": backup_manager.calculate_file_hash(backup_file_path),
    }
    backup_manager.add_new_entry(entry)
    print(f"Файл {backup_file_path} добавлен в резервирование.")


if __name__ == "__main__":
    set_environment_variable_to_program_path()
    create_initial_backup_info()
