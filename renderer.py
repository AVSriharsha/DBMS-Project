from PIL import Image, ImageDraw


def create_car_preview(parts):

    width = 800
    height = 400

    image = Image.new(
        "RGBA",
        (width, height),
        (240, 240, 240, 255)
    )

    draw = ImageDraw.Draw(image)

    # -------------------------
    # PLACEHOLDER CAR BODY
    # -------------------------

    draw.rounded_rectangle(
        (100, 140, 700, 300),
        radius=40,
        fill=(80, 80, 80),
        outline=(20, 20, 20),
        width=5
    )

    # Roof

    draw.polygon(
        [
            (230, 140),
            (300, 70),
            (500, 70),
            (570, 140)
        ],
        fill=(90, 90, 90),
        outline=(20, 20, 20)
    )

    # Windows

    draw.polygon(
        [
            (310, 85),
            (355, 85),
            (355, 135),
            (265, 135)
        ],
        fill=(40, 60, 80)
    )

    draw.polygon(
        [
            (365, 85),
            (490, 85),
            (535, 135),
            (365, 135)
        ],
        fill=(40, 60, 80)
    )

    # -------------------------
    # WHEELS
    # -------------------------

    draw.ellipse(
        (150, 255, 250, 355),
        fill=(20, 20, 20)
    )

    draw.ellipse(
        (550, 255, 650, 355),
        fill=(20, 20, 20)
    )

    # Wheel centers

    draw.ellipse(
        (180, 285, 220, 325),
        fill=(150, 150, 150)
    )

    draw.ellipse(
        (580, 285, 620, 325),
        fill=(150, 150, 150)
    )

    # -------------------------
    # PART VISUALIZATION
    # -------------------------

    for part in parts:

        category = part["category_name"]

        if category == "Spoiler":

            draw.rectangle(
                (580, 100, 680, 115),
                fill=(20, 20, 20)
            )

            draw.line(
                (600, 115, 600, 140),
                fill=(20, 20, 20),
                width=6
            )

            draw.line(
                (660, 115, 660, 140),
                fill=(20, 20, 20),
                width=6
            )

        elif category == "Bumper":

            draw.rectangle(
                (80, 190, 120, 250),
                fill=(30, 30, 30)
            )

        elif category == "Paint":

            color = part["part_name"]

            if color == "Red Paint":
                body_color = (200, 40, 40)

            elif color == "Blue Paint":
                body_color = (40, 80, 200)

            else:
                body_color = (80, 80, 80)

            draw.rounded_rectangle(
                (105, 145, 695, 250),
                radius=30,
                fill=body_color
            )

        elif category == "Engine":

            if part["part_name"] == "Turbo Engine":

                draw.ellipse(
                    (330, 165, 400, 235),
                    fill=(180, 180, 180),
                    outline=(20, 20, 20),
                    width=4
                )

    return image