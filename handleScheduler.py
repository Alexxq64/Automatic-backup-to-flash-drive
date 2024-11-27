import win32com.client

def list_scheduled_tasks():
    """
    🔍 **Описание:**
    Выводит список всех задач, зарегистрированных в корневой папке Планировщика задач Windows.

    🛠 **Как работает:**
    - Подключается к Планировщику задач через COM-интерфейс.
    - Получает доступ к корневой папке задач.
    - Перечисляет все задачи в этой папке и выводит их имена.

    📋 **Что делает:**
    - Выводит список задач в формате: `Task Name: <имя_задачи>`.

    ⚠ **Ограничения:**
    - Работает только с задачами в корневой папке (подпапки не анализируются).
    - Требует установленной библиотеки `pywin32`.

    📌 **Пример использования:**
    >>> list_scheduled_tasks()
    Task Name: MyBackupTask
    Task Name: SystemMaintenance
    Task Name: UpdateChecker

    📚 **Требования:**
    - Windows OS с поддержкой Планировщика задач.
    - Установленный модуль `pywin32`.
    """

    # 🌟 Подключаемся к Планировщику задач
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()

    # 📂 Получаем доступ к корневой папке задач
    root_folder = scheduler.GetFolder('\\')

    # 🔄 Перебираем задачи в корневой папке
    tasks = root_folder.GetTasks(0)
    for task in tasks:
        # 📌 Выводим имя каждой задачи
        print(f"Task Name: {task.Name}")



def list_all_scheduled_tasks():
    """
    🔍 **Описание:**
    Выводит список всех задач, зарегистрированных в Планировщике задач Windows, включая задачи в подпапках.

    🛠 **Как работает:**
    - Подключается к Планировщику задач через COM-интерфейс.
    - Рекурсивно обходит корневую папку задач и все вложенные подпапки.
    - Выводит имена всех найденных задач, добавляя отступы для визуализации иерархии папок.

    📋 **Что делает:**
    - Выводит список задач с учетом вложенности в формате:
        ```
        Task Name: RootTask1
          Task Name: SubFolderTask1
          Task Name: SubFolderTask2
        ```

    ⚠ **Ограничения:**
    - Требует установленной библиотеки `pywin32`.

    📌 **Пример использования:**
    >>> list_all_scheduled_tasks()
    Task Name: BackupTask
      Task Name: MaintenanceTask
        Task Name: UpdateChecker

    📚 **Требования:**
    - Windows OS с поддержкой Планировщика задач.
    - Установленный модуль `pywin32`.
    """

    # 🌟 Подключаемся к Планировщику задач
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()

    # 📂 Получаем доступ к корневой папке задач
    root_folder = scheduler.GetFolder('\\')

    # 🌀 Рекурсивная функция для обхода папок и их задач
    def list_tasks_in_folder(folder, prefix=""):
        # 🔄 Перебираем задачи в текущей папке
        tasks = folder.GetTasks(0)
        for task in tasks:
            # 📌 Выводим имя каждой задачи с отступом
            print(f"{prefix}Task Name: {task.Name}")

        # 📂 Перебираем подпапки
        subfolders = folder.GetFolders(0)
        for subfolder in subfolders:
            # 🔁 Рекурсивно вызываем функцию для подпапок
            list_tasks_in_folder(subfolder, prefix=prefix + "  ")

    # 🔄 Запускаем рекурсивный обход с корневой папки
    list_tasks_in_folder(root_folder)


def duplicate_task(old_name, new_name):
    """
    🔄 **Описание:**
    Дублирует существующую задачу в Планировщике задач Windows с новым именем. 
    При дублировании убираются ограничения на запуск задачи только при электропитании.

    📋 **Что делает:**
    - Ищет задачу по указанному имени (`old_name`).
    - Создает новую задачу с указанным именем (`new_name`).
    - Копирует настройки, триггеры, и действия из старой задачи.
    - Отключает параметры, связанные с ограничениями питания.

    ⚠ **Ограничения:**
    - Если задача с именем `old_name` не найдена, выполнение прекращается.
    - Требуется установленная библиотека `pywin32`.

    📌 **Пример использования:**
    >>> duplicate_task("Резервное копирование", "Резервное копирование (новое)")

    📚 **Требования:**
    - Windows OS с поддержкой Планировщика задач.
    - Установленный модуль `pywin32`.
    """

    # 🌟 Подключаемся к Планировщику задач
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()
    tasks_folder = scheduler.GetFolder('\\')  # 📂 Получаем доступ к корневой папке задач

    # 🔍 Поиск существующей задачи по имени
    old_task = None
    tasks = tasks_folder.GetTasks(0)
    for task in tasks:
        if task.Name == old_name:
            old_task = task
            break

    if not old_task:
        # ❌ Завершаем, если задача не найдена
        print(f"Задача с именем '{old_name}' не найдена.")
        return

    # ✨ Создаем новую задачу на основе старой
    new_task = scheduler.NewTask(0)
    new_task.RegistrationInfo.Description = old_task.Definition.RegistrationInfo.Description  # 📝 Описание
    new_task.Principal.UserId = old_task.Definition.Principal.UserId  # 👤 Пользователь
    new_task.Principal.LogonType = old_task.Definition.Principal.LogonType  # 🔒 Тип входа

    # 🔄 Копируем триггеры из старой задачи
    for trigger in old_task.Definition.Triggers:
        new_trigger = new_task.Triggers.Create(trigger.Type)
        new_trigger.Id = trigger.Id  # 🆔 Идентификатор триггера
        new_trigger.Enabled = trigger.Enabled  # ✅ Активность триггера
        new_trigger.Subscription = trigger.Subscription  # 📜 Подписка на событие (например, EventID=2003)

    # 🔄 Копируем действия из старой задачи
    for action in old_task.Definition.Actions:
        new_action = new_task.Actions.Create(action.Type)
        new_action.Path = action.Path  # 🛠 Путь к исполняемому файлу
        new_action.Arguments = action.Arguments  # ⚙ Аргументы команды
        new_action.WorkingDirectory = action.WorkingDirectory  # 📂 Рабочая директория

    # 🔧 Копируем параметры задачи
    new_task.Settings.Enabled = old_task.Definition.Settings.Enabled  # ✅ Задача включена
    new_task.Settings.StartWhenAvailable = old_task.Definition.Settings.StartWhenAvailable  # 🕒 Запуск, когда доступно
    new_task.Settings.Hidden = old_task.Definition.Settings.Hidden  # 👁‍🗨 Задача скрыта
    new_task.Settings.DisallowStartIfOnBatteries = False  # 🔋 Разрешить запуск на батарее
    new_task.Settings.StopIfGoingOnBatteries = False  # 🔋 Не останавливать на батарее

    # 📝 Регистрируем новую задачу
    tasks_folder.RegisterTaskDefinition(
        new_name,  # 📌 Новое имя задачи
        new_task,
        6,  # 📂 TASK_CREATE_OR_UPDATE (создание или обновление)
        None,  # 🔑 Пользователь не указан
        None,  # 🔑 Пароль не указан
        old_task.Definition.Principal.LogonType,  # 🔒 Тип входа
        None  # Дополнительные данные
    )
    # ✅ Сообщаем об успешном выполнении
    print(f"Задача '{old_name}' успешно продублирована как '{new_name}'.")



def create_USB_backup_task():
    # Подключение к Планировщику задач
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()
    
    # Папка для размещения задачи
    main_folder = scheduler.GetFolder("\\")
    
    # Удаляем задачу, если она уже существует
    task_name = "USBBackupTask"
    try:
        main_folder.DeleteTask(task_name, 0)
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
        main_folder.RegisterTaskDefinition(
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
# create_USB_backup_task()

list_scheduled_tasks()
import win32com.client

def list_scheduled_tasks():
    """
    🔍 **Описание:**
    Выводит список всех задач, зарегистрированных в корневой папке Планировщика задач Windows.

    🛠 **Как работает:**
    - Подключается к Планировщику задач через COM-интерфейс.
    - Получает доступ к корневой папке задач.
    - Перечисляет все задачи в этой папке и выводит их имена.

    📋 **Что делает:**
    - Выводит список задач в формате: `Task Name: <имя_задачи>`.

    ⚠ **Ограничения:**
    - Работает только с задачами в корневой папке (подпапки не анализируются).
    - Требует установленной библиотеки `pywin32`.

    📌 **Пример использования:**
    >>> list_scheduled_tasks()
    Task Name: MyBackupTask
    Task Name: SystemMaintenance
    Task Name: UpdateChecker

    📚 **Требования:**
    - Windows OS с поддержкой Планировщика задач.
    - Установленный модуль `pywin32`.
    """

    # 🌟 Подключаемся к Планировщику задач
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()

    # 📂 Получаем доступ к корневой папке задач
    root_folder = scheduler.GetFolder('\\')

    # 🔄 Перебираем задачи в корневой папке
    tasks = root_folder.GetTasks(0)
    for task in tasks:
        # 📌 Выводим имя каждой задачи
        print(f"Task Name: {task.Name}")



def list_all_scheduled_tasks():
    """
    🔍 **Описание:**
    Выводит список всех задач, зарегистрированных в Планировщике задач Windows, включая задачи в подпапках.

    🛠 **Как работает:**
    - Подключается к Планировщику задач через COM-интерфейс.
    - Рекурсивно обходит корневую папку задач и все вложенные подпапки.
    - Выводит имена всех найденных задач, добавляя отступы для визуализации иерархии папок.

    📋 **Что делает:**
    - Выводит список задач с учетом вложенности в формате:
        ```
        Task Name: RootTask1
          Task Name: SubFolderTask1
          Task Name: SubFolderTask2
        ```

    ⚠ **Ограничения:**
    - Требует установленной библиотеки `pywin32`.

    📌 **Пример использования:**
    >>> list_all_scheduled_tasks()
    Task Name: BackupTask
      Task Name: MaintenanceTask
        Task Name: UpdateChecker

    📚 **Требования:**
    - Windows OS с поддержкой Планировщика задач.
    - Установленный модуль `pywin32`.
    """

    # 🌟 Подключаемся к Планировщику задач
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()

    # 📂 Получаем доступ к корневой папке задач
    root_folder = scheduler.GetFolder('\\')

    # 🌀 Рекурсивная функция для обхода папок и их задач
    def list_tasks_in_folder(folder, prefix=""):
        # 🔄 Перебираем задачи в текущей папке
        tasks = folder.GetTasks(0)
        for task in tasks:
            # 📌 Выводим имя каждой задачи с отступом
            print(f"{prefix}Task Name: {task.Name}")

        # 📂 Перебираем подпапки
        subfolders = folder.GetFolders(0)
        for subfolder in subfolders:
            # 🔁 Рекурсивно вызываем функцию для подпапок
            list_tasks_in_folder(subfolder, prefix=prefix + "  ")

    # 🔄 Запускаем рекурсивный обход с корневой папки
    list_tasks_in_folder(root_folder)


def duplicate_task(old_name, new_name):
    """
    🔄 **Описание:**
    Дублирует существующую задачу в Планировщике задач Windows с новым именем. 
    При дублировании убираются ограничения на запуск задачи только при электропитании.

    📋 **Что делает:**
    - Ищет задачу по указанному имени (`old_name`).
    - Создает новую задачу с указанным именем (`new_name`).
    - Копирует настройки, триггеры, и действия из старой задачи.
    - Отключает параметры, связанные с ограничениями питания.

    ⚠ **Ограничения:**
    - Если задача с именем `old_name` не найдена, выполнение прекращается.
    - Требуется установленная библиотека `pywin32`.

    📌 **Пример использования:**
    >>> duplicate_task("Резервное копирование", "Резервное копирование (новое)")

    📚 **Требования:**
    - Windows OS с поддержкой Планировщика задач.
    - Установленный модуль `pywin32`.
    """

    # 🌟 Подключаемся к Планировщику задач
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()
    tasks_folder = scheduler.GetFolder('\\')  # 📂 Получаем доступ к корневой папке задач

    # 🔍 Поиск существующей задачи по имени
    old_task = None
    tasks = tasks_folder.GetTasks(0)
    for task in tasks:
        if task.Name == old_name:
            old_task = task
            break

    if not old_task:
        # ❌ Завершаем, если задача не найдена
        print(f"Задача с именем '{old_name}' не найдена.")
        return

    # ✨ Создаем новую задачу на основе старой
    new_task = scheduler.NewTask(0)
    new_task.RegistrationInfo.Description = old_task.Definition.RegistrationInfo.Description  # 📝 Описание
    new_task.Principal.UserId = old_task.Definition.Principal.UserId  # 👤 Пользователь
    new_task.Principal.LogonType = old_task.Definition.Principal.LogonType  # 🔒 Тип входа

    # 🔄 Копируем триггеры из старой задачи
    for trigger in old_task.Definition.Triggers:
        new_trigger = new_task.Triggers.Create(trigger.Type)
        new_trigger.Id = trigger.Id  # 🆔 Идентификатор триггера
        new_trigger.Enabled = trigger.Enabled  # ✅ Активность триггера
        new_trigger.Subscription = trigger.Subscription  # 📜 Подписка на событие (например, EventID=2003)

    # 🔄 Копируем действия из старой задачи
    for action in old_task.Definition.Actions:
        new_action = new_task.Actions.Create(action.Type)
        new_action.Path = action.Path  # 🛠 Путь к исполняемому файлу
        new_action.Arguments = action.Arguments  # ⚙ Аргументы команды
        new_action.WorkingDirectory = action.WorkingDirectory  # 📂 Рабочая директория

    # 🔧 Копируем параметры задачи
    new_task.Settings.Enabled = old_task.Definition.Settings.Enabled  # ✅ Задача включена
    new_task.Settings.StartWhenAvailable = old_task.Definition.Settings.StartWhenAvailable  # 🕒 Запуск, когда доступно
    new_task.Settings.Hidden = old_task.Definition.Settings.Hidden  # 👁‍🗨 Задача скрыта
    new_task.Settings.DisallowStartIfOnBatteries = False  # 🔋 Разрешить запуск на батарее
    new_task.Settings.StopIfGoingOnBatteries = False  # 🔋 Не останавливать на батарее

    # 📝 Регистрируем новую задачу
    tasks_folder.RegisterTaskDefinition(
        new_name,  # 📌 Новое имя задачи
        new_task,
        6,  # 📂 TASK_CREATE_OR_UPDATE (создание или обновление)
        None,  # 🔑 Пользователь не указан
        None,  # 🔑 Пароль не указан
        old_task.Definition.Principal.LogonType,  # 🔒 Тип входа
        None  # Дополнительные данные
    )
    # ✅ Сообщаем об успешном выполнении
    print(f"Задача '{old_name}' успешно продублирована как '{new_name}'.")



def create_USB_backup_task():
    """
    🔄 **Описание:**
    Создает или обновляет задачу Планировщика Windows для автоматического резервного копирования
    на флешку при ее подключении.

    📋 **Что делает:**
    - Удаляет существующую задачу с именем `USBBackupTask` (если она есть).
    - Создает новую задачу:
        - Триггер: подключение устройства (EventID 2003).
        - Действие: запуск скрипта резервного копирования.
        - Отключает ограничения на запуск при питании от батареи.

    📌 **Пример использования:**
    >>> create_USB_backup_task()

    📚 **Требования:**
    - Windows OS с Планировщиком задач.
    - Установленный модуль `pywin32`.
    - Корректный путь к исполняемому Python-скрипту.
    """

    # 🌟 Подключаемся к Планировщику задач
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()

    # 📂 Папка для задач (корневая)
    main_folder = scheduler.GetFolder("\\")

    # 🗑 Удаляем существующую задачу, если она есть
    task_name = "USBBackupTask"
    try:
        main_folder.DeleteTask(task_name, 0)
        print(f"Задача '{task_name}' уже существует, будет заменена.")
    except Exception:
        print(f"Задача '{task_name}' не существует, будет создана.")

    # ✨ Создаем новую задачу
    this_task = scheduler.NewTask(0)

    # 🔧 Настройки задачи
    this_task.RegistrationInfo.Description = "Резервное копирование на флешку"  # 📝 Описание
    this_task.Principal.LogonType = 3  # 🔒 Сохранение учетных данных (TASK_LOGON_PASSWORD)

    # 📅 Настройка триггера
    trigger = this_task.Triggers.Create(0)  # 📋 Тип: при событии
    trigger.Id = "EventTrigger1"  # 🆔 Идентификатор триггера
    trigger.Enabled = True  # ✅ Активен
    trigger.Subscription = (
        "<QueryList>"  # 🔍 Запрос событий
        "  <Query Id='0' Path='Microsoft-Windows-DriverFrameworks-UserMode/Operational'>"
        "    <Select Path='Microsoft-Windows-DriverFrameworks-UserMode/Operational'>"
        "      *[System[(EventID=2003)]]"  # 📜 EventID 2003 — подключение флешки
        "    </Select>"
        "  </Query>"
        "</QueryList>"
    )

    # ⚙ Настройка действия
    action = this_task.Actions.Create(0)  # 🛠 Тип действия: запуск программы
    action.Path = r"C:\Users\User\AppData\Local\Programs\Python\Python38-32\python.exe"  # 🐍 Путь к Python
    action.Arguments = r"C:\Users\User\Desktop\Python\Projects\Automatic-backup-to-flash-drive\main.py"  # 📜 Скрипт

    # 🔧 Устанавливаем параметры задачи
    settings = this_task.Settings
    settings.Enabled = True  # ✅ Включена
    settings.StartWhenAvailable = True  # 🕒 Запуск при доступности
    settings.StopIfGoingOnBatteries = False  # 🔋 Разрешить выполнение на батарее
    settings.DisallowStartIfOnBatteries = False  # 🔋 Снять ограничения на батарее

    # 📝 Регистрируем задачу
    try:
        main_folder.RegisterTaskDefinition(
            task_name,  # 📌 Имя задачи
            this_task,  # 🔄 Определение задачи
            6,  # TASK_CREATE_OR_UPDATE (создание или обновление)
            None,  # 🔑 Пользователь
            None,  # 🔑 Пароль
            3,  # TASK_LOGON_S4U (не требует пароля)
        )
        print(f"Задача '{task_name}' успешно создана или обновлена!")
    except Exception as e:
        # ❌ Обрабатываем ошибки
        print(f"Ошибка при создании задачи: {e}")


# Запуск процедуры
# create_USB_backup_task()

list_scheduled_tasks()
