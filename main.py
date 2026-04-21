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
    return result.fetchone()

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
    return render_template("index.html")

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
        return redirect(url_for("home"))

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

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))



















































































if __name__ == "__main__":
    app.run(debug=True)

