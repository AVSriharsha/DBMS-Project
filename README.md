# Car Customizer

A database-driven car customization application built as a **DBMS project**. The application allows users to manage vehicles, purchase and customize car parts, maintain inventories, and interact with a role-based management system.

> **🚧 Work in Progress**
>
> This project is currently under active development. Features, UI components, database structures, and application logic may change as development continues.

---

## 📌 Overview

**Car Customizer** is a desktop application that combines a graphical user interface with a MySQL relational database to simulate a car customization and parts-management system.

Users can:

* Create and manage accounts
* Log in using role-based access
* Own and customize vehicles
* Browse available car parts
* Purchase parts from the shop
* Maintain a personal parts inventory
* Install parts on their vehicle
* View purchase history
* Manage vehicle customization

Administrators and managers have additional management capabilities for maintaining users, roles, parts, and shop inventory.

---

## ✨ Features

### 👤 User Accounts

* User login system
* User registration / sign-up
* Username and password validation
* Custom nicknames for personalized greetings
* Account activation/deactivation
* Role-based access control
* User-specific money balance

### 🚗 Vehicle Management

* Vehicle ownership associated with individual users
* Multiple supported vehicle models
* Vehicle nicknames
* Manufacturer and model information
* Base vehicle statistics including:

  * Horsepower
  * Weight
  * Top speed
  * Acceleration

Current vehicle models include:

* **Nissan Skyline GT-R R34**
* **Honda Civic EK9** (Work in Progress)
* **BMW M3 E46** (Work in Progress)

### 🛠️ Car Customization

Users can customize their vehicle using different categories of parts, including:

* Wheels
* Spoilers
* Bumpers
* Paint
* Engines

Parts can affect vehicle statistics such as:

* Horsepower
* Weight
* Top speed
* Acceleration

### 🛒 Shop & Purchasing

* Browse available parts
* View prices
* View shop stock
* Purchase parts
* Automatic money deduction
* Automatic stock management
* Purchase history tracking

### 🎒 Player Inventory

Purchased parts can be stored in the player's inventory and used for vehicle customization.

### 🧾 Purchase History

The system records:

* User
* Purchased part
* Quantity
* Total price
* Purchase date

### ⚙️ Management System

Administrative functionality includes management of:

* Shop inventory
* Parts
* Users
* Roles

Management permissions are controlled according to the user's role.

### 🔐 Role-Based Access

The application currently supports:

| Role          | Description                                 |
| ------------- | ------------------------------------------- |
| Guest         | Access to limited application functionality |
| Player        | Purchase and customize vehicles             |
| Shop Manager  | Manage shop-related inventory               |
| Administrator | Manage users, roles, and system data        |

---

## 🗄️ Database Design

The project uses **MySQL** as its relational database.

The database contains tables for major entities such as:

* `users`
* `roles`
* `vehicles`
* `car_models`
* `manufacturers`
* `categories`
* `parts`
* `shop_inventory`
* `player_inventory`
* `vehicle_parts`
* `purchases`

The database uses **primary keys and foreign keys** to maintain relationships between entities and preserve data integrity.

### Basic Relationship Structure

```text
Users
  │
  ├── Roles
  │
  ├── Vehicles
  │      │
  │      └── Vehicle Parts
  │
  ├── Player Inventory
  │      │
  │      └── Parts
  │
  └── Purchases
         │
         └── Parts

Manufacturers
      │
      └── Car Models

Categories
      │
      └── Parts
             │
             └── Shop Inventory
```

---

## 🖥️ Technology Stack

| Technology                 | Purpose                          |
| -------------------------- | -------------------------------- |
| **Python**                 | Application logic                |
| **PyQt5**                  | Desktop graphical user interface |
| **MySQL**                  | Relational database              |
| **mysql-connector-python** | Python–MySQL connectivity        |
| **SQL**                    | Database design and queries      |

---

## 📁 Project Structure

A typical project structure is:

```text
dbms_prj/
│
├── main.py
├── database.sql
├── README.md
│
├── assets/
│   └── ...
│
└── ...
```

The exact structure may change during development.

---

## ⚙️ Installation

WORK IN PROGRESS

### 5. Run the application

```bash
python main.py
```

---

## 👥 Default Accounts

The project includes default accounts for testing the different roles.

| Username  | Role          |
| --------- | ------------- |
| `admin`   | Administrator |
| `manager` | Shop Manager  |
| `player`  | Player        |

The exact credentials should be kept consistent with the values defined in `database.sql`.

New users can also register through the application's sign-up system.

---

## 🔄 Application Flow

A typical player workflow is:

```text
Sign Up / Login
       ↓
   Garage
       ↓
 Select Vehicle
       ↓
 Browse Parts
       ↓
 Purchase Parts
       ↓
 Player Inventory
       ↓
 Install Parts
       ↓
 Customize Vehicle
       ↓
 View Purchase History
```

Administrative workflow:

```text
Admin Login
     ↓
Management
     ├── Shop Inventory
     ├── Parts
     ├── Users
     └── Roles
```

---

## 🧠 DBMS Concepts Demonstrated

This project is designed to demonstrate practical database-management concepts, including:

* Relational database design
* Entity relationships
* Primary keys
* Foreign keys
* Referential integrity
* One-to-many relationships
* Many-to-many relationships through junction tables
* SQL `SELECT`, `INSERT`, `UPDATE`, and `DELETE`
* Transactions
* Inventory management
* Role-based access control
* Database-driven application development
* Data validation
* Soft deletion / account deactivation
* Application-to-database integration

---

## 🚧 Current Development Status

This project is **not yet complete**.

Current development focuses on improving:

* User account management
* Vehicle customization
* Inventory and installation logic
* Administrative controls
* Database consistency
* UI/UX
* Validation and error handling
* Overall application stability

Some functionality may still be modified, redesigned, or expanded.

---

## 🗺️ Future Plans

Potential future improvements include:

* Improved vehicle visualization
* More vehicle models
* More customization categories
* More parts and manufacturers
* Enhanced inventory management
* Improved admin controls
* Better password security and password hashing
* Improved transaction handling
* More detailed vehicle performance calculations
* Improved UI animations and visual feedback
* Expanded reporting and database queries
* Additional user roles and permissions

---

## 🔒 Security Note

This is an **academic DBMS project** and should not be considered production-ready software.

In particular, authentication and credential handling are currently intended for demonstration purposes. A production implementation should use secure password hashing, environment-based configuration, stronger authentication mechanisms, and additional security controls.

---

## 📄 License

This project is currently intended for **educational and academic purposes**.

A formal open-source license may be added in a future version.

---

## 📌 Project Status

**Status:** 🚧 Work in Progress

**Project Type:** DBMS / Database Application

**Primary Database:** MySQL

**Application:** Python + PyQt5

**Current Focus:** Building and refining the complete car customization, purchasing, inventory, and management system.
