import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QComboBox, QTabWidget, QAction, QFileDialog, QMessageBox,
    QTableView, QDialog, QTextEdit, QLabel
)
from PyQt5.QtSql import QSqlQueryModel
from PyQt5.QtCore import Qt

# Импортируем наш менеджер базы данных
from database import DatabaseManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лаба 3 — Работа с SQL (РПЛ)")
        self.resize(900, 600)

        # Менеджер подключения к БД
        self.db_manager = DatabaseManager()

        # --- СОЗДАЁМ ИНТЕРФЕЙС ---
        self.init_ui()

    def init_ui(self):
        # 1. Меню
        menubar = self.menuBar()
        db_menu = menubar.addMenu("Database")

        # 1.1. Пункт "Set connection"
        set_conn_action = QAction("Set connection", self)
        set_conn_action.triggered.connect(self.set_connection)
        db_menu.addAction(set_conn_action)

        # 1.2. Пункт "Close connection"
        close_conn_action = QAction("Close connection", self)
        close_conn_action.triggered.connect(self.close_connection)
        db_menu.addAction(close_conn_action)

        # Бонус: модальное окно с запросом
        query_action = QAction("Custom Query (Bonus)", self)
        query_action.triggered.connect(self.open_custom_query)
        db_menu.addAction(query_action)

        # 2. Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 3. Верхняя панель с кнопками
        top_panel = QHBoxLayout()

        self.btn1 = QPushButton('bt1 "SELECT Column"')
        self.btn2 = QPushButton('bt2 "Query2"')
        self.btn3 = QPushButton('bt3 "Query3"')
        self.combo = QComboBox()
        self.combo.setMinimumWidth(200)

        # Добавляем кнопки и комбо в верхнюю панель
        top_panel.addWidget(self.btn1)
        top_panel.addWidget(self.combo)
        top_panel.addWidget(self.btn2)
        top_panel.addWidget(self.btn3)
        main_layout.addLayout(top_panel)

        # 4. Вкладки
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Создаём 5 пустых вкладок
        for i in range(1, 6):
            self.tabs.addTab(QWidget(), f"Tab{i}")

        # 5. Подключаем сигналы к кнопкам
        self.btn1.clicked.connect(self.query_bt1)
        self.btn2.clicked.connect(self.query_bt2)
        self.btn3.clicked.connect(self.query_bt3)
        self.combo.currentTextChanged.connect(self.query_combo)

    # ==========================================
    # ЛОГИКА РАБОТЫ С БАЗОЙ ДАННЫХ
    # ==========================================

    def set_connection(self):
        """Открывает диалог выбора БД и подключается к ней."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл базы данных", "", "SQLite Database (*.db *.sqlite)"
        )
        if not path:
            return

        if self.db_manager.connect(path):
            QMessageBox.information(self, "Успех", "Подключение установлено!")
            self.on_connected()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к БД.")

    def close_connection(self):
        """Закрывает БД и очищает все вкладки."""
        self.db_manager.close()
        # Очищаем все вкладки (заменяем их пустыми виджетами)
        for i in range(5):
            self.tabs.removeTab(0)
        for i in range(1, 6):
            self.tabs.addTab(QWidget(), f"Tab{i}")
        self.combo.clear()
        QMessageBox.information(self, "Готово", "Соединение закрыто, данные очищены.")

    def on_connected(self):
        """Вызывается сразу после успешного подключения."""
        # 1. Выполняем запрос в Tab1
        self.run_query("SELECT * FROM sqlite_master", 0)

        # 2. Заполняем QComboBox системными колонками (как требует задание)
        self.combo.clear()
        self.combo.addItems(["type", "name", "tbl_name", "rootpage", "sql"])

    def run_query(self, query_text, tab_index):
        """Выполняет SQL-запрос и выводит результат в указанную вкладку."""
        if self.db_manager.db is None:
            QMessageBox.warning(self, "Внимание", "Сначала подключитесь к базе данных!")
            return

        model = QSqlQueryModel()
        model.setQuery(query_text, self.db_manager.db)

        if model.lastError().isValid():
            QMessageBox.warning(self, "Ошибка SQL", model.lastError().text())
            return

        # Создаём таблицу для отображения
        view = QTableView()
        view.setModel(model)
        view.resizeColumnsToContents()

        # Вставляем её во вкладку
        self.tabs.removeTab(tab_index)
        self.tabs.insertTab(tab_index, view, f"Tab{tab_index + 1}")

    # ==========================================
    # ЗАПРОСЫ ДЛЯ КНОПОК
    # ==========================================

    def query_bt1(self):
        """bt1: SELECT name FROM sqlite_master (Tab2)."""
        self.run_query("SELECT name FROM sqlite_master", 1)

    def query_bt2(self):
        """bt2: команды с очками > 40 (Tab4)."""
        self.run_query("SELECT name, points FROM teams WHERE points > 40", 3)

    def query_bt3(self):
        """bt3: сортировка по забитым голам (Tab5)."""
        self.run_query("SELECT name, goals_scored FROM teams ORDER BY goals_scored DESC", 4)

    def query_combo(self, column_name):
        """QComboBox: выводит выбранную системную колонку в Tab3."""
        if not column_name or self.db_manager.db is None:
            return
        allowed = {"type", "name", "tbl_name", "rootpage", "sql"}
        if column_name in allowed:
            self.run_query(f"SELECT {column_name} FROM sqlite_master", 2)

    # ==========================================
    # БОНУС: МОДАЛЬНОЕ ОКНО
    # ==========================================

    def open_custom_query(self):
        """Открывает модальное окно для ввода произвольного SQL-запроса."""
        if self.db_manager.db is None:
            QMessageBox.warning(self, "Внимание", "Сначала подключитесь к базе данных!")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Произвольный SQL-запрос")
        dialog.resize(500, 400)

        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel("Введите SQL-запрос:"))
        text_edit = QTextEdit()
        text_edit.setPlainText("SELECT * FROM teams")
        layout.addWidget(text_edit)

        btn_exec = QPushButton("Выполнить")
        layout.addWidget(btn_exec)

        result_view = QTableView()
        layout.addWidget(result_view)

        def execute():
            query_text = text_edit.toPlainText()
            model = QSqlQueryModel()
            model.setQuery(query_text, self.db_manager.db)

            if model.lastError().isValid():
                QMessageBox.warning(dialog, "Ошибка SQL", model.lastError().text())
                return

            result_view.setModel(model)
            result_view.resizeColumnsToContents()

        btn_exec.clicked.connect(execute)

        dialog.exec_()