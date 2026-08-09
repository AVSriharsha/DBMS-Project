from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QComboBox,
    QVBoxLayout,
    QHBoxLayout
)

from PyQt6.QtGui import QPixmap

from database import get_connection

from renderer import create_car_preview


class GarageWindow(QWidget):

    def __init__(self, user):

        super().__init__()

        self.user = user

        self.setWindowTitle(
            "Car Customizer - Garage"
        )

        self.resize(1000, 700)

        self.layout = QVBoxLayout()

        # -------------------------
        # USER INFO
        # -------------------------

        self.user_label = QLabel(
            f"Player: {user['username']} | "
            f"Role: {user['role_name']} | "
            f"Money: ${user['money']}"
        )

        self.layout.addWidget(
            self.user_label
        )

        # -------------------------
        # CAR PREVIEW
        # -------------------------

        self.preview = QLabel()

        self.preview.setFixedSize(
            800,
            400
        )

        self.layout.addWidget(
            self.preview
        )

        # -------------------------
        # CUSTOMIZATION
        # -------------------------

        self.categories = {}

        categories = [
            "Wheels",
            "Spoiler",
            "Bumper",
            "Paint",
            "Engine"
        ]

        for category in categories:

            row = QHBoxLayout()

            label = QLabel(category)

            combo = QComboBox()

            combo.currentIndexChanged.connect(
                lambda index,
                category=category:
                self.part_changed(category)
            )

            row.addWidget(label)
            row.addWidget(combo)

            self.layout.addLayout(row)

            self.categories[category] = combo

        self.setLayout(self.layout)

        self.load_parts()

        self.refresh_preview()


    def load_parts(self):

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        query = """

        SELECT
            parts.part_id,
            parts.part_name,
            categories.category_name

        FROM parts

        JOIN categories
        ON parts.category_id =
           categories.category_id

        ORDER BY categories.category_name

        """

        cursor.execute(query)

        parts = cursor.fetchall()

        cursor.close()
        connection.close()

        for part in parts:

            category = part[
                "category_name"
            ]

            if category in self.categories:

                self.categories[
                    category
                ].addItem(
                    part["part_name"],
                    part["part_id"]
                )


    def part_changed(self, category):

        combo = self.categories[
            category
        ]

        part_id = combo.currentData()

        if not part_id:
            return

        connection = get_connection()

        cursor = connection.cursor()

        category_query = """

        SELECT category_id

        FROM categories

        WHERE category_name = %s

        """

        cursor.execute(
            category_query,
            (category,)
        )

        category_id = cursor.fetchone()[0]

        query = """

        INSERT INTO vehicle_parts
        (vehicle_id, category_id, part_id)

        VALUES (1, %s, %s)

        ON DUPLICATE KEY UPDATE
        part_id = VALUES(part_id)

        """

        cursor.execute(
            query,
            (
                category_id,
                part_id
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        self.refresh_preview()


    def refresh_preview(self):

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        query = """

        SELECT
            parts.part_name,
            parts.sprite_file,
            categories.category_name,
            parts.layer_order

        FROM vehicle_parts

        JOIN parts
        ON vehicle_parts.part_id =
           parts.part_id

        JOIN categories
        ON vehicle_parts.category_id =
           categories.category_id

        WHERE vehicle_parts.vehicle_id = 1

        ORDER BY parts.layer_order

        """

        cursor.execute(query)

        parts = cursor.fetchall()

        cursor.close()
        connection.close()

        image = create_car_preview(
            parts
        )

        image.save(
            "current_car.png"
        )

        pixmap = QPixmap(
            "current_car.png"
        )

        self.preview.setPixmap(
            pixmap
        )