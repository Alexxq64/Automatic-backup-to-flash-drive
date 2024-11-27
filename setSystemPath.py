import os
import winreg  # Работа с реестром Windows

def set_environment_variable_to_program_path():
    program_folder = os.path.dirname(os.path.abspath(__file__))
    env_var_name = "AUTOMATIC_BACKUP_TO_FLASH_DRIVE"

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Environment",  # Раздел реестра для переменных окружения
                            0,
                            winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, env_var_name, 0, winreg.REG_SZ, program_folder)
        os.system(f"setx {env_var_name} \"{program_folder}\" > nul 2>&1")
        print(f"Переменная окружения {env_var_name} установлена: {program_folder}")
    except Exception as e:
        print(f"Ошибка при установке переменной окружения: {e}")


def main():
    set_environment_variable_to_program_path()
if __name__ == "__main__":
    main()
