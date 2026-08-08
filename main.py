import sys

from PyQt6.QtWidgets import QApplication

from login import LoginWindow


def main():

    app = QApplication(sys.argv)

    app.setApplicationName(
        "Car Customizer"
    )

    window = LoginWindow()

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":

    main()