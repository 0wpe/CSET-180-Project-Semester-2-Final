from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash, check_password_hash
from decimal import Decimal
import random
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = "static/images/products"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

conn_str = "mysql://root:cset155@localhost/ecommerce"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()

def get_current_user():
    if "user_id" not in session:
        return None

    query = text("""
    SELECT id, first_name, last_name, email, role
    FROM users
    WHERE id = :id
    """)

    result = conn.execute(query, {"id": session["user_id"]})
    return result.mappings().fetchone()

def is_admin(user):
    return user and user.role == "admin"

def is_vendor(user):
    return user and user.role == "vendor"

def is_customer(user):
    return user and user.role == "customer"

@app.context_processor
def inject_user():
    return dict(current_user=get_current_user())

@app.route("/")
def home():

    sponsored = conn.execute(text("""
        SELECT p.*, pi.image_url
        FROM products p
        LEFT JOIN product_images pi ON p.id = pi.product_id
        WHERE p.is_sponsored = 1
    """)).fetchall()

    discounted = conn.execute(text("""
        SELECT p.*, pi.image_url, d.new_price
        FROM products p
        JOIN discounts d ON p.id = d.product_id
        LEFT JOIN product_images pi ON p.id = pi.product_id
    """)).fetchall()

    packages = conn.execute(text("""
        SELECT p.*, pi.image_url
        FROM products p
        LEFT JOIN product_images pi ON p.id = pi.product_id
        WHERE p.is_package = 1
    """)).fetchall()

    return render_template("index.html", sponsored=sponsored, discounted=discounted, packages=packages)

@app.route("/search")
def search():

    q = request.args.get("q","")

    if q:
        products = conn.execute(text("""
        SELECT p.*, pi.image_url, pv.id AS variant_id
        FROM products p
        LEFT JOIN product_images pi ON p.id = pi.product_id
        JOIN product_variants pv ON pv.product_id = p.id
        WHERE p.title LIKE :q
        """),{"q":f"%{q}%"}).fetchall()
    else:
        products = conn.execute(text("""
        SELECT p.*, pi.image_url, pv.id AS variant_id
        FROM products p
        LEFT JOIN product_images pi ON p.id = pi.product_id
        JOIN product_variants pv ON pv.product_id = p.id
        """)).fetchall()

    return render_template("search.html", products=products, query=q)

@app.route("/search/<int:product_id>")
def product_page(product_id):

    product = conn.execute(text("""
    SELECT p.*, pi.image_url
    FROM products p
    LEFT JOIN product_images pi ON p.id = pi.product_id
    WHERE p.id = :id
    LIMIT 1
    """), {"id":product_id}).fetchone()

    return render_template("item_template.html", product=product)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        conn.execute(text("""
        INSERT INTO users (first_name, last_name, email, username, password, role)
        VALUES (:first_name, :last_name, :email, :username, :password, :role)
        """), {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "username": username,
            "password": generate_password_hash(password),
            "role": role
        })

        conn.commit()

        if role == "vendor":
            user_id = conn.execute(text("""
            SELECT id FROM users WHERE username = :username
            """), {"username": username}).fetchone()[0]

            conn.execute(text("""
            INSERT INTO vendors (user_id)
            VALUES (:id)
            """), {"id": user_id})

            conn.commit()

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = conn.execute(text("""
        SELECT id, role, password
        FROM users
        WHERE username = :username
        """), {"username": username}).fetchone()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["role"] = user.role
            return redirect(url_for("home"))

        return render_template("login.html", error="Invalid Login")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

def cart_Total(user_id):
    cart_items = conn.execute(text("""
    SELECT *
    FROM cart_items ci
    JOIN product_variants pv ON ci.product_variant_id = pv.id
    JOIN products p ON pv.product_id = p.id
    WHERE ci.cart_id = (SELECT id FROM carts WHERE user_id = :user_id)
    """), {"user_id": user_id}).fetchall()

    total = 0
    for i in cart_items:
        total += (i.price * i.quantity)
    return total

@app.route("/cart")
def cart():
    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "customer":
        return redirect("/home")

    user_id = session["user_id"]

    cart_items = conn.execute(text("""
    SELECT ci.id AS cart_item_id,
    ci.quantity,
    pv.*,
    p.*
    FROM cart_items ci
    JOIN product_variants pv ON ci.product_variant_id = pv.id
    JOIN products p ON pv.product_id = p.id
    WHERE ci.cart_id = (SELECT id FROM carts WHERE user_id = :user_id)
    """), {"user_id": user_id}).fetchall()

    subtotal = cart_Total(user_id)
    tax = subtotal * Decimal("0.06")
    total = f"{subtotal + tax:.2f}"

    return render_template("cart.html", cart_items=cart_items, subtotal=f"{subtotal:.2f}", tax=f"{tax:.2f}", total=total, user_id=user_id)

@app.route("/update_cart_quantity", methods=["POST"])
def update_cart_quantity():
    item_id = request.form["id"]
    quantity = request.form["quantity"]

    conn.execute(text("""
    UPDATE cart_items SET quantity = :quantity WHERE id = :item_id
    """), {"item_id": item_id, "quantity": quantity})

    conn.commit()
    return redirect("/cart")

@app.route("/remove_cart_item", methods=["POST"])
def remove_cart_item():
    item_id = request.form["id"]

    conn.execute(text("""
    DELETE FROM cart_items WHERE id = :item_id
    """), {"item_id": item_id})

    conn.commit()
    return redirect("/cart")

@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    product_variant_id = int(request.form["product_variant_id"])
    quantity = int(request.form.get("quantity", 1))

    cart = conn.execute(text("""
    SELECT id FROM carts WHERE user_id = :user_id
    """), {"user_id": user_id}).fetchone()

    if not cart:
        conn.execute(text("""
        INSERT INTO carts (user_id) VALUES (:user_id)
        """), {"user_id": user_id})
        conn.commit()

        cart = conn.execute(text("""
        SELECT id FROM carts WHERE user_id = :user_id
        """), {"user_id": user_id}).fetchone()

    cart_id = cart[0]

    item = conn.execute(text("""
    SELECT id, quantity FROM cart_items
    WHERE cart_id = :cart_id AND product_variant_id = :product_id
    """), {"cart_id": cart_id, "product_id": product_variant_id}).fetchone()

    if item:
        conn.execute(text("""
        UPDATE cart_items
        SET quantity = quantity + :quantity
        WHERE id = :id
        """), {"quantity": quantity, "id": item[0]})
    else:
        conn.execute(text("""
        INSERT INTO cart_items (cart_id, product_variant_id, quantity)
        VALUES (:cart_id, :product_id, :quantity)
        """), {"cart_id": cart_id, "product_id": product_variant_id, "quantity": quantity})

    conn.commit()
    return redirect(request.referrer)

@app.route("/checkout", methods=["POST"])
def checkout():
    user_id = request.form["id"]

    cart_items = conn.execute(text("""
    SELECT ci.id AS cart_item_id,
    ci.quantity,
    pv.*,
    p.*
    FROM cart_items ci
    JOIN product_variants pv ON ci.product_variant_id = pv.id
    JOIN products p ON pv.product_id = p.id
    WHERE ci.cart_id = (SELECT id FROM carts WHERE user_id = :user_id)
    """), {"user_id": user_id}).fetchall()

    subtotal = cart_Total(user_id)
    shipping = subtotal * random.randrange(1,150) * Decimal("0.01")
    tax = (shipping + subtotal) * Decimal("0.06")
    total = f"{shipping + subtotal + tax:.2f}"

    return render_template("checkout.html", cart_items=cart_items, subtotal=subtotal, tax=tax, total=total, shipping=shipping, user_id=user_id)

@app.route("/purchase", methods=["POST"])
def purchase():
    user_id= request.form['id']

    items=conn.execute(text("""
        SELECT * FROM cart_items WHERE cart_id = (SELECT id FROM carts WHERE user_id = :user_id)    
        """),{"user_id": user_id})

    for i in items:
        print("item","id",i[0],"cart_id",i[1],"product_varient_id",i[2],"quantity",i[3])

    conn.execute(text("""
        DELETE FROM cart_items WHERE cart_id = (SELECT id FROM carts WHERE user_id = :user_id)    
        """),{"user_id": user_id})
    conn.commit()

    return render_template("index.html",thank=True)


#Account page
@app.route("/account")
def account():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    admin = conn.execute(text("""
        SELECT id FROM users WHERE role = 'admin' LIMIT 1
    """)).fetchone()
    return render_template("account.html", user=user, admin=admin)

@app.route("/orders")
def orders():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    orders = conn.execute(text("""
    SELECT o.*,
    COALESCE(SUM(oi.quantity * oi.price_at_purchase), 0) AS total_price,
    COALESCE(SUM(oi.quantity), 0) AS total_items
    FROM orders o
    LEFT JOIN order_items oi ON o.id = oi.order_id
    WHERE o.user_id = :id
    GROUP BY o.id
    ORDER BY o.order_date DESC
    """), {"id": user.id}).fetchall()

    order_items_map = {}

    for order in orders:
        items = conn.execute(text("""
            SELECT 
                oi.*,
                p.title,
                u.username,
                u.id AS vendor_user_id,
                v.shop_name
            FROM order_items oi
            JOIN product_variants pv ON oi.product_variant_id = pv.id
            JOIN products p ON pv.product_id = p.id
            JOIN vendors v ON oi.vendor_id = v.id
            JOIN users u ON v.user_id = u.id
            WHERE oi.order_id = :order_id
        """), {"order_id": order.id}).fetchall()

        order_items_map[order.id] = items

    return render_template("orders.html", orders=orders, order_items_map=order_items_map)

@app.route("/cancel_order", methods=["POST"])
def cancel_order():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    order_id = request.form["order_id"]

    conn.execute(text("""
    UPDATE orders
    SET status = 'cancelled'
    WHERE id = :order_id
    AND user_id = :user_id
    AND status IN ('pending','confirmed')
    """), {"order_id": order_id, "user_id": user.id})

    conn.commit()
    return redirect(url_for("orders"))

@app.route("/vendor/shop")
def vendor_shop():
    user = get_current_user()
    if not user or user.role != "vendor":
        return redirect(url_for("login"))

    vendor = conn.execute(text("""
    SELECT id FROM vendors WHERE user_id = :uid
    """), {"uid": user.id}).fetchone()

    products = conn.execute(text("""
    SELECT p.*, pi.image_url
    FROM products p
    LEFT JOIN product_images pi ON p.id = pi.product_id
    WHERE p.vendor_id = :vendor_id
    """), {"vendor_id": vendor.id}).fetchall()

    return render_template("vendor/shop.html", products=products)

@app.route("/vendor/create-product", methods=["GET", "POST"])
def create_product():
    user = get_current_user()

    if not user or user.role != "vendor":
        return redirect(url_for("home"))

    if request.method == "POST":

        vendor = conn.execute(text("""
        SELECT id FROM vendors WHERE user_id = :uid
        """), {"uid": user.id}).fetchone()

        vendor_id = vendor.id

        title = request.form.get("title")
        description = request.form.get("description")
        price = request.form.get("price") or 0
        warranty = request.form.get("warranty_period") or 0
        inventory = request.form.get("inventory") or 0

        result = conn.execute(text("""
        INSERT INTO products (title, description, vendor_id, warranty_period, price, inventory)
        VALUES (:title, :description, :vendor_id, :warranty_period, :price, :inventory)
        """), {
            "title": title,
            "description": description,
            "vendor_id": vendor_id,
            "warranty_period": int(warranty),
            "price": float(price),
            "inventory": int(inventory)
        })

        conn.commit()

        product_id = result.lastrowid

        image = request.files.get("image")

        if image and image.filename != "":
            filename = secure_filename(image.filename)
            unique_name = f"{product_id}_{filename}"

            filepath = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
            image.save(filepath)

            db_path = f"/static/images/products/{unique_name}"

            conn.execute(text("""
            INSERT INTO product_images (product_id, image_url)
            VALUES (:product_id, :image_url)
            """), {"product_id": product_id, "image_url": db_path})

            conn.commit()

            return redirect("/account")

    return render_template("vendor/create_product.html")

@app.route("/inbox")
def inbox():
    user = get_current_user()

    conversations = conn.execute(text("""
        SELECT 
            u.id,
            u.username,
            v.shop_name,
            m.message,
            m.created_at
        FROM users u
        JOIN (
            SELECT 
                CASE 
                    WHEN sender_id = :user_id THEN receiver_id
                    ELSE sender_id
                END AS other_user_id,
                MAX(created_at) as last_time
            FROM chat_messages
            WHERE sender_id = :user_id OR receiver_id = :user_id
            GROUP BY other_user_id
        ) latest ON u.id = latest.other_user_id
        JOIN chat_messages m 
            ON (
                (m.sender_id = :user_id AND m.receiver_id = u.id)
                OR
                (m.sender_id = u.id AND m.receiver_id = :user_id)
            )
            AND m.created_at = latest.last_time
        LEFT JOIN vendors v ON u.id = v.user_id
        ORDER BY m.created_at DESC
    """), {"user_id": user.id}).fetchall()

    return render_template(
        "inbox.html",
        conversations=conversations,
        now=datetime.now()
    )

#chat route
@app.route("/chat/<int:user_id>")
def chat(user_id):
    current_user = get_current_user()

    messages = conn.execute(text("""
        SELECT *
        FROM chat_messages
        WHERE 
            (sender_id = :me AND receiver_id = :them)
            OR
            (sender_id = :them AND receiver_id = :me)
        ORDER BY created_at ASC
    """), {
        "me": current_user.id,
        "them": user_id
    }).fetchall()

    other_user = conn.execute(text("""
        SELECT 
            u.username,
            u.first_name,
            u.last_name,
            u.role,
            v.shop_name
        FROM users u
        LEFT JOIN vendors v ON u.id = v.user_id
        WHERE u.id = :id
    """), {"id": user_id}).fetchone()

    return render_template(
        "chat.html",
        messages=messages,
        other_user_id=user_id,
        other_user=other_user,
        now=datetime.now()
    )

#send message
@app.route("/send_message", methods=["POST"])
def send_message():
    user = get_current_user()

    receiver_id = request.form["receiver_id"]
    message = request.form.get("message") or None
    image = request.files.get("image")

    image_url = None

    if image and image.filename:
        filename = f"{uuid.uuid4().hex}_{secure_filename(image.filename)}"

        upload_folder = "static/uploads"
        os.makedirs(upload_folder, exist_ok=True)

        filepath = os.path.join(upload_folder, filename)
        image.save(filepath)

        image_url = f"/static/uploads/{filename}"

    conn.execute(text("""
        INSERT INTO chat_messages (sender_id, receiver_id, message, image_url)
        VALUES (:sender, :receiver, :message, :image_url)
    """), {
        "sender": user.id,
        "receiver": receiver_id,
        "message": message,
        "image_url": image_url
    })

    conn.commit()

    return redirect(f"/chat/{receiver_id}")

@app.route("/vendor/delete-product", methods=["POST"])
def delete_product():
    user = get_current_user()

    if not user or user.role != "vendor":
        return redirect("/")

    product_id = request.form["product_id"]

    conn.execute(text("""
    DELETE FROM product_images WHERE product_id = :pid
    """), {"pid": product_id})

    conn.execute(text("""
    DELETE FROM product_variants WHERE product_id = :pid
    """), {"pid": product_id})

    conn.execute(text("""
    DELETE FROM products
    WHERE id = :pid
    AND vendor_id = (
        SELECT id FROM vendors WHERE user_id = :uid
    )
    """), {
        "pid": product_id,
        "uid": user.id
    })

    conn.commit()
    return redirect("/vendor/shop")

@app.route("/vendor/product/<int:product_id>/variants", methods=["GET","POST"])
def manage_variants(product_id):
    user = get_current_user()
    if not user or user.role != "vendor":
        return redirect("/")

    if request.method == "POST":
        conn.execute(text("""
        INSERT INTO product_variants (product_id, color, size, stock)
        VALUES (:pid, :color, :size, :stock)
        """), {
            "pid": product_id,
            "color": request.form["color"],
            "size": request.form["size"],
            "stock": request.form["stock"]
        })
        conn.commit()

    variants = conn.execute(text("""
    SELECT * FROM product_variants WHERE product_id = :pid
    """), {"pid": product_id}).fetchall()

    return render_template("vendor/variants.html", variants=variants, product_id=product_id)

@app.route("/vendor/edit-product/<int:product_id>", methods=["GET","POST"])
def edit_product(product_id):
    user = get_current_user()

    if not user or user.role != "vendor":
        return redirect(url_for("home"))

    product = conn.execute(text("""
    SELECT p.*
    FROM products p
    JOIN vendors v ON p.vendor_id = v.id
    WHERE p.id = :pid AND v.user_id = :uid
    """), {"pid": product_id, "uid": user.id}).fetchone()

    if not product:
        return "Unauthorized"

    if request.method == "POST":
        conn.execute(text("""
        UPDATE products SET title=:title, description=:description,
        price=:price, warranty_period=:warranty, inventory=:inventory
        WHERE id=:pid
        """), {
            "title": request.form.get("title"),
            "description": request.form.get("description"),
            "price": float(request.form.get("price") or 0),
            "warranty": int(request.form.get("warranty_period") or 0),
            "inventory": int(request.form.get("inventory") or 0),
            "pid": product_id
        })

        conn.commit()
        return redirect("/vendor/shop")

    return render_template("vendor/edit_product.html", product=product)

@app.route("/vendor/add-discount/<int:product_id>", methods=["GET","POST"])
def add_discount(product_id):
    user = get_current_user()

    if not user or user.role != "vendor":
        return redirect(url_for("home"))

    product = conn.execute(text("""
    SELECT p.*
    FROM products p
    JOIN vendors v ON p.vendor_id = v.id
    WHERE p.id = :pid AND v.user_id = :uid
    """), {"pid": product_id, "uid": user.id}).fetchone()

    if not product:
        return "Unauthorized"

    if request.method == "POST":

        new_price = float(request.form.get("new_price"))

        conn.execute(text("""
        INSERT INTO discounts (product_id, old_price, new_price, start_time, end_time)
        VALUES (:pid, :old, :new, NOW(), NULL)
        """), {
            "pid": product_id,
            "old": product.price,
            "new": new_price
        })

        conn.commit()
        return redirect("/vendor/shop")

    return render_template("vendor/discount.html", product=product)

if __name__ == "__main__":
    app.run(debug=True)