import os
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = r'C:\Users\Егор\PycharmProjects\PythonProject7\.venv\Lib\site-packages\PyQt5\Qt5\plugins\platforms'

os.environ['QT_PLUGIN_PATH'] = r'C:\Users\Егор\PycharmProjects\PythonProject7\.venv\Lib\site-packages\PyQt5\Qt5\plugins'
import sys
from PyQt5.QtWidgets import QApplication
from okno import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())