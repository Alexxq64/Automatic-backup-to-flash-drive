import os
import hashlib


class BackupManager:
    def __init__(self):
        """Инициализация менеджера резервирования."""
        self.backup_file = "backup_info.txt"

    def check_backup_info_exists(self):
        """Проверка наличия файла резервирования."""
        return os.path.exists(self.backup_file)

    def create_initial_backup_info(self):
        """Создание начального файла резервирования."""
        with open(self.backup_file, 'w', encoding='utf-8') as file:
            file.write("")
        print(f"Файл {self.backup_file} создан.")

    def read_backup_info(self):
        """Чтение содержимого файла резервирования."""
        if not self.check_backup_info_exists():
            return []
        with open(self.backup_file, 'r', encoding='utf-8') as file:
            entries = file.read().strip().split("\n\n")
        return [self._parse_entry(entry) for entry in entries if entry.strip()]

    def write_backup_info(self, entries):
        """Запись данных в файл резервирования."""
        with open(self.backup_file, 'w', encoding='utf-8') as file:
            file.write("\n\n".join(self._format_entry(entry) for entry in entries))

    def add_new_entry(self, entry):
        """Добавление новой записи в резервирование."""
        entries = self.read_backup_info()
        if any(e['Name'] == entry['Name'] for e in entries):
            print(f"Запись с именем {entry['Name']} уже существует.")
            return False
        # Добавляем поле `To`, если оно отсутствует
        if 'To' not in entry or not entry['To']:
            entry['To'] = "/"  # По умолчанию, корень флешки
        entries.append(entry)
        self.write_backup_info(entries)
        print(f"Файл {entry['Name']} добавлен в резервирование.")
        return True

    def calculate_file_hash(self, file_path):
        """Вычисление хэша SHA256 для файла."""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except FileNotFoundError:
            print(f"Файл {file_path} не найден.")
            return None

    def get_flash_drive_path(self, entry):
        """Получение полного пути файла на флешке."""
        folder = entry['To'].rstrip('/')
        return os.path.join(folder, entry['Name'])

    def _parse_entry(self, raw_entry):
        """Парсинг одной записи."""
        lines = raw_entry.split("\n")
        return {line.split(": ", 1)[0]: line.split(": ", 1)[1] for line in lines}

    def _format_entry(self, entry):
        """Форматирование записи для сохранения."""
        return "\n".join(f"{key}: {value}" for key, value in entry.items())
