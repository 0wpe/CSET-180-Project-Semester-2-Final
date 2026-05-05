from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from decimal import Decimal
from datetime import datetime
import random
import os
import uuid

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = "static/images/products"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

engine = create_engine("mysql://root:cset155@localhost/ecommerce", echo=True)
conn = engine.connect()


def get_current_user():
    if "user_id" not in session:
        return None

    return conn.execute(text("""
        SELECT id, first_name, last_name, email, role
        FROM users
        WHERE id = :id
    """), {"id": session["user_id"]}).mappings().fetchone()


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
    q = request.args.get("q", "")

    if q:
        products = conn.execute(text("""
            SELECT p.*, pi.image_url, pv.id AS variant_id
            FROM products p
            LEFT JOIN product_images pi ON p.id = pi.product_id
            JOIN product_variants pv ON pv.product_id = p.id
            WHERE p.title LIKE :q
        """), {"q": f"%{q}%"}).fetchall()
    else:
        products = conn.execute(text("""
            SELECT p.*, pi.image_url
            FROM products p
            LEFT JOIN product_images pi ON p.id = pi.product_id
        """)).fetchall()

    return render_template("search.html", products=products, query=q)


@app.route("/search/<int:product_id>")
def product_page(product_id):
    product = conn.execute(text("""
        SELECT p.*, pi.image_url
        FROM products p
        LEFT JOIN product_images pi ON p.id = pi.product_id
        WHERE p.id = :id
    """), {"id": product_id}).fetchone()

    return render_template("item_template.html", product=product)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        conn.execute(text("""
            INSERT INTO users (first_name,last_name,email,username,password,role)
            VALUES (:fn,:ln,:em,:un,:pw,:role)
        """), {
            "fn": request.form["first_name"],
            "ln": request.form["last_name"],
            "em": request.form["email"],
            "un": request.form["username"],
            "pw": generate_password_hash(request.form["password"]),
            "role": request.form["role"]
        })
        conn.commit()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = conn.execute(text("""
            SELECT * FROM users WHERE username=:u
        """), {"u": request.form["username"]}).fetchone()

        if user and check_password_hash(user.password, request.form["password"]):
            session["user_id"] = user.id
            session["role"] = user.role
            return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


def cart_total(user_id):
    items = conn.execute(text("""
        SELECT pv.price, ci.quantity
        FROM cart_items ci
        JOIN product_variants pv ON ci.product_variant_id = pv.id
        WHERE ci.cart_id = (SELECT id FROM carts WHERE user_id=:uid)
    """), {"uid": user_id}).fetchall()

    return sum(i.price * i.quantity for i in items)


@app.route("/cart")
def cart():
    if "user_id" not in session:
        return redirect("/login")

    items = conn.execute(text("""
        SELECT ci.id, ci.quantity, pv.*, p.*
        FROM cart_items ci
        JOIN product_variants pv ON ci.product_variant_id = pv.id
        JOIN products p ON pv.product_id = p.id
        WHERE ci.cart_id = (SELECT id FROM carts WHERE user_id=:uid)
    """), {"uid": session["user_id"]}).fetchall()

    subtotal = cart_total(session["user_id"])
    tax = subtotal * Decimal("0.06")

    return render_template("cart.html",
        cart_items=items,
        subtotal=f"{subtotal:.2f}",
        tax=f"{tax:.2f}",
        total=f"{subtotal + tax:.2f}",
        user_id=session["user_id"]
    )


@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    uid = session["user_id"]
    vid = request.form["product_variant_id"]
    qty = int(request.form.get("quantity", 1))

    cart = conn.execute(text("SELECT id FROM carts WHERE user_id=:u"), {"u": uid}).fetchone()

    if not cart:
        conn.execute(text("INSERT INTO carts (user_id) VALUES (:u)"), {"u": uid})
        conn.commit()
        cart = conn.execute(text("SELECT id FROM carts WHERE user_id=:u"), {"u": uid}).fetchone()

    cart_id = cart[0]

    item = conn.execute(text("""
        SELECT id, quantity FROM cart_items
        WHERE cart_id=:c AND product_variant_id=:v
    """), {"c": cart_id, "v": vid}).fetchone()

    if item:
        conn.execute(text("""
            UPDATE cart_items SET quantity = quantity + :q WHERE id=:id
        """), {"q": qty, "id": item.id})
    else:
        conn.execute(text("""
            INSERT INTO cart_items (cart_id, product_variant_id, quantity)
            VALUES (:c,:v,:q)
        """), {"c": cart_id, "v": vid, "q": qty})

    conn.commit()
    return redirect(request.referrer)


@app.route("/remove_cart_item", methods=["POST"])
def remove_cart_item():
    conn.execute(text("DELETE FROM cart_items WHERE id=:id"),
        {"id": request.form["id"]})
    conn.commit()
    return redirect("/cart")


@app.route("/checkout", methods=["POST"])
def checkout():
    uid = request.form["id"]

    items = conn.execute(text("""
        SELECT * FROM cart_items
        WHERE cart_id = (SELECT id FROM carts WHERE user_id=:uid)
    """), {"uid": uid}).fetchall()

    subtotal = cart_total(uid)
    shipping = subtotal * random.randrange(1, 150) * Decimal("0.01")
    tax = (subtotal + shipping) * Decimal("0.06")

    return render_template("checkout.html",
        cart_items=items,
        subtotal=subtotal,
        shipping=shipping,
        tax=tax,
        total=subtotal + shipping + tax,
        user_id=uid
    )


@app.route("/purchase", methods=["POST"])
def purchase():
    uid = request.form["id"]

    conn.execute(text("""
        DELETE FROM cart_items
        WHERE cart_id = (SELECT id FROM carts WHERE user_id=:uid)
    """), {"uid": uid})

    conn.commit()
    return render_template("index.html", thank=True)


@app.route("/vendor/shop")
def vendor_shop():
    user = get_current_user()

    vendor = conn.execute(text("""
        SELECT id FROM vendors WHERE user_id=:uid
    """), {"uid": user.id}).fetchone()

    products = conn.execute(text("""
        SELECT p.*, pi.image_url
        FROM products p
        LEFT JOIN product_images pi ON p.id = pi.product_id
        WHERE p.vendor_id=:vid
    """), {"vid": vendor.id}).fetchall()

    return render_template("vendor/shop.html", products=products)


@app.route("/vendor/create-product", methods=["GET", "POST"])
def create_product():
    user = get_current_user()

    if request.method == "POST":
        vendor = conn.execute(text("SELECT id FROM vendors WHERE user_id=:u"),
            {"u": user.id}).fetchone()

        res = conn.execute(text("""
            INSERT INTO products (title,description,vendor_id,warranty_period,price,inventory)
            VALUES (:t,:d,:v,:w,:p,:i)
        """), {
            "t": request.form["title"],
            "d": request.form["description"],
            "v": vendor.id,
            "w": request.form.get("warranty_period", 0),
            "p": request.form.get("price", 0),
            "i": request.form.get("inventory", 0)
        })

        conn.commit()
        pid = res.lastrowid

        img = request.files.get("image")
        if img:
            name = f"{pid}_{secure_filename(img.filename)}"
            img.save(os.path.join(app.config["UPLOAD_FOLDER"], name))

            conn.execute(text("""
                INSERT INTO product_images (product_id,image_url)
                VALUES (:p,:u)
            """), {"p": pid, "u": f"/static/images/products/{name}"})

            conn.commit()

        return redirect("/vendor/shop")

    return render_template("vendor/create_product.html")


@app.route("/vendor/edit-product/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    user = get_current_user()

    product = conn.execute(text("""
        SELECT p.* FROM products p
        JOIN vendors v ON p.vendor_id=v.id
        WHERE p.id=:pid AND v.user_id=:uid
    """), {"pid": product_id, "uid": user.id}).fetchone()

    if request.method == "POST":
        conn.execute(text("""
            UPDATE products
            SET title=:t, description=:d, price=:p,
            warranty_period=:w, inventory=:i
            WHERE id=:pid
        """), {
            "t": request.form["title"],
            "d": request.form["description"],
            "p": request.form["price"],
            "w": request.form["warranty_period"],
            "i": request.form["inventory"],
            "pid": product_id
        })
        conn.commit()
        return redirect("/vendor/shop")

    return render_template("vendor/edit_product.html", product=product)


@app.route("/vendor/delete-product", methods=["POST"])
def delete_product():
    pid = request.form["product_id"]

    conn.execute(text("DELETE FROM product_images WHERE product_id=:p"), {"p": pid})
    conn.execute(text("DELETE FROM product_variants WHERE product_id=:p"), {"p": pid})
    conn.execute(text("DELETE FROM discounts WHERE product_id=:p"), {"p": pid})

    conn.execute(text("DELETE FROM products WHERE id=:p"), {"p": pid})

    conn.commit()
    return redirect("/vendor/shop")


@app.route("/vendor/product/<int:product_id>/variants", methods=["GET", "POST"])
def manage_variants(product_id):
    if request.method == "POST":
        conn.execute(text("""
            INSERT INTO product_variants (product_id,color,size,stock)
            VALUES (:p,:c,:s,:st)
        """), {
            "p": product_id,
            "c": request.form["color"],
            "s": request.form["size"],
            "st": request.form["stock"]
        })
        conn.commit()

    variants = conn.execute(text("""
        SELECT * FROM product_variants WHERE product_id=:p
    """), {"p": product_id}).fetchall()

    return render_template("vendor/variants.html", variants=variants, product_id=product_id)


@app.route("/vendor/add-discount/<int:product_id>", methods=["GET", "POST"])
def add_discount(product_id):
    user = get_current_user()

    product = conn.execute(text("""
        SELECT p.* FROM products p
        JOIN vendors v ON p.vendor_id=v.id
        WHERE p.id=:pid AND v.user_id=:uid
    """), {"pid": product_id, "uid": user.id}).fetchone()

    if request.method == "POST":
        new_price = float(request.form["new_price"])

        conn.execute(text("""
            INSERT INTO discounts (product_id,old_price,new_price,start_time)
            VALUES (:p,:o,:n,NOW())
        """), {
            "p": product_id,
            "o": product.price,
            "n": new_price
        })

        conn.commit()
        return redirect("/vendor/shop")

    return render_template("vendor/discount.html", product=product)


@app.route("/inbox")
def inbox():
    user = get_current_user()

    conv = conn.execute(text("""
        SELECT u.id,u.username,m.message,m.created_at
        FROM users u
        JOIN chat_messages m
        ON u.id = m.sender_id OR u.id = m.receiver_id
        WHERE :uid IN (m.sender_id,m.receiver_id)
        ORDER BY m.created_at DESC
    """), {"uid": user.id}).fetchall()

    return render_template("inbox.html", conversations=conv)


@app.route("/chat/<int:user_id>")
def chat(user_id):
    me = get_current_user()

    messages = conn.execute(text("""
        SELECT * FROM chat_messages
        WHERE (sender_id=:me AND receiver_id=:u)
        OR (sender_id=:u AND receiver_id=:me)
        ORDER BY created_at
    """), {"me": me.id, "u": user_id}).fetchall()

    return render_template("chat.html", messages=messages, other_user_id=user_id)


@app.route("/send_message", methods=["POST"])
def send_message():
    user = get_current_user()

    conn.execute(text("""
        INSERT INTO chat_messages (sender_id,receiver_id,message)
        VALUES (:s,:r,:m)
    """), {
        "s": user.id,
        "r": request.form["receiver_id"],
        "m": request.form["message"]
    })

    conn.commit()
    return redirect(f"/chat/{request.form['receiver_id']}")


if __name__ == "__main__":
    app.run(debug=True)