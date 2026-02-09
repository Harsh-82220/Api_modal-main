# ✅ 1️⃣ IMPORTS
from flask import Flask, request, render_template
import pickle
import sqlite3
from flask import redirect, session



# ✅ 2️⃣ CREATE FLASK APP
app = Flask(__name__)

app.secret_key = "supersecretkey"


# ✅ 3️⃣ LOAD MODEL
model = pickle.load(open("model.pkl", "rb"))


# ✅ 4️⃣ DATABASE CREATE FUNCTION
def init_db():

    conn = sqlite3.connect('house_price.db')
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        area REAL,
        bedrooms INTEGER,
        age INTEGER,
        predicted_price REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

    cursor.execute("SELECT * FROM admin")

    if not cursor.fetchall():
        cursor.execute("""
    INSERT INTO admin (username, password)
    VALUES ('admin', 'admin123')
    """)


    conn.commit()
    conn.close()


# ✅ 5️⃣ CALL DATABASE FUNCTION
init_db()


# ✅ HOME ROUTE
@app.route('/')
def home():
    return render_template("index.html")


# ✅ PREDICT ROUTE
@app.route('/predict', methods=['POST'])
def predict():

    area = float(request.form['area'])
    bedrooms = int(request.form['bedrooms'])
    age = int(request.form['age'])

    prediction = model.predict([[area, bedrooms, age]])[0]

    # ⭐ SAVE DATA INTO SQLITE
    conn = sqlite3.connect('house_price.db')
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO predictions (area, bedrooms, age, predicted_price)
    VALUES (?, ?, ?, ?)
    """, (area, bedrooms, age, float(prediction)))

    conn.commit()
    conn.close()

    return render_template(
        "index.html",
        prediction_text=f"₹{prediction:,.0f}"
    )


# ✅ VIEW DATA ROUTE
@app.route('/view-data')
def view_data():

    conn = sqlite3.connect('house_price.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM predictions")
    data = cursor.fetchall()

    conn.close()

    return render_template("data.html", data=data)


@app.route('/admin', methods=['GET','POST'])
def admin_login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('house_price.db')
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM admin 
        WHERE username=? AND password=?
        """, (username, password))

        admin = cursor.fetchone()
        conn.close()

        if admin:
            session['admin'] = username
            return redirect('/dashboard')
        else:
            return render_template("login.html", error="Invalid Credentials")

    return render_template("login.html")


@app.route('/dashboard')
def dashboard():

    if 'admin' not in session:
        return redirect('/admin')

    conn = sqlite3.connect('house_price.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM predictions")
    data = cursor.fetchall()
    conn.close()

    return render_template("data.html", data=data)


@app.route('/delete/<int:id>')
def delete(id):

    if 'admin' not in session:
        return redirect('/admin')

    conn = sqlite3.connect('house_price.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM predictions WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/dashboard')




# ✅ 7️⃣ RUN APP
if __name__ == "__main__":
    app.run(debug=True)
