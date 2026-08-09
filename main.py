from pathlib import Path

import os
import sys
import mysql.connector

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QVBoxLayout, QHBoxLayout,
    QFrame, QMessageBox
)

# ============================================================
# DATABASE CONFIGURATION
# ============================================================
DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "P14Y3R"          # <-- PUT YOUR MYSQL PASSWORD HERE
DB_NAME = "car_customizer"

# Temporary development user.
# Your current "player" account / vehicle uses user_id = 3.
CURRENT_USER_ID = 3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAR_ASSET_DIR = os.path.join(BASE_DIR, "assets", "car")


# ============================================================
# DATABASE
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
            autocommit=False
        )
        print("Connected to MySQL")

    def cursor(self):
        return self.conn.cursor(dictionary=True)

    def fetchone(self, query, params=()):
        cur = self.cursor()
        try:
            cur.execute(query, params)
            return cur.fetchone()
        finally:
            cur.close()

    def fetchall(self, query, params=()):
        cur = self.cursor()
        try:
            cur.execute(query, params)
            return cur.fetchall()
        finally:
            cur.close()

    def execute(self, query, params=()):
        cur = self.cursor()
        try:
            cur.execute(query, params)
            return cur.lastrowid, cur.rowcount
        finally:
            cur.close()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        if self.conn and self.conn.is_connected():
            self.conn.close()


# ============================================================
# LIVE CAR PREVIEW
# ============================================================
class CarPreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.base = self.load_pixmap("base.png")

        # Each category is a separate transparent layer.
        self.layers = {
            "Paint": None,
            "Engine": None,
            "Wheels": None,
            "Bumper": None,
            "Spoiler": None,
        }

        self.setMinimumSize(720, 400)

    def load_pixmap(self, filename):
        if not filename:
            return None

        path = os.path.join(CAR_ASSET_DIR, filename)

        if not os.path.exists(path):
            print("Asset not found:", path)
            return None

        pixmap = QPixmap(path)

        if pixmap.isNull():
            print("Could not load image:", path)
            return None

        return pixmap

    def set_part(self, category_name, filename):
        if category_name not in self.layers:
            return

        self.layers[category_name] = self.load_pixmap(filename)
        self.update()

    def clear_part(self, category_name):
        if category_name in self.layers:
            self.layers[category_name] = None
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(
            QPainter.RenderHint.SmoothPixmapTransform
        )

        if self.base is None:
            painter.end()
            return

        base_size = self.base.size()

        scale = min(
            self.width() / base_size.width(),
            self.height() / base_size.height()
        )

        draw_w = int(base_size.width() * scale)
        draw_h = int(base_size.height() * scale)

        x = (self.width() - draw_w) // 2
        y = (self.height() - draw_h) // 2

        def draw_layer(image):
            if image is None:
                return

            scaled = image.scaled(
                draw_w,
                draw_h,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            painter.drawPixmap(x, y, scaled)

        # Layer order is important.
        draw_layer(self.base)
        draw_layer(self.layers["Paint"])
        draw_layer(self.layers["Engine"])
        draw_layer(self.layers["Wheels"])
        draw_layer(self.layers["Bumper"])
        draw_layer(self.layers["Spoiler"])

        painter.end()


# ============================================================
# MAIN GARAGE WINDOW
# ============================================================
class GarageWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()

        self.db = db

        self.current_vehicle = None
        self.parts = []
        self.categories = []
        self.selected_part = None

        # category_id -> currently installed part
        self.installed_parts = {}

        self.setWindowTitle("Car Customizer - Garage")
        self.resize(1400, 850)

        self.load_vehicle()
        self.load_categories()
        self.load_parts()

        self.build_ui()

        self.load_installed_parts()
        self.update_money()
        self.refresh_stats()

    # --------------------------------------------------------
    # DATABASE DATA
    # --------------------------------------------------------
    def load_vehicle(self):
        self.current_vehicle = self.db.fetchone(
            """
            SELECT
                v.vehicle_id,
                v.user_id,
                v.model_id,
                v.nickname,
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
            LIMIT 1
            """,
            (CURRENT_USER_ID,)
        )

        if not self.current_vehicle:
            raise RuntimeError(
                f"No vehicle found for user_id={CURRENT_USER_ID}."
            )

    def load_categories(self):
        self.categories = self.db.fetchall(
            """
            SELECT category_id, category_name
            FROM categories
            ORDER BY category_id
            """
        )

    def load_parts(self):
        self.parts = self.db.fetchall(
            """
            SELECT
                p.part_id,
                p.category_id,
                c.category_name,
                p.part_name,
                p.manufacturer,
                p.price,
                p.hp_bonus,
                p.weight_change,
                p.top_speed_bonus,
                p.acceleration_bonus,
                p.sprite_file,
                p.layer_order
            FROM parts p
            JOIN categories c
                ON p.category_id = c.category_id
            ORDER BY p.layer_order, c.category_name, p.part_id
            """
        )

    def load_installed_parts(self):
        vehicle_id = self.current_vehicle["vehicle_id"]

        rows = self.db.fetchall(
            """
            SELECT
                vp.category_id,
                vp.part_id,
                p.part_name,
                p.sprite_file,
                p.layer_order,
                p.hp_bonus,
                p.weight_change,
                p.top_speed_bonus,
                p.acceleration_bonus,
                c.category_name
            FROM vehicle_parts vp
            JOIN parts p
                ON vp.part_id = p.part_id
            JOIN categories c
                ON vp.category_id = c.category_id
            WHERE vp.vehicle_id = %s
            ORDER BY p.layer_order
            """,
            (vehicle_id,)
        )

        self.installed_parts.clear()

        for row in rows:
            self.installed_parts[row["category_id"]] = row

            self.preview.set_part(
                row["category_name"],
                row["sprite_file"]
            )

    def get_inventory_quantity(self, part_id):
        row = self.db.fetchone(
            """
            SELECT quantity
            FROM player_inventory
            WHERE user_id = %s
              AND part_id = %s
            """,
            (CURRENT_USER_ID, part_id)
        )

        return int(row["quantity"]) if row else 0

    def update_money(self):
        row = self.db.fetchone(
            """
            SELECT money
            FROM users
            WHERE user_id = %s
            """,
            (CURRENT_USER_ID,)
        )

        if row:
            self.money_label.setText(
                f"Money: ₹{float(row['money']):,.2f}"
            )

    # --------------------------------------------------------
    # USER INTERFACE
    # --------------------------------------------------------
    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        # Garage-style UI. We can replace this with a proper
        # garage background image later.
        central.setStyleSheet("""
            QWidget {
                background: #20242a;
                color: #eeeeee;
            }

            QFrame#topbar {
                background: #111418;
                border-bottom: 2px solid #3b414a;
            }

            QFrame#panel {
                background: #171a1f;
                border: 1px solid #3b414a;
                border-radius: 10px;
            }

            QListWidget {
                background: #101216;
                border: 1px solid #3b414a;
                border-radius: 8px;
                padding: 4px;
            }

            QListWidget::item {
                padding: 12px 8px;
                border-radius: 6px;
            }

            QListWidget::item:selected {
                background: #3b4654;
            }

            QPushButton {
                background: #343c47;
                border: 1px solid #596574;
                border-radius: 7px;
                padding: 9px 12px;
            }

            QPushButton:hover {
                background: #46515f;
            }

            QPushButton#buyButton {
                background: #2f6f4e;
                font-weight: bold;
            }

            QPushButton#buyButton:hover {
                background: #3b875f;
            }

            QLabel#title {
                font-size: 22px;
                font-weight: bold;
            }

            QLabel#money {
                font-size: 18px;
                font-weight: bold;
            }

            QLabel#section {
                font-size: 15px;
                font-weight: bold;
            }

            QLabel#stat {
                font-size: 14px;
            }
        """)

        root = QVBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        # ==========================
        # TOP BAR
        # ==========================
        topbar = QFrame()
        topbar.setObjectName("topbar")

        top_layout = QHBoxLayout(topbar)
        top_layout.setContentsMargins(15, 10, 15, 10)

        title = QLabel("🔧 CAR CUSTOMIZER GARAGE")
        title.setObjectName("title")

        vehicle_name = QLabel(
            f"{self.current_vehicle['nickname']}  •  "
            f"{self.current_vehicle['manufacturer_name']} "
            f"{self.current_vehicle['model_name']}"
        )

        self.money_label = QLabel("Money: ₹0.00")
        self.money_label.setObjectName("money")

        top_layout.addWidget(title)
        top_layout.addStretch()
        top_layout.addWidget(vehicle_name)
        top_layout.addSpacing(30)
        top_layout.addWidget(self.money_label)

        root.addWidget(topbar)

        # ==========================
        # THREE MAIN COLUMNS
        # ==========================
        main = QHBoxLayout()
        main.setSpacing(10)

        # LEFT: CATEGORIES
        left_panel = QFrame()
        left_panel.setObjectName("panel")

        left_layout = QVBoxLayout(left_panel)

        category_title = QLabel("CATEGORIES")
        category_title.setObjectName("section")

        left_layout.addWidget(category_title)

        self.category_list = QListWidget()

        for category in self.categories:
            item = QListWidgetItem(
                category["category_name"]
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                category["category_id"]
            )

            self.category_list.addItem(item)

        self.category_list.currentItemChanged.connect(
            self.category_changed
        )

        left_layout.addWidget(self.category_list)

        main.addWidget(left_panel, 1)

        # CENTER: CAR PREVIEW
        center_panel = QFrame()
        center_panel.setObjectName("panel")

        center_layout = QVBoxLayout(center_panel)

        preview_title = QLabel("LIVE PREVIEW")
        preview_title.setObjectName("section")
        preview_title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        center_layout.addWidget(preview_title)

        self.preview = CarPreviewWidget()
        center_layout.addWidget(self.preview, 1)

        self.preview_info = QLabel(
            "Select a part to preview it on the car."
        )
        self.preview_info.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        center_layout.addWidget(self.preview_info)

        main.addWidget(center_panel, 4)

        # RIGHT: PARTS
        right_panel = QFrame()
        right_panel.setObjectName("panel")

        right_layout = QVBoxLayout(right_panel)

        parts_title = QLabel("PARTS SHOP")
        parts_title.setObjectName("section")

        right_layout.addWidget(parts_title)

        self.part_list = QListWidget()

        self.part_list.currentItemChanged.connect(
            self.part_selected
        )

        right_layout.addWidget(
            self.part_list,
            1
        )

        self.part_details = QLabel(
            "Select a part."
        )

        self.part_details.setWordWrap(True)

        right_layout.addWidget(
            self.part_details
        )

        self.buy_button = QPushButton(
            "BUY / INSTALL"
        )

        self.buy_button.setObjectName(
            "buyButton"
        )

        self.buy_button.clicked.connect(
            self.install_selected_part
        )

        right_layout.addWidget(
            self.buy_button
        )

        main.addWidget(
            right_panel,
            2
        )

        root.addLayout(main, 1)

        # ==========================
        # STATS BAR
        # ==========================
        stats_panel = QFrame()
        stats_panel.setObjectName("panel")

        stats_layout = QHBoxLayout(stats_panel)

        self.hp_label = QLabel()
        self.weight_label = QLabel()
        self.speed_label = QLabel()
        self.accel_label = QLabel()

        for label in [
            self.hp_label,
            self.weight_label,
            self.speed_label,
            self.accel_label
        ]:
            label.setObjectName("stat")
            stats_layout.addWidget(label)

        root.addWidget(stats_panel)

        # Start with first category.
        if self.category_list.count() > 0:
            self.category_list.setCurrentRow(0)

    # --------------------------------------------------------
    # CATEGORY SELECTION
    # --------------------------------------------------------
    def category_changed(self, current, previous):
        if not current:
            return

        category_id = current.data(
            Qt.ItemDataRole.UserRole
        )

        self.part_list.clear()
        self.selected_part = None
        self.part_details.setText(
            "Select a part."
        )

        for part in self.parts:
            if part["category_id"] == category_id:
                item = QListWidgetItem(
                    f"{part['part_name']}  —  "
                    f"₹{float(part['price']):,.2f}"
                )

                item.setData(
                    Qt.ItemDataRole.UserRole,
                    part["part_id"]
                )

                self.part_list.addItem(item)

    # --------------------------------------------------------
    # PART SELECTION
    # --------------------------------------------------------
    def find_part(self, part_id):
        for part in self.parts:
            if part["part_id"] == part_id:
                return part

        return None

    def part_selected(self, current, previous):
        if not current:
            self.selected_part = None
            return

        part_id = current.data(
            Qt.ItemDataRole.UserRole
        )

        part = self.find_part(part_id)

        if not part:
            return

        self.selected_part = part

        quantity = self.get_inventory_quantity(
            part_id
        )

        self.part_details.setText(
            f"<b>{part['part_name']}</b><br>"
            f"Category: {part['category_name']}<br>"
            f"Price: ₹{float(part['price']):,.2f}<br>"
            f"HP bonus: {int(part['hp_bonus'] or 0):+d}<br>"
            f"Weight change: {int(part['weight_change'] or 0):+d}<br>"
            f"Top speed: {int(part['top_speed_bonus'] or 0):+d}<br>"
            f"Acceleration: "
            f"{float(part['acceleration_bonus'] or 0):+.2f}<br>"
            f"Owned: {quantity}"
        )

        # ====================================================
        # THIS IS THE LIVE PREVIEW
        # It does NOT change MySQL.
        # ====================================================
        self.preview.set_part(
            part["category_name"],
            part["sprite_file"]
        )

        self.preview_info.setText(
            f"Previewing: {part['part_name']} "
            f"(not installed yet)"
        )

    # --------------------------------------------------------
    # STATS
    # --------------------------------------------------------
    def refresh_stats(self):
        hp = int(
            self.current_vehicle["base_hp"] or 0
        )

        weight = int(
            self.current_vehicle["base_weight"] or 0
        )

        speed = int(
            self.current_vehicle["base_top_speed"] or 0
        )

        accel = float(
            self.current_vehicle["base_acceleration"] or 0
        )

        for part in self.installed_parts.values():
            hp += int(
                part.get("hp_bonus", 0) or 0
            )

            weight += int(
                part.get("weight_change", 0) or 0
            )

            speed += int(
                part.get("top_speed_bonus", 0) or 0
            )

            accel += float(
                part.get("acceleration_bonus", 0) or 0
            )

        self.hp_label.setText(
            f"HP: {hp}"
        )

        self.weight_label.setText(
            f"Weight: {weight} kg"
        )

        self.speed_label.setText(
            f"Top Speed: {speed} km/h"
        )

        self.accel_label.setText(
            f"Acceleration: {accel:.2f} s"
        )

    # --------------------------------------------------------
    # BUY / INSTALL
    # --------------------------------------------------------
    def install_selected_part(self):
        if not self.selected_part:
            QMessageBox.warning(
                self,
                "No Part Selected",
                "Select a part first."
            )
            return

        self.install_part(
            self.selected_part
        )

    def install_part(self, part):
        vehicle_id = self.current_vehicle[
            "vehicle_id"
        ]

        part_id = part["part_id"]
        category_id = part["category_id"]
        category_name = part["category_name"]
        price = float(part["price"])

        try:
            self.db.conn.start_transaction()

            # Check whether player already owns it.
            inventory = self.db.fetchone(
                """
                SELECT inventory_id, quantity
                FROM player_inventory
                WHERE user_id = %s
                  AND part_id = %s
                FOR UPDATE
                """,
                (
                    CURRENT_USER_ID,
                    part_id
                )
            )

            if (
                inventory
                and int(inventory["quantity"]) > 0
            ):
                # Already owned -> install for free.
                self.set_vehicle_part(
                    vehicle_id,
                    category_id,
                    part_id
                )

                self.db.commit()

                self.installed_parts[
                    category_id
                ] = part

                self.preview.set_part(
                    category_name,
                    part["sprite_file"]
                )

                self.refresh_stats()

                QMessageBox.information(
                    self,
                    "Installed",
                    f"{part['part_name']} "
                    "is now installed."
                )

                return

            # Check user's money.
            user = self.db.fetchone(
                """
                SELECT money
                FROM users
                WHERE user_id = %s
                FOR UPDATE
                """,
                (CURRENT_USER_ID,)
            )

            if not user:
                raise RuntimeError(
                    "Current user was not found."
                )

            money = float(
                user["money"]
            )

            if money < price:
                self.db.rollback()

                QMessageBox.warning(
                    self,
                    "Not Enough Money",
                    f"You need "
                    f"₹{price:,.2f}, but only have "
                    f"₹{money:,.2f}."
                )

                return

            # Check shop stock for paid parts.
            if price > 0:
                stock = self.db.fetchone(
                    """
                    SELECT inventory_id, stock
                    FROM shop_inventory
                    WHERE part_id = %s
                    FOR UPDATE
                    """,
                    (part_id,)
                )

                if (
                    not stock
                    or int(stock["stock"]) <= 0
                ):
                    self.db.rollback()

                    QMessageBox.warning(
                        self,
                        "Out of Stock",
                        f"{part['part_name']} "
                        "is currently out of stock."
                    )

                    return

                self.db.execute(
                    """
                    UPDATE shop_inventory
                    SET stock = stock - 1
                    WHERE inventory_id = %s
                    """,
                    (stock["inventory_id"],)
                )

            # Deduct money.
            self.db.execute(
                """
                UPDATE users
                SET money = money - %s
                WHERE user_id = %s
                """,
                (
                    price,
                    CURRENT_USER_ID
                )
            )

            # Add to player inventory.
            if inventory:
                self.db.execute(
                    """
                    UPDATE player_inventory
                    SET quantity = quantity + 1
                    WHERE inventory_id = %s
                    """,
                    (inventory["inventory_id"],)
                )
            else:
                self.db.execute(
                    """
                    INSERT INTO player_inventory
                    (user_id, part_id, quantity)
                    VALUES (%s, %s, 1)
                    """,
                    (
                        CURRENT_USER_ID,
                        part_id
                    )
                )

            # Purchase history.
            self.db.execute(
                """
                INSERT INTO purchases
                (user_id, part_id, quantity, total_price)
                VALUES (%s, %s, 1, %s)
                """,
                (
                    CURRENT_USER_ID,
                    part_id,
                    price
                )
            )

            # Install the part on the vehicle.
            self.set_vehicle_part(
                vehicle_id,
                category_id,
                part_id
            )

            self.db.commit()

            # Update live application state.
            self.installed_parts[
                category_id
            ] = part

            self.preview.set_part(
                category_name,
                part["sprite_file"]
            )

            self.refresh_stats()
            self.update_money()

            QMessageBox.information(
                self,
                "Success",
                f"{part['part_name']} "
                "was purchased and installed."
            )

            # Refresh "Owned" number.
            self.part_selected(
                self.part_list.currentItem(),
                None
            )

        except Exception as exc:
            self.db.rollback()

            QMessageBox.critical(
                self,
                "Database Error",
                str(exc)
            )

    # --------------------------------------------------------
    # VEHICLE PART DATABASE UPDATE
    # --------------------------------------------------------
    def set_vehicle_part(
        self,
        vehicle_id,
        category_id,
        part_id
    ):
        existing = self.db.fetchone(
            """
            SELECT vehicle_id
            FROM vehicle_parts
            WHERE vehicle_id = %s
              AND category_id = %s
            """,
            (
                vehicle_id,
                category_id
            )
        )

        if existing:
            self.db.execute(
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
            self.db.execute(
                """
                INSERT INTO vehicle_parts
                (vehicle_id, category_id, part_id)
                VALUES (%s, %s, %s)
                """,
                (
                    vehicle_id,
                    category_id,
                    part_id
                )
            )

    # --------------------------------------------------------
    # CLOSE
    # --------------------------------------------------------
    def closeEvent(self, event):
        self.db.close()
        event.accept()


# ============================================================
# APPLICATION START
# ============================================================
def main():
    app = QApplication(sys.argv)

    try:
        db = Database()

        window = GarageWindow(db)
        window.show()

        sys.exit(app.exec())

    except Exception as exc:
        print("Startup Error:", exc)

        QMessageBox.critical(
            None,
            "Startup Error",
            str(exc)
        )

        sys.exit(1)


if __name__ == "__main__":
    main()