from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QMessageBox
)


class ManagerWindow(QWidget):

    def __init__(self, user):

        super().__init__()

        self.user = user

        self.setWindowTitle(
            "Car Customizer - Shop Manager"
        )

        self.resize(900, 650)

        self.setup_ui()

    def setup_ui(self):

        layout = QVBoxLayout()

        title = QLabel(
            "SHOP MANAGER PANEL"
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

        layout.addWidget(title)
        layout.addWidget(welcome)
        layout.addWidget(role)

        layout.addSpacing(30)

        inventory_button = QPushButton(
            "Manage Inventory"
        )

        prices_button = QPushButton(
            "Manage Prices"
        )

        sales_button = QPushButton(
            "View Sales"
        )

        shop_button = QPushButton(
            "Open Shop"
        )

        logout_button = QPushButton(
            "Logout"
        )

        buttons = [
            inventory_button,
            prices_button,
            sales_button,
            shop_button,
            logout_button
        ]

        for button in buttons:

            button.setMinimumHeight(40)
            layout.addWidget(button)

        self.setLayout(layout)

        # --------------------------------
        # BUTTON CONNECTIONS
        # --------------------------------

        inventory_button.clicked.connect(
            self.inventory_clicked
        )

        prices_button.clicked.connect(
            self.prices_clicked
        )

        sales_button.clicked.connect(
            self.sales_clicked
        )

        shop_button.clicked.connect(
            self.shop_clicked
        )

        logout_button.clicked.connect(
            self.logout
        )

    # --------------------------------
    # BUTTON FUNCTIONS
    # --------------------------------

    def inventory_clicked(self):

        QMessageBox.information(
            self,
            "Inventory Management",
            "Inventory management will be implemented next."
        )

    def prices_clicked(self):

        QMessageBox.information(
            self,
            "Price Management",
            "Price management will be implemented next."
        )

    def sales_clicked(self):

        QMessageBox.information(
            self,
            "Sales",
            "Sales reports will be implemented next."
        )

    def shop_clicked(self):

        QMessageBox.information(
            self,
            "Shop",
            "The shop interface will be implemented next."
        )

    def logout(self):

        from login import LoginWindow

        self.login_window = LoginWindow()

        self.login_window.show()

        self.close()