from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PyQt5.QtWidgets import QMessageBox


class DatabaseManager:
    def __init__(self):
        self.db = None

    def connect(self, db_path):
        """Подключение к файлу базы данных SQLite."""
        # Если уже было подключение — закрываем старое
        self.close()

        # Создаём подключение через драйвер SQLite
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(db_path)

        if not self.db.open():
            QMessageBox.critical(None, "Ошибка", f"Не удалось открыть БД:\n{self.db.lastError().text()}")
            self.db = None
            return False

        return True

    def close(self):
        """Закрытие соединения с БД."""
        if self.db is not None:
            self.db.close()
            self.db = None
        # Удаляем соединение из списка Qt, чтобы можно было подключиться заново


    def get_table_model(self, query_text):
        """Возвращает модель для табличного отображения по SQL-запросу."""
        model = QSqlTableModel()
        model.setQuery(QSqlQuery(query_text, self.db))
        return model