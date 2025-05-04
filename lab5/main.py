import sys
from PySide6.QtWidgets import QApplication
from ui import MainWindow


def main():
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
