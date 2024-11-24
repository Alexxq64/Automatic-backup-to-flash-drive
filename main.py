import os
import shutil
import psutil
from datetime import datetime

# Путь к файлу с адресами и именами файлов
file_list_path = r"C:\Users\User\Desktop\Work\file_list.txt"  # Сырой путь


# Читаем список файлов из указанного файла
def read_file_list(file_list_path):
    file_list = []
    if not os.path.exists(file_list_path):
        print(f"Файл списка не найден: {file_list_path}")
        return file_list
    with open(file_list_path, "r") as file:
        for line in file:
            file = line.strip()
            if file:
                file_list.append(file)
    return file_list


# Поиск подключенной флешки
def get_flash_drive():
    partitions = psutil.disk_partitions()
    for partition in partitions:
        if 'removable' in partition.opts:
            return partition.device
    return None


# Сравнение файлов по дате изменения
def is_newer(source_file, target_file):
    return os.path.getmtime(source_file) > os.path.getmtime(target_file)


# Основная логика обновления файлов
def update_files(file_list, flash_drive):
    update_candidates = []  # Файлы для обновления
    skipped_files = []      # Пропущенные файлы (актуальные)

    for source_file in file_list:
        if not os.path.exists(source_file):
            print(f"Файл не найден: {source_file}")
            continue

        # Генерируем путь на флешке (только имя файла)
        target_file = os.path.join(flash_drive, os.path.basename(source_file))

        # Проверяем наличие файла на флешке
        if os.path.exists(target_file):
            if is_newer(source_file, target_file):
                update_candidates.append((source_file, target_file))
            else:
                skipped_files.append((source_file, target_file))
        else:
            update_candidates.append((source_file, target_file))

    # Вывод пропущенных файлов
    if skipped_files:
        print("Пропущенные файлы (актуальны на флешке):")
        for source, target in skipped_files:
            print(f"- {source} -> {target}")

    # Если нет файлов для обновления
    if not update_candidates:
        print("Все файлы на флешке актуальны.")
        return

    # Вывод списка файлов для обновления
    print("Список файлов для обновления:")
    for idx, (source, target) in enumerate(update_candidates, start=1):
        print(f"{idx}. {source} -> {target}")

    # Предложение пользователю выбрать файлы для копирования
    print("Введите номера файлов для обновления через запятую (или '*' для копирования всех, или '-' для пропуска): ")
    choice = input().strip()

    # Обработка выбора
    if not choice or choice in {'-', '0'}:  # Если ввод пустой, '-' или '0'
        print("Копирование файлов отменено.")
        return

    if choice == '*':  # Проверяем ввод '*'
        selected_indices = range(1, len(update_candidates) + 1)  # Выбираем все файлы
    else:
        try:
            selected_indices = [int(num.strip()) for num in choice.split(',') if num.strip().isdigit()]
        except ValueError:
            print("Ошибка: ввод некорректен. Ожидались номера файлов через запятую.")
            return

    # Копирование выбранных файлов
    for idx in selected_indices:
        if 1 <= idx <= len(update_candidates):
            source, target = update_candidates[idx - 1]
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copy2(source, target)
            print(f"Файл скопирован: {source} -> {target}")
        else:
            print(f"Предупреждение: номер {idx} не существует в списке.")


# Главная функция
def main():
    print(f"[{datetime.now()}] Проверка подключения флешки...")
    flash_drive = get_flash_drive()

    if not flash_drive:
        print("Флешка не подключена.")
        return

    print(f"Флешка обнаружена: {flash_drive}")
    file_list = read_file_list(file_list_path)

    if not file_list:
        print("Список файлов пуст или не найден.")
        return

    update_files(file_list, flash_drive)


if __name__ == "__main__":
    main()
