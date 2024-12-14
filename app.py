from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = "A1b2C3d4E5!@#F6g7H8"  # Replace with your secure key

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'PushpaRaj2207',
    'database': 'NGOHUB'
}

@app.route('/test-db-connection')
def test_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            conn_status = "Connected to MySQL database NGOHUB successfully"
        else:
            conn_status = "Failed to connect to the database"
        conn.close()
    except mysql.connector.Error as err:
        conn_status = f"Error: {err}"
    return conn_status  # Display connection status directly on the page


# Home Page Route
@app.route('/')
def home():
    return render_template('home.html')

# About Us Page Route
@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

# Services Page Route
@app.route('/services')
def services():
    return render_template('services.html')

# Services Form Page Route
@app.route('/servicesform', methods=['GET', 'POST'])
def servicesform():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        return redirect(url_for('servicety'))
    return render_template('servicesform.html')

@app.route('/upload', methods=['POST'])
def upload():
    # Logic to handle the uploaded data
    return redirect(url_for('servicety'))  # Redirect to servicety.html

# Services Thank You Page Route
@app.route('/servicety')
def servicety():
    return render_template('servicety.html')

# Donate Page Route
@app.route('/donate')
def donate():
    return render_template('donate.html')

# Donate Form Page Route
@app.route('/donate-form', methods=['GET', 'POST'])
def donate_form():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        item_description = request.form.get('item_description')
        address = request.form.get('address')
        email = request.form.get('email')
        phone = request.form.get('phone')
        image_file = request.files.get('image_file')

        # Save image to static/uploads folder
        if image_file:
            image_file_path = f'static/uploads/{image_file.filename}'
            image_file.save(image_file_path)

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO donations (full_name, item_description, address, email, phone, image_file_path) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (full_name, item_description, address, email, phone, image_file_path)
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash("Donation submitted successfully!", "success")
        except Exception as e:
            flash("An error occurred while submitting the donation.", "danger")
            print(e)  # Log the error for debugging

        return redirect(url_for('donatety'))
    return render_template('donate-form.html')


# Donate Thank You Page Route
@app.route('/donatety')
def donatety():
    return render_template('donatety.html')

# Signup Page Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        return redirect(url_for('register'))
    return render_template('signup.html')

# Register Page Route
@app.route('/register')
def register():
    return render_template('register.html')

# Login Page Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        return redirect(url_for('register'))
    return render_template('login.html')

# Admin Dashboard Route
@app.route('/admin')
def admin_dashboard():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT full_name, email, phone, item_description, image_file_path FROM donations")
        donations = cursor.fetchall()
        cursor.close()
        conn.close()

        # Prepare data for the template
        donation_data = [{
            'name': donation[0],
            'email': donation[1],
            'phone': donation[2],
            'item_description': donation[3],
            'image_path': donation[4]
        } for donation in donations]

        return render_template('admin.html', donations=donation_data)
    except Exception as e:
        flash("An error occurred while retrieving donation data.", "danger")
        print(e)  # Log the error for debugging
        return render_template('admin.html', donations=[])

if __name__ == '__main__':
    app.run(debug=True)

