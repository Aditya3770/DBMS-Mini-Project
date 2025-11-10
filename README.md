# 🏪 Quick Commerce Inventory & Driver Management System

**A complete database-driven management application for a quick commerce service, built as part of the PES University DBMS Mini Project.**

This project provides an end-to-end management system for handling **inventory**, **drivers**, and **customer orders** using a desktop GUI made with Python (Tkinter) and a robust **MySQL** backend.  
It emphasizes **data integrity**, **transaction safety**, and **database-side business logic** through **stored procedures** and **triggers**.

---

## 👨‍💻 Team Details

| Name | Register Number |
|------|------------------|
| **Aditya Venkatesh** | PES1UG23AM024 |
| **Adarsh R Menon** | PES1UG23AM016 |

---

## ⚙️ Features Overview

The application is divided into **four primary tabs**, corresponding to key user roles and functions:

### 🛒 1. Customer App
- **Place Orders:** Simple interface for selecting products and placing new orders.  
- **Real-Time Stock:** Only displays products that are in stock, fetched dynamically from the database.  
- **Cart Functionality:** Add/remove items before confirming the final order.  
- **Order Validation:** Stored procedure validates stock availability before order confirmation.  

### 🏭 2. Warehouse Manager
- **Manage Products:** CRUD operations for maintaining the master product catalog.  
- **Manage Inventory:** Add or update stock quantities for existing products.  

### 🚚 3. Fleet Manager
- **Manage Drivers:** CRUD interface for adding drivers and updating availability (`Available`, `On-Trip`, `Unavailable`).  
- **Manage Fleet:** CRUD interface for vehicle management (`Available`, `In-Use`, `Maintenance`).  
- **Assign Driver to Vehicle:** Pairs available drivers and vehicles securely in a single transaction.  

### 🖥️ 4. System Administrator
- **Manage Customers:** CRUD operations for customer registration.  
- **Generate Sales Reports:** View sales between specific date ranges using efficient SQL joins.  

---

## 🧰 Technologies Used

| Layer | Technology |
|--------|-------------|
| **Frontend (GUI)** | Python 3, Tkinter |
| **Backend Database** | MySQL |
| **Database Connector** | `mysql-connector-python` |
| **Database Logic** | Stored Procedures, Triggers, Transactions |

---

## 🚀 How to Run This Project

### 🧩 Prerequisites

- **MySQL Server & Workbench** (ensure the server is running)
- **Python 3** (latest version recommended)

---

### 🗄️ Step 1: Set Up the Database

1. Open **MySQL Workbench** and connect to your local server.  
2. Open the file: **`QuickCommerceDB_CompleteSetup.sql`**  
3. Execute the script — this will:
   - Create the database **`QuickCommerceDB`**
   - Create all required tables (`PRODUCT`, `INVENTORY`, `DRIVER`, `ORDER`, etc.)
   - Insert the **Main Warehouse (ID = 1)**
   - Define all stored procedures and triggers  

---

### 🐍 Step 2: Set Up the Python Environment

Open your terminal or command prompt, then navigate to the project directory (where `app.py` is located):

<pre>
cd path/to/project

Create and activate a virtual environment:

python -m venv venv
# On macOS/Linux
source venv/bin/activate
# On Windows
venv\Scripts\activate

Install the required library:

pip install mysql-connector-python
</pre>


### ⚙️ Step 3: Configure the Application

Open **`app.py`** and locate the `db_config` dictionary near the top (around line 14):

<pre>
```python
db_config = {
    'host': 'localhost',
    'user': 'your_username',     # e.g., 'root'
    'password': 'your_password', # your MySQL password
    'database': 'QuickCommerceDB'
}
</pre>
### ▶️ Step 4: Run the Application

With your virtual environment activated, run the app:

<pre>
python app.py
</pre>
The Tkinter application window will open.
Start by adding Products and Inventory in the Warehouse tab, then proceed to place an order in the Customer App tab.

🧠 Database Logic
This project emphasizes secure, transaction-based operations — core business logic is implemented at the database level.

🧾 Stored Procedures
Procedure	Description
PlaceNewOrder(...)	Handles the entire order placement as a single transaction. Checks stock, creates an order, updates inventory, and records payment. Rolls back on failure.
AssignDriverToVehicle(...)	Safely pairs a driver and a vehicle within one transaction.
GenerateSalesReport(...)	Efficiently joins multiple tables to produce sales reports.

🧩 Triggers
Trigger	Description
After_OrderStatusUpdate_Log	Automatically logs every order status change into the Order_History table for audit tracking.

📁 File Structure
graphql
├── app.py                            # Main Python Tkinter GUI application
├── QuickCommerceDB_CompleteSetup.sql  # Full MySQL database setup script
└── README.md                         # Project documentation
🧾 Summary
This system demonstrates the integration of database-centric design with a Tkinter desktop GUI, ensuring:

✅ Data integrity

🔒 Transaction safety

👥 Role-based functionality

⚡ Seamless user experience

It serves as a practical model for small-scale quick commerce systems that balance real-time usability with strong backend consistency.
