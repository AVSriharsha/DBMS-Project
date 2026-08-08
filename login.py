from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QMessageBox
)

from database import get_connection


class LoginWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Car Customizer - Login")
        self.setFixedSize(450, 350)

        layout = QVBoxLayout()

        title = QLabel("CAR CUSTOMIZER")
        title.setStyleSheet(
            "font-size: 28px; "
            "font-weight: bold; "
            "margin-bottom: 20px;"
        )

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        login_button = QPushButton("LOGIN")
        login_button.setMinimumHeight(40)

        login_button.clicked.connect(self.login)

        layout.addWidget(title)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addSpacing(10)
        layout.addWidget(login_button)

        self.setLayout(layout)

    def login(self):

        username = self.username.text().strip()
        password = self.password.text()

        if not username or not password:

            QMessageBox.warning(
                self,
                "Login Failed",
                "Please enter both username and password."
            )

            return

        try:

            connection = get_connection()

            cursor = connection.cursor(
                dictionary=True
            )

            query = """
                SELECT
                    users.user_id,
                    users.username,
                    users.money,
                    users.role_id,
                    roles.role_name
                FROM users
                JOIN roles
                    ON users.role_id = roles.role_id
                WHERE users.username = %s
                AND users.password = %s
            """

            cursor.execute(
                query,
                (username, password)
            )

            user = cursor.fetchone()

            cursor.close()
            connection.close()

            if user:

                self.open_main_window(user)

            else:

                QMessageBox.warning(
                    self,
                    "Login Failed",
                    "Invalid username or password."
                )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not connect to the database.\n\n{error}"
            )

    def open_main_window(self, user):

        role = user["role_name"]

        if role == "Player":

            from garage import GarageWindow

            self.main_window = GarageWindow(user)

        elif role == "Shop Manager":

            from manager import ManagerWindow

            self.main_window = ManagerWindow(user)

        elif role == "Administrator":

            from admin import AdminWindow

            self.main_window = AdminWindow(user)

        else:

            QMessageBox.warning(
                self,
                "Access Error",
                f"Unknown user role: {role}"
            )

            return

        self.main_window.show()
        self.close()