from flask import Flask, render_template, request, redirect, session
import sqlite3
import bcrypt

app = Flask(__name__)
app.secret_key = "secretkey"

# ---------- Database ----------
conn = sqlite3.connect("blog.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password BLOB
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    content TEXT
)
""")

conn.commit()
conn.close()

# ---------- Register ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]

        hashed = bcrypt.hashpw(
            request.form["password"].encode(),
            bcrypt.gensalt()
        )

        conn = sqlite3.connect("blog.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register.html")

# ---------- Login ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("blog.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )

        user = cursor.fetchone()

        conn.close()

        if user and bcrypt.checkpw(
            password.encode(),
            user[2]
        ):
            session["user"] = username
            return redirect("/dashboard")

    return render_template("login.html")

# ---------- Dashboard ----------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("blog.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        posts=posts
    )

# ---------- Add Post ----------
@app.route("/add", methods=["POST"])
def add_post():
    if "user" not in session:
        return redirect("/")

    title = request.form["title"]
    content = request.form["content"]

    conn = sqlite3.connect("blog.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO posts (title, content) VALUES (?, ?)",
        (title, content)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")

# ---------- Delete Post ----------
@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("blog.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM posts WHERE id=?",
        (post_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")

# ---------- Logout ----------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

# ---------- Run ----------
if __name__ == "__main__":
    app.run(debug=True)
