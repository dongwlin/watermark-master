from PySide6 import QtWidgets
from frontend import MainWindow
import sys


def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
