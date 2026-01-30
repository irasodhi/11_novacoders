# # from flask import Flask, render_template, request, redirect, session, url_for, flash
# # import sqlite3
# # import os

# # app = Flask(__name__)
# # app.secret_key = "secret123"

# # UPLOAD_FOLDER = "static/uploads"
# # app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# # # ---------------- DATABASE CONNECTION ----------------
# # def get_db():
# #     return sqlite3.connect("database.db")


# # # ---------------- HOME / LANDING PAGE ----------------
# # @app.route("/")
# # def home():
# #     return render_template("index.html")


# # # ---------------- PRODUCTS / MARKETPLACE ----------------
# # @app.route("/products")
# # def products():
# #     con = get_db()
# #     cur = con.cursor()

# #     cur.execute("SELECT * FROM products")
# #     products = cur.fetchall()

# #     pending_orders = []
# #     if "user_id" in session:
# #         cur.execute("""
# #             SELECT product_id FROM orders
# #             WHERE user_id=? AND status='pending'
# #         """, (session["user_id"],))
# #         pending_orders = [row[0] for row in cur.fetchall()]

# #     con.close()

# #     return render_template(
# #         "products.html",
# #         products=products,
# #         pending_orders=pending_orders
# #     )


# # # ---------------- USER REGISTER ----------------
# # @app.route("/register", methods=["GET", "POST"])
# # def register():
# #     if request.method == "POST":
# #         name = request.form["name"]
# #         email = request.form["email"]
# #         password = request.form["password"]

# #         con = get_db()
# #         cur = con.cursor()

# #         try:
# #             cur.execute("""
# #                 INSERT INTO users (name, email, password, role)
# #                 VALUES (?, ?, ?, 'user')
# #             """, (name, email, password))
# #             con.commit()
# #         except:
# #             flash("⚠ Email already exists", "error")
# #             return redirect("/register")

# #         con.close()
# #         flash("✅ Registration successful. Please login.", "success")
# #         return redirect("/login")

# #     return render_template("register.html")


# # # ---------------- LOGIN (USER + ADMIN SAME PAGE) ----------------
# # @app.route("/login", methods=["GET", "POST"])
# # def login():
# #     if request.method == "POST":
# #         # Try getting email or username
# #         email_or_username = request.form.get("email") or request.form.get("username")
# #         password = request.form.get("password")

# #         if not email_or_username or not password:
# #             flash("⚠ Please fill all fields", "error")
# #             return redirect("/login")

# #         email_or_username = email_or_username.strip().lower()
# #         password = password.strip()

# #         # Admin login check
# #         if email_or_username in ["admin", "admin@gmail.com"] and password == "admin123":
# #             session.clear()
# #             session["role"] = "admin"
# #             session["user_id"] = 0
# #             flash("✅ Admin logged in", "success")
# #             return redirect("/add_product")

# #         # Normal user login
# #         con = get_db()
# #         cur = con.cursor()
# #         cur.execute(
# #             "SELECT id, role FROM users WHERE email=? AND password=?",
# #             (email_or_username, password)
# #         )
# #         user = cur.fetchone()
# #         con.close()

# #         if user:
# #             session.clear()
# #             session["user_id"] = user[0]
# #             session["role"] = user[1]
# #             flash("✅ Login successful", "success")
# #             return redirect(url_for("home"))
# #         else:
# #             flash("❌ Invalid credentials", "error")
# #             return redirect("/login")

# #     return render_template("login.html")

# # # ---------------- LOGOUT ----------------
# # @app.route("/logout")
# # def logout():
# #     session.clear()
# #     return redirect("/login")


# # # ---------------- BUY PRODUCT (ADD TO CART / PENDING) ----------------
# # @app.route("/order/<int:product_id>", methods=["POST"])
# # def buy_product(product_id):
# #     if "user_id" not in session:
# #         flash("⚠ Please login first", "error")
# #         return redirect("/login")

# #     con = get_db()
# #     cur = con.cursor()

# #     # Only insert if not already pending
# #     cur.execute("""
# #         SELECT id FROM orders
# #         WHERE user_id=? AND product_id=? AND status='pending'
# #     """, (session["user_id"], product_id))

# #     if not cur.fetchone():
# #         cur.execute("""
# #             INSERT INTO orders (user_id, product_id, status)
# #             VALUES (?, ?, 'pending')
# #         """, (session["user_id"], product_id))
# #         con.commit()

# #     con.close()
# #     flash("⏳ Waiting for admin approval", "info")
# #     return redirect("/products")



# # # ---------------- ADMIN: ADD PRODUCT ----------------
# # @app.route("/add_product", methods=["GET", "POST"])
# # def add_product():

# #     if session.get("role") != "admin":
# #         return redirect("/login")

# #     if request.method == "POST":
# #         name = request.form["name"]
# #         price = request.form["price"]
# #         image = request.files["image"]

# #         image_name = image.filename
# #         image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_name))

# #         con = get_db()
# #         cur = con.cursor()

# #         cur.execute("""
# #             INSERT INTO products (name, price, image)
# #             VALUES (?, ?, ?)
# #         """, (name, price, image_name))

# #         con.commit()
# #         con.close()

# #         flash("✅ Product added successfully", "success")
# #         return redirect("/add_product")

# #     return render_template("add_product.html")


# # # ---------------- ADMIN: VIEW ORDERS ----------------
# # @app.route("/admin/orders")
# # def admin_orders():

# #     if session.get("role") != "admin":
# #         return redirect("/login")

# #     con = get_db()
# #     cur = con.cursor()

# #     cur.execute("""
# #         SELECT orders.id, users.email, products.name, orders.status
# #         FROM orders
# #         JOIN users ON orders.user_id = users.id
# #         JOIN products ON orders.product_id = products.id
# #     """)

# #     orders = cur.fetchall()
# #     con.close()

# #     return render_template("admin.html", orders=orders)


# # # ---------------- ADMIN: APPROVE / REJECT ORDER ----------------
# # @app.route("/admin/order/<int:order_id>/<status>")
# # def update_order(order_id, status):

# #     if session.get("role") != "admin":
# #         return redirect("/login")

# #     con = get_db()
# #     cur = con.cursor()

# #     cur.execute("""
# #         UPDATE orders SET status=?
# #         WHERE id=?
# #     """, (status, order_id))

# #     con.commit()
# #     con.close()

# #     return redirect("/admin/orders")
# from flask import Flask, render_template, request, redirect, session, url_for, flash
# import sqlite3
# import os
# import random

# app = Flask(__name__)
# app.secret_key = "secret123"

# UPLOAD_FOLDER = "static/uploads"
# app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# # ---------------- DATABASE CONNECTION ----------------
# def get_db():
#     return sqlite3.connect("database.db")


# # ---------------- HOME / LANDING PAGE ----------------
# @app.route("/")
# def home():
#     return render_template("index.html")


# # ---------------- PRODUCTS / MARKETPLACE ----------------
# @app.route("/products")
# def products():
#     con = get_db()
#     cur = con.cursor()

#     # FIX: Only show products that have NOT been approved in an order
#     cur.execute("""
#         SELECT * FROM products 
#         WHERE id NOT IN (SELECT product_id FROM orders WHERE status='approved')
#     """)
#     products = cur.fetchall()

#     pending_orders = []
#     if "user_id" in session:
#         cur.execute("""
#             SELECT product_id FROM orders
#             WHERE user_id=? AND status='pending'
#         """, (session["user_id"],))
#         pending_orders = [row[0] for row in cur.fetchall()]

#     con.close()

#     return render_template(
#         "products.html",
#         products=products,
#         pending_orders=pending_orders
#     )


# # ---------------- USER REGISTER ----------------
# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         name = request.form["name"]
#         email = request.form["email"]
#         password = request.form["password"]

#         con = get_db()
#         cur = con.cursor()

#         try:
#             cur.execute("""
#                 INSERT INTO users (name, email, password, role)
#                 VALUES (?, ?, ?, 'user')
#             """, (name, email, password))
#             con.commit()
#         except:
#             flash("⚠ Email already exists", "error")
#             return redirect("/register")

#         con.close()
#         flash("✅ Registration successful. Please login.", "success")
#         return redirect("/login")

#     return render_template("register.html")


# # ---------------- LOGIN (USER + ADMIN SAME PAGE) ----------------
# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         email_or_username = request.form.get("email") or request.form.get("username")
#         password = request.form.get("password")

#         if not email_or_username or not password:
#             flash("⚠ Please fill all fields", "error")
#             return redirect("/login")

#         email_or_username = email_or_username.strip().lower()
#         password = password.strip()

#         # FIX: Removed session.clear() so Admin login doesn't kick out the User
#         if email_or_username in ["admin", "admin@gmail.com"] and password == "admin123":
#             session["role"] = "admin"
#             session["admin_id"] = 0
#             flash("✅ Admin logged in", "success")
#             return redirect("/add_product")

#         con = get_db()
#         cur = con.cursor()
#         cur.execute(
#             "SELECT id, role FROM users WHERE email=? AND password=?",
#             (email_or_username, password)
#         )
#         user = cur.fetchone()
#         con.close()

#         if user:
#             # FIX: Removed session.clear() to maintain parallel sessions
#             session["user_id"] = user[0]
#             session["role"] = user[1]
#             session["user"] = email_or_username  # <-- add this
#             flash("✅ Login successful", "success")
#             # FIX: Redirects to the home function (index.html)
#             return redirect(url_for("home"))
#         else:
#             flash("❌ Invalid credentials", "error")
#             return redirect("/login")

#     return render_template("login.html")

# # ---------------- LOGOUT ----------------
# @app.route("/logout")
# def logout():
#     session.clear()
#     return redirect("/login")


# # ---------------- BUY PRODUCT (ADD TO CART / PENDING) ----------------
# @app.route("/order/<int:product_id>", methods=["POST"])
# def buy_product(product_id):
#     if "user_id" not in session:
#         flash("⚠ Please login first", "error")
#         return redirect("/login")

#     con = get_db()
#     cur = con.cursor()

#     cur.execute("""
#         SELECT id FROM orders
#         WHERE user_id=? AND product_id=? AND status='pending'
#     """, (session["user_id"], product_id))

#     if not cur.fetchone():
#         cur.execute("""
#             INSERT INTO orders (user_id, product_id, status)
#             VALUES (?, ?, 'pending')
#         """, (session["user_id"], product_id))
#         con.commit()

#     con.close()
#     flash("⏳ Waiting for admin approval", "info")
#     return redirect("/products")


# # ---------------- ADMIN: ADD PRODUCT ----------------
# @app.route("/add_product", methods=["GET", "POST"])
# def add_product():
#     if session.get("role") != "admin":
#         return redirect("/login")

#     if request.method == "POST":
#         name = request.form["name"]
#         price = request.form["price"]
#         image = request.files["image"]

#         image_name = image.filename
#         image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_name))

#         con = get_db()
#         cur = con.cursor()

#         cur.execute("""
#             INSERT INTO products (name, price, image)
#             VALUES (?, ?, ?)
#         """, (name, price, image_name))

#         con.commit()
#         con.close()

#         flash("✅ Product added successfully", "success")
#         return redirect("/add_product")

#     return render_template("add_product.html")


# # ---------------- ADMIN: VIEW ORDERS ----------------
# @app.route("/admin/orders")
# def admin_orders():
#     if session.get("role") != "admin":
#         return redirect("/login")

#     con = get_db()
#     cur = con.cursor()

#     cur.execute("""
#         SELECT orders.id, users.email, products.name, orders.status
#         FROM orders
#         JOIN users ON orders.user_id = users.id
#         JOIN products ON orders.product_id = products.id
#     """)

#     orders = cur.fetchall()
#     con.close()

#     return render_template("admin.html", orders=orders)


# # ---------------- ADMIN: APPROVE / REJECT ORDER ----------------
# @app.route("/admin/order/<int:order_id>/<status>")
# def update_order(order_id, status):

#     if session.get("role") != "admin":
#         return redirect("/login")

#     con = get_db()
#     cur = con.cursor()

#     cur.execute("""
#         UPDATE orders SET status=?
#         WHERE id=?
#     """, (status, order_id))

#     con.commit()
#     con.close()

#     # Custom flash message for approval
#     if status == 'approved':
#         days = random.randint(2, 5)  # Generates a random number between 2 and 5
#         flash(f"✅ Request accepted! Your order will be delivered in {days} days.", "success")
#     elif status == 'rejected':
#         flash("❌ Order has been rejected.", "error")

#     return redirect("/admin/orders")


# @app.route("/about")
# def about():
#     return render_template("about.html")

# # Farmer detail / expert ecosystem page
# @app.route("/farmers")
# def farmers():
#     return render_template("farmerdetail.html")

# @app.route("/crop")
# def crop():
#     return render_template("crop.html")
# # ---------------- RUN APP ----------------
# if __name__ == "__main__":
#     app.run(debug=True)
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
import sqlite3
import os
import random
import logging
from planet1 import UltimatePlantCare

# ---------------- APP SETUP ----------------
app = Flask(__name__)
app.secret_key = "secret123"
bot = UltimatePlantCare()
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ---------------- AI BOT SETUP ----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# plant_app = UltimatePlantCare()

# ---------------- DATABASE CONNECTION ----------------
def get_db():
    return sqlite3.connect("database.db")

# ---------------- HOME / LANDING PAGE ----------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------- AI CHAT PAGE (NOT LANDING) ----------------
@app.route("/ai")
def ai_chat():
    return render_template("ai.html")

# ---------------- AI CHAT API ----------------
from werkzeug.utils import secure_filename


@app.route("/chat", methods=["POST"])
def chat():
    message = request.form.get("message", "").strip()
    image = request.files.get("image")

    plant_info = None

    # 🟢 IMAGE HANDLING (THIS WAS MISSING / WRONG)
    if image and image.filename:
        filename = secure_filename(image.filename)
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image.save(image_path)   # ✅ MUST SAVE

        plant_info = bot.smart_identify_plant(image_path)

    # 🟢 TEXT HANDLING
    if not plant_info and message:
        plant_info = bot.get_plant_care(message)

    if not plant_info:
        return jsonify({
            "reply": "❌ Sorry, I couldn’t recognize this plant.\nTry a clearer image or type the plant name 🌱"
        })

    weather = bot.get_weather()
    analysis = bot.analyze(plant_info, weather)

    reply = f"""
🌿 **Plant Identified:** {analysis['plant']}
🌡️ **Temperature:** {analysis['temp']}°C (Ideal: {analysis['range']})
📊 **Status:** {analysis['status']}
💧 **Water:** {analysis['water']}
☀️ **Light:** {analysis['light']}
💡 **Tip:** {analysis['tip']}
"""

    return jsonify({"reply": reply})


# ---------------- PRODUCTS / MARKETPLACE ----------------
@app.route("/products")
def products():
    con = get_db()
    cur = con.cursor()

    # FIX: Only show products that have NOT been approved in an order
    cur.execute("""
        SELECT * FROM products 
        WHERE id NOT IN (SELECT product_id FROM orders WHERE status='approved')
    """)
    products = cur.fetchall()

    pending_orders = []
    if "user_id" in session:
        cur.execute("""
            SELECT product_id FROM orders
            WHERE user_id=? AND status='pending'
        """, (session["user_id"],))
        pending_orders = [row[0] for row in cur.fetchall()]

    con.close()

    return render_template(
        "products.html",
        products=products,
        pending_orders=pending_orders
    )


# ---------------- USER REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        con = get_db()
        cur = con.cursor()

        try:
            cur.execute("""
                INSERT INTO users (name, email, password, role)
                VALUES (?, ?, ?, 'user')
            """, (name, email, password))
            con.commit()
        except:
            flash("⚠ Email already exists", "error")
            return redirect("/register")

        con.close()
        flash("✅ Registration successful. Please login.", "success")
        return redirect("/login")

    return render_template("register.html")


# ---------------- LOGIN (USER + ADMIN SAME PAGE) ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email_or_username = request.form.get("email") or request.form.get("username")
        password = request.form.get("password")

        if not email_or_username or not password:
            flash("⚠ Please fill all fields", "error")
            return redirect("/login")

        email_or_username = email_or_username.strip().lower()
        password = password.strip()

        # FIX: Removed session.clear() so Admin login doesn't kick out the User
        if email_or_username in ["admin", "admin@gmail.com"] and password == "admin123":
            session["role"] = "admin"
            session["admin_id"] = 0
            flash("✅ Admin logged in", "success")
            return redirect("/add_product")

        con = get_db()
        cur = con.cursor()
        cur.execute(
            "SELECT id, role FROM users WHERE email=? AND password=?",
            (email_or_username, password)
        )
        user = cur.fetchone()
        con.close()

        if user:
            # FIX: Removed session.clear() to maintain parallel sessions
            session["user_id"] = user[0]
            session["role"] = user[1]
            session["user"] = email_or_username  # <-- add this
            flash("✅ Login successful", "success")
            # FIX: Redirects to the home function (index.html)
            return redirect(url_for("home"))
        else:
            flash("❌ Invalid credentials", "error")
            return redirect("/login")

    return render_template("login.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------------- BUY PRODUCT (ADD TO CART / PENDING) ----------------
@app.route("/order/<int:product_id>", methods=["POST"])
def buy_product(product_id):
    if "user_id" not in session:
        flash("⚠ Please login first", "error")
        return redirect("/login")

    con = get_db()
    cur = con.cursor()

    cur.execute("""
        SELECT id FROM orders
        WHERE user_id=? AND product_id=? AND status='pending'
    """, (session["user_id"], product_id))

    if not cur.fetchone():
        cur.execute("""
            INSERT INTO orders (user_id, product_id, status)
            VALUES (?, ?, 'pending')
        """, (session["user_id"], product_id))
        con.commit()

    con.close()
    flash("⏳ Waiting for admin approval", "info")
    return redirect("/products")


# ---------------- ADMIN: ADD PRODUCT ----------------
@app.route("/add_product", methods=["GET", "POST"])
def add_product():
    if session.get("role") != "admin":
        return redirect("/login")

    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        image = request.files["image"]

        image_name = image.filename
        image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_name))

        con = get_db()
        cur = con.cursor()

        cur.execute("""
            INSERT INTO products (name, price, image)
            VALUES (?, ?, ?)
        """, (name, price, image_name))

        con.commit()
        con.close()

        flash("✅ Product added successfully", "success")
        return redirect("/add_product")

    return render_template("add_product.html")


# ---------------- ADMIN: VIEW ORDERS ----------------
@app.route("/admin/orders")
def admin_orders():
    if session.get("role") != "admin":
        return redirect("/login")

    con = get_db()
    cur = con.cursor()

    cur.execute("""
        SELECT orders.id, users.email, products.name, orders.status
        FROM orders
        JOIN users ON orders.user_id = users.id
        JOIN products ON orders.product_id = products.id
    """)

    orders = cur.fetchall()
    con.close()

    return render_template("admin.html", orders=orders)


# ---------------- ADMIN: APPROVE / REJECT ORDER ----------------
@app.route("/admin/order/<int:order_id>/<status>")
def update_order(order_id, status):

    if session.get("role") != "admin":
        return redirect("/login")

    con = get_db()
    cur = con.cursor()

    cur.execute("""
        UPDATE orders SET status=?
        WHERE id=?
    """, (status, order_id))

    con.commit()
    con.close()

    # Custom flash message for approval
    if status == 'approved':
        days = random.randint(2, 5)  # Generates a random number between 2 and 5
        flash(f"✅ Request accepted! Your order will be delivered in {days} days.", "success")
    elif status == 'rejected':
        flash("❌ Order has been rejected.", "error")

    return redirect("/admin/orders")

#---------------- LOGOUT ----------------


# ---------------- EXTRA PAGES ----------------
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/farmers")
def farmers():
    return render_template("farmerdetail.html")

@app.route("/crop")
def crop():
    return render_template("crop.html")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
