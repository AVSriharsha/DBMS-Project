import os
import sys
from decimal import Decimal

import mysql.connector
from mysql.connector import Error

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QFont, QPainter
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
    QMessageBox,
    QSizePolicy,
    QDialog,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QInputDialog,
    QHeaderView,
)


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_NAME = "car_customizer"
DB_USER = "root"
DB_PASSWORD = "" #Insert password in the quotes

CURRENT_USER_ID = 3


# ============================================================
# ASSETS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets", "car")


# ============================================================
# ROLE NAMES
# ============================================================

ROLE_GUEST = "Guest"
ROLE_PLAYER = "Player"
ROLE_SHOP_MANAGER = "Shop Manager"
ROLE_ADMIN = "Administrator"


# ============================================================
# HELPER
# ============================================================

def money(value):
    try:
        return f"₹{float(value):,.2f}"
    except Exception:
        return "₹0.00"


# ============================================================
# DATABASE CLASS
# ============================================================

class Database:

    def __init__(self):
        self.conn = None
        self.connect()

    def connect(self):
        self.conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            autocommit=True
        )

        print("Connected to MySQL")

    def ensure_connection(self):

        if self.conn is None or not self.conn.is_connected():
            self.connect()

        else:
            self.conn.ping(
                reconnect=True,
                attempts=3,
                delay=1
            )

    def query(self, sql, params=()):

        self.ensure_connection()

        cursor = self.conn.cursor(dictionary=True)

        try:
            cursor.execute(sql, params)
            return cursor.fetchall()

        finally:
            cursor.close()

    def one(self, sql, params=()):

        rows = self.query(sql, params)

        return rows[0] if rows else None

    def execute(self, sql, params=()):

        self.ensure_connection()

        cursor = self.conn.cursor()

        try:
            cursor.execute(sql, params)
            return cursor.lastrowid

        finally:
            cursor.close()

    def close(self):

        if self.conn and self.conn.is_connected():
            self.conn.close()


# ============================================================
# PART BUTTON
# ============================================================

class PartButton(QPushButton):

    def __init__(self, part):

        super().__init__()

        self.part = part

        self.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.setMinimumHeight(78)

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

        price = Decimal(
            str(part.get("price", 0) or 0)
        )

        hp = int(
            part.get("hp_bonus", 0) or 0
        )

        weight = int(
            part.get("weight_change", 0) or 0
        )

        speed = int(
            part.get("top_speed_bonus", 0) or 0
        )

        stock = int(
            part.get("stock", 0) or 0
        )

        extras = []

        if hp:
            extras.append(f"HP {hp:+d}")

        if speed:
            extras.append(f"Speed {speed:+d}")

        if weight:
            extras.append(f"Weight {weight:+d}")

        if not extras:
            extras.append("Stock / Standard")

        self.setText(
            f"{part['part_name']}\n"
            f"{money(price)}   •   "
            f"{'   '.join(extras)}   •   "
            f"Stock: {stock}"
        )


# ============================================================
# PURCHASE HISTORY DIALOG
# ============================================================

class PurchaseHistoryDialog(QDialog):

    def __init__(self, db, user_id, username, parent=None):

        super().__init__(parent)

        self.db = db
        self.user_id = user_id

        self.setWindowTitle(
            f"Purchase History — {username}"
        )

        self.resize(950, 600)

        self.setStyleSheet(
            """
            QDialog {
                background: #17191d;
            }

            QLabel {
                color: #e8edf2;
            }

            QTableWidget {
                background: #20242a;
                color: #e8edf2;
                border: 1px solid #454c55;
                gridline-color: #3d444c;
                selection-background-color: #66502f;
                selection-color: white;
            }

            QHeaderView::section {
                background: #30363e;
                color: #f0f2f4;
                padding: 8px;
                border: 1px solid #454c55;
                font-weight: bold;
            }

            QPushButton {
                background: #39424b;
                color: white;
                border: 1px solid #65717d;
                border-radius: 8px;
                padding: 9px 18px;
                font-weight: bold;
            }

            QPushButton:hover {
                background: #4a5662;
            }
            """
        )

        layout = QVBoxLayout(self)

        title = QLabel("PURCHASE HISTORY")

        title.setFont(
            QFont(
                "Segoe UI",
                20,
                QFont.Weight.Bold
            )
        )

        title.setStyleSheet(
            "color:#ffb55c;"
        )

        layout.addWidget(title)

        self.summary_label = QLabel()

        self.summary_label.setStyleSheet(
            """
            color:#c5ccd4;
            font-size:14px;
            padding:5px;
            """
        )

        layout.addWidget(self.summary_label)

        self.table = QTableWidget()

        self.table.setColumnCount(6)

        self.table.setHorizontalHeaderLabels(
            [
                "Part",
                "Category",
                "Quantity",
                "Amount Paid",
                "Purchase Date",
                "Purchase ID"
            ]
        )

        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.table.horizontalHeader().setStretchLastSection(True)

        self.table.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch
        )

        for column in (1, 2, 3, 4, 5):

            self.table.horizontalHeader().setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.ResizeToContents
            )

        layout.addWidget(self.table, 1)

        bottom = QHBoxLayout()

        self.total_label = QLabel()

        self.total_label.setFont(
            QFont(
                "Segoe UI",
                14,
                QFont.Weight.Bold
            )
        )

        self.total_label.setStyleSheet(
            "color:#ffd166;"
        )

        bottom.addWidget(self.total_label)

        bottom.addStretch()

        refresh_button = QPushButton("REFRESH")

        refresh_button.clicked.connect(
            self.load_history
        )

        bottom.addWidget(refresh_button)

        close_button = QPushButton("CLOSE")

        close_button.clicked.connect(
            self.accept
        )

        bottom.addWidget(close_button)

        layout.addLayout(bottom)

        self.load_history()

    def load_history(self):

        try:

            rows = self.db.query(
                """
                SELECT
                    pu.purchase_id,
                    p.part_name,
                    c.category_name,
                    pu.quantity,
                    pu.total_price,
                    pu.purchase_date
                FROM purchases pu
                JOIN parts p
                    ON p.part_id = pu.part_id
                JOIN categories c
                    ON c.category_id = p.category_id
                WHERE pu.user_id = %s
                ORDER BY pu.purchase_date DESC,
                         pu.purchase_id DESC
                """,
                (self.user_id,)
            )

            self.table.setRowCount(len(rows))

            total_spent = Decimal("0")
            total_items = 0

            for r, row in enumerate(rows):

                quantity = int(row["quantity"] or 0)

                amount = Decimal(
                    str(row["total_price"] or 0)
                )

                total_spent += amount
                total_items += quantity

                purchase_date = row["purchase_date"]

                if purchase_date:
                    date_text = purchase_date.strftime(
                        "%d-%m-%Y %H:%M"
                    )
                else:
                    date_text = "-"

                values = [
                    row["part_name"],
                    row["category_name"],
                    quantity,
                    money(amount),
                    date_text,
                    row["purchase_id"]
                ]

                for c, value in enumerate(values):

                    self.table.setItem(
                        r,
                        c,
                        QTableWidgetItem(str(value))
                    )

            self.summary_label.setText(
                f"Total purchases: {len(rows)}    •    "
                f"Items purchased: {total_items}"
            )

            self.total_label.setText(
                f"TOTAL SPENT: {money(total_spent)}"
            )

        except Exception as exc:

            QMessageBox.critical(
                self,
                "Purchase History Error",
                str(exc)
            )


# ============================================================
# MANAGEMENT DIALOG
# ============================================================

class ManagementDialog(QDialog):

    def __init__(
        self,
        db,
        role_name,
        parent=None
    ):

        super().__init__(parent)

        self.db = db
        self.role_name = role_name

        self.setWindowTitle(
            f"{role_name} Management"
        )

        self.resize(1000, 650)

        layout = QVBoxLayout(self)

        title = QLabel(
            f"{role_name.upper()} MANAGEMENT"
        )

        title.setFont(
            QFont(
                "Segoe UI",
                18,
                QFont.Weight.Bold
            )
        )

        title.setStyleSheet(
            "color:#ffb55c;"
        )

        layout.addWidget(title)

        self.tabs = QTabWidget()

        layout.addWidget(self.tabs)

        if role_name in (
            ROLE_SHOP_MANAGER,
            ROLE_ADMIN
        ):

            self.build_shop_tab()
            self.build_parts_tab()

        if role_name == ROLE_ADMIN:

            self.build_users_tab()
            self.build_roles_tab()

    # ========================================================
    # SHOP INVENTORY
    # ========================================================

    def build_shop_tab(self):

        tab = QWidget()

        layout = QVBoxLayout(tab)

        self.shop_table = QTableWidget()

        layout.addWidget(self.shop_table)

        buttons = QHBoxLayout()

        restock_button = QPushButton(
            "RESTOCK SELECTED"
        )

        restock_button.clicked.connect(
            self.restock_selected
        )

        buttons.addWidget(restock_button)

        price_button = QPushButton(
            "CHANGE PRICE"
        )

        price_button.clicked.connect(
            self.change_price
        )

        buttons.addWidget(price_button)

        refresh_button = QPushButton(
            "REFRESH"
        )

        refresh_button.clicked.connect(
            self.load_shop_inventory
        )

        buttons.addWidget(refresh_button)

        layout.addLayout(buttons)

        self.tabs.addTab(
            tab,
            "Shop Inventory"
        )

        self.load_shop_inventory()

    def load_shop_inventory(self):

        rows = self.db.query(
            """
            SELECT
                si.inventory_id,
                si.part_id,
                p.part_name,
                p.price,
                si.stock
            FROM shop_inventory si
            JOIN parts p
                ON p.part_id = si.part_id
            ORDER BY p.part_id
            """
        )

        self.shop_table.setRowCount(len(rows))
        self.shop_table.setColumnCount(5)

        self.shop_table.setHorizontalHeaderLabels(
            [
                "Inventory ID",
                "Part ID",
                "Part",
                "Price",
                "Stock"
            ]
        )

        for r, row in enumerate(rows):

            values = [
                row["inventory_id"],
                row["part_id"],
                row["part_name"],
                money(row["price"]),
                row["stock"]
            ]

            for c, value in enumerate(values):

                self.shop_table.setItem(
                    r,
                    c,
                    QTableWidgetItem(str(value))
                )

        self.shop_table.resizeColumnsToContents()

    def restock_selected(self):

        row = self.shop_table.currentRow()

        if row < 0:

            QMessageBox.warning(
                self,
                "No Selection",
                "Select a part first."
            )

            return

        part_id = int(
            self.shop_table.item(
                row,
                1
            ).text()
        )

        amount, ok = QInputDialog.getInt(
            self,
            "Restock",
            "How many units should be added?",
            10,
            1,
            1000
        )

        if not ok:
            return

        try:

            self.db.execute(
                """
                UPDATE shop_inventory
                SET stock = stock + %s
                WHERE part_id = %s
                """,
                (amount, part_id)
            )

            QMessageBox.information(
                self,
                "Restocked",
                "Shop inventory updated."
            )

            self.load_shop_inventory()

        except Exception as exc:

            QMessageBox.critical(
                self,
                "Error",
                str(exc)
            )

    def change_price(self):

        row = self.shop_table.currentRow()

        if row < 0:

            QMessageBox.warning(
                self,
                "No Selection",
                "Select a part first."
            )

            return

        part_id = int(
            self.shop_table.item(
                row,
                1
            ).text()
        )

        current_price_text = (
            self.shop_table.item(
                row,
                3
            ).text()
            .replace("₹", "")
            .replace(",", "")
        )

        try:
            current_price = float(current_price_text)
        except Exception:
            current_price = 0.0

        price, ok = QInputDialog.getDouble(
            self,
            "Change Price",
            "New price:",
            current_price,
            0,
            100000000,
            2
        )

        if not ok:
            return

        try:

            self.db.execute(
                """
                UPDATE parts
                SET price = %s
                WHERE part_id = %s
                """,
                (price, part_id)
            )

            QMessageBox.information(
                self,
                "Price Updated",
                "Part price updated successfully."
            )

            self.load_shop_inventory()

        except Exception as exc:

            QMessageBox.critical(
                self,
                "Error",
                str(exc)
            )

    # ========================================================
    # PARTS TAB
    # ========================================================

    def build_parts_tab(self):

        tab = QWidget()

        layout = QVBoxLayout(tab)

        self.parts_table = QTableWidget()

        layout.addWidget(self.parts_table)

        refresh = QPushButton(
            "REFRESH PARTS"
        )

        refresh.clicked.connect(
            self.load_parts_table
        )

        layout.addWidget(refresh)

        self.tabs.addTab(
            tab,
            "Parts"
        )

        self.load_parts_table()

    def load_parts_table(self):

        rows = self.db.query(
            """
            SELECT
                p.part_id,
                c.category_name,
                p.part_name,
                p.manufacturer,
                p.price,
                p.hp_bonus,
                p.weight_change,
                p.top_speed_bonus
            FROM parts p
            JOIN categories c
                ON c.category_id = p.category_id
            ORDER BY p.part_id
            """
        )

        self.parts_table.setRowCount(len(rows))
        self.parts_table.setColumnCount(8)

        self.parts_table.setHorizontalHeaderLabels(
            [
                "ID",
                "Category",
                "Part",
                "Manufacturer",
                "Price",
                "HP",
                "Weight",
                "Speed"
            ]
        )

        for r, row in enumerate(rows):

            values = [
                row["part_id"],
                row["category_name"],
                row["part_name"],
                row["manufacturer"],
                money(row["price"]),
                row["hp_bonus"],
                row["weight_change"],
                row["top_speed_bonus"]
            ]

            for c, value in enumerate(values):

                self.parts_table.setItem(
                    r,
                    c,
                    QTableWidgetItem(str(value))
                )

        self.parts_table.resizeColumnsToContents()

    # ========================================================
    # USERS TAB
    # ========================================================

    def build_users_tab(self):

        tab = QWidget()

        layout = QVBoxLayout(tab)

        self.users_table = QTableWidget()

        layout.addWidget(self.users_table)

        change_role = QPushButton(
            "CHANGE SELECTED USER ROLE"
        )

        change_role.clicked.connect(
            self.change_user_role
        )

        layout.addWidget(change_role)

        refresh = QPushButton(
            "REFRESH USERS"
        )

        refresh.clicked.connect(
            self.load_users
        )

        layout.addWidget(refresh)

        self.tabs.addTab(
            tab,
            "Users"
        )

        self.load_users()

    def load_users(self):

        rows = self.db.query(
            """
            SELECT
                u.user_id,
                u.username,
                u.money,
                r.role_name
            FROM users u
            JOIN roles r
                ON r.role_id = u.role_id
            ORDER BY u.user_id
            """
        )

        self.users_table.setRowCount(len(rows))
        self.users_table.setColumnCount(4)

        self.users_table.setHorizontalHeaderLabels(
            [
                "User ID",
                "Username",
                "Money",
                "Role"
            ]
        )

        for r, row in enumerate(rows):

            values = [
                row["user_id"],
                row["username"],
                money(row["money"]),
                row["role_name"]
            ]

            for c, value in enumerate(values):

                self.users_table.setItem(
                    r,
                    c,
                    QTableWidgetItem(str(value))
                )

        self.users_table.resizeColumnsToContents()

    def change_user_role(self):

        row = self.users_table.currentRow()

        if row < 0:

            QMessageBox.warning(
                self,
                "No Selection",
                "Select a user first."
            )

            return

        user_id = int(
            self.users_table.item(
                row,
                0
            ).text()
        )

        roles = self.db.query(
            """
            SELECT role_id, role_name
            FROM roles
            ORDER BY role_id
            """
        )

        role_names = [
            r["role_name"]
            for r in roles
        ]

        selected, ok = QInputDialog.getItem(
            self,
            "Change Role",
            "Select new role:",
            role_names,
            0,
            False
        )

        if not ok:
            return

        role_id = next(
            r["role_id"]
            for r in roles
            if r["role_name"] == selected
        )

        try:

            self.db.execute(
                """
                UPDATE users
                SET role_id = %s
                WHERE user_id = %s
                """,
                (role_id, user_id)
            )

            QMessageBox.information(
                self,
                "Role Updated",
                "User role changed successfully."
            )

            self.load_users()

        except Exception as exc:

            QMessageBox.critical(
                self,
                "Error",
                str(exc)
            )

    # ========================================================
    # ROLES TAB
    # ========================================================

    def build_roles_tab(self):

        tab = QWidget()

        layout = QVBoxLayout(tab)

        self.roles_table = QTableWidget()

        layout.addWidget(self.roles_table)

        refresh = QPushButton(
            "REFRESH ROLES"
        )

        refresh.clicked.connect(
            self.load_roles
        )

        layout.addWidget(refresh)

        self.tabs.addTab(
            tab,
            "Roles"
        )

        self.load_roles()

    def load_roles(self):

        rows = self.db.query(
            """
            SELECT role_id, role_name
            FROM roles
            ORDER BY role_id
            """
        )

        self.roles_table.setRowCount(len(rows))
        self.roles_table.setColumnCount(2)

        self.roles_table.setHorizontalHeaderLabels(
            [
                "Role ID",
                "Role Name"
            ]
        )

        for r, row in enumerate(rows):

            self.roles_table.setItem(
                r,
                0,
                QTableWidgetItem(
                    str(row["role_id"])
                )
            )

            self.roles_table.setItem(
                r,
                1,
                QTableWidgetItem(
                    str(row["role_name"])
                )
            )

        self.roles_table.resizeColumnsToContents()


# ============================================================
# MAIN GARAGE WINDOW
# ============================================================

class GarageWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.db = Database()

        self.user = None
        self.current_vehicle = None

        self.categories = []
        self.parts = []

        self.installed_parts = {}
        self.preview_parts = {}

        self.current_category_id = None
        self.selected_part = None

        self.role_name = ROLE_GUEST

        self.setWindowTitle(
            "Car Customizer Garage"
        )

        self.resize(1450, 850)

        self.setMinimumSize(1100, 700)

        self.load_user_and_vehicle()

        self.load_categories()

        self.load_installed_parts()

        self.build_ui()

        self.refresh_user_display()

        self.select_first_category()

        self.refresh_car_preview()

    # ========================================================
    # DATABASE LOADING
    # ========================================================

    def load_user_and_vehicle(self):

        self.user = self.db.one(
            """
            SELECT
                u.user_id,
                u.username,
                u.money,
                u.role_id,
                r.role_name
            FROM users u
            JOIN roles r
                ON r.role_id = u.role_id
            WHERE u.user_id = %s
            """,
            (CURRENT_USER_ID,)
        )

        if not self.user:

            raise RuntimeError(
                f"No user with user_id={CURRENT_USER_ID} exists."
            )

        self.role_name = (
            self.user["role_name"]
            or ROLE_GUEST
        )

        # ----------------------------------------------------
        # FIRST TRY TO LOAD THE USER'S OWN VEHICLE
        # ----------------------------------------------------

        self.current_vehicle = self.db.one(
            """
            SELECT
                v.vehicle_id,
                v.user_id,
                v.nickname,
                v.model_id,
                cm.model_name,
                cm.base_hp,
                cm.base_weight,
                cm.base_top_speed,
                cm.base_acceleration
            FROM vehicles v
            JOIN car_models cm
                ON cm.model_id = v.model_id
            WHERE v.user_id = %s
            ORDER BY v.vehicle_id
            LIMIT 1
            """,
            (CURRENT_USER_ID,)
        )

        # ----------------------------------------------------
        # ADMIN / MANAGER FALLBACK
        #
        # Admin and manager do not need their own vehicle to
        # access management. If they don't have one, use an
        # existing vehicle only for the garage preview.
        # ----------------------------------------------------

        if not self.current_vehicle and self.role_name in (
            ROLE_ADMIN,
            ROLE_SHOP_MANAGER
        ):

            self.current_vehicle = self.db.one(
                """
                SELECT
                    v.vehicle_id,
                    v.user_id,
                    v.nickname,
                    v.model_id,
                    cm.model_name,
                    cm.base_hp,
                    cm.base_weight,
                    cm.base_top_speed,
                    cm.base_acceleration
                FROM vehicles v
                JOIN car_models cm
                    ON cm.model_id = v.model_id
                ORDER BY v.vehicle_id
                LIMIT 1
                """
            )

            if self.current_vehicle:

                print(
                    f"{self.role_name} has no personal vehicle. "
                    f"Using vehicle_id="
                    f"{self.current_vehicle['vehicle_id']} "
                    f"for preview/management."
                )

        # ----------------------------------------------------
        # PLAYER STILL REQUIRES A VEHICLE
        # ----------------------------------------------------

        if not self.current_vehicle:

            raise RuntimeError(
                f"No vehicle exists for user_id={CURRENT_USER_ID}."
            )

    def load_categories(self):

        self.categories = self.db.query(
            """
            SELECT
                category_id,
                category_name
            FROM categories
            ORDER BY category_id
            """
        )

    def load_parts(self):

        if self.current_category_id is None:

            self.parts = []

            return

        self.parts = self.db.query(
            """
            SELECT
                p.part_id,
                p.category_id,
                p.part_name,
                p.manufacturer,
                p.price,
                p.hp_bonus,
                p.weight_change,
                p.top_speed_bonus,
                p.acceleration_bonus,
                p.sprite_file,
                p.layer_order,
                c.category_name,
                COALESCE(si.stock, 0) AS stock
            FROM parts p
            JOIN categories c
                ON c.category_id = p.category_id
            LEFT JOIN shop_inventory si
                ON si.part_id = p.part_id
            WHERE p.category_id = %s
            ORDER BY p.price, p.part_id
            """,
            (self.current_category_id,)
        )

    def load_installed_parts(self):

        self.installed_parts = {}

        rows = self.db.query(
            """
            SELECT
                vp.vehicle_id,
                vp.category_id,
                vp.part_id,
                p.part_name,
                p.manufacturer,
                p.price,
                p.hp_bonus,
                p.weight_change,
                p.top_speed_bonus,
                p.acceleration_bonus,
                p.sprite_file,
                p.layer_order,
                c.category_name
            FROM vehicle_parts vp
            JOIN parts p
                ON p.part_id = vp.part_id
            JOIN categories c
                ON c.category_id = vp.category_id
            WHERE vp.vehicle_id = %s
            """,
            (
                self.current_vehicle["vehicle_id"],
            )
        )

        for row in rows:

            self.installed_parts[
                row["category_id"]
            ] = row

        self.preview_parts = dict(
            self.installed_parts
        )

    # ========================================================
    # UI
    # ========================================================

    def build_ui(self):

        central = QWidget()

        self.setCentralWidget(central)

        main = QVBoxLayout(central)

        main.setContentsMargins(
            18,
            18,
            18,
            18
        )

        main.setSpacing(14)

        # ====================================================
        # HEADER
        # ====================================================

        header = QFrame()

        header.setObjectName("header")

        header.setStyleSheet(
            """
            QFrame#header {
                background: rgba(20, 23, 28, 235);
                border: 1px solid #444a52;
                border-radius: 14px;
            }
            """
        )

        h = QHBoxLayout(header)

        h.setContentsMargins(
            20,
            14,
            20,
            14
        )

        title = QLabel(
            "🔧  CAR CUSTOMIZER"
        )

        title.setFont(
            QFont(
                "Segoe UI",
                20,
                QFont.Weight.Bold
            )
        )

        subtitle = QLabel(
            f"{self.current_vehicle['nickname']}  •  "
            f"{self.current_vehicle['model_name']}"
        )

        subtitle.setStyleSheet(
            "color:#b9c0c8; font-size:14px;"
        )

        self.role_label = QLabel(
            f"ROLE: {self.role_name.upper()}"
        )

        self.role_label.setFont(
            QFont(
                "Segoe UI",
                11,
                QFont.Weight.Bold
            )
        )

        self.role_label.setStyleSheet(
            """
            color:#ffb55c;
            background:#292f36;
            border:1px solid #4a515b;
            border-radius:8px;
            padding:7px 10px;
            """
        )

        self.money_label = QLabel()

        self.money_label.setFont(
            QFont(
                "Segoe UI",
                16,
                QFont.Weight.Bold
            )
        )

        self.money_label.setStyleSheet(
            "color:#ffd166;"
        )

        h.addWidget(title)

        h.addSpacing(20)

        h.addWidget(subtitle)

        h.addStretch()

        h.addWidget(self.role_label)

        h.addSpacing(12)

        h.addWidget(self.money_label)

        main.addWidget(header)

        # ====================================================
        # CONTENT
        # ====================================================

        content = QHBoxLayout()

        content.setSpacing(14)

        main.addLayout(content, 1)

        # ====================================================
        # CATEGORIES
        # ====================================================

        left = QFrame()

        left.setFixedWidth(185)

        left.setStyleSheet(
            """
            QFrame {
                background: rgba(20, 23, 28, 235);
                border: 1px solid #444a52;
                border-radius: 14px;
            }

            QPushButton {
                background: #292f36;
                border: 1px solid #4a515b;
                border-radius: 9px;
                padding: 12px;
                text-align: left;
                font-size: 14px;
            }

            QPushButton:hover {
                background: #353c45;
            }

            QPushButton:checked {
                background: #d98b32;
                color: white;
                border-color: #ffb55c;
            }
            """
        )

        left_layout = QVBoxLayout(left)

        left_layout.setContentsMargins(
            12,
            12,
            12,
            12
        )

        cat_title = QLabel("CATEGORIES")

        cat_title.setFont(
            QFont(
                "Segoe UI",
                11,
                QFont.Weight.Bold
            )
        )

        cat_title.setStyleSheet(
            "color:#aeb5bd;"
        )

        left_layout.addWidget(cat_title)

        left_layout.addSpacing(6)

        self.category_buttons = []

        for category in self.categories:

            button = QPushButton(
                category["category_name"]
            )

            button.setCheckable(True)

            button.clicked.connect(
                lambda checked,
                cid=category["category_id"]:
                self.select_category(cid)
            )

            self.category_buttons.append(
                (
                    category["category_id"],
                    button
                )
            )

            left_layout.addWidget(button)

        left_layout.addStretch()

        content.addWidget(left)

        # ====================================================
        # CENTER CAR
        # ====================================================

        center = QFrame()

        center.setStyleSheet(
            """
            QFrame {
                background: rgba(38, 31, 24, 220);
                border: 1px solid #5d5144;
                border-radius: 14px;
            }
            """
        )

        center_layout = QVBoxLayout(center)

        center_layout.setContentsMargins(
            20,
            18,
            20,
            18
        )

        garage_label = QLabel(
            "GARAGE WORKSPACE"
        )

        garage_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        garage_label.setFont(
            QFont(
                "Segoe UI",
                12,
                QFont.Weight.Bold
            )
        )

        garage_label.setStyleSheet(
            "color:#d8c5aa;"
        )

        center_layout.addWidget(garage_label)

        self.car_label = QLabel()

        self.car_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.car_label.setMinimumSize(
            650,
            450
        )

        self.car_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        center_layout.addWidget(
            self.car_label,
            1
        )

        self.status_label = QLabel(
            "Select a modification."
        )

        self.status_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.status_label.setStyleSheet(
            "color:#c5ccd4; font-size:14px; padding:8px;"
        )

        center_layout.addWidget(self.status_label)

        content.addWidget(center, 1)

        # ====================================================
        # PARTS
        # ====================================================

        right = QFrame()

        right.setFixedWidth(355)

        right.setStyleSheet(
            """
            QFrame {
                background: rgba(20, 23, 28, 235);
                border: 1px solid #444a52;
                border-radius: 14px;
            }

            QListWidget {
                background: transparent;
                border: none;
            }
            """
        )

        right_layout = QVBoxLayout(right)

        right_layout.setContentsMargins(
            14,
            14,
            14,
            14
        )

        self.parts_title = QLabel("PARTS")

        self.parts_title.setFont(
            QFont(
                "Segoe UI",
                14,
                QFont.Weight.Bold
            )
        )

        right_layout.addWidget(self.parts_title)

        self.parts_list = QListWidget()

        self.parts_list.setSpacing(7)

        self.parts_list.itemClicked.connect(
            self.part_clicked
        )

        right_layout.addWidget(
            self.parts_list,
            1
        )

        self.selected_label = QLabel(
            "No part selected"
        )

        self.selected_label.setWordWrap(True)

        self.selected_label.setStyleSheet(
            "color:#c5ccd4; padding:5px;"
        )

        right_layout.addWidget(self.selected_label)

        self.buy_button = QPushButton(
            "BUY / INSTALL"
        )

        self.buy_button.setMinimumHeight(48)

        self.buy_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.buy_button.clicked.connect(
            self.install_selected_part
        )

        self.buy_button.setStyleSheet(
            """
            QPushButton {
                background: #d98b32;
                border: 1px solid #ffb55c;
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
                padding: 10px;
            }

            QPushButton:hover {
                background: #ee9a3b;
            }

            QPushButton:disabled {
                background: #4a4f55;
                border-color: #555a61;
                color: #a0a5aa;
            }
            """
        )

        right_layout.addWidget(self.buy_button)

        # ====================================================
        # PURCHASE HISTORY
        # ====================================================

        history_button = QPushButton(
            "📋 PURCHASE HISTORY"
        )

        history_button.setMinimumHeight(42)

        history_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        history_button.clicked.connect(
            self.open_purchase_history
        )

        history_button.setStyleSheet(
            """
            QPushButton {
                background:#303840;
                border:1px solid #65717d;
                border-radius:9px;
                padding:8px;
                font-weight:bold;
            }

            QPushButton:hover {
                background:#414c57;
            }
            """
        )

        right_layout.addWidget(history_button)

        # ====================================================
        # MANAGEMENT
        # ====================================================

        if self.role_name in (
            ROLE_SHOP_MANAGER,
            ROLE_ADMIN
        ):

            management_button = QPushButton(
                "⚙ MANAGEMENT"
            )

            management_button.setMinimumHeight(42)

            management_button.clicked.connect(
                self.open_management
            )

            management_button.setStyleSheet(
                """
                QPushButton {
                    background:#39424b;
                    border:1px solid #65717d;
                    border-radius:9px;
                    padding:8px;
                    font-weight:bold;
                }

                QPushButton:hover {
                    background:#4a5662;
                }
                """
            )

            right_layout.addWidget(management_button)

        content.addWidget(right)

        # ====================================================
        # STATS
        # ====================================================

        stats = QFrame()

        stats.setStyleSheet(
            """
            QFrame {
                background: rgba(20, 23, 28, 235);
                border: 1px solid #444a52;
                border-radius: 14px;
            }
            """
        )

        stats_layout = QHBoxLayout(stats)

        stats_layout.setContentsMargins(
            18,
            12,
            18,
            12
        )

        self.hp_label = QLabel()
        self.weight_label = QLabel()
        self.speed_label = QLabel()
        self.accel_label = QLabel()

        for label in (
            self.hp_label,
            self.weight_label,
            self.speed_label,
            self.accel_label
        ):

            label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            label.setFont(
                QFont(
                    "Segoe UI",
                    11,
                    QFont.Weight.Bold
                )
            )

            stats_layout.addWidget(label, 1)

        main.addWidget(stats)

        # ====================================================
        # WINDOW STYLE
        # ====================================================

        self.setStyleSheet(
            """
            QMainWindow {
                background:
                    qlineargradient(
                        x1:0,
                        y1:0,
                        x2:0,
                        y2:1,
                        stop:0 #17191d,
                        stop:0.45 #2b241e,
                        stop:1 #111315
                    );
            }
            """
        )

    # ========================================================
    # ROLE ACCESS
    # ========================================================

    def can_buy(self):

        return self.role_name in (
            ROLE_PLAYER,
            ROLE_SHOP_MANAGER,
            ROLE_ADMIN
        )

    def can_manage_shop(self):

        return self.role_name in (
            ROLE_SHOP_MANAGER,
            ROLE_ADMIN
        )

    def can_manage_users(self):

        return self.role_name == ROLE_ADMIN

    # ========================================================
    # PURCHASE HISTORY
    # ========================================================

    def open_purchase_history(self):

        if not self.user:

            QMessageBox.warning(
                self,
                "No User",
                "No user account is currently loaded."
            )

            return

        dialog = PurchaseHistoryDialog(
            self.db,
            self.user["user_id"],
            self.user["username"],
            self
        )

        dialog.exec()

    # ========================================================
    # MANAGEMENT
    # ========================================================

    def open_management(self):

        if not self.can_manage_shop():

            QMessageBox.warning(
                self,
                "Access Denied",
                "You do not have management access."
            )

            return

        dialog = ManagementDialog(
            self.db,
            self.role_name,
            self
        )

        dialog.exec()

        self.load_parts()
        self.populate_parts()
        self.refresh_user_display()

    # ========================================================
    # CATEGORY / PARTS
    # ========================================================

    def select_first_category(self):

        if self.categories:

            self.select_category(
                self.categories[0]["category_id"]
            )

    def select_category(
        self,
        category_id
    ):

        self.current_category_id = category_id

        for cid, button in self.category_buttons:

            button.setChecked(
                cid == category_id
            )

        self.load_parts()

        self.populate_parts()

    def populate_parts(self):

        self.parts_list.clear()

        category_name = "Parts"

        for category in self.categories:

            if category["category_id"] == self.current_category_id:

                category_name = category["category_name"]

                break

        self.parts_title.setText(
            category_name.upper()
        )

        for part in self.parts:

            item = QListWidgetItem()

            button = PartButton(part)

            installed = self.installed_parts.get(
                part["category_id"]
            )

            if (
                installed
                and installed["part_id"] == part["part_id"]
            ):

                button.setStyleSheet(
                    """
                    QPushButton {
                        background: #394b3b;
                        border: 1px solid #76a879;
                        border-radius: 9px;
                        padding: 8px;
                        text-align: left;
                    }
                    """
                )

            self.parts_list.addItem(item)

            self.parts_list.setItemWidget(
                item,
                button
            )

            item.setSizeHint(
                QSize(0, 82)
            )

            button.clicked.connect(
                lambda checked=False,
                p=part:
                self.select_part(p)
            )

        # ----------------------------------------------------
        # IMPORTANT:
        # Do NOT automatically preview the first part.
        #
        # This prevents the paint category from automatically
        # switching to Red Paint.
        # ----------------------------------------------------

        if self.current_category_id in self.preview_parts:

            installed_preview = self.preview_parts[
                self.current_category_id
            ]

            for part in self.parts:

                if (
                    part["part_id"]
                    == installed_preview["part_id"]
                ):

                    self.select_part(
                        part,
                        update_preview=False
                    )

                    break

        elif self.parts:

            # If there is no installed part in this category,
            # show the first part as a selection but do not
            # permanently alter the preview.
            self.selected_part = None

            self.selected_label.setText(
                "Select a part to preview it."
            )

            self.buy_button.setText(
                "SELECT A PART"
            )

            self.buy_button.setEnabled(False)

    def part_clicked(
        self,
        item
    ):

        button = self.parts_list.itemWidget(item)

        if button:

            self.select_part(button.part)

    def select_part(
        self,
        part,
        update_preview=True
    ):

        self.selected_part = part

        category_id = part["category_id"]

        if update_preview:

            self.preview_parts[category_id] = part

        price = Decimal(
            str(
                part.get("price", 0) or 0
            )
        )

        stock = int(
            part.get("stock", 0) or 0
        )

        installed = self.installed_parts.get(
            category_id
        )

        is_installed = (
            installed is not None
            and installed["part_id"] == part["part_id"]
        )

        if is_installed:

            self.selected_label.setText(
                f"<b>{part['part_name']}</b><br>"
                f"{money(price)}<br>"
                f"Already installed on this vehicle."
            )

            self.buy_button.setText(
                "INSTALLED"
            )

            self.buy_button.setEnabled(False)

            self.status_label.setText(
                f"{part['part_name']} "
                f"is currently installed."
            )

        else:

            self.selected_label.setText(
                f"<b>{part['part_name']}</b><br>"
                f"Price: {money(price)}<br>"
                f"Shop stock: {stock}"
            )

            if not self.can_buy():

                self.buy_button.setText(
                    "GUEST — PURCHASE DISABLED"
                )

                self.buy_button.setEnabled(False)

                self.status_label.setText(
                    "Guest access: "
                    "you can preview parts, "
                    "but cannot purchase them."
                )

            else:

                self.buy_button.setText(
                    "INSTALL"
                    if price == 0
                    else "BUY / INSTALL"
                )

                self.buy_button.setEnabled(
                    stock > 0
                )

                if stock <= 0:

                    self.status_label.setText(
                        "This part is currently "
                        "out of stock."
                    )

                else:

                    self.status_label.setText(
                        f"Previewing: "
                        f"{part['part_name']} — "
                        f"click BUY / INSTALL "
                        f"to save it."
                    )

        self.refresh_car_preview()

    # ========================================================
    # IMAGE / PREVIEW
    # ========================================================

    def find_asset(
        self,
        filename
    ):

        if not filename:
            return None

        filename = os.path.basename(
            str(filename)
        )

        candidates = [
            os.path.join(
                ASSET_DIR,
                filename
            )
        ]

        if filename.endswith(".png"):

            candidates.append(
                os.path.join(
                    ASSET_DIR,
                    filename + ".png"
                )
            )

        for path in candidates:

            if os.path.exists(path):

                return path

        return None

    def load_pixmap(
        self,
        filename
    ):

        path = self.find_asset(filename)

        if not path:
            return None

        pixmap = QPixmap(path)

        if pixmap.isNull():
            return None

        return pixmap

    def base_pixmap(self):

        return (
            self.load_pixmap("base.png")
            or
            self.load_pixmap("base.png.png")
        )

    def refresh_car_preview(self):

        if not hasattr(self, "car_label"):
            return

        base = self.base_pixmap()

        if base is None:

            self.car_label.setText(
                "BASE CAR IMAGE NOT FOUND\n\n"
                "Put base.png inside:\n"
                "assets/car/"
            )

            return

        result = QPixmap(base.size())

        result.fill(
            Qt.GlobalColor.transparent
        )

        painter = QPainter(result)

        painter.setCompositionMode(
            QPainter.CompositionMode.CompositionMode_Source
        )

        painter.drawPixmap(
            0,
            0,
            base
        )

        parts = list(
            self.preview_parts.values()
        )

        parts.sort(
            key=lambda p: (
                int(
                    p.get("layer_order", 1) or 1
                ),
                int(
                    p.get("part_id", 0) or 0
                )
            )
        )

        painter.setCompositionMode(
            QPainter.CompositionMode.CompositionMode_SourceOver
        )

        for part in parts:

            sprite = self.load_pixmap(
                part.get("sprite_file")
            )

            if not sprite:
                continue

            if sprite.size() == result.size():

                painter.drawPixmap(
                    0,
                    0,
                    sprite
                )

            else:

                scaled = sprite.scaled(
                    result.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )

                x = (
                    result.width()
                    - scaled.width()
                ) // 2

                y = (
                    result.height()
                    - scaled.height()
                ) // 2

                painter.drawPixmap(
                    x,
                    y,
                    scaled
                )

        painter.end()

        display = result.scaled(
            self.car_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.car_label.setPixmap(display)

        self.update_stats()

    # ========================================================
    # STATS
    # ========================================================

    def update_stats(self):

        hp = int(
            self.current_vehicle.get(
                "base_hp",
                100
            ) or 0
        )

        weight = int(
            self.current_vehicle.get(
                "base_weight",
                1000
            ) or 0
        )

        speed = int(
            self.current_vehicle.get(
                "base_top_speed",
                150
            ) or 0
        )

        accel = Decimal(
            str(
                self.current_vehicle.get(
                    "base_acceleration",
                    10
                ) or 0
            )
        )

        for part in self.preview_parts.values():

            hp += int(
                part.get("hp_bonus", 0) or 0
            )

            weight += int(
                part.get("weight_change", 0) or 0
            )

            speed += int(
                part.get("top_speed_bonus", 0) or 0
            )

            accel += Decimal(
                str(
                    part.get(
                        "acceleration_bonus",
                        0
                    ) or 0
                )
            )

        self.hp_label.setText(
            f"⚡ HP\n{hp}"
        )

        self.weight_label.setText(
            f"⚖ Weight\n{weight} kg"
        )

        self.speed_label.setText(
            f"🏁 Top Speed\n{speed} km/h"
        )

        self.accel_label.setText(
            f"🚀 Acceleration\n{accel:.2f}"
        )

    # ========================================================
    # MONEY
    # ========================================================

    def refresh_user_display(self):

        self.user = self.db.one(
            """
            SELECT
                u.user_id,
                u.username,
                u.money,
                u.role_id,
                r.role_name
            FROM users u
            JOIN roles r
                ON r.role_id = u.role_id
            WHERE u.user_id = %s
            """,
            (CURRENT_USER_ID,)
        )

        if not self.user:
            return

        self.money_label.setText(
            f"💰 {money(self.user['money'])}"
        )

        self.role_name = (
            self.user["role_name"]
            or ROLE_GUEST
        )

        self.role_label.setText(
            f"ROLE: {self.role_name.upper()}"
        )

    # ========================================================
    # BUY / INSTALL
    # ========================================================

    def install_selected_part(self):

        if not self.can_buy():

            QMessageBox.warning(
                self,
                "Access Denied",
                "Guest accounts cannot purchase "
                "or install modifications."
            )

            return

        if not self.selected_part:

            QMessageBox.warning(
                self,
                "No Part Selected",
                "Please select a modification first."
            )

            return

        # ----------------------------------------------------
        # ADMIN / MANAGER MUST NOT INSTALL ON A VEHICLE
        # BELONGING TO ANOTHER USER.
        #
        # They can use the preview and management screens,
        # but purchases/installations belong to the player.
        # ----------------------------------------------------

        if (
            self.role_name in (
                ROLE_ADMIN,
                ROLE_SHOP_MANAGER
            )
            and self.current_vehicle.get("user_id")
            != CURRENT_USER_ID
        ):

            QMessageBox.information(
                self,
                "Management Account",
                "Management accounts can preview "
                "vehicle modifications and manage the shop, "
                "but they cannot install parts on another "
                "user's vehicle."
            )

            return

        self.install_part(
            self.selected_part
        )

    def install_part(
        self,
        part
    ):

        if not self.can_buy():
            return

        if not self.current_vehicle:

            QMessageBox.warning(
                self,
                "No Vehicle",
                "No vehicle is available."
            )

            return

        vehicle_id = self.current_vehicle[
            "vehicle_id"
        ]

        user_id = CURRENT_USER_ID

        part_id = int(
            part["part_id"]
        )

        category_id = int(
            part["category_id"]
        )

        price = Decimal(
            str(
                part.get("price", 0) or 0
            )
        )

        cursor = None

        try:

            self.db.ensure_connection()

            self.db.conn.rollback()

            self.db.conn.autocommit = False

            self.db.conn.start_transaction()

            cursor = self.db.conn.cursor(
                dictionary=True
            )

            # ------------------------------------------------
            # LOCK PLAYER
            # ------------------------------------------------

            cursor.execute(
                """
                SELECT money
                FROM users
                WHERE user_id = %s
                FOR UPDATE
                """,
                (user_id,)
            )

            user_row = cursor.fetchone()

            if not user_row:

                raise RuntimeError(
                    "Player account was not found."
                )

            current_money = Decimal(
                str(
                    user_row["money"] or 0
                )
            )

            if current_money < price:

                raise RuntimeError(
                    "Not enough money.\n\n"
                    f"Your money: "
                    f"{money(current_money)}\n"
                    f"Part price: "
                    f"{money(price)}"
                )

            # ------------------------------------------------
            # LOCK STOCK
            # ------------------------------------------------

            cursor.execute(
                """
                SELECT stock
                FROM shop_inventory
                WHERE part_id = %s
                FOR UPDATE
                """,
                (part_id,)
            )

            stock_row = cursor.fetchone()

            if not stock_row:

                raise RuntimeError(
                    "This part is not present "
                    "in shop inventory."
                )

            stock = int(
                stock_row["stock"] or 0
            )

            if stock <= 0:

                raise RuntimeError(
                    "This part is currently out of stock."
                )

            # ------------------------------------------------
            # PLAYER INVENTORY
            # ------------------------------------------------

            cursor.execute(
                """
                SELECT
                    inventory_id,
                    quantity
                FROM player_inventory
                WHERE user_id = %s
                  AND part_id = %s
                FOR UPDATE
                """,
                (
                    user_id,
                    part_id
                )
            )

            inv_row = cursor.fetchone()

            # ------------------------------------------------
            # CURRENT VEHICLE PART
            # ------------------------------------------------

            cursor.execute(
                """
                SELECT part_id
                FROM vehicle_parts
                WHERE vehicle_id = %s
                  AND category_id = %s
                FOR UPDATE
                """,
                (
                    vehicle_id,
                    category_id
                )
            )

            installed_row = cursor.fetchone()

            if (
                installed_row
                and int(
                    installed_row["part_id"]
                ) == part_id
            ):

                self.db.conn.rollback()

                self.db.conn.autocommit = True

                self.load_installed_parts()

                self.refresh_user_display()

                self.refresh_car_preview()

                QMessageBox.information(
                    self,
                    "Already Installed",
                    f"{part['part_name']} "
                    f"is already installed."
                )

                return

            # ------------------------------------------------
            # DEDUCT MONEY
            # ------------------------------------------------

            cursor.execute(
                """
                UPDATE users
                SET money = money - %s
                WHERE user_id = %s
                """,
                (
                    price,
                    user_id
                )
            )

            # ------------------------------------------------
            # REDUCE SHOP STOCK
            # ------------------------------------------------

            cursor.execute(
                """
                UPDATE shop_inventory
                SET stock = stock - 1
                WHERE part_id = %s
                """,
                (part_id,)
            )

            # ------------------------------------------------
            # PLAYER INVENTORY
            # ------------------------------------------------

            if inv_row:

                cursor.execute(
                    """
                    UPDATE player_inventory
                    SET quantity = quantity + 1
                    WHERE inventory_id = %s
                    """,
                    (
                        inv_row["inventory_id"],
                    )
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
                    VALUES
                        (
                            %s,
                            %s,
                            1
                        )
                    """,
                    (
                        user_id,
                        part_id
                    )
                )

            # ------------------------------------------------
            # PURCHASE RECORD
            # ------------------------------------------------

            cursor.execute(
                """
                INSERT INTO purchases
                    (
                        user_id,
                        part_id,
                        quantity,
                        total_price
                    )
                VALUES
                    (
                        %s,
                        %s,
                        1,
                        %s
                    )
                """,
                (
                    user_id,
                    part_id,
                    price
                )
            )

            # ------------------------------------------------
            # INSTALL / REPLACE PART
            # ------------------------------------------------

            if installed_row:

                cursor.execute(
                    """
                    UPDATE vehicle_parts
                    SET part_id = %s
                    WHERE vehicle_id = %s
                      AND category_id = %s
                    """,
                    (
                        part_id,
                        vehicle_id,
                        category_id
                    )
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
                    VALUES
                        (
                            %s,
                            %s,
                            %s
                        )
                    """,
                    (
                        vehicle_id,
                        category_id,
                        part_id
                    )
                )

            # ------------------------------------------------
            # COMMIT
            # ------------------------------------------------

            self.db.conn.commit()

            self.db.conn.autocommit = True

            # ------------------------------------------------
            # REFRESH
            # ------------------------------------------------

            self.load_installed_parts()

            self.refresh_user_display()

            self.load_parts()

            self.populate_parts()

            self.refresh_car_preview()

            self.status_label.setText(
                f"✓ {part['part_name']} "
                f"purchased and installed."
            )

            QMessageBox.information(
                self,
                "Purchase Complete",
                f"{part['part_name']} "
                f"was purchased and installed successfully.\n\n"
                f"Amount paid: {money(price)}"
            )

        except Exception as exc:

            try:
                self.db.conn.rollback()
            except Exception:
                pass

            try:
                self.db.conn.autocommit = True
            except Exception:
                pass

            print(
                "Purchase error:",
                repr(exc)
            )

            QMessageBox.critical(
                self,
                "Purchase Error",
                f"The purchase could not be completed.\n\n"
                f"{exc}"
            )

        finally:

            if cursor is not None:

                try:
                    cursor.close()
                except Exception:
                    pass

    # ========================================================
    # EVENTS
    # ========================================================

    def resizeEvent(
        self,
        event
    ):

        super().resizeEvent(event)

        if hasattr(self, "car_label"):

            self.refresh_car_preview()

    def closeEvent(
        self,
        event
    ):

        try:
            self.db.close()
        except Exception:
            pass

        event.accept()


# ============================================================
# MAIN
# ============================================================

def main():

    app = QApplication(sys.argv)

    app.setApplicationName(
        "Car Customizer"
    )

    app.setFont(
        QFont(
            "Segoe UI",
            10
        )
    )

    try:

        window = GarageWindow()

        print(
            f"Logged in as "
            f"{window.user['username']} "
            f"(user_id={window.user['user_id']})"
        )

        window.show()

        sys.exit(
            app.exec()
        )

    except Error as exc:

        QMessageBox.critical(
            None,
            "MySQL Error",
            f"Could not connect to MySQL.\n\n{exc}"
        )

        print(
            "MySQL error:",
            exc
        )

        sys.exit(1)

    except Exception as exc:

        QMessageBox.critical(
            None,
            "Application Error",
            f"The application could not start.\n\n{exc}"
        )

        print(
            "Application error:",
            repr(exc)
        )

        sys.exit(1)


if __name__ == "__main__":
    main()
