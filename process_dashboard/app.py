"""Application entry point."""
import sys
from PySide6.QtWidgets import QApplication
from .config import APP_NAME
from .dashboard import Dashboard

def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    window = Dashboard()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
