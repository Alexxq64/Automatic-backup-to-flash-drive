import win32com.client

def list_scheduled_tasks():
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()
    root_folder = scheduler.GetFolder('\\')
    tasks = root_folder.GetTasks(0)
    for task in tasks:
        print(f"Task Name: {task.Name}")



def list_scheduled_tasks1():
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()
    root_folder = scheduler.GetFolder('\\')

    def list_tasks_in_folder(folder, prefix=""):
        tasks = folder.GetTasks(0)
        for task in tasks:
            print(f"{prefix}Task Name: {task.Name}")

        subfolders = folder.GetFolders(0)
        for subfolder in subfolders:
            list_tasks_in_folder(subfolder, prefix=prefix + "  ")

    list_tasks_in_folder(root_folder)


def duplicate_task(old_task_name, new_task_name):
    """
    Дублирует существующую задачу Планировщика Windows с новым именем
    и отключает настройку "Запускать при электропитании от сети".
    
    :param old_task_name: Имя существующей задачи.
    :param new_task_name: Имя для новой задачи.
    """
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()
    root_folder = scheduler.GetFolder('\\')

    # Поиск существующей задачи
    old_task = None
    tasks = root_folder.GetTasks(0)
    for task in tasks:
        if task.Name == old_task_name:
            old_task = task
            break

    if not old_task:
        print(f"Задача с именем '{old_task_name}' не найдена.")
        return

    # Создание новой задачи на основе старой
    new_task = scheduler.NewTask(0)
    new_task.RegistrationInfo.Description = old_task.Definition.RegistrationInfo.Description
    new_task.Principal.UserId = old_task.Definition.Principal.UserId
    new_task.Principal.LogonType = old_task.Definition.Principal.LogonType

    # Копируем триггеры
    for trigger in old_task.Definition.Triggers:
        new_trigger = new_task.Triggers.Create(trigger.Type)
        new_trigger.Id = trigger.Id
        new_trigger.Enabled = trigger.Enabled
        new_trigger.Subscription = trigger.Subscription  # Для событий, таких как 2003 (подключение флешки)

    # Копируем действия
    for action in old_task.Definition.Actions:
        new_action = new_task.Actions.Create(action.Type)
        new_action.Path = action.Path
        new_action.Arguments = action.Arguments
        new_action.WorkingDirectory = action.WorkingDirectory

    # Копируем параметры задачи
    new_task.Settings.Enabled = old_task.Definition.Settings.Enabled
    new_task.Settings.StartWhenAvailable = old_task.Definition.Settings.StartWhenAvailable
    new_task.Settings.Hidden = old_task.Definition.Settings.Hidden
    new_task.Settings.DisallowStartIfOnBatteries = False  # Отключаем "Запуск только при подключении к сети"
    new_task.Settings.StopIfGoingOnBatteries = False  # Не останавливать задачу при переходе на батарею

    # Регистрация новой задачи
    root_folder.RegisterTaskDefinition(
        new_task_name,
        new_task,
        6,  # TASK_CREATE_OR_UPDATE
        None,
        None,
        old_task.Definition.Principal.LogonType,
        None
    )
    print(f"Задача '{old_task_name}' успешно продублирована как '{new_task_name}'.")

# Пример вызова функции
duplicate_task("Резервное копирование на флешку", "USBBackupTask")





def create_USB_backup_task():
    # Подключение к Планировщику задач
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()
    
    # Папка для размещения задачи
    tasks_folder = scheduler.GetFolder("\\")
    
    # Удаляем задачу, если она уже существует
    task_name = "USBBackupTask"
    try:
        tasks_folder.DeleteTask(task_name, 0)
        print(f"Задача '{task_name}' уже существует, будет заменена.")
    except Exception:
        print(f"Задача '{task_name}' не существует, будет создана.")

    # Создание новой задачи
    this_task = scheduler.NewTask(0)
    
    # Настройки задачи
    this_task.RegistrationInfo.Description = "Резервное копирование на флешку"
    this_task.Principal.LogonType = 3  # Сохранение учетных данных
    
    # Настройка триггера (простая настройка)
    trigger = this_task.Triggers.Create(0)  # Тип: При событии
    trigger.Id = "EventTrigger1"
    trigger.Enabled = True
    trigger.Subscription = (
        "<QueryList>"
        "  <Query Id='0' Path='Microsoft-Windows-DriverFrameworks-UserMode/Operational'>"
        "    <Select Path='Microsoft-Windows-DriverFrameworks-UserMode/Operational'>"
        "      *[System[(EventID=2003)]]"
        "    </Select>"
        "  </Query>"
        "</QueryList>"
    )
    
    # Настройка действия
    action = this_task.Actions.Create(0)  # Тип действия: Запуск программы
    action.Path = r"C:\Users\User\AppData\Local\Programs\Python\Python38-32\python.exe"
    action.Arguments = r"C:\Users\User\Desktop\Python\Projects\Automatic-backup-to-flash-drive\main.py"

    # Устанавливаем настройки
    settings = this_task.Settings
    settings.Enabled = True
    settings.StartWhenAvailable = True
    settings.StopIfGoingOnBatteries = False  # Снимаем галочку "запускать только при электропитании"
    settings.DisallowStartIfOnBatteries = False  # Тоже снимаем ограничение для батареи
    
    # Регистрируем задачу
    try:
        tasks_folder.RegisterTaskDefinition(
            task_name,
            this_task,
            6,  # CREATE_OR_UPDATE
            None,  # Пользователь
            None,  # Пароль
            3,  # LogonType: S4U
        )
        print(f"Задача '{task_name}' успешно создана или обновлена!")
    except Exception as e:
        print(f"Ошибка при создании задачи: {e}")

# Запуск процедуры
create_USB_backup_task()
