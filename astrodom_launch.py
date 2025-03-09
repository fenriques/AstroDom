import astrodom.__main__ as astrodom
import sys
from PyQt6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = astrodom.MainWindow()
    window.show()
    sys.exit(app.exec())