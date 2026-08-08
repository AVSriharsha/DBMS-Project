from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QMessageBox
)


class AdminWindow(QWidget):

    def __init__(self, user):

        super().__init__()

        self.user = user

        self.setWindowTitle(
            "Car Customizer - Administrator"
        )

        self.resize(900, 650)

        self.setup_ui()

    def setup_ui(self):

        layout = QVBoxLayout()

        title = QLabel(
            "ADMINISTRATOR PANEL"
        )

        title.setStyleSheet(
            "font-size: 30px; "
            "font-weight: bold;"
        )

        welcome = QLabel(
            f"Logged in as: {self.user['username']}"
        )

        role = QLabel(
            f"Access Level: {self.user['role_name']}"
        )

        money = QLabel(
            f"Account Balance: "
            f"${float(self.user['money']):,.2f}"
        )

        layout.addWidget(title)
        layout.addWidget(welcome)
        layout.addWidget(role)
        layout.addWidget(money)

        layout.addSpacing(30)

        users_button = QPushButton(
            "Manage Users"
        )

        cars_button = QPushButton(
            "Manage Cars"
        )

        parts_button = QPushButton(
            "Manage Parts"
        )

        manufacturers_button = QPushButton(
            "Manage Manufacturers"
        )

        reports_button = QPushButton(
            "View Reports"
        )

        garage_button = QPushButton(
            "Open Garage"
        )

        logout_button = QPushButton(
            "Logout"
        )

        buttons = [
            users_button,
            cars_button,
            parts_button,
            manufacturers_button,
            reports_button,
            garage_button,
            logout_button
        ]

        for button in buttons:

            button.setMinimumHeight(40)
            layout.addWidget(button)

        self.setLayout(layout)

        # --------------------------------
        # BUTTON CONNECTIONS
        # --------------------------------

        users_button.clicked.connect(
            self.users_clicked
        )

        cars_button.clicked.connect(
            self.cars_clicked
        )

        parts_button.clicked.connect(
            self.parts_clicked
        )

        manufacturers_button.clicked.connect(
            self.manufacturers_clicked
        )

        reports_button.clicked.connect(
            self.reports_clicked
        )

        garage_button.clicked.connect(
            self.open_garage
        )

        logout_button.clicked.connect(
            self.logout
        )

    # --------------------------------
    # BUTTON FUNCTIONS
    # --------------------------------

    def users_clicked(self):

        QMessageBox.information(
            self,
            "Manage Users",
            "User management will be implemented next."
        )

    def cars_clicked(self):

        QMessageBox.information(
            self,
            "Manage Cars",
            "Car management will be implemented next."
        )

    def parts_clicked(self):

        QMessageBox.information(
            self,
            "Manage Parts",
            "Part management will be implemented next."
        )

    def manufacturers_clicked(self):

        QMessageBox.information(
            self,
            "Manage Manufacturers",
            "Manufacturer management will be implemented next."
        )

    def reports_clicked(self):

        QMessageBox.information(
            self,
            "Reports",
            "Reports will be implemented next."
        )

    def open_garage(self):

        from garage import GarageWindow

        self.garage = GarageWindow(
            self.user
        )

        self.garage.show()

    def logout(self):

        from login import LoginWindow

        self.login_window = LoginWindow()

        self.login_window.show()

        self.close()