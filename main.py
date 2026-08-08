import sys
import os
import mysql.connector

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QLabel,
    QPushButton,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QComboBox,
    QMessageBox,
    QFrame,
    QStackedWidget,
    QListWidget,
    QListWidgetItem,
    QDoubleSpinBox,
    QSpinBox,
)


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_USER = "root"

# ============================================================
# CHANGE THIS TO YOUR MYSQL PASSWORD
# ============================================================

DB_PASSWORD = "InsertYourPasswordHere"

DB_NAME = "car_customizer"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        return connection

    except mysql.connector.Error as error:
        print("Database connection error:", error)
        return None


# ============================================================
# DATABASE HELPER FUNCTIONS
# ============================================================

def fetch_all(query, params=None):
    connection = get_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(query, params or ())
        results = cursor.fetchall()
        return results

    except mysql.connector.Error as error:
        print("Database error:", error)
        return []

    finally:
        cursor.close()
        connection.close()


def fetch_one(query, params=None):
    connection = get_connection()

    if connection is None:
        return None

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(query, params or ())
        result = cursor.fetchone()
        return result

    except mysql.connector.Error as error:
        print("Database error:", error)
        return None

    finally:
        cursor.close()
        connection.close()


def execute_query(query, params=None):
    connection = get_connection()

    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        cursor.execute(query, params or ())
        connection.commit()
        return True

    except mysql.connector.Error as error:
        print("Database error:", error)
        connection.rollback()
        return False

    finally:
        cursor.close()
        connection.close()


# ============================================================
# LOGIN
# ============================================================

def login_user(username, password):

    query = """
        SELECT
            u.user_id,
            u.username,
            u.money,
            u.role_id,
            r.role_name
        FROM users u
        JOIN roles r
            ON u.role_id = r.role_id
        WHERE u.username = %s
        AND u.password = %s
    """

    return fetch_one(query, (username, password))


# ============================================================
# GET USER VEHICLES
# ============================================================

def get_user_vehicles(user_id):

    query = """
        SELECT
            v.vehicle_id,
            v.nickname,
            v.model_id,
            cm.model_name,
            cm.model_year,
            cm.base_hp,
            cm.base_weight,
            cm.base_top_speed,
            cm.base_acceleration,
            m.manufacturer_name
        FROM vehicles v
        JOIN car_models cm
            ON v.model_id = cm.model_id
        JOIN manufacturers m
            ON cm.manufacturer_id = m.manufacturer_id
        WHERE v.user_id = %s
        ORDER BY v.vehicle_id
    """

    return fetch_all(query, (user_id,))


# ============================================================
# GET CATEGORIES
# ============================================================

def get_categories():

    query = """
        SELECT
            category_id,
            category_name
        FROM categories
        ORDER BY category_id
    """

    return fetch_all(query)


# ============================================================
# GET PARTS FOR CATEGORY
# ============================================================

def get_parts_by_category(category_id):

    query = """
        SELECT
            part_id,
            category_id,
            part_name,
            manufacturer,
            price,
            hp_bonus,
            weight_change,
            top_speed_bonus,
            acceleration_bonus,
            sprite_file,
            layer_order
        FROM parts
        WHERE category_id = %s
        ORDER BY price
    """

    return fetch_all(query, (category_id,))


# ============================================================
# GET INSTALLED PART
# ============================================================

def get_installed_part(vehicle_id, category_id):

    query = """
        SELECT
            vp.part_id,
            p.part_name,
            p.price,
            p.hp_bonus,
            p.weight_change,
            p.top_speed_bonus,
            p.acceleration_bonus,
            p.sprite_file,
            p.layer_order
        FROM vehicle_parts vp
        JOIN parts p
            ON vp.part_id = p.part_id
        WHERE vp.vehicle_id = %s
        AND vp.category_id = %s
    """

    return fetch_one(query, (vehicle_id, category_id))


# ============================================================
# GET ALL INSTALLED PARTS
# ============================================================

def get_installed_parts(vehicle_id):

    query = """
        SELECT
            vp.category_id,
            vp.part_id,
            c.category_name,
            p.part_name,
            p.price,
            p.hp_bonus,
            p.weight_change,
            p.top_speed_bonus,
            p.acceleration_bonus,
            p.sprite_file,
            p.layer_order
        FROM vehicle_parts vp
        JOIN categories c
            ON vp.category_id = c.category_id
        JOIN parts p
            ON vp.part_id = p.part_id
        WHERE vp.vehicle_id = %s
        ORDER BY p.layer_order
    """

    return fetch_all(query, (vehicle_id,))


# ============================================================
# INSTALL PART
# ============================================================

def install_part(vehicle_id, category_id, part_id):

    connection = get_connection()

    if connection is None:
        return False, "Could not connect to database."

    cursor = connection.cursor()

    try:

        # Check whether this part exists
        cursor.execute(
            """
            SELECT part_id, part_name
            FROM parts
            WHERE part_id = %s
            """,
            (part_id,)
        )

        part = cursor.fetchone()

        if part is None:
            return False, "Part does not exist."

        # Check whether the vehicle exists
        cursor.execute(
            """
            SELECT vehicle_id
            FROM vehicles
            WHERE vehicle_id = %s
            """,
            (vehicle_id,)
        )

        vehicle = cursor.fetchone()

        if vehicle is None:
            return False, "Vehicle does not exist."

        # vehicle_parts uses vehicle_id + category_id as primary key.
        # Therefore one part per category can be installed.

        cursor.execute(
            """
            SELECT part_id
            FROM vehicle_parts
            WHERE vehicle_id = %s
            AND category_id = %s
            """,
            (vehicle_id, category_id)
        )

        existing = cursor.fetchone()

        if existing:

            cursor.execute(
                """
                UPDATE vehicle_parts
                SET part_id = %s
                WHERE vehicle_id = %s
                AND category_id = %s
                """,
                (part_id, vehicle_id, category_id)
            )

        else:

            cursor.execute(
                """
                INSERT INTO vehicle_parts
                (
                    vehicle_id,
                    category_id,
                    part_id
                )
                VALUES (%s, %s, %s)
                """,
                (vehicle_id, category_id, part_id)
            )

        connection.commit()

        return True, "Part installed successfully."

    except mysql.connector.Error as error:

        connection.rollback()

        return False, str(error)

    finally:

        cursor.close()
        connection.close()


# ============================================================
# GET SHOP INVENTORY
# ============================================================

def get_shop_inventory():

    query = """
        SELECT
            si.inventory_id,
            si.part_id,
            si.stock,
            p.part_name,
            p.manufacturer,
            p.price,
            c.category_name
        FROM shop_inventory si
        JOIN parts p
            ON si.part_id = p.part_id
        JOIN categories c
            ON p.category_id = c.category_id
        ORDER BY c.category_name, p.price
    """

    return fetch_all(query)


# ============================================================
# BUY PART
# ============================================================

def buy_part(user_id, part_id, quantity):

    connection = get_connection()

    if connection is None:
        return False, "Database connection failed."

    cursor = connection.cursor(dictionary=True)

    try:

        # Get user money
        cursor.execute(
            """
            SELECT money
            FROM users
            WHERE user_id = %s
            FOR UPDATE
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if user is None:
            return False, "User not found."

        # Get shop stock and price
        cursor.execute(
            """
            SELECT
                si.stock,
                p.price,
                p.part_name
            FROM shop_inventory si
            JOIN parts p
                ON si.part_id = p.part_id
            WHERE si.part_id = %s
            FOR UPDATE
            """,
            (part_id,)
        )

        item = cursor.fetchone()

        if item is None:
            return False, "Part is not available in the shop."

        if item["stock"] < quantity:
            return False, "Not enough stock."

        total_price = float(item["price"]) * quantity

        if float(user["money"]) < total_price:
            return False, "You do not have enough money."

        # Deduct money
        cursor.execute(
            """
            UPDATE users
            SET money = money - %s
            WHERE user_id = %s
            """,
            (total_price, user_id)
        )

        # Reduce stock
        cursor.execute(
            """
            UPDATE shop_inventory
            SET stock = stock - %s
            WHERE part_id = %s
            """,
            (quantity, part_id)
        )

        # Check player inventory
        cursor.execute(
            """
            SELECT inventory_id
            FROM player_inventory
            WHERE user_id = %s
            AND part_id = %s
            """,
            (user_id, part_id)
        )

        inventory = cursor.fetchone()

        if inventory:

            cursor.execute(
                """
                UPDATE player_inventory
                SET quantity = quantity + %s
                WHERE user_id = %s
                AND part_id = %s
                """,
                (quantity, user_id, part_id)
            )

        else:

            cursor.execute(
                """
                INSERT INTO player_inventory
                (
                    user_id,
                    part_id,
                    quantity
                )
                VALUES (%s, %s, %s)
                """,
                (user_id, part_id, quantity)
            )

        # Add purchase record
        cursor.execute(
            """
            INSERT INTO purchases
            (
                user_id,
                part_id,
                quantity,
                total_price
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                user_id,
                part_id,
                quantity,
                total_price
            )
        )

        connection.commit()

        return True, f"Purchased {quantity} x {item['part_name']}."

    except mysql.connector.Error as error:

        connection.rollback()

        return False, str(error)

    finally:

        cursor.close()
        connection.close()


# ============================================================
# CAR PREVIEW
# ============================================================

class CarPreview(QFrame):

    def __init__(self):

        super().__init__()

        self.setMinimumSize(600, 330)

        self.setFrameShape(QFrame.Shape.StyledPanel)

        self.setStyleSheet(
            """
            QFrame {
                background-color: #20242b;
                border: 1px solid #444;
                border-radius: 10px;
            }
            """
        )

        self.vehicle_id = None

        self.installed_parts = []

    def set_vehicle(self, vehicle_id):

        self.vehicle_id = vehicle_id

        self.installed_parts = get_installed_parts(vehicle_id)

        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        # Background
        painter.fillRect(
            0,
            0,
            width,
            height,
            QColor("#20242b")
        )

        # Ground
        ground_y = int(height * 0.72)

        painter.setPen(
            QPen(QColor("#555"), 2)
        )

        painter.drawLine(
            40,
            ground_y,
            width - 40,
            ground_y
        )

        # ----------------------------------------------------
        # SIMPLE PLACEHOLDER CAR
        #
        # This gives us a working preview before we add
        # the actual PNG sprites.
        # ----------------------------------------------------

        car_x = int(width * 0.18)
        car_y = int(height * 0.42)

        car_width = int(width * 0.64)
        car_height = int(height * 0.25)

        body_color = QColor("#bfc5cc")

        # Body
        painter.setBrush(
            QBrush(body_color)
        )

        painter.setPen(
            QPen(QColor("#111"), 3)
        )

        painter.drawRoundedRect(
            car_x,
            car_y,
            car_width,
            car_height,
            20,
            20
        )

        # Roof
        roof_points = [
            (car_x + 100, car_y),
            (car_x + 170, car_y - 65),
            (car_x + 370, car_y - 65),
            (car_x + 450, car_y)
        ]

        from PyQt6.QtGui import QPolygon

        polygon = QPolygon()

        for x, y in roof_points:
            polygon.append(
                __import__("PyQt6.QtCore", fromlist=["QPoint"]).QPoint(
                    x,
                    y
                )
            )

        painter.setBrush(
            QBrush(QColor("#858b93"))
        )

        painter.drawPolygon(polygon)

        # Windows
        painter.setBrush(
            QBrush(QColor("#242b34"))
        )

        painter.drawPolygon(
            QPolygon(
                [
                    __import__("PyQt6.QtCore", fromlist=["QPoint"]).QPoint(
                        car_x + 175,
                        car_y - 55
                    ),
                    __import__("PyQt6.QtCore", fromlist=["QPoint"]).QPoint(
                        car_x + 265,
                        car_y - 55
                    ),
                    __import__("PyQt6.QtCore", fromlist=["QPoint"]).QPoint(
                        car_x + 265,
                        car_y - 5
                    ),
                    __import__("PyQt6.QtCore", fromlist=["QPoint"]).QPoint(
                        car_x + 165,
                        car_y - 5
                    )
                ]
            )
        )

        painter.drawPolygon(
            QPolygon(
                [
                    __import__("PyQt6.QtCore", fromlist=["QPoint"]).QPoint(
                        car_x + 275,
                        car_y - 55
                    ),
                    __import__("PyQt6.QtCore", fromlist=["QPoint"]).QPoint(
                        car_x + 365,
                        car_y - 55
                    ),
                    __import__("PyQt6.QtCore", fromlist=["QPoint"]).QPoint(
                        car_x + 430,
                        car_y - 5
                    ),
                    __import__("PyQt6.QtCore", fromlist=["QPoint"]).QPoint(
                        car_x + 275,
                        car_y - 5
                    )
                ]
            )
        )

        # Wheels
        wheel_radius = 38

        wheel_centers = [
            (
                car_x + 110,
                car_y + car_height
            ),
            (
                car_x + car_width - 110,
                car_y + car_height
            )
        ]

        for center_x, center_y in wheel_centers:

            painter.setBrush(
                QBrush(QColor("#101010"))
            )

            painter.drawEllipse(
                center_x - wheel_radius,
                center_y - wheel_radius,
                wheel_radius * 2,
                wheel_radius * 2
            )

            painter.setBrush(
                QBrush(QColor("#777"))
            )

            painter.drawEllipse(
                center_x - 18,
                center_y - 18,
                36,
                36
            )

        # ----------------------------------------------------
        # INSTALLED PART LABELS
        # ----------------------------------------------------

        if self.installed_parts:

            y = 25

            painter.setFont(
                QFont("Arial", 9)
            )

            painter.setPen(
                QPen(QColor("#dddddd"))
            )

            for part in self.installed_parts:

                text = (
                    f"{part['category_name']}: "
                    f"{part['part_name']}"
                )

                painter.drawText(
                    15,
                    y,
                    text
                )

                y += 18

        else:

            painter.setPen(
                QPen(QColor("#aaaaaa"))
            )

            painter.drawText(
                20,
                30,
                "No modifications installed"
            )

        painter.end()


# ============================================================
# LOGIN WINDOW
# ============================================================

class LoginWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.dashboard = None

        self.setWindowTitle(
            "Car Customizer - Login"
        )

        self.setFixedSize(
            450,
            350
        )

        self.setStyleSheet(
            """
            QWidget {
                background-color: #17191d;
                color: #eeeeee;
                font-family: Arial;
            }

            QLineEdit {
                background-color: #252930;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 10px;
                color: white;
            }

            QPushButton {
                background-color: #3d6df2;
                border: none;
                border-radius: 6px;
                padding: 10px;
                color: white;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #527ef5;
            }
            """
        )

        layout = QVBoxLayout()

        title = QLabel(
            "CAR CUSTOMIZER"
        )

        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        title.setFont(
            QFont("Arial", 24, QFont.Weight.Bold)
        )

        layout.addWidget(title)

        subtitle = QLabel(
            "2D Vehicle Upgrade Garage"
        )

        subtitle.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(subtitle)

        layout.addSpacing(25)

        self.username = QLineEdit()

        self.username.setPlaceholderText(
            "Username"
        )

        layout.addWidget(
            self.username
        )

        self.password = QLineEdit()

        self.password.setPlaceholderText(
            "Password"
        )

        self.password.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        layout.addWidget(
            self.password
        )

        layout.addSpacing(10)

        login_button = QPushButton(
            "LOGIN"
        )

        login_button.clicked.connect(
            self.login
        )

        layout.addWidget(
            login_button
        )

        guest_button = QPushButton(
            "CONTINUE AS GUEST"
        )

        guest_button.clicked.connect(
            self.guest_login
        )

        layout.addWidget(
            guest_button
        )

        self.status = QLabel()

        self.status.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(
            self.status
        )

        self.setLayout(layout)

    def login(self):

        username = self.username.text().strip()

        password = self.password.text()

        if not username or not password:

            self.status.setText(
                "Enter username and password."
            )

            return

        user = login_user(
            username,
            password
        )

        if user is None:

            self.status.setText(
                "Invalid username or password."
            )

            return

        self.open_dashboard(user)

    def guest_login(self):

        guest_user = {
            "user_id": None,
            "username": "Guest",
            "money": 0,
            "role_id": None,
            "role_name": "Guest"
        }

        self.open_dashboard(
            guest_user
        )

    def open_dashboard(self, user):

        self.dashboard = MainWindow(
            user
        )

        self.dashboard.show()

        self.close()


# ============================================================
# MAIN WINDOW
# ============================================================

class MainWindow(QMainWindow):

    def __init__(self, user):

        super().__init__()

        self.user = user

        self.selected_vehicle = None

        self.setWindowTitle(
            "Car Customizer"
        )

        self.resize(
            1200,
            750
        )

        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #17191d;
            }

            QWidget {
                color: #eeeeee;
                font-family: Arial;
            }

            QPushButton {
                background-color: #303640;
                border: 1px solid #4a505a;
                border-radius: 6px;
                padding: 9px;
            }

            QPushButton:hover {
                background-color: #414954;
            }

            QComboBox {
                background-color: #252930;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 8px;
            }

            QListWidget {
                background-color: #20242b;
                border: 1px solid #444;
                border-radius: 6px;
            }

            QLabel {
                color: #eeeeee;
            }
            """
        )

        self.create_ui()

        self.load_vehicles()

    # --------------------------------------------------------
    # UI
    # --------------------------------------------------------

    def create_ui(self):

        central = QWidget()

        self.setCentralWidget(
            central
        )

        main_layout = QVBoxLayout()

        # Header
        header = QHBoxLayout()

        title = QLabel(
            "CAR CUSTOMIZER"
        )

        title.setFont(
            QFont(
                "Arial",
                22,
                QFont.Weight.Bold
            )
        )

        header.addWidget(
            title
        )

        header.addStretch()

        self.user_label = QLabel()

        self.update_user_label()

        header.addWidget(
            self.user_label
        )

        logout_button = QPushButton(
            "Logout"
        )

        logout_button.clicked.connect(
            self.logout
        )

        header.addWidget(
            logout_button
        )

        main_layout.addLayout(
            header
        )

        # Main stack
        self.stack = QStackedWidget()

        self.garage_page = self.create_garage_page()

        self.shop_page = self.create_shop_page()

        self.stack.addWidget(
            self.garage_page
        )

        self.stack.addWidget(
            self.shop_page
        )

        main_layout.addWidget(
            self.stack
        )

        # Navigation
        navigation = QHBoxLayout()

        garage_button = QPushButton(
            "GARAGE"
        )

        garage_button.clicked.connect(
            lambda: self.stack.setCurrentWidget(
                self.garage_page
            )
        )

        navigation.addWidget(
            garage_button
        )

        shop_button = QPushButton(
            "SHOP"
        )

        shop_button.clicked.connect(
            lambda: self.stack.setCurrentWidget(
                self.shop_page
            )
        )

        navigation.addWidget(
            shop_button
        )

        # Admin / manager buttons
        role = self.user.get(
            "role_name",
            "Guest"
        )

        if role in (
            "Administrator",
            "Shop Manager"
        ):

            manager_button = QPushButton(
                "MANAGEMENT"
            )

            manager_button.clicked.connect(
                self.open_management
            )

            navigation.addWidget(
                manager_button
            )

        main_layout.addLayout(
            navigation
        )

        central.setLayout(
            main_layout
        )

    # --------------------------------------------------------
    # Garage Page
    # --------------------------------------------------------

    def create_garage_page(self):

        page = QWidget()

        layout = QHBoxLayout()

        # Left side
        left = QVBoxLayout()

        garage_title = QLabel(
            "MY GARAGE"
        )

        garage_title.setFont(
            QFont(
                "Arial",
                18,
                QFont.Weight.Bold
            )
        )

        left.addWidget(
            garage_title
        )

        self.vehicle_list = QListWidget()

        self.vehicle_list.itemClicked.connect(
            self.vehicle_selected
        )

        left.addWidget(
            self.vehicle_list
        )

        # Right side
        right = QVBoxLayout()

        preview_title = QLabel(
            "LIVE 2D PREVIEW"
        )

        preview_title.setFont(
            QFont(
                "Arial",
                18,
                QFont.Weight.Bold
            )
        )

        right.addWidget(
            preview_title
        )

        self.preview = CarPreview()

        right.addWidget(
            self.preview
        )

        # Stats
        self.stats_label = QLabel(
            "Select a vehicle."
        )

        self.stats_label.setFont(
            QFont(
                "Arial",
                12
            )
        )

        right.addWidget(
            self.stats_label
        )

        # Categories
        customization_title = QLabel(
            "CUSTOMIZATION"
        )

        customization_title.setFont(
            QFont(
                "Arial",
                16,
                QFont.Weight.Bold
            )
        )

        right.addWidget(
            customization_title
        )

        self.customization_layout = QGridLayout()

        right.addLayout(
            self.customization_layout
        )

        layout.addLayout(
            left,
            1
        )

        layout.addLayout(
            right,
            3
        )

        page.setLayout(
            layout
        )

        return page

    # --------------------------------------------------------
    # Load Vehicles
    # --------------------------------------------------------

    def load_vehicles(self):

        self.vehicle_list.clear()

        if self.user["user_id"] is None:

            item = QListWidgetItem(
                "Guest Mode - Login to access your garage"
            )

            self.vehicle_list.addItem(
                item
            )

            return

        vehicles = get_user_vehicles(
            self.user["user_id"]
        )

        for vehicle in vehicles:

            manufacturer = vehicle[
                "manufacturer_name"
            ]

            model = vehicle[
                "model_name"
            ]

            nickname = vehicle[
                "nickname"
            ]

            text = (
                f"{nickname or 'Unnamed Car'}\n"
                f"{manufacturer} {model}"
            )

            item = QListWidgetItem(
                text
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                vehicle
            )

            self.vehicle_list.addItem(
                item
            )

        if vehicles:

            self.vehicle_list.setCurrentRow(
                0
            )

            self.vehicle_selected(
                self.vehicle_list.item(0)
            )

        else:

            self.stats_label.setText(
                "You do not own any vehicles."
            )

    # --------------------------------------------------------
    # Vehicle Selected
    # --------------------------------------------------------

    def vehicle_selected(self, item):

        vehicle = item.data(
            Qt.ItemDataRole.UserRole
        )

        if vehicle is None:
            return

        self.selected_vehicle = vehicle

        vehicle_id = vehicle[
            "vehicle_id"
        ]

        self.preview.set_vehicle(
            vehicle_id
        )

        self.update_stats()

        self.create_customization_controls()

    # --------------------------------------------------------
    # Stats
    # --------------------------------------------------------

    def update_stats(self):

        if self.selected_vehicle is None:
            return

        vehicle = self.selected_vehicle

        hp = vehicle["base_hp"] or 0

        weight = vehicle["base_weight"] or 0

        top_speed = (
            vehicle["base_top_speed"]
            or 0
        )

        acceleration = (
            float(
                vehicle["base_acceleration"]
                or 0
            )
        )

        parts = get_installed_parts(
            vehicle["vehicle_id"]
        )

        for part in parts:

            hp += (
                part["hp_bonus"]
                or 0
            )

            weight += (
                part["weight_change"]
                or 0
            )

            top_speed += (
                part["top_speed_bonus"]
                or 0
            )

            acceleration += float(
                part["acceleration_bonus"]
                or 0
            )

        self.stats_label.setText(
            f"""
            <b>{vehicle['manufacturer_name']} {vehicle['model_name']}</b>
            &nbsp;&nbsp;|&nbsp;&nbsp;
            HP: <b>{hp}</b>
            &nbsp;&nbsp;|&nbsp;&nbsp;
            Weight: <b>{weight} kg</b>
            &nbsp;&nbsp;|&nbsp;&nbsp;
            Top Speed: <b>{top_speed} km/h</b>
            &nbsp;&nbsp;|&nbsp;&nbsp;
            Acceleration: <b>{acceleration:.2f}</b>
            """
        )

    # --------------------------------------------------------
    # Customization Controls
    # --------------------------------------------------------

    def create_customization_controls(self):

        # Remove previous controls
        while self.customization_layout.count():

            item = (
                self.customization_layout.takeAt(0)
            )

            widget = item.widget()

            if widget:
                widget.deleteLater()

        if self.selected_vehicle is None:
            return

        categories = get_categories()

        for row, category in enumerate(categories):

            category_id = category[
                "category_id"
            ]

            category_name = category[
                "category_name"
            ]

            label = QLabel(
                category_name
            )

            combo = QComboBox()

            combo.addItem(
                "Select part...",
                None
            )

            parts = get_parts_by_category(
                category_id
            )

            installed = get_installed_part(
                self.selected_vehicle[
                    "vehicle_id"
                ],
                category_id
            )

            installed_index = -1

            for part in parts:

                display = (
                    f"{part['part_name']} "
                    f"- ${float(part['price']):,.2f}"
                )

                combo.addItem(
                    display,
                    part
                )

                if (
                    installed
                    and part["part_id"]
                    == installed["part_id"]
                ):
                    installed_index = (
                        combo.count() - 1
                    )

            if installed_index >= 0:

                combo.setCurrentIndex(
                    installed_index
                )

            combo.currentIndexChanged.connect(
                lambda index,
                combo=combo,
                category_id=category_id:
                    self.part_changed(
                        combo,
                        category_id
                    )
            )

            self.customization_layout.addWidget(
                label,
                row,
                0
            )

            self.customization_layout.addWidget(
                combo,
                row,
                1
            )

    # --------------------------------------------------------
    # Part Changed
    # --------------------------------------------------------

    def part_changed(
        self,
        combo,
        category_id
    ):

        if self.selected_vehicle is None:
            return

        part = combo.currentData()

        if part is None:
            return

        role = self.user.get(
            "role_name",
            "Guest"
        )

        if role == "Guest":

            QMessageBox.information(
                self,
                "Login Required",
                "Please login as a Player to customize a vehicle."
            )

            return

        success, message = install_part(
            self.selected_vehicle[
                "vehicle_id"
            ],
            category_id,
            part["part_id"]
        )

        if not success:

            QMessageBox.warning(
                self,
                "Installation Error",
                message
            )

            return

        # Refresh preview
        self.preview.set_vehicle(
            self.selected_vehicle[
                "vehicle_id"
            ]
        )

        # Refresh statistics
        self.update_stats()

    # --------------------------------------------------------
    # Shop Page
    # --------------------------------------------------------

    def create_shop_page(self):

        page = QWidget()

        layout = QVBoxLayout()

        title = QLabel(
            "PARTS SHOP"
        )

        title.setFont(
            QFont(
                "Arial",
                22,
                QFont.Weight.Bold
            )
        )

        layout.addWidget(
            title
        )

        self.shop_list = QListWidget()

        layout.addWidget(
            self.shop_list
        )

        bottom = QHBoxLayout()

        self.quantity = QSpinBox()

        self.quantity.setMinimum(1)

        self.quantity.setMaximum(99)

        self.quantity.setValue(1)

        bottom.addWidget(
            QLabel("Quantity:")
        )

        bottom.addWidget(
            self.quantity
        )

        buy_button = QPushButton(
            "BUY SELECTED PART"
        )

        buy_button.clicked.connect(
            self.buy_selected_part
        )

        bottom.addWidget(
            buy_button
        )

        bottom.addStretch()

        layout.addLayout(
            bottom
        )

        page.setLayout(
            layout
        )

        self.load_shop()

        return page

    # --------------------------------------------------------
    # Load Shop
    # --------------------------------------------------------

    def load_shop(self):

        self.shop_list.clear()

        inventory = get_shop_inventory()

        for item in inventory:

            stock = item["stock"]

            text = (
                f"{item['category_name']} | "
                f"{item['part_name']} | "
                f"{item['manufacturer'] or 'Unknown'} | "
                f"${float(item['price']):,.2f} | "
                f"Stock: {stock}"
            )

            list_item = QListWidgetItem(
                text
            )

            list_item.setData(
                Qt.ItemDataRole.UserRole,
                item
            )

            self.shop_list.addItem(
                list_item
            )

    # --------------------------------------------------------
    # Buy
    # --------------------------------------------------------

    def buy_selected_part(self):

        if self.user["user_id"] is None:

            QMessageBox.information(
                self,
                "Login Required",
                "Guests cannot purchase parts."
            )

            return

        selected = (
            self.shop_list.currentItem()
        )

        if selected is None:

            QMessageBox.information(
                self,
                "Select Part",
                "Select a part first."
            )

            return

        item = selected.data(
            Qt.ItemDataRole.UserRole
        )

        quantity = self.quantity.value()

        success, message = buy_part(
            self.user["user_id"],
            item["part_id"],
            quantity
        )

        if success:

            QMessageBox.information(
                self,
                "Purchase Complete",
                message
            )

            # Refresh money
            updated_user = fetch_one(
                """
                SELECT
                    u.user_id,
                    u.username,
                    u.money,
                    u.role_id,
                    r.role_name
                FROM users u
                JOIN roles r
                    ON u.role_id = r.role_id
                WHERE u.user_id = %s
                """,
                (self.user["user_id"],)
            )

            if updated_user:
                self.user = updated_user

            self.update_user_label()

            self.load_shop()

        else:

            QMessageBox.warning(
                self,
                "Purchase Failed",
                message
            )

    # --------------------------------------------------------
    # User Label
    # --------------------------------------------------------

    def update_user_label(self):

        role = self.user.get(
            "role_name",
            "Guest"
        )

        money = float(
            self.user.get(
                "money",
                0
            ) or 0
        )

        self.user_label.setText(
            f"{self.user['username']} "
            f"| {role} "
            f"| ${money:,.2f}"
        )

    # --------------------------------------------------------
    # Management
    # --------------------------------------------------------

    def open_management(self):

        role = self.user.get(
            "role_name",
            "Guest"
        )

        if role == "Administrator":

            QMessageBox.information(
                self,
                "Administrator",
                """
Administrator panel will contain:

• User management
• Role management
• Manufacturer management
• Car model management
• Part management
• Category management
• Shop management
"""
            )

        elif role == "Shop Manager":

            QMessageBox.information(
                self,
                "Shop Manager",
                """
Shop Manager panel will contain:

• Part prices
• Shop stock
• Purchase history
• Inventory management
"""
            )

    # --------------------------------------------------------
    # Logout
    # --------------------------------------------------------

    def logout(self):

        self.login_window = LoginWindow()

        self.login_window.show()

        self.close()


# ============================================================
# APPLICATION START
# ============================================================

def main():

    app = QApplication(
        sys.argv
    )

    app.setApplicationName(
        "Car Customizer"
    )

    login_window = LoginWindow()

    login_window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()
