import sqlite3
import datetime as dt
import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt

# --- STYLING ---
BG_MAIN = "#f4f7f6"
SIDEBAR_BG = "#2c3e50"
ACCENT_BLUE = "#3498db"
ACCENT_GREEN = "#27ae60"
ACCENT_RED = "#e74c3c"
ACCENT_ORANGE = "#e67e22"

DB_NAME = "restaurant.db"


# ---------------- DATABASE ---------------- #
def init_db():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS all_dish (dish_code INTEGER PRIMARY KEY, dish_name TEXT, dish_price REAL)")
    cur.execute(
        "CREATE TABLE IF NOT EXISTS all_bills (bill_number INTEGER PRIMARY KEY AUTOINCREMENT, bill_amt REAL, bill_date TEXT)")
    cur.execute(
        "CREATE TABLE IF NOT EXISTS bill_items (id INTEGER PRIMARY KEY AUTOINCREMENT, bill_no INTEGER, dish_code INTEGER, qty INTEGER, amount REAL)")
    con.commit()
    con.close()


# ---------------- LOGIC ---------------- #
cart = []


def add_dish_logic(c, n, p):
    if not (c and n and p):
        messagebox.showwarning("Input Error", "Fill all dish details")
        return
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    try:
        cur.execute("INSERT INTO all_dish VALUES (?,?,?)", (c, n, p))
        con.commit()
        messagebox.showinfo("Success", "Dish added to menu")
    except:
        messagebox.showerror("Error", "Dish code already exists")
    finally:
        con.close()


def delete_from_cart(tree, label):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Select Item", "Please select an item in the cart to delete")
        return
    index = tree.index(selected_item[0])
    del cart[index]
    refresh_cart(tree, label)


def refresh_cart(tree, total_label):
    for i in tree.get_children(): tree.delete(i)
    total = sum(item[4] for item in cart)
    for item in cart: tree.insert("", "end", values=item)
    total_label.config(text=f"Total: ₹{total:.2f}")


def finalize_bill(tree, label):
    if not cart: return
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    total = sum(item[4] for item in cart)
    cur.execute("INSERT INTO all_bills (bill_amt, bill_date) VALUES (?,?)", (total, dt.date.today().isoformat()))
    bill_no = cur.lastrowid
    for itm in cart:
        cur.execute("INSERT INTO bill_items (bill_no, dish_code, qty, amount) VALUES (?,?,?,?)",
                    (bill_no, itm[0], itm[2], itm[4]))
    con.commit()
    con.close()

    win = tk.Toplevel()
    win.title("Receipt")
    win.geometry("350x500")
    txt = tk.Text(win, font=("Courier", 10), padx=10, pady=10)
    txt.pack(fill="both", expand=True)
    txt.insert("1.0", f"{'RESTAURANT PRO':^35}\n{'-' * 35}\nBill No: {bill_no}\nDate: {dt.date.today()}\n{'-' * 35}\n")
    for itm in cart:
        txt.insert("end", f"{itm[1][:18]:<18} x{itm[2]:<3} {itm[4]:>10.2f}\n")
    txt.insert("end", f"{'-' * 35}\nTOTAL: ₹{total:>25.2f}\n\n{'THANK YOU FOR VISITING!':^35}")

    cart.clear()
    refresh_cart(tree, label)


# ---------------- DASHBOARD (3 GRAPHS) ---------------- #
def open_dashboard():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    # Data 1: Daily Sales
    cur.execute("SELECT bill_date, SUM(bill_amt) FROM all_bills GROUP BY bill_date")
    sales_data = cur.fetchall()

    # Data 2: Bills Per Day
    cur.execute("SELECT bill_date, COUNT(*) FROM all_bills GROUP BY bill_date")
    bills_data = cur.fetchall()

    # Data 3: Top Dishes
    cur.execute("SELECT dish_code, SUM(qty) FROM bill_items GROUP BY dish_code ORDER BY SUM(qty) DESC LIMIT 5")
    dishes_data = cur.fetchall()

    con.close()

    dash_win = tk.Toplevel()
    dash_win.title("Analytics Dashboard")
    dash_win.geometry("300x450")
    dash_win.configure(bg=SIDEBAR_BG)

    tk.Label(dash_win, text="REPORTS & ANALYTICS", font=("Arial", 12, "bold"), fg="white", bg=SIDEBAR_BG).pack(pady=20)

    # Button 1: Daily Sales (Line Graph)
    tk.Button(dash_win, text="📈 View Daily Sales", bg=ACCENT_BLUE, fg="white", font=("Arial", 10),
              command=lambda: show_sales_plot(sales_data)).pack(fill="x", padx=30, pady=10, ipady=5)

    # Button 2: Bills Per Day (Bar Graph)
    tk.Button(dash_win, text="📊 Bills Per Day", bg=ACCENT_ORANGE, fg="white", font=("Arial", 10),
              command=lambda: show_bills_plot(bills_data)).pack(fill="x", padx=30, pady=10, ipady=5)

    # Button 3: Top 5 Dishes (Bar Graph)
    tk.Button(dash_win, text="🏆 Top 5 Dishes", bg=ACCENT_GREEN, fg="white", font=("Arial", 10),
              command=lambda: show_dishes_plot(dishes_data)).pack(fill="x", padx=30, pady=10, ipady=5)


def show_sales_plot(data):
    if not data: return
    d, t = [x[0] for x in data], [x[1] for x in data]
    plt.figure()
    plt.plot(d, t, marker='o', color='blue')
    plt.title("Total Sales Revenue")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def show_bills_plot(data):
    if not data: return
    d, c = [x[0] for x in data], [x[1] for x in data]
    plt.figure()
    plt.bar(d, c, color='orange')
    plt.title("Number of Bills Per Day")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def show_dishes_plot(data):
    if not data: return
    d, q = [str(x[0]) for x in data], [x[1] for x in data]
    plt.figure()
    plt.bar(d, q, color='green')
    plt.title("Top 5 Popular Dishes (by Qty)")
    plt.tight_layout()
    plt.show()


# ---------------- LOGIN ---------------- #
def login_screen():
    login = tk.Tk()
    login.title("System Login")
    login.geometry("350x450")
    login.configure(bg=SIDEBAR_BG)

    frame = tk.Frame(login, bg=SIDEBAR_BG)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(frame, text="RESTAURANT PRO", font=("Arial", 18, "bold"), fg="white", bg=SIDEBAR_BG).pack(pady=20)

    tk.Label(frame, text="Username", fg="#adb5bd", bg=SIDEBAR_BG).pack(anchor="w")
    user = tk.Entry(frame, font=("Arial", 12), bd=0)
    user.pack(pady=5, ipady=5)

    tk.Label(frame, text="Password", fg="#adb5bd", bg=SIDEBAR_BG).pack(anchor="w")
    pwd = tk.Entry(frame, show="*", font=("Arial", 12), bd=0)
    pwd.pack(pady=5, ipady=5)

    def check():
        if user.get().lower() == "admin" and pwd.get() == "1234":
            login.destroy()
            launch_gui()
        else:
            messagebox.showerror("Error", "Invalid Login")

    tk.Button(frame, text="LOGIN", bg=ACCENT_BLUE, fg="white", font=("Arial", 10, "bold"),
              bd=0, width=20, command=check).pack(pady=30, ipady=8)
    login.mainloop()


# ---------------- MAIN GUI ---------------- #
def launch_gui():
    root = tk.Tk()
    root.title("Restaurant Management System")
    root.geometry("1100x750")
    root.configure(bg=BG_MAIN)

    # --- SIDEBAR ---
    sidebar = tk.Frame(root, bg=SIDEBAR_BG, width=250)
    sidebar.pack(side="left", fill="y")

    tk.Label(sidebar, text="MENU MANAGEMENT", font=("Arial", 11, "bold"), bg=SIDEBAR_BG, fg="white").pack(pady=20)

    f_add = tk.Frame(sidebar, bg=SIDEBAR_BG, padx=15)
    f_add.pack(fill="x")

    tk.Label(f_add, text="Dish Code", fg="white", bg=SIDEBAR_BG).pack(anchor="w")
    ac_entry = tk.Entry(f_add)
    ac_entry.pack(fill="x", pady=2)
    tk.Label(f_add, text="Dish Name", fg="white", bg=SIDEBAR_BG).pack(anchor="w")
    an_entry = tk.Entry(f_add)
    an_entry.pack(fill="x", pady=2)
    tk.Label(f_add, text="Price", fg="white", bg=SIDEBAR_BG).pack(anchor="w")
    ap_entry = tk.Entry(f_add)
    ap_entry.pack(fill="x", pady=2)

    tk.Button(f_add, text="Add Dish", bg=ACCENT_GREEN, fg="white", bd=0,
              command=lambda: add_dish_logic(ac_entry.get(), an_entry.get(), ap_entry.get())).pack(fill="x", pady=10,
                                                                                                   ipady=5)

    tk.Frame(sidebar, height=2, bg="#3e4f5f").pack(fill="x", pady=20)

    tk.Button(sidebar, text="📊 Open Dashboard", bg=SIDEBAR_BG, fg="white", bd=0, font=("Arial", 10), anchor="w",
              padx=20, command=open_dashboard).pack(fill="x")
    tk.Button(sidebar, text="🗑 Clear Entire Cart", bg=SIDEBAR_BG, fg="white", bd=0, font=("Arial", 10), anchor="w",
              padx=20, command=lambda: [cart.clear(), refresh_cart(cart_tree, total_lbl)]).pack(fill="x")

    # --- MAIN AREA ---
    main = tk.Frame(root, bg=BG_MAIN, padx=20, pady=10)
    main.pack(side="right", fill="both", expand=True)

    # Search
    s_frame = tk.Frame(main, bg=BG_MAIN)
    s_frame.pack(fill="x", pady=10)
    tk.Label(s_frame, text="Search Dish:", font=("Arial", 10, "bold"), bg=BG_MAIN).pack(side="left")
    s_entry = tk.Entry(s_frame, font=("Arial", 11))
    s_entry.pack(side="left", padx=10, fill="x", expand=True)

    s_tree = ttk.Treeview(main, columns=("C", "N", "P"), show="headings", height=5)
    for c, h in zip(("C", "N", "P"), ("Code", "Dish Name", "Price")): s_tree.heading(c, text=h)
    s_tree.pack(fill="x")

    # Enter key search logic
    def run_search(e=None):
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("SELECT * FROM all_dish WHERE dish_name LIKE ?", (f"%{s_entry.get()}%",))
        rows = cur.fetchall()
        con.close()
        for i in s_tree.get_children(): s_tree.delete(i)
        for r in rows: s_tree.insert("", "end", values=r)

    s_entry.bind("<Return>", run_search)

    # Billing Actions
    act_frame = tk.Frame(main, bg=BG_MAIN)
    act_frame.pack(fill="x", pady=15)

    tk.Label(act_frame, text="Code:", bg=BG_MAIN).pack(side="left")
    bc_entry = tk.Entry(act_frame, width=10)
    bc_entry.pack(side="left", padx=5)
    tk.Label(act_frame, text="Qty:", bg=BG_MAIN).pack(side="left")
    bq_entry = tk.Entry(act_frame, width=10)
    bq_entry.pack(side="left", padx=5)

    def add_to_cart_local(e=None):
        try:
            code, qty = bc_entry.get(), int(bq_entry.get())
            con = sqlite3.connect(DB_NAME)
            cur = con.cursor()
            cur.execute("SELECT dish_name, dish_price FROM all_dish WHERE dish_code=?", (code,))
            res = cur.fetchone()
            con.close()
            if res:
                cart.append((code, res[0], qty, res[1], res[1] * qty))
                refresh_cart(cart_tree, total_lbl)
                bq_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "Invalid Code")
        except:
            messagebox.showwarning("Error", "Check Qty")

    bq_entry.bind("<Return>", add_to_cart_local)

    tk.Button(act_frame, text="Add to Cart", bg=ACCENT_BLUE, fg="white", command=add_to_cart_local, padx=10).pack(
        side="left", padx=5)
    tk.Button(act_frame, text="Delete Selected", bg=ACCENT_RED, fg="white",
              command=lambda: delete_from_cart(cart_tree, total_lbl), padx=10).pack(side="left", padx=5)

    # Cart Table
    cart_tree = ttk.Treeview(main, columns=("C", "N", "Q", "P", "A"), show="headings", height=12)
    for c, h in zip(("C", "N", "Q", "P", "A"), ("Code", "Item", "Qty", "Price", "Amount")): cart_tree.heading(c, text=h)
    cart_tree.pack(fill="both", expand=True)

    total_lbl = tk.Label(main, text="Total: ₹0", font=("Arial", 20, "bold"), bg=BG_MAIN, fg=SIDEBAR_BG)
    total_lbl.pack(pady=10, anchor="e")

    tk.Button(main, text="COMPLETE ORDER & PRINT BILL", bg=ACCENT_GREEN, fg="white", font=("Arial", 12, "bold"),
              pady=10, command=lambda: finalize_bill(cart_tree, total_lbl)).pack(fill="x")

    # Helper: Search selection
    def sync_code(e):
        sel = s_tree.focus()
        if sel:
            val = s_tree.item(sel, "values")
            bc_entry.delete(0, tk.END)
            bc_entry.insert(0, val[0])
            bq_entry.focus()

    s_tree.bind("<<TreeviewSelect>>", sync_code)

    root.mainloop()


if __name__ == "__main__":
    init_db()
    login_screen()