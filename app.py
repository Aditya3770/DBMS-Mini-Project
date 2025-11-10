import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector
import json
from datetime import date

# --- DATABASE CONNECTION ---
# IMPORTANT: Update this dictionary with your MySQL credentials!
# I have set the user to 'root' based on the image you provided.
db_config = {
    'host': 'localhost',
    'user': 'root',           # Your username is 'root'
    'password': 'Daaji123@', # ENTER YOUR PASSWORD HERE
    'database': 'QuickCommerceDB'
}

def get_db_connection():
    """Establishes a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to connect to database: {err}")
        return None

# --- HELPER FUNCTIONS ---

def clear_treeview(tree):
    """Removes all items from a Treeview."""
    for item in tree.get_children():
        tree.delete(item)

def show_error(title, message):
    messagebox.showerror(title, message)

def show_info(title, message):
    messagebox.showinfo(title, message)

def populate_combobox(combobox, query, display_col, id_col=None):
    """Populates a ComboBox from a database query."""
    conn = get_db_connection()
    if not conn:
        return
        
    combobox_data = {}
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        
        display_values = []
        for row in rows:
            display_text = row[cursor.column_names.index(display_col)]
            key = row[cursor.column_names.index(id_col or display_col)]
            
            # Format display text (e.g., "John Doe (ID: 1)")
            formatted_text = f"{display_text} (ID: {key})"
            display_values.append(formatted_text)
            combobox_data[formatted_text] = key
            
        combobox['values'] = display_values
        return combobox_data
    except mysql.connector.Error as err:
        show_error("Database Error", f"Failed to load data: {err}")
    finally:
        if conn:
            conn.close()
    return combobox_data

# --- MAIN APPLICATION ---

class QuickCommerceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quick Commerce Management System")
        self.geometry("1200x800")

        # --- Create Main Tab Control ---
        self.notebook = ttk.Notebook(self)

        # --- Create Tab Frames ---
        self.tab_customer = ttk.Frame(self.notebook, padding=10)
        self.tab_warehouse = ttk.Frame(self.notebook, padding=10)
        self.tab_fleet = ttk.Frame(self.notebook, padding=10)
        self.tab_admin = ttk.Frame(self.notebook, padding=10)

        # --- Add Tabs to Notebook ---
        self.notebook.add(self.tab_customer, text="Customer App")
        self.notebook.add(self.tab_warehouse, text="Warehouse Manager")
        self.notebook.add(self.tab_fleet, text="Fleet Manager")
        self.notebook.add(self.tab_admin, text="System Administrator")

        self.notebook.pack(expand=True, fill="both")

        # --- Populate Each Tab ---
        self.create_customer_tab()
        self.create_warehouse_tab()
        self.create_fleet_tab()
        self.create_admin_tab()
        
        # --- Variables to store selected items for update ---
        self.selected_driver_id = None
        self.selected_vehicle_id = None

        # --- Initial Data Load ---
        # Load all data on startup
        self.refresh_all_tabs()

    def refresh_all_tabs(self):
        """Calls the refresh method for every tab in the application."""
        self.refresh_customer_tab_data()
        self.refresh_warehouse_tab_data()
        self.refresh_fleet_tab_data()
        self.refresh_admin_tab_data()
        
    # --- TAB 1: CUSTOMER APP ---
    def create_customer_tab(self):
        # --- Data Storage ---
        self.customer_data = {}
        # self.warehouse_data = {} # Removed for simplicity
        self.cart_items = {}  # {product_id: {name, price, quantity}}

        # --- Main Frames ---
        top_frame = ttk.Frame(self.tab_customer)
        top_frame.pack(fill="x", pady=5)
        
        main_paned_window = ttk.PanedWindow(self.tab_customer, orient=tk.HORIZONTAL)
        main_paned_window.pack(fill="both", expand=True)
        
        shop_frame = ttk.Frame(main_paned_window, padding=10)
        cart_frame = ttk.Frame(main_paned_window, padding=10)
        
        main_paned_window.add(shop_frame)
        main_paned_window.add(cart_frame)

        # --- Top Frame: User Selection (Warehouse Removed) ---
        ttk.Label(top_frame, text="Select Customer:").pack(side=tk.LEFT, padx=5)
        self.customer_combo = ttk.Combobox(top_frame, state="readonly", width=30)
        self.customer_combo.pack(side=tk.LEFT, padx=5)

        # --- !! WAREHOUSE SELECTION REMOVED !! ---
        # ttk.Label(top_frame, text="Select Warehouse:").pack(side=tk.LEFT, padx=5)
        # self.warehouse_combo = ttk.Combobox(top_frame, state="readonly", width=30)
        # self.warehouse_combo.pack(side=tk.LEFT, padx=5)
        # self.warehouse_combo.bind("<<ComboboxSelected>>", self.load_available_products)

        # --- !! NEW REFRESH BUTTON !! ---
        ttk.Button(top_frame, text="Refresh Data", command=self.refresh_customer_tab_data).pack(side=tk.RIGHT, padx=10)


        # --- Shop Frame: Available Products ---
        ttk.Label(shop_frame, text="Available Products (From Main Warehouse)", font=("Arial", 14, "bold")).pack(pady=5)
        
        cols = ("Product_ID", "Name", "Price", "Stock")
        self.shop_tree = ttk.Treeview(shop_frame, columns=cols, show="headings", height=20)
        for col in cols:
            self.shop_tree.heading(col, text=col)
            self.shop_tree.column(col, width=100)
        self.shop_tree.pack(fill="both", expand=True)

        ttk.Button(shop_frame, text="Add to Cart", command=self.add_to_cart).pack(pady=10)

        # --- Cart Frame: Your Cart ---
        ttk.Label(cart_frame, text="Your Cart", font=("Arial", 14, "bold")).pack(pady=5)
        
        cart_cols = ("Product_ID", "Name", "Quantity", "Price")
        self.cart_tree = ttk.Treeview(cart_frame, columns=cart_cols, show="headings", height=20)
        for col in cart_cols:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=80)
        self.cart_tree.pack(fill="both", expand=True)

        btn_frame = ttk.Frame(cart_frame)
        btn_frame.pack(fill="x", pady=10)
        ttk.Button(btn_frame, text="Place Order", command=self.place_order).pack(side=tk.LEFT, fill="x", expand=True, padx=5)
        ttk.Button(btn_frame, text="Clear Cart", command=self.clear_cart).pack(side=tk.LEFT, fill="x", expand=True, padx=5)
        

    def refresh_customer_tab_data(self):
        """Refreshes all dynamic data on the Customer tab."""
        # Refresh comboboxes
        self.customer_data = populate_combobox(self.customer_combo, "SELECT * FROM CUSTOMER", "C_Name", "Customer_ID")
        # self.warehouse_data = populate_combobox(self.warehouse_combo, "SELECT * FROM WAREHOUSE", "Location", "Warehouse_ID") # Removed
        
        # Clear selections and product list
        self.customer_combo.set('')
        # self.warehouse_combo.set('') # Removed
        clear_treeview(self.shop_tree)
        self.clear_cart()
        
        # --- !! AUTO-LOAD PRODUCTS FROM WAREHOUSE 1 !! ---
        self.load_available_products()
        print("Customer Tab Refreshed") # For debugging

    def load_available_products(self):
        """Loads products into the shop view from the default warehouse (ID 1)."""
        clear_treeview(self.shop_tree)
        
        # --- !! HARDCODED WAREHOUSE ID = 1 !! ---
        warehouse_id = 1 

        conn = get_db_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT p.Product_ID, p.P_Name, p.Price, i.Quantity 
                FROM PRODUCT p
                JOIN Inventory i ON p.Product_ID = i.Product_ID
                WHERE i.Warehouse_ID = %s AND i.Quantity > 0
            """
            cursor.execute(query, (warehouse_id,))
            for row in cursor.fetchall():
                self.shop_tree.insert("", tk.END, values=(row['Product_ID'], row['P_Name'], f"{row['Price']:.2f}", row['Quantity']))
        except mysql.connector.Error as err:
            show_error("Database Error", f"Failed to load products: {err}")
        finally:
            conn.close()

    def add_to_cart(self):
        selected_item = self.shop_tree.focus()
        if not selected_item:
            show_error("Select Error", "Please select a product from the list.")
            return

        item = self.shop_tree.item(selected_item)
        product_id, name, price, stock = item['values']
        
        quantity = simpledialog.askinteger("Quantity", f"Enter quantity for {name}:", minvalue=1, maxvalue=stock)
        
        if quantity:
            if product_id in self.cart_items:
                # Check stock against combined quantity
                new_qty = self.cart_items[product_id]['quantity'] + quantity
                if new_qty > stock:
                    show_error("Stock Error", f"Not enough stock. You have {self.cart_items[product_id]['quantity']} in cart, and only {stock} available.")
                    return
                self.cart_items[product_id]['quantity'] = new_qty
            else:
                self.cart_items[product_id] = {'name': name, 'price': float(price), 'quantity': quantity}
            
            self.refresh_cart_tree()

    def refresh_cart_tree(self):
        clear_treeview(self.cart_tree)
        for pid, item in self.cart_items.items():
            self.cart_tree.insert("", tk.END, values=(pid, item['name'], item['quantity'], f"{item['price']:.2f}"))

    def clear_cart(self):
        self.cart_items = {}
        self.refresh_cart_tree()

    def place_order(self):
        # --- Constraint Checks ---
        if not self.cart_items:
            show_error("Order Error", "Your cart is empty.")
            return

        customer_text = self.customer_combo.get()
        if not customer_text:
            show_error("Order Error", "Please select a customer.")
            return
            
        # --- !! WAREHOUSE ID IS NOW HARDCODED !! ---
        customer_id = self.customer_data.get(customer_text)
        warehouse_id = 1 # Default warehouse
        
        # Format cart for JSON
        cart_json_list = []
        for pid, item in self.cart_items.items():
            cart_json_list.append({"product_id": pid, "quantity": item['quantity']})
        
        cart_json_string = json.dumps(cart_json_list)

        conn = get_db_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            # Call the new stored procedure
            cursor.callproc('PlaceNewOrder', (customer_id, warehouse_id, cart_json_string))
            conn.commit()
            
            show_info("Success", "Order placed successfully!")
            self.clear_cart()
            self.load_available_products() # Refresh stock
            
            # --- !! AUTO-REFRESH OTHER TABS !! ---
            self.refresh_warehouse_tab_data() # Update inventory counts visible on WH tab
            
        except mysql.connector.Error as err:
            conn.rollback()
            # This will show our custom error message from the procedure!
            show_error("Order Failed", f"{err}")
        finally:
            conn.close()

    # --- TAB 2: WAREHOUSE MANAGER ---
    def create_warehouse_tab(self):
        # --- !! NEW REFRESH BUTTON !! ---
        refresh_btn = ttk.Button(self.tab_warehouse, text="Refresh All Data", command=self.refresh_warehouse_tab_data)
        refresh_btn.pack(anchor="ne", padx=10, pady=5)

        # Tab-level notebook
        wh_notebook = ttk.Notebook(self.tab_warehouse)
        wh_notebook.pack(fill="both", expand=True)

        product_tab = ttk.Frame(wh_notebook, padding=10)
        inventory_tab = ttk.Frame(wh_notebook, padding=10)
        
        wh_notebook.add(product_tab, text="Manage Products")
        wh_notebook.add(inventory_tab, text="Manage Inventory")

        # --- Product Tab Content ---
        self.create_product_crud_ui(product_tab)

        # --- Inventory Tab Content ---
        self.create_inventory_crud_ui(inventory_tab)

    def refresh_warehouse_tab_data(self):
        """Refreshes all dynamic data on the Warehouse tab."""
        self.refresh_product_tree()
        self.refresh_inventory_tree()
        # Refresh comboboxes in the "Manage Inventory" sub-tab
        self.inv_product_data = populate_combobox(self.inv_product_combo, "SELECT * FROM PRODUCT", "P_Name", "Product_ID")
        # --- !! REMOVED WAREHOUSE COMBO REFRESH !! ---
        # self.inv_warehouse_data = populate_combobox(self.inv_warehouse_combo, "SELECT * FROM WAREHOUSE", "Location", "Warehouse_ID")
        self.inv_product_combo.set('')
        # self.inv_warehouse_combo.set('')
        print("Warehouse Tab Refreshed") # For debugging

    def create_product_crud_ui(self, parent_frame):
        # Form
        form = ttk.Frame(parent_frame, padding=10, relief=tk.GROOVE)
        form.pack(fill="x")
        
        ttk.Label(form, text="Product Name:").grid(row=0, column=0, sticky="w")
        self.p_name_entry = ttk.Entry(form, width=40)
        self.p_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form, text="Price:").grid(row=0, column=2, sticky="w")
        self.p_price_entry = ttk.Entry(form, width=20)
        self.p_price_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="Description:").grid(row=1, column=0, sticky="w")
        self.p_desc_entry = ttk.Entry(form, width=40)
        self.p_desc_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form, text="Expiry (YYYY-MM-DD):").grid(row=1, column=2, sticky="w")
        self.p_expiry_entry = ttk.Entry(form, width=20)
        self.p_expiry_entry.grid(row=1, column=3, padx=5, pady=5)

        btn = ttk.Button(form, text="Add New Product", command=self.add_product)
        btn.grid(row=2, column=0, columnspan=4, pady=10)

        # Treeview
        cols = ("Product_ID", "P_Name", "Description", "Price", "Expiry_Date")
        self.product_tree = ttk.Treeview(parent_frame, columns=cols, show="headings")
        for col in cols:
            self.product_tree.heading(col, text=col)
        self.product_tree.pack(fill="both", expand=True, pady=10)
        
        # Data loaded by refresh_warehouse_tab_data()
        # self.refresh_product_tree()

    def add_product(self):
        name = self.p_name_entry.get()
        desc = self.p_desc_entry.get()
        price = self.p_price_entry.get()
        expiry = self.p_expiry_entry.get() or None

        if not name or not price:
            show_error("Input Error", "Product Name and Price are required.")
            return

        conn = get_db_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            query = "INSERT INTO PRODUCT (P_Name, Description, Price, Expiry_Date) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (name, desc, float(price), expiry))
            conn.commit()
            show_info("Success", "Product added.")
            # Clear entries
            self.p_name_entry.delete(0, tk.END)
            self.p_desc_entry.delete(0, tk.END)
            self.p_price_entry.delete(0, tk.END)
            self.p_expiry_entry.delete(0, tk.END)
            
            # --- !! AUTO-REFRESH OTHER TABS !! ---
            self.refresh_warehouse_tab_data() # Refresh this tab's dropdowns
            self.refresh_customer_tab_data() # Refresh customer shop
        except mysql.connector.Error as err:
            conn.rollback()
            show_error("Database Error", f"Failed to add product: {err}")
        finally:
            conn.close()

    def refresh_product_tree(self):
        clear_treeview(self.product_tree)
        conn = get_db_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM PRODUCT")
            for row in cursor.fetchall():
                self.product_tree.insert("", tk.END, values=row)
        except mysql.connector.Error as err:
            show_error("Database Error", f"Failed to fetch products: {err}")
        finally:
            conn.close()

    def create_inventory_crud_ui(self, parent_frame):
        # Form
        form = ttk.Frame(parent_frame, padding=10, relief=tk.GROOVE)
        form.pack(fill="x")

        ttk.Label(form, text="Select Product:").grid(row=0, column=0, sticky="w")
        self.inv_product_combo = ttk.Combobox(form, state="readonly", width=30)
        self.inv_product_data = populate_combobox(self.inv_product_combo, "SELECT * FROM PRODUCT", "P_Name", "Product_ID")
        self.inv_product_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # --- !! WAREHOUSE SELECTION REMOVED !! ---
        # ttk.Label(form, text="Select Warehouse:").grid(row=1, column=0, sticky="w")
        # self.inv_warehouse_combo = ttk.Combobox(form, state="readonly", width=30)
        # self.inv_warehouse_data = populate_combobox(self.inv_warehouse_combo, "SELECT * FROM WAREHOUSE", "Location", "Warehouse_ID")
        # self.inv_warehouse_combo.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form, text="Quantity:").grid(row=0, column=2, sticky="w")
        self.inv_qty_entry = ttk.Entry(form, width=10)
        self.inv_qty_entry.grid(row=0, column=3, padx=5, pady=5)
        
        btn = ttk.Button(form, text="Add/Update Stock", command=self.add_update_inventory)
        # --- !! ADJUSTED GRID !! ---
        btn.grid(row=1, column=0, columnspan=4, pady=10)

        # Treeview
        cols = ("Inventory_ID", "Product", "Warehouse", "Quantity")
        self.inventory_tree = ttk.Treeview(parent_frame, columns=cols, show="headings")
        for col in cols:
            self.inventory_tree.heading(col, text=col)
        self.inventory_tree.pack(fill="both", expand=True, pady=10)
        
        # Data loaded by refresh_warehouse_tab_data()
        # self.refresh_inventory_tree()

    def add_update_inventory(self):
        product_text = self.inv_product_combo.get()
        # --- !! REMOVED WAREHOUSE TEXT !! ---
        # warehouse_text = self.inv_warehouse_combo.get()
        qty = self.inv_qty_entry.get()

        # --- !! UPDATED VALIDATION !! ---
        if not product_text or not qty:
            show_error("Input Error", "Product and Quantity are required.")
            return

        product_id = self.inv_product_data[product_text]
        # --- !! HARDCODED WAREHOUSE ID = 1 !! ---
        warehouse_id = 1 
        
        conn = get_db_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            # UPSERT logic: Insert new, or update quantity if it exists
            query = """
                INSERT INTO Inventory (Product_ID, Warehouse_ID, Quantity)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE Quantity = Quantity + VALUES(Quantity)
            """
            cursor.execute(query, (product_id, warehouse_id, int(qty)))
            conn.commit()
            show_info("Success", f"Stock updated for {product_text}.")
            self.inv_qty_entry.delete(0, tk.END)
            
            # --- !! AUTO-REFRESH OTHER TABS !! ---
            self.refresh_warehouse_tab_data() # Refresh this tab
            self.refresh_customer_tab_data() # Refresh customer shop stock
        except mysql.connector.Error as err:
            conn.rollback()
            show_error("Database Error", f"Failed to update stock: {err}")
        finally:
            conn.close()

    def refresh_inventory_tree(self):
        clear_treeview(self.inventory_tree)
        conn = get_db_connection()
        if not conn: return
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT i.Inventory_ID, p.P_Name, w.Location, i.Quantity 
                FROM Inventory i
                JOIN PRODUCT p ON i.Product_ID = p.Product_ID
                JOIN WAREHOUSE w ON i.Warehouse_ID = w.Warehouse_ID
            """
            cursor.execute(query)
            for row in cursor.fetchall():
                self.inventory_tree.insert("", tk.END, values=(row['Inventory_ID'], row['P_Name'], row['Location'], row['Quantity']))
        except mysql.connector.Error as err:
            show_error("Database Error", f"Failed to fetch inventory: {err}")
        finally:
            conn.close()

    # --- TAB 3: FLEET MANAGER ---
    def create_fleet_tab(self):
        # --- !! NEW REFRESH BUTTON !! ---
        refresh_btn = ttk.Button(self.tab_fleet, text="Refresh All Data", command=self.refresh_fleet_tab_data)
        refresh_btn.pack(anchor="ne", padx=10, pady=5)

        # Tab-level notebook
        fleet_notebook = ttk.Notebook(self.tab_fleet)
        fleet_notebook.pack(fill="both", expand=True)

        driver_tab = ttk.Frame(fleet_notebook, padding=10)
        vehicle_tab = ttk.Frame(fleet_notebook, padding=10)
        assign_tab = ttk.Frame(fleet_notebook, padding=10)
        
        fleet_notebook.add(driver_tab, text="Manage Drivers")
        fleet_notebook.add(vehicle_tab, text="Manage Fleet")
        fleet_notebook.add(assign_tab, text="Assign Driver to Vehicle")

        self.create_driver_crud_ui(driver_tab)
        self.create_fleet_crud_ui(vehicle_tab)
        self.create_assignment_ui(assign_tab)

    def refresh_fleet_tab_data(self):
        """Refreshes all dynamic data on the Fleet tab."""
        self.refresh_driver_tree()
        self.refresh_fleet_tree()
        # Refresh comboboxes in the "Assign" sub-tab
        self.assign_driver_data = populate_combobox(self.assign_driver_combo, "SELECT Driver_ID, D_Name FROM DRIVER WHERE Availability = 'Available'", "D_Name", "Driver_ID")
        self.assign_vehicle_data = populate_combobox(self.assign_vehicle_combo, "SELECT Vehicle_no FROM FLEET WHERE Availability = 'Available'", "Vehicle_no")
        self.assign_driver_combo.set('')
        self.assign_vehicle_combo.set('')
        
        # Reset selections
        self.selected_driver_id = None
        self.selected_vehicle_id = None
        if hasattr(self, 'selected_driver_label'):
             self.selected_driver_label.config(text="-- Select a driver from the list --")
        if hasattr(self, 'selected_vehicle_label'):
             self.selected_vehicle_label.config(text="-- Select a vehicle from the list --")

        print("Fleet Tab Refreshed") # For debugging

    def create_driver_crud_ui(self, parent_frame):
        # Form
        form = ttk.Frame(parent_frame, padding=10, relief=tk.GROOVE)
        form.pack(fill="x")
        
        ttk.Label(form, text="Driver Name:").grid(row=0, column=0, sticky="w")
        self.d_name_entry = ttk.Entry(form, width=30)
        self.d_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form, text="Availability:").grid(row=0, column=2, sticky="w")
        self.d_avail_combo = ttk.Combobox(form, state="readonly", values=['Available', 'On-Trip', 'Unavailable'])
        self.d_avail_combo.grid(row=0, column=3, padx=5, pady=5)

        btn = ttk.Button(form, text="Add New Driver", command=self.add_driver)
        btn.grid(row=1, column=0, columnspan=4, pady=10)

        # Treeview
        cols = ("Driver_ID", "D_Name", "Availability", "Vehicle_no")
        self.driver_tree = ttk.Treeview(parent_frame, columns=cols, show="headings")
        for col in cols:
            self.driver_tree.heading(col, text=col)
        self.driver_tree.pack(fill="both", expand=True, pady=10)
        
        # --- !! BIND CLICK EVENT !! ---
        self.driver_tree.bind('<<TreeviewSelect>>', self.on_driver_select)
        
        # --- !! NEW UPDATE FORM !! ---
        update_frame = ttk.Frame(parent_frame, padding=10, relief=tk.GROOVE)
        update_frame.pack(fill="x", pady=5)
        
        ttk.Label(update_frame, text="Update Status for:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, sticky="w")
        self.selected_driver_label = ttk.Label(update_frame, text="-- Select a driver from the list --", font=("Arial", 10, "italic"))
        self.selected_driver_label.grid(row=0, column=1, padx=5, sticky="w")
        
        ttk.Label(update_frame, text="Set New Status:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.new_driver_status_combo = ttk.Combobox(update_frame, state="readonly", values=['Available', 'On-Trip', 'Unavailable'])
        self.new_driver_status_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        btn_update = ttk.Button(update_frame, text="Update Driver Status", command=self.update_driver_status)
        btn_update.grid(row=1, column=2, padx=10, pady=5)
        
        
    def add_driver(self):
        name = self.d_name_entry.get()
        avail = self.d_avail_combo.get()
        if not name or not avail:
            show_error("Input Error", "Name and Availability are required.")
            return

        conn = get_db_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            query = "INSERT INTO DRIVER (D_Name, Availability) VALUES (%s, %s)"
            cursor.execute(query, (name, avail))
            conn.commit()
            show_info("Success", "Driver added.")
            self.d_name_entry.delete(0, tk.END)
            self.d_avail_combo.set('')
            
            # --- !! AUTO-REFRESH !! ---
            self.refresh_fleet_tab_data() # Refresh this tab's trees and dropdowns
        except mysql.connector.Error as err:
            conn.rollback()
            show_error("Database Error", f"Failed to add driver: {err}")
        finally:
            conn.close()

    def refresh_driver_tree(self):
        clear_treeview(self.driver_tree)
        conn = get_db_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM DRIVER")
            for row in cursor.fetchall():
                self.driver_tree.insert("", tk.END, values=row)
        except mysql.connector.Error as err:
            show_error("Database Error", f"Failed to fetch drivers: {err}")
        finally:
            conn.close()
            
    def create_fleet_crud_ui(self, parent_frame):
        # Form
        form = ttk.Frame(parent_frame, padding=10, relief=tk.GROOVE)
        form.pack(fill="x")
        
        ttk.Label(form, text="Vehicle No:").grid(row=0, column=0, sticky="w")
        self.f_vehicle_entry = ttk.Entry(form, width=30)
        self.f_vehicle_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form, text="Availability:").grid(row=0, column=2, sticky="w")
        self.f_avail_combo = ttk.Combobox(form, state="readonly", values=['Available', 'In-Use', 'Maintenance'])
        self.f_avail_combo.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form, text="Location:").grid(row=1, column=0, sticky="w")
        self.f_location_entry = ttk.Entry(form, width=30)
        self.f_location_entry.grid(row=1, column=1, padx=5, pady=5)

        btn = ttk.Button(form, text="Add New Vehicle", command=self.add_vehicle)
        btn.grid(row=2, column=0, columnspan=4, pady=10)

        # Treeview
        cols = ("Vehicle_no", "Availability", "Location", "Driver_ID")
        self.fleet_tree = ttk.Treeview(parent_frame, columns=cols, show="headings")
        for col in cols:
            self.fleet_tree.heading(col, text=col)
        self.fleet_tree.pack(fill="both", expand=True, pady=10)
        
        # --- !! BIND CLICK EVENT !! ---
        self.fleet_tree.bind('<<TreeviewSelect>>', self.on_fleet_select)
        
        # --- !! NEW UPDATE FORM !! ---
        update_frame = ttk.Frame(parent_frame, padding=10, relief=tk.GROOVE)
        update_frame.pack(fill="x", pady=5)
        
        ttk.Label(update_frame, text="Update Status for:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, sticky="w")
        self.selected_vehicle_label = ttk.Label(update_frame, text="-- Select a vehicle from the list --", font=("Arial", 10, "italic"))
        self.selected_vehicle_label.grid(row=0, column=1, padx=5, sticky="w")
        
        ttk.Label(update_frame, text="Set New Status:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.new_vehicle_status_combo = ttk.Combobox(update_frame, state="readonly", values=['Available', 'In-Use', 'Maintenance'])
        self.new_vehicle_status_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        btn_update = ttk.Button(update_frame, text="Update Vehicle Status", command=self.update_vehicle_status)
        btn_update.grid(row=1, column=2, padx=10, pady=5)


    def add_vehicle(self):
        vehicle_no = self.f_vehicle_entry.get()
        avail = self.f_avail_combo.get()
        location = self.f_location_entry.get()
        
        if not vehicle_no or not avail or not location:
            show_error("Input Error", "All fields are required.")
            return

        conn = get_db_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            query = "INSERT INTO FLEET (Vehicle_no, Availability, Location) VALUES (%s, %s, %s)"
            cursor.execute(query, (vehicle_no, avail, location))
            conn.commit()
            show_info("Success", "Vehicle added.")
            self.f_vehicle_entry.delete(0, tk.END)
            self.f_avail_combo.set('')
            self.f_location_entry.delete(0, tk.END)
            
            # --- !! AUTO-REFRESH !! ---
            self.refresh_fleet_tab_data() # Refresh this tab's trees and dropdowns
        except mysql.connector.Error as err:
            conn.rollback()
            show_error("Database Error", f"Failed to add vehicle: {err}")
        finally:
            conn.close()

    def refresh_fleet_tree(self):
        clear_treeview(self.fleet_tree)
        conn = get_db_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM FLEET")
            for row in cursor.fetchall():
                self.fleet_tree.insert("", tk.END, values=row)
        except mysql.connector.Error as err:
            show_error("Database Error", f"Failed to fetch fleet: {err}")
        finally:
            conn.close()
            
    def create_assignment_ui(self, parent_frame):
        # Form
        form = ttk.Frame(parent_frame, padding=10, relief=tk.GROOVE)
        form.pack(fill="x", pady=20)
        
        ttk.Label(form, text="Select Driver:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.assign_driver_combo = ttk.Combobox(form, state="readonly", width=30)
        self.assign_driver_data = populate_combobox(self.assign_driver_combo, "SELECT Driver_ID, D_Name FROM DRIVER WHERE Availability = 'Available'", "D_Name", "Driver_ID")
        self.assign_driver_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Select Vehicle:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.assign_vehicle_combo = ttk.Combobox(form, state="readonly", width=30)
        self.assign_vehicle_data = populate_combobox(self.assign_vehicle_combo, "SELECT Vehicle_no FROM FLEET WHERE Availability = 'Available'", "Vehicle_no")
        self.assign_vehicle_combo.grid(row=1, column=1, padx=5, pady=5)
        
        btn = ttk.Button(form, text="Assign Driver to Vehicle", command=self.assign_driver_vehicle)
        btn.grid(row=2, column=0, columnspan=2, pady=10)
        
    def assign_driver_vehicle(self):
        driver_text = self.assign_driver_combo.get()
        vehicle_text = self.assign_vehicle_combo.get()
        
        if not driver_text or not vehicle_text:
            show_error("Input Error", "Must select one driver and one vehicle.")
            return
            
        driver_id = self.assign_driver_data[driver_text]
        vehicle_no = self.assign_vehicle_data[vehicle_text]

        conn = get_db_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.callproc('AssignDriverToVehicle', (driver_id, vehicle_no))
            conn.commit()
            show_info("Success", f"Assigned {driver_text} to {vehicle_no}.")
            
            # --- !! AUTO-REFRESH !! ---
            self.refresh_fleet_tab_data()

        except mysql.connector.Error as err:
            conn.rollback()
            show_error("Database Error", f"Failed to assign driver: {err}")
        finally:
            conn.close()
            
    # --- !! NEW FUNCTIONS FOR UPDATING STATUS !! ---
    
    def on_driver_select(self, event=None):
        try:
            selected_item = self.driver_tree.focus()
            if not selected_item: return
            
            item = self.driver_tree.item(selected_item)
            self.selected_driver_id = item['values'][0] # Get ID
            driver_name = item['values'][1] # Get Name
            self.selected_driver_label.config(text=f"ID: {self.selected_driver_id}, Name: {driver_name}")
        except Exception as e:
            print(f"Error on driver select: {e}") # Log error
            self.selected_driver_id = None
            self.selected_driver_label.config(text="-- Error selecting driver --")

    def on_fleet_select(self, event=None):
        try:
            selected_item = self.fleet_tree.focus()
            if not selected_item: return
            
            item = self.fleet_tree.item(selected_item)
            self.selected_vehicle_id = item['values'][0] # Get Vehicle No
            self.selected_vehicle_label.config(text=f"Vehicle No: {self.selected_vehicle_id}")
        except Exception as e:
            print(f"Error on fleet select: {e}") # Log error
            self.selected_vehicle_id = None
            self.selected_vehicle_label.config(text="-- Error selecting vehicle --")

    def update_driver_status(self):
        new_status = self.new_driver_status_combo.get()
        
        if self.selected_driver_id is None:
            show_error("Update Error", "Please select a driver from the list first.")
            return
        
        if not new_status:
            show_error("Update Error", "Please select a new status from the dropdown.")
            return
            
        conn = get_db_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            query = "UPDATE DRIVER SET Availability = %s WHERE Driver_ID = %s"
            cursor.execute(query, (new_status, self.selected_driver_id))
            conn.commit()
            show_info("Success", "Driver status updated.")
            
            # Refresh all fleet data
            self.refresh_fleet_tab_data()
            
        except mysql.connector.Error as err:
            conn.rollback()
            show_error("Database Error", f"Failed to update driver status: {err}")
        finally:
            conn.close()

    def update_vehicle_status(self):
        new_status = self.new_vehicle_status_combo.get()
        
        if self.selected_vehicle_id is None:
            show_error("Update Error", "Please select a vehicle from the list first.")
            return
        
        if not new_status:
            show_error("Update Error", "Please select a new status from the dropdown.")
            return
            
        conn = get_db_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            query = "UPDATE FLEET SET Availability = %s WHERE Vehicle_no = %s"
            cursor.execute(query, (new_status, self.selected_vehicle_id))
            conn.commit()
            show_info("Success", "Vehicle status updated.")
            
            # Refresh all fleet data
            self.refresh_fleet_tab_data()

        except mysql.connector.Error as err:
            conn.rollback()
            show_error("Database Error", f"Failed to update vehicle status: {err}")
        finally:
            conn.close()

    # --- TAB 4: SYSTEM ADMINISTRATOR ---
    def create_admin_tab(self):
        # --- !! NEW REFRESH BUTTON !! ---
        refresh_btn = ttk.Button(self.tab_admin, text="Refresh All Data", command=self.refresh_admin_tab_data)
        refresh_btn.pack(anchor="ne", padx=10, pady=5)

        # Tab-level notebook
        admin_notebook = ttk.Notebook(self.tab_admin)
        admin_notebook.pack(fill="both", expand=True)

        customer_tab = ttk.Frame(admin_notebook, padding=10)
        reports_tab = ttk.Frame(admin_notebook, padding=10)
        
        admin_notebook.add(customer_tab, text="Manage Customers")
        admin_notebook.add(reports_tab, text="Sales Reports")
        
        self.create_customer_crud_ui(customer_tab)
        self.create_reports_ui(reports_tab)

    def refresh_admin_tab_data(self):
        """Refreshes all dynamic data on the Admin tab."""
        self.refresh_customer_tree()
        self.generate_report() # Re-run the report with current dates
        print("Admin Tab Refreshed") # For debugging

    def create_customer_crud_ui(self, parent_frame):
        # Form
        form = ttk.Frame(parent_frame, padding=10, relief=tk.GROOVE)
        form.pack(fill="x")
        
        ttk.Label(form, text="Customer Name:").grid(row=0, column=0, sticky="w")
        self.c_name_entry = ttk.Entry(form, width=30)
        self.c_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form, text="Email:").grid(row=0, column=2, sticky="w")
        self.c_email_entry = ttk.Entry(form, width=30)
        self.c_email_entry.grid(row=0, column=3, padx=5, pady=5)
        
        btn = ttk.Button(form, text="Add New Customer", command=self.add_customer)
        btn.grid(row=1, column=0, columnspan=4, pady=10)

        # Treeview
        cols = ("Customer_ID", "C_Name", "Email_ID", "Payment_ID", "Driver_ID")
        self.customer_tree = ttk.Treeview(parent_frame, columns=cols, show="headings")
        for col in cols:
            self.customer_tree.heading(col, text=col)
        self.customer_tree.pack(fill="both", expand=True, pady=10)
        
        # Data loaded by refresh_admin_tab_data()
        # self.refresh_customer_tree()

    def add_customer(self):
        name = self.c_name_entry.get()
        email = self.c_email_entry.get()
        
        if not name or not email:
            show_error("Input Error", "Name and Email are required.")
            return

        conn = get_db_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            query = "INSERT INTO CUSTOMER (C_Name, Email_ID) VALUES (%s, %s)"
            cursor.execute(query, (name, email))
            conn.commit()
            show_info("Success", "Customer added.")
            self.c_name_entry.delete(0, tk.END)
            self.c_email_entry.delete(0, tk.END)
            
            # --- !! AUTO-REFRESH OTHER TABS !! ---
            self.refresh_admin_tab_data() # Refresh this tab
            self.refresh_customer_tab_data() # Refresh customer tab's dropdown
        except mysql.connector.Error as err:
            conn.rollback()
            show_error("Database Error", f"Failed to add customer: {err}")
        finally:
            conn.close()

    def refresh_customer_tree(self):
        clear_treeview(self.customer_tree)
        conn = get_db_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM CUSTOMER")
            for row in cursor.fetchall():
                self.customer_tree.insert("", tk.END, values=row)
        except mysql.connector.Error as err:
            show_error("Database Error", f"Failed to fetch customers: {err}")
        finally:
            conn.close()
            
    def create_reports_ui(self, parent_frame):
        # Form
        form = ttk.Frame(parent_frame, padding=10, relief=tk.GROOVE)
        form.pack(fill="x")
        
        today = date.today()
        
        ttk.Label(form, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="w")
        self.r_start_date_entry = ttk.Entry(form, width=20)
        self.r_start_date_entry.insert(0, f"{today.year}-01-01")
        self.r_start_date_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form, text="End Date (YYYY-MM-DD):").grid(row=0, column=2, sticky="w")
        self.r_end_date_entry = ttk.Entry(form, width=20)
        self.r_end_date_entry.insert(0, str(today))
        self.r_end_date_entry.grid(row=0, column=3, padx=5, pady=5)
        
        btn = ttk.Button(form, text="Generate Sales Report", command=self.generate_report)
        btn.grid(row=1, column=0, columnspan=4, pady=10)

        # Treeview
        cols = ("Order_ID", "Customer_Name", "Order_Total", "Payment_Date", "Warehouse")
        self.report_tree = ttk.Treeview(parent_frame, columns=cols, show="headings")
        for col in cols:
            self.report_tree.heading(col, text=col)
        self.report_tree.pack(fill="both", expand=True, pady=10)

    def generate_report(self):
        clear_treeview(self.report_tree)
        start_date = self.r_start_date_entry.get()
        end_date = self.r_end_date_entry.get()
        
        if not start_date or not end_date:
            show_error("Input Error", "Start Date and End Date are required.")
            return

        conn = get_db_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            # Call the stored procedure
            cursor.callproc('GenerateSalesReport', (start_date, end_date))
            
            # Fetch results from the procedure
            for result in cursor.stored_results():
                for row in result.fetchall():
                    self.report_tree.insert("", tk.END, values=row)
            
        except mysql.connector.Error as err:
            show_error("Database Error", f"Failed to generate report: {err}")
        finally:
            conn.close()

# --- RUN THE APPLICATION ---
if __name__ == "__main__":
    app = QuickCommerceApp()
    app.mainloop()
