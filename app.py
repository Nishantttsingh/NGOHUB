from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "************"  

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'nishant123',
    'database': 'NGOHUB'
}

# File upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def execute_query(query, params=None, fetch=False):
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch:
            if 'SELECT' in query.upper():
                result = cursor.fetchall()
            else:
                result = cursor.fetchone()
        else:
            conn.commit()
            result = cursor.lastrowid
        
        cursor.close()
        conn.close()
        return result
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        conn.close()
        return None

# ===== BASIC ROUTES =====

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/services')
def services():
    return render_template('services.html')

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
    return redirect(url_for('servicety'))

@app.route('/servicety')
def servicety():
    return render_template('servicety.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        return redirect(url_for('register'))
    return render_template('signup.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        return redirect(url_for('register'))
    return render_template('login.html')

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
    return conn_status

# ===== ENHANCED DONATION ROUTES =====

@app.route('/donate')
def donate():
    return render_template('donate.html')

@app.route('/submit-donation', methods=['POST'])
def submit_donation():
    try:
        data = request.json
        
        # Extract donation data
        full_name = data.get('fullName')
        email = data.get('email')
        phone = data.get('phone')
        item_type = data.get('itemType')
        item_description = data.get('itemDescription')
        quantity = data.get('quantity')
        pickup_address = data.get('pickupAddress')
        contact_info = data.get('contactInfo')
        ngo_id = data.get('ngoId')
        ngo_name = data.get('ngoName')
        timing = data.get('timing')
        
        # Insert into donations table
        result = execute_query(
            """INSERT INTO donations (full_name, email, phone, item_description, 
            address, category, quantity, status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending')""",
            (full_name, email, phone, item_description, pickup_address, 
             item_type, quantity)
        )
        
        if result:
            return jsonify({
                'success': True, 
                'message': 'Donation submitted successfully! It will be reviewed by admin.'
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'Failed to submit donation. Please try again.'
            })
            
    except Exception as e:
        print(f"Error submitting donation: {e}")
        return jsonify({
            'success': False, 
            'message': 'An error occurred while submitting your donation.'
        })

@app.route('/donatety')
def donatety():
    return render_template('donatety.html')

# ===== ENHANCED NGO ROUTES =====

@app.route('/ngo')
def ngo():
    return render_template('ngo.html')

@app.route('/ngo-register', methods=['POST'])
def ngo_register():
    name = request.form.get('ngoName')
    registration_number = request.form.get('registrationNumber')
    contact_person = request.form.get('contactPerson')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')
    mission = request.form.get('mission')
    focus_areas = ','.join(request.form.getlist('focusAreas'))
    
    # Handle file uploads
    documents = request.files.getlist('registrationDocs')
    documents_paths = []
    
    for doc in documents:
        if doc and allowed_file(doc.filename):
            filename = secure_filename(doc.filename)
            docs_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'docs')
            os.makedirs(docs_folder, exist_ok=True)
            filepath = os.path.join(docs_folder, filename)
            doc.save(filepath)
            documents_paths.append(filepath)
    
    documents_path = ','.join(documents_paths) if documents_paths else None
    
    try:
        result = execute_query(
            """INSERT INTO ngos (name, registration_number, contact_person, email, phone, 
            address, mission, focus_areas, documents_path, status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')""",
            (name, registration_number, contact_person, email, phone, address, 
             mission, focus_areas, documents_path)
        )
        
        if result:
            return jsonify({
                'success': True,
                'message': 'NGO registration submitted successfully! It will be reviewed by our admin team.'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'An error occurred while submitting the registration.'
            })
            
    except mysql.connector.IntegrityError:
        return jsonify({
            'success': False,
            'message': 'An NGO with this registration number or email already exists.'
        })
    except Exception as e:
        print(e)
        return jsonify({
            'success': False,
            'message': 'An error occurred while submitting the registration.'
        })

@app.route('/ngo-add-requirement', methods=['POST'])
def ngo_add_requirement():
    title = request.form.get('requirementTitle')
    description = request.form.get('requirementDescription')
    category = request.form.get('requirementCategory')
    quantity = request.form.get('quantity')
    urgency = request.form.get('urgency')
    deadline = request.form.get('deadline')
    specific_requirements = request.form.get('specificRequirements')
    
    # For demo, use NGO ID 1. In real app, get from session
    ngo_id = 1
    
    try:
        result = execute_query(
            """INSERT INTO ngo_requirements (ngo_id, title, description, category, quantity, 
            urgency, deadline, specific_requirements, status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pending')""",
            (ngo_id, title, description, category, quantity, 
             urgency, deadline if deadline else None, specific_requirements)
        )
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Requirement submitted successfully! It will be reviewed by admin.'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'An error occurred while submitting the requirement.'
            })
    except Exception as e:
        print(e)
        return jsonify({
            'success': False,
            'message': 'An error occurred while submitting the requirement.'
        })

# ===== ENHANCED ADMIN ROUTES =====

@app.route('/admin')
def admin_dashboard():
    return render_template('admin.html')

@app.route('/admin-data')
def admin_data():
    try:
        # Get pending NGOs
        pending_ngos = execute_query("SELECT * FROM ngos WHERE status = 'pending'", fetch=True) or []
        
        # Get pending requirements
        pending_requirements = execute_query('''
            SELECT nr.*, n.name as ngo_name 
            FROM ngo_requirements nr 
            JOIN ngos n ON nr.ngo_id = n.id 
            WHERE nr.status = 'pending'
        ''', fetch=True) or []
        
        # Get pending donations
        pending_donations = execute_query("SELECT * FROM donations WHERE status = 'pending'", fetch=True) or []
        
        # Get statistics
        stats = execute_query('''
            SELECT 
                (SELECT COUNT(*) FROM ngos WHERE status='approved') as approved_ngos,
                (SELECT COUNT(*) FROM ngo_requirements WHERE status='approved') as approved_requirements,
                (SELECT COUNT(*) FROM donations WHERE status='approved') as approved_donations,
                (SELECT COUNT(*) FROM donations WHERE status='pending') as pending_donations_count,
                (SELECT COUNT(*) FROM ngos WHERE status='pending') as pending_ngos_count,
                (SELECT COUNT(*) FROM ngo_requirements WHERE status='pending') as pending_requirements_count
        ''', fetch=True)

        return jsonify({
            'pending_ngos': pending_ngos,
            'pending_requirements': pending_requirements,
            'pending_donations': pending_donations,
            'stats': stats[0] if stats else {}
        })
    except Exception as e:
        print(f"Error in admin_data: {e}")
        return jsonify({'error': 'Failed to load admin data'}), 500

# Route to get approved NGOs for donate page
@app.route('/api/approved-ngos')
def get_approved_ngos():
    try:
        approved_ngos = execute_query(
            "SELECT * FROM ngos WHERE status = 'approved'", 
            fetch=True
        ) or []
        return jsonify(approved_ngos)
    except Exception as e:
        print(f"Error fetching approved NGOs: {e}")
        return jsonify([])

# Route to get approved requirements for donate page
@app.route('/api/approved-requirements')
def get_approved_requirements():
    try:
        approved_requirements = execute_query('''
            SELECT nr.*, n.name as ngo_name 
            FROM ngo_requirements nr 
            JOIN ngos n ON nr.ngo_id = n.id 
            WHERE nr.status = 'approved'
        ''', fetch=True) or []
        return jsonify(approved_requirements)
    except Exception as e:
        print(f"Error fetching approved requirements: {e}")
        return jsonify([])

# Admin Approve/Reject NGO Route
@app.route('/admin/ngo/approve/<int:ngo_id>', methods=['POST'])
def admin_approve_ngo(ngo_id):
    try:
        execute_query(
            "UPDATE ngos SET status = 'approved' WHERE id = %s",
            (ngo_id,)
        )
        return jsonify({'success': True, 'message': 'NGO approved successfully!'})
    except Exception as e:
        print(f"Error approving NGO: {e}")
        return jsonify({'success': False, 'message': 'Error approving NGO'}), 500

@app.route('/admin/ngo/reject/<int:ngo_id>', methods=['POST'])
def admin_reject_ngo(ngo_id):
    try:
        execute_query(
            "UPDATE ngos SET status = 'rejected' WHERE id = %s",
            (ngo_id,)
        )
        return jsonify({'success': True, 'message': 'NGO rejected successfully!'})
    except Exception as e:
        print(f"Error rejecting NGO: {e}")
        return jsonify({'success': False, 'message': 'Error rejecting NGO'}), 500

# Admin Approve/Reject Requirement Route
@app.route('/admin/requirement/approve/<int:req_id>', methods=['POST'])
def admin_approve_requirement(req_id):
    try:
        execute_query(
            "UPDATE ngo_requirements SET status = 'approved' WHERE id = %s",
            (req_id,)
        )
        return jsonify({'success': True, 'message': 'Requirement approved successfully!'})
    except Exception as e:
        print(f"Error approving requirement: {e}")
        return jsonify({'success': False, 'message': 'Error approving requirement'}), 500

@app.route('/admin/requirement/reject/<int:req_id>', methods=['POST'])
def admin_reject_requirement(req_id):
    try:
        execute_query(
            "UPDATE ngo_requirements SET status = 'rejected' WHERE id = %s",
            (req_id,)
        )
        return jsonify({'success': True, 'message': 'Requirement rejected successfully!'})
    except Exception as e:
        print(f"Error rejecting requirement: {e}")
        return jsonify({'success': False, 'message': 'Error rejecting requirement'}), 500

# Admin Approve/Reject Donation Route
@app.route('/admin/donation/approve/<int:donation_id>', methods=['POST'])
def admin_approve_donation(donation_id):
    try:
        execute_query(
            "UPDATE donations SET status = 'approved' WHERE id = %s",
            (donation_id,)
        )
        return jsonify({'success': True, 'message': 'Donation approved successfully!'})
    except Exception as e:
        print(f"Error approving donation: {e}")
        return jsonify({'success': False, 'message': 'Error approving donation'}), 500

@app.route('/admin/donation/reject/<int:donation_id>', methods=['POST'])
def admin_reject_donation(donation_id):
    try:
        execute_query(
            "UPDATE donations SET status = 'rejected' WHERE id = %s",
            (donation_id,)
        )
        return jsonify({'success': True, 'message': 'Donation rejected successfully!'})
    except Exception as e:
        print(f"Error rejecting donation: {e}")
        return jsonify({'success': False, 'message': 'Error rejecting donation'}), 500

if __name__ == '__main__':
    app.run(debug=True)