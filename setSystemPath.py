import os
import winreg  # Работа с реестром Windows
import win32com.client


def set_environment_variable_to_program_path():
    """
    Устанавливает переменную окружения AUTOMATIC_BACKUP_TO_FLASH_DRIVE
    с путём к папке, где находится текущая программа.
    """
    # Определяем путь к папке, где находится программа
    program_folder = os.path.dirname(os.path.abspath(__file__))
    env_var_name = "AUTOMATIC_BACKUP_TO_FLASH_DRIVE"

    try:
        # Записываем переменную окружения в реестр
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Environment",
                            0,
                            winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, env_var_name, 0, winreg.REG_SZ, program_folder)

        # Устанавливаем переменную окружения для текущей сессии
        os.system(f"setx {env_var_name} \"{program_folder}\"")
        print(f"Переменная окружения {env_var_name} установлена: {program_folder}")
    except Exception as e:
        print(f"Ошибка при установке переменной окружения: {e}")




def list_scheduled_tasks():
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()
    root_folder = scheduler.GetFolder('\\')
    tasks = root_folder.GetTasks(0)
    for task in tasks:
        print(f"Task Name: {task.Name}")


def main():
    # Установить переменную окружения, если она ещё не существует
    set_environment_variable_to_program_path()


if __name__ == "__main__":
    main()
