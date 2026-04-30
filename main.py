from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"

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
    return user and user.role in ["vendor", "customer"]

def is_customer(user):
    return user and user.role in ["customer", "vendor"]

@app.context_processor
def inject_user():
    return dict(current_user=get_current_user())

@app.route("/")
def home():

    products = conn.execute(text("""
    SELECT * FROM products
    """)).fetchall()

    sponsored = conn.execute(text("""
    SELECT * FROM products
    LIMIT 3
    """)).fetchall()

    discounted = conn.execute(text("""
    SELECT p.* FROM products p
    JOIN discounts d ON p.id = d.product_id
    """)).fetchall()

    return render_template("index.html", products=products, sponsored=sponsored, discounted=discounted)

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
    LIMIT 1
    """), {"id":product_id}).fetchone()

    return render_template("item_template.html",product=product)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        query = text("""
            INSERT INTO users (first_name, last_name, email, username, password, role)
            VALUES (:first_name, :last_name, :email, :username, :password, :role)
        """)

        conn.execute(query, {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "username": username,
            "password": generate_password_hash(password),
            "role": role
        })

        conn.commit()

        if role == "vendor":
            id = conn.execute(text("""
                SELECT id FROM users WHERE username = :username
            """), {"username": username}).fetchone()[0]

            conn.execute(text("""
                INSERT INTO vendors (user_id)
                VALUES (:id)
            """), {"id": id})


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
        """), {
            "username": username
        }).fetchone()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["role"] = user.role

            return redirect(url_for("home"))

        return render_template("login.html", error="Invalid Login")

    return render_template("login.html")

#Log out
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
    total=0
    for i in cart_items:
        total+=(i.price*i.quantity)
    return total

# Cart
@app.route("/cart")
def cart():
    if 'user_id' not in session:
        return redirect('/login')
    
    if session["role"] != "customer": 
        return redirect('/home')
    
    user_id=session["user_id"]
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
    print("cart items:",cart_items)
    return render_template("cart.html",cart_items=cart_items,cart_Total=cart_Total(user_id))

@app.route("/update_cart_quantity", methods=['POST'])
def update_cart_quantity():
    item_id = request.form['id']
    quantity = request.form['quantity']

    conn.execute(text("""
    UPDATE cart_items SET quantity = :quantity WHERE id = :item_id
    """), {"item_id": item_id, "quantity": quantity})    
    conn.commit()

    return redirect('/cart')

@app.route("/remove_cart_item", methods=['POST'])
def remove_cart_item():
    item_id = request.form['id']

    conn.execute(text("""
    DELETE FROM cart_items WHERE id = :item_id
    """), {"item_id": item_id})    
    conn.commit()

    return redirect('/cart')

# Add to Cart
@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    if "user_id" not in session:
        return redirect(url_for('login'))

    user_id = session["user_id"]
    product_variant_id = int(request.form["product_variant_id"])
    quantity = int(request.form.get("quantity", 1))

    # Get or Create Cart
    cart = conn.execute(text("""
    SELECT id FROM carts WHERE user_id = :user_id
    """), {"user_id":user_id}).fetchone()

    if not cart:
        conn.execute(text("""
        INSERT INTO carts (user_id)
        VALUES (:user_id)
        """), {"user_id":user_id})
        conn.commit()

        cart = conn.execute(text("""
        SELECT id FROM carts WHERE user_id = :user_id
        """), {"user_id":user_id}).fetchone()

    cart_id = cart[0]

    # Checks if item already exists
    item = conn.execute(text("""
    SELECT id, quantity FROM cart_items
    WHERE cart_id = :cart_id AND product_variant_id = :product_id
    """), {
        "cart_id":cart_id,
        "product_id":product_variant_id
    }).fetchone()

    if item:
        conn.execute(text("""
        UPDATE cart_items
        SET quantity = quantity + :quantity
        WHERE id = :id
        """), {
            "quantity":quantity,
            "id":item[0]
        })
    else:
        conn.execute(text("""
        INSERT INTO cart_items (cart_id, product_variant_id, quantity)
        VALUES (:cart_id, :product_id, :quantity)
        """), {
            "cart_id":cart_id,
            "product_id":product_variant_id,
            "quantity":quantity
        })

    conn.commit()

    return redirect(request.referrer)

#Account page
@app.route("/account")
def account():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    return render_template("account.html", user=user)

#Orders page
@app.route("/orders")
def orders():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    orders = conn.execute(text("""
        SELECT * FROM orders
        WHERE user_id = :id
        ORDER BY order_date DESC
    """), {"id": user.id}).fetchall()

    return render_template("orders.html", orders=orders)













































































if __name__ == "__main__":
    app.run(debug=True)

