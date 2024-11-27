from io import StringIO
import pytest
from unittest.mock import Mock
from createMetadataFile import calculate_file_hash, get_default_metadata_path, write_metadata_entry, \
    add_source_file  # Импорт функций из createMetadataFile.py
import unittest
from unittest.mock import patch, mock_open
import os
import datetime
import hashlib
from datetime import datetime


# Тестирование функции calculate_file_hash
def test_calculate_file_hash():
    # Подготовим тестовый файл с содержимым
    test_file_path = 'test.txt'
    test_data = b"Hello, World!"
    with open(test_file_path, 'wb') as f:
        f.write(test_data)

    # Вычисляем хеш и проверяем
    result = calculate_file_hash(test_file_path)
    expected_hash = hashlib.md5(test_data).hexdigest()

    assert result == expected_hash

    # Удаляем файл после теста
    os.remove(test_file_path)

#
# # Тестирование функции get_default_metadata_path
# def test_get_default_metadata_path():
#     expected_path = os.path.join(os.path.expanduser("~"), "Desktop", "filesToBackUp.txt")
#     result = get_default_metadata_path()
#
#     assert result == expected_path
#
#


class TestWriteMetadataEntry(unittest.TestCase):
    def test_write_metadata_entry(self):
        # Создаем временный файл в памяти
        meta_file = StringIO()

        # Данные для тестирования
        name = "test_file.txt"
        from_path = "/source/test_file.txt"
        modified = "2023-10-01 12:00:00"
        to_path = "/backup/test_file.txt"
        backup_date = "2023-10-02"
        size = 1024
        file_hash = "abc123hash"

        # Вызов тестируемой функции
        write_metadata_entry(
            meta_file,
            name=name,
            from_path=from_path,
            modified=modified,
            to_path=to_path,
            backup_date=backup_date,
            size=size,
            file_hash=file_hash
        )

        # Получаем содержимое временного файла
        output = meta_file.getvalue()

        # Ожидаемый результат
        expected_output = (
                f"Name: {name}\n"
                f"From: {from_path}\n"
                f"Modified: {modified}\n"
                f"To: {to_path}\n"
                f"Backup: {backup_date}\n"
                f"Size: {size} bytes\n"
                f"Hash: {file_hash}\n"
                + "-" * 40 + "\n"
        )

        # Проверяем, совпадает ли вывод с ожидаемым
        self.assertEqual(output, expected_output)


# Тестирование функции add_source_file с мокированием диалогов




class TestAddSourceFile(unittest.TestCase):
    @patch("tkinter.filedialog.askopenfilename", return_value="C:\\path\\to\\source_file.txt")
    @patch("tkinter.filedialog.asksaveasfilename", return_value="C:\\path\\to\\metadata.txt")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=False)  # Файл метаданных не существует (создаём новый)
    @patch("createMetadataFile.get_default_metadata_path", return_value="C:\\default\\metadata.txt")
    @patch("createMetadataFile.calculate_file_hash", return_value=hashlib.md5(b"").hexdigest())
    def test_create_new_metadata_file(self, mock_get_default_path, mock_calculate_hash, mock_exists, mock_open_file,
                                      mock_saveas, mock_openfile):
        # Вызов функции
        add_source_file()

        # Проверяем, что файл открылся на запись
        mock_open_file.assert_called_once_with("C:\\path\\to\\metadata.txt", "w")

        # Проверяем содержимое, которое было записано в файл
        handle = mock_open_file()
        handle.write.assert_any_call("Name: metadata.txt\n")
        handle.write.assert_any_call("From: C:\\path\\to\\metadata.txt\n")
        handle.write.assert_any_call("Modified: null\n")
        handle.write.assert_any_call("To: null\n")
        handle.write.assert_any_call("Backup: null\n")
        handle.write.assert_any_call(f"Size: 0 bytes\n")  # Изменение на "bytes"
        handle.write.assert_any_call(f"Hash: {hashlib.md5(b'').hexdigest()}\n")

    @patch("tkinter.filedialog.askopenfilename", return_value="C:\\path\\to\\source_file.txt")
    @patch("tkinter.filedialog.asksaveasfilename", return_value="C:\\path\\to\\metadata.txt")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=True)  # Файл метаданных уже существует
    @patch("createMetadataFile.get_default_metadata_path", return_value="C:\\default\\metadata.txt")
    @patch("createMetadataFile.calculate_file_hash", return_value=hashlib.md5(b"test content").hexdigest())
    def test_add_source_to_existing_metadata_file(self, mock_get_default_path, mock_calculate_hash, mock_exists,
                                                  mock_open_file, mock_saveas, mock_openfile):
        # Мокаем возвращение размера и времени изменения файла
        mock_timestamp = 1691691600  # Примерное время
        with patch("os.path.getsize", return_value=12345), \
             patch("os.path.getmtime", return_value=mock_timestamp):  # Timestamp для теста
            add_source_file()

        # Форматируем дату в нужный вид
        modified_time = datetime.fromtimestamp(mock_timestamp).strftime('%Y-%m-%d %H:%M:%S')

        # Проверяем, что файл открылся для добавления
        mock_open_file.assert_called_once_with("C:\\path\\to\\metadata.txt", "a")

        # Проверяем содержимое, которое было записано в файл
        handle = mock_open_file()
        handle.write.assert_any_call("Name: source_file.txt\n")
        handle.write.assert_any_call("From: C:\\path\\to\\source_file.txt\n")
        handle.write.assert_any_call(f"Modified: {modified_time}\n")  # Дата в нужном формате
        handle.write.assert_any_call("To: null\n")
        handle.write.assert_any_call("Backup: null\n")
        handle.write.assert_any_call("Size: 12345 bytes\n")  # Изменение на "bytes"
        handle.write.assert_any_call(f"Hash: {hashlib.md5(b'test content').hexdigest()}\n")

if __name__ == '__main__':
    unittest.main()