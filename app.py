from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from functools import wraps
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

MECHANIC_SPECIALIZATIONS = [
    'Tractor',
    'Harvester',
    'Pump',
    'Sprayer',
    'Tiller',
    'General Farm Machinery'
]

MECHANIC_REQUEST_STATUSES = ['Pending', 'Accepted', 'Completed']

# Serve assets folder
@app.route('/assets/<path:filename>')
def assets(filename):
    return send_from_directory('assets', filename)

# Serve uploads folder
@app.route('/static/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('static/uploads', filename)

# Database configuration
DATABASE = 'agrorent.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with users and listings tables"""
    conn = get_db()
    
    # Users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Listings table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            owner_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            contact_method TEXT NOT NULL,
            category TEXT NOT NULL,
            equipment_name TEXT NOT NULL,
            brand TEXT NOT NULL,
            year INTEGER,
            condition TEXT NOT NULL,
            power_spec TEXT,
            state TEXT NOT NULL,
            district TEXT NOT NULL,
            village_city TEXT NOT NULL,
            pincode TEXT NOT NULL,
            landmark TEXT,
            service_radius TEXT NOT NULL,
            pricing_type TEXT NOT NULL,
            price REAL NOT NULL,
            min_duration TEXT,
            available_from DATE NOT NULL,
            available_till DATE,
            transport_included TEXT NOT NULL,
            transport_charge REAL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            rules TEXT,
            main_image TEXT,
            additional_images TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Rentals table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS rentals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            listing_id INTEGER NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            days INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (listing_id) REFERENCES listings(id)
        )
    ''')

    # Mechanics table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS mechanics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            experience_years INTEGER,
            specialization TEXT NOT NULL,
            service_locations TEXT NOT NULL,
            base_charge REAL NOT NULL,
            description TEXT,
            is_available INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Mechanic service requests table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS mechanic_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mechanic_id INTEGER NOT NULL,
            farmer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            location TEXT NOT NULL,
            issue_description TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (mechanic_id) REFERENCES mechanics(id)
        )
    ''')
    
    # Add phone column if it doesn't exist (for existing databases)
    try:
        cursor = conn.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'phone' not in columns:
            conn.execute('ALTER TABLE users ADD COLUMN phone TEXT')
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Add default listings if database is empty
def add_default_listings():
    """Add sample listings if database is empty"""
    conn = get_db()
    existing_listings = conn.execute('SELECT COUNT(*) as count FROM listings').fetchone()
    existing_users = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()
    
    # Only add default listings if listings table is empty and at least one user exists
    if existing_listings['count'] == 0 and existing_users['count'] > 0:
        # Get first user ID
        first_user = conn.execute('SELECT id FROM users LIMIT 1').fetchone()
        user_id = first_user['id'] if first_user else 1
        # Sample listings data
        sample_listings = [
            {
                'user_id': user_id,
                'owner_name': 'Rajesh Kumar',
                'phone': '+91 9876543210',
                'email': 'rajesh@example.com',
                'contact_method': 'WhatsApp',
                'category': 'Tractor',
                'equipment_name': 'Mahindra 575 DI',
                'brand': 'Mahindra',
                'year': 2020,
                'condition': 'Good',
                'power_spec': '65 HP',
                'state': 'Maharashtra',
                'district': 'Pune',
                'village_city': 'Baramati',
                'pincode': '413102',
                'landmark': 'Near Bus Stand',
                'service_radius': 'within 25 km',
                'pricing_type': 'Per day',
                'price': 2500.0,
                'min_duration': '1 day',
                'available_from': '2024-01-01',
                'available_till': None,
                'transport_included': 'Yes',
                'transport_charge': None,
                'title': '65 HP Mahindra Tractor with Trolley',
                'description': 'Well-maintained Mahindra 575 DI tractor available for rent. Comes with trolley. Perfect for farming operations. Regular servicing done. Diesel by renter.',
                'rules': 'Diesel by renter. Operator must be provided. Advance payment required.',
                'main_image': None,
                'additional_images': None
            },
            {
                'user_id': user_id,
                'owner_name': 'Priya Sharma',
                'phone': '+91 9876543211',
                'email': 'priya@example.com',
                'contact_method': 'Call',
                'category': 'Harvester',
                'equipment_name': 'John Deere S685',
                'brand': 'John Deere',
                'year': 2019,
                'condition': 'Good',
                'power_spec': '450 HP',
                'state': 'Maharashtra',
                'district': 'Nashik',
                'village_city': 'Nashik',
                'pincode': '422001',
                'landmark': 'Near Agricultural College',
                'service_radius': 'within 30 km',
                'pricing_type': 'Per acre',
                'price': 3500.0,
                'min_duration': '5 acres',
                'available_from': '2024-01-01',
                'available_till': '2024-12-31',
                'transport_included': 'No',
                'transport_charge': 5000.0,
                'title': 'John Deere Combine Harvester',
                'description': 'High-capacity combine harvester suitable for wheat, rice, and soybean harvesting. Excellent condition with all attachments.',
                'rules': 'Minimum 5 acres. Fuel by renter. Experienced operator available at extra cost.',
                'main_image': None,
                'additional_images': None
            },
            {
                'user_id': user_id,
                'owner_name': 'Amit Patel',
                'phone': '+91 9876543212',
                'email': 'amit@example.com',
                'contact_method': 'WhatsApp',
                'category': 'Sprayer',
                'equipment_name': 'Mahindra 475 DI with Boom Sprayer',
                'brand': 'Mahindra',
                'year': 2021,
                'condition': 'New',
                'power_spec': '47 HP',
                'state': 'Gujarat',
                'district': 'Ahmedabad',
                'village_city': 'Ahmedabad',
                'pincode': '380001',
                'landmark': 'Near Highway',
                'service_radius': 'only local village',
                'pricing_type': 'Per hour',
                'price': 800.0,
                'min_duration': '4 hours',
                'available_from': '2024-01-01',
                'available_till': None,
                'transport_included': 'Yes',
                'transport_charge': None,
                'title': '47 HP Tractor with Boom Sprayer',
                'description': 'New Mahindra 475 DI tractor with advanced boom sprayer. Perfect for pesticide and fertilizer application. Very efficient and easy to operate.',
                'rules': 'Minimum 4 hours. Chemical/fertilizer by renter. Proper cleaning required after use.',
                'main_image': None,
                'additional_images': None
            },
            {
                'user_id': user_id,
                'owner_name': 'Sunita Devi',
                'phone': '+91 9876543213',
                'email': 'sunita@example.com',
                'contact_method': 'SMS',
                'category': 'Pump',
                'equipment_name': 'Kirloskar 5 HP Submersible Pump',
                'brand': 'Kirloskar',
                'year': 2022,
                'condition': 'Good',
                'power_spec': '5 HP',
                'state': 'Punjab',
                'district': 'Ludhiana',
                'village_city': 'Ludhiana',
                'pincode': '141001',
                'landmark': 'Near Canal',
                'service_radius': 'within 20 km',
                'pricing_type': 'Per day',
                'price': 1200.0,
                'min_duration': '1 day',
                'available_from': '2024-01-01',
                'available_till': None,
                'transport_included': 'No',
                'transport_charge': 500.0,
                'title': '5 HP Submersible Water Pump',
                'description': 'High-quality Kirloskar submersible pump for irrigation. Excellent water output. Well maintained and serviced regularly.',
                'rules': 'Electricity connection required. Proper installation needed. Deposit required.',
                'main_image': None,
                'additional_images': None
            },
            {
                'user_id': user_id,
                'owner_name': 'Vikram Singh',
                'phone': '+91 9876543214',
                'email': 'vikram@example.com',
                'contact_method': 'Call',
                'category': 'Tiller',
                'equipment_name': 'Maschio Gaspardo Rotavator',
                'brand': 'Maschio Gaspardo',
                'year': 2020,
                'condition': 'Good',
                'power_spec': '35 HP',
                'state': 'Haryana',
                'district': 'Karnal',
                'village_city': 'Karnal',
                'pincode': '132001',
                'landmark': 'Near Market',
                'service_radius': 'within 15 km',
                'pricing_type': 'Per acre',
                'price': 2000.0,
                'min_duration': '2 acres',
                'available_from': '2024-01-01',
                'available_till': None,
                'transport_included': 'Yes',
                'transport_charge': None,
                'title': 'Rotavator for Land Preparation',
                'description': 'Efficient rotavator for land preparation and tilling. Cuts through hard soil easily. Perfect for preparing seedbeds.',
                'rules': 'Minimum 2 acres. Tractor required (can be arranged separately).',
                'main_image': None,
                'additional_images': None
            },
            {
                'user_id': user_id,
                'owner_name': 'Lakshmi Nair',
                'phone': '+91 9876543215',
                'email': 'lakshmi@example.com',
                'contact_method': 'WhatsApp',
                'category': 'Seed Drill',
                'equipment_name': 'Mahindra Seed Drill 9 Row',
                'brand': 'Mahindra',
                'year': 2021,
                'condition': 'Good',
                'power_spec': '45 HP',
                'state': 'Kerala',
                'district': 'Thrissur',
                'village_city': 'Thrissur',
                'pincode': '680001',
                'landmark': 'Near Agricultural Office',
                'service_radius': 'within 25 km',
                'pricing_type': 'Per acre',
                'price': 1800.0,
                'min_duration': '1 acre',
                'available_from': '2024-01-01',
                'available_till': '2024-06-30',
                'transport_included': 'No',
                'transport_charge': 800.0,
                'title': '9 Row Seed Drill for Precision Sowing',
                'description': 'Modern seed drill for precise seed placement. Suitable for various crops. Well maintained and calibrated.',
                'rules': 'Seeds by renter. Proper calibration required. Advance booking preferred.',
                'main_image': None,
                'additional_images': None
            }
        ]
        
        # Insert sample listings
        for listing in sample_listings:
            conn.execute('''
                INSERT INTO listings (
                    user_id, owner_name, phone, email, contact_method,
                    category, equipment_name, brand, year, condition, power_spec,
                    state, district, village_city, pincode, landmark, service_radius,
                    pricing_type, price, min_duration, available_from, available_till,
                    transport_included, transport_charge, title, description, rules,
                    main_image, additional_images
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                listing['user_id'], listing['owner_name'], listing['phone'], listing['email'], listing['contact_method'],
                listing['category'], listing['equipment_name'], listing['brand'], listing['year'], listing['condition'], listing['power_spec'],
                listing['state'], listing['district'], listing['village_city'], listing['pincode'], listing['landmark'], listing['service_radius'],
                listing['pricing_type'], listing['price'], listing['min_duration'], listing['available_from'], listing['available_till'],
                listing['transport_included'], listing['transport_charge'], listing['title'], listing['description'], listing['rules'],
                listing['main_image'], listing['additional_images']
            ))
        
        conn.commit()
    conn.close()

# Add default listings on startup (only if empty)
add_default_listings()

def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('signin'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if request.method == 'POST':
        name = request.form.get('fullname', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '').strip()
        
        # Validation
        if not name or not email or not password:
            flash('Name, email, and password are required.', 'danger')
            return render_template('signup.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('signup.html')
        
        # Basic email validation
        if '@' not in email or '.' not in email.split('@')[1]:
            flash('Please enter a valid email address.', 'danger')
            return render_template('signup.html')
        
        # Check if user already exists
        conn = get_db()
        existing_user = conn.execute(
            'SELECT id FROM users WHERE email = ?', (email,)
        ).fetchone()
        
        if existing_user:
            conn.close()
            flash('Email already registered. Please sign in instead.', 'danger')
            return render_template('signup.html')
        
        # Create new user
        hashed_password = generate_password_hash(password)
        try:
            conn.execute(
                'INSERT INTO users (name, email, phone, password) VALUES (?, ?, ?, ?)',
                (name, email, phone if phone else None, hashed_password)
            )
            conn.commit()
            conn.close()
            flash('Account created successfully! Please sign in.', 'success')
            return redirect(url_for('signin'))
        except Exception as e:
            conn.close()
            flash('An error occurred. Please try again.', 'danger')
            return render_template('signup.html')
    
    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        
        # Validation
        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('signin.html')
        
        # Check user credentials
        conn = get_db()
        user = conn.execute(
            'SELECT * FROM users WHERE email = ?', (email,)
        ).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            # Set session
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')
            return render_template('signin.html')
    
    return render_template('signin.html')

@app.route('/signout')
def signout():
    """User logout"""
    session.clear()
    flash('You have been signed out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/rentdashboard')
@login_required
def rentdashboard():
    """Renting dashboard page"""
    return render_template('rentdashboard.html')

@app.route('/api/my_rentals')
@login_required
def get_my_rentals():
    """Get current user's rentals"""
    user_id = session['user_id']
    conn = get_db()
    rentals = conn.execute('''
        SELECT r.*, l.title, l.category, l.equipment_name, l.brand, l.main_image,
               l.price, l.pricing_type, l.state, l.district, l.village_city,
               l.owner_name, l.phone, l.contact_method
        FROM rentals r
        JOIN listings l ON r.listing_id = l.id
        WHERE r.user_id = ?
        ORDER BY r.start_date DESC
    ''', (user_id,)).fetchall()
    conn.close()
    
    rentals_data = []
    today = datetime.now().date()
    
    for rental in rentals:
        end_date = datetime.strptime(rental['end_date'], '%Y-%m-%d').date()
        is_expired = end_date < today
        days_remaining = (end_date - today).days if not is_expired else 0
        
        rentals_data.append({
            'id': rental['id'],
            'listing_id': rental['listing_id'],
            'title': rental['title'],
            'category': rental['category'],
            'equipment_name': rental['equipment_name'],
            'brand': rental['brand'],
            'main_image': rental['main_image'],
            'start_date': rental['start_date'],
            'end_date': rental['end_date'],
            'days': rental['days'],
            'total_amount': rental['total_amount'],
            'status': 'Expired' if is_expired else rental['status'],
            'days_remaining': days_remaining,
            'is_expired': is_expired,
            'price': rental['price'],
            'pricing_type': rental['pricing_type'],
            'location': f"{rental['village_city']}, {rental['district']}, {rental['state']}",
            'owner_name': rental['owner_name'],
            'phone': rental['phone'],
            'contact_method': rental['contact_method'],
            'created_at': rental['created_at']
        })
    
    return jsonify(rentals_data)

@app.route('/listdashboard')
@login_required
def listdashboard():
    """Listing dashboard page"""
    return render_template('listdashboard.html')

@app.route('/listing')
@login_required
def listing():
    """Create listing page"""
    # Check if editing mode
    editing_data = None
    editing_id = None
    if 'editing_listing_data' in session and 'editing_listing_id' in session:
        # Verify ownership before allowing edit
        user_id = session['user_id']
        session_editing_id = session.get('editing_listing_id')
        
        if session_editing_id:
            conn = get_db()
            listing = conn.execute('SELECT * FROM listings WHERE id = ? AND user_id = ?', (session_editing_id, user_id)).fetchone()
            conn.close()
            
            if listing:
                # Only allow editing if user owns the listing
                editing_data = session.pop('editing_listing_data', None)
                editing_id = session.pop('editing_listing_id', None)
            else:
                # Clear invalid session data
                session.pop('editing_listing_data', None)
                session.pop('editing_listing_id', None)
                flash('You do not have permission to edit this listing.', 'danger')
    
    return render_template('listing.html', editing_data=editing_data, editing_id=editing_id)

@app.route('/create_listing', methods=['POST'])
@login_required
def create_listing():
    """Handle listing form submission (create or update)"""
    try:
        user_id = session['user_id']
        editing_id = request.form.get('editing_id')
        is_edit = editing_id and editing_id.strip()
        
        # Get form data
        owner_name = request.form.get('owner_name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        contact_method = request.form.get('contact_method', '').strip()
        category = request.form.get('category', '').strip()
        equipment_name = request.form.get('equipment_name', '').strip()
        brand = request.form.get('brand', '').strip()
        year = request.form.get('year')
        condition = request.form.get('condition', '').strip()
        power_spec = request.form.get('power_spec', '').strip()
        state = request.form.get('state', '').strip()
        district = request.form.get('district', '').strip()
        village_city = request.form.get('village_city', '').strip()
        pincode = request.form.get('pincode', '').strip()
        landmark = request.form.get('landmark', '').strip()
        service_radius = request.form.get('service_radius', '').strip()
        pricing_type = request.form.get('pricing_type', '').strip()
        price = request.form.get('price', '0')
        min_duration = request.form.get('min_duration', '').strip()
        available_from = request.form.get('available_from', '').strip()
        available_till = request.form.get('available_till', '').strip()
        transport_included = request.form.get('transport_included', '').strip()
        transport_charge = request.form.get('transport_charge', '0')
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        rules = request.form.get('rules', '').strip()
        
        conn = get_db()
        
        # If editing, verify ownership
        if is_edit:
            try:
                editing_id_int = int(editing_id)
            except (ValueError, TypeError):
                conn.close()
                return jsonify({
                    'success': False,
                    'message': 'Invalid listing ID'
                }), 400
            
            listing = conn.execute('SELECT * FROM listings WHERE id = ? AND user_id = ?', (editing_id_int, user_id)).fetchone()
            if not listing:
                conn.close()
                return jsonify({
                    'success': False,
                    'message': 'Listing not found or you do not have permission to edit it'
                }), 403
        
        # Handle file uploads
        upload_folder = os.path.join('static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        main_image_path = None
        if 'main_image' in request.files:
            main_image = request.files['main_image']
            if main_image.filename:
                # Delete old image if editing
                if is_edit and listing['main_image']:
                    try:
                        old_path = os.path.join('static', listing['main_image'])
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    except:
                        pass
                
                filename = f"main_{user_id}_{int(os.urandom(4).hex(), 16)}.{main_image.filename.rsplit('.', 1)[1].lower()}"
                filepath = os.path.join(upload_folder, filename)
                main_image.save(filepath)
                main_image_path = f"uploads/{filename}"
            elif is_edit:
                # Keep existing image if no new one uploaded
                main_image_path = listing['main_image']
        
        additional_images_paths = []
        if 'additional_images' in request.files:
            files = request.files.getlist('additional_images')
            if files and any(f.filename for f in files):
                # Delete old additional images if editing
                if is_edit and listing['additional_images']:
                    try:
                        for img_path in listing['additional_images'].split(','):
                            old_path = os.path.join('static', img_path.strip())
                            if os.path.exists(old_path):
                                os.remove(old_path)
                    except:
                        pass
                
                for idx, file in enumerate(files):
                    if file.filename:
                        filename = f"add_{user_id}_{int(os.urandom(4).hex(), 16)}_{idx}.{file.filename.rsplit('.', 1)[1].lower()}"
                        filepath = os.path.join(upload_folder, filename)
                        file.save(filepath)
                        additional_images_paths.append(f"uploads/{filename}")
            elif is_edit and listing['additional_images']:
                # Keep existing images if no new ones uploaded
                additional_images_paths = listing['additional_images'].split(',')
        
        # Save to database
        if is_edit:
            # Update existing listing
            conn.execute('''
                UPDATE listings SET
                    owner_name = ?, phone = ?, email = ?, contact_method = ?,
                    category = ?, equipment_name = ?, brand = ?, year = ?, condition = ?, power_spec = ?,
                    state = ?, district = ?, village_city = ?, pincode = ?, landmark = ?, service_radius = ?,
                    pricing_type = ?, price = ?, min_duration = ?, available_from = ?, available_till = ?,
                    transport_included = ?, transport_charge = ?, title = ?, description = ?, rules = ?,
                    main_image = ?, additional_images = ?
                WHERE id = ? AND user_id = ?
            ''', (
                owner_name, phone, email if email else None, contact_method,
                category, equipment_name, brand, int(year) if year else None, condition, power_spec if power_spec else None,
                state, district, village_city, pincode, landmark if landmark else None, service_radius,
                pricing_type, float(price), min_duration if min_duration else None, available_from, available_till if available_till else None,
                transport_included, float(transport_charge) if transport_charge else None, title, description, rules if rules else None,
                main_image_path, ','.join(additional_images_paths) if additional_images_paths else None,
                editing_id_int, user_id
            ))
            message = 'Your listing has been updated successfully!'
        else:
            # Insert new listing
            conn.execute('''
                INSERT INTO listings (
                    user_id, owner_name, phone, email, contact_method,
                    category, equipment_name, brand, year, condition, power_spec,
                    state, district, village_city, pincode, landmark, service_radius,
                    pricing_type, price, min_duration, available_from, available_till,
                    transport_included, transport_charge, title, description, rules,
                    main_image, additional_images
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, owner_name, phone, email if email else None, contact_method,
                category, equipment_name, brand, int(year) if year else None, condition, power_spec if power_spec else None,
                state, district, village_city, pincode, landmark if landmark else None, service_radius,
                pricing_type, float(price), min_duration if min_duration else None, available_from, available_till if available_till else None,
                transport_included, float(transport_charge) if transport_charge else None, title, description, rules if rules else None,
                main_image_path, ','.join(additional_images_paths) if additional_images_paths else None
            ))
            message = 'Your equipment has been listed successfully!'
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': message
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error saving listing: {str(e)}'
        }), 500

@app.route('/renting')
@login_required
def renting():
    """Renting page with equipment listings"""
    return render_template('renting.html')

@app.route('/api/listings')
@login_required
def get_listings():
    """Get all available listings"""
    conn = get_db()
    # Get all listings, including those available in the future
    # Filter out only those that have passed their available_till date
    listings = conn.execute('''
        SELECT * FROM listings 
        WHERE (available_till IS NULL OR available_till >= date('now'))
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    listings_data = []
    for listing in listings:
        listings_data.append({
            'id': listing['id'],
            'title': listing['title'],
            'category': listing['category'],
            'equipment_name': listing['equipment_name'],
            'brand': listing['brand'],
            'price': listing['price'],
            'pricing_type': listing['pricing_type'],
            'state': listing['state'],
            'district': listing['district'],
            'village_city': listing['village_city'],
            'main_image': listing['main_image'],
            'condition': listing['condition'],
            'power_spec': listing['power_spec'],
            'service_radius': listing['service_radius'],
            'transport_included': listing['transport_included'],
            'transport_charge': listing['transport_charge'],
            'available_from': listing['available_from'],
            'available_till': listing['available_till']
        })
    
    return jsonify(listings_data)

@app.route('/api/listing/<int:listing_id>')
@login_required
def get_listing_details(listing_id):
    """Get detailed information about a specific listing"""
    conn = get_db()
    listing = conn.execute('SELECT * FROM listings WHERE id = ?', (listing_id,)).fetchone()
    conn.close()
    
    if not listing:
        return jsonify({'error': 'Listing not found'}), 404
    
    listing_data = dict(listing)
    # Parse additional images
    if listing_data['additional_images']:
        listing_data['additional_images'] = listing_data['additional_images'].split(',')
    else:
        listing_data['additional_images'] = []
    
    return jsonify(listing_data)

@app.route('/rent_equipment', methods=['POST'])
@login_required
def rent_equipment():
    """Handle equipment rental request"""
    try:
        user_id = session['user_id']
        listing_id = request.form.get('listing_id')
        days = int(request.form.get('days', 0))
        start_date = request.form.get('start_date')
        
        if not listing_id or not days or not start_date:
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400
        
        # Get listing details to calculate total amount
        conn = get_db()
        listing = conn.execute('SELECT * FROM listings WHERE id = ?', (listing_id,)).fetchone()
        
        if not listing:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Listing not found'
            }), 404
        
        # Calculate total amount
        price = listing['price']
        pricing_type = listing['pricing_type']
        transport_charge = listing['transport_charge'] if listing['transport_included'] == 'No' else 0
        
        if pricing_type == 'Per day':
            total_amount = price * days
        elif pricing_type == 'Per hour':
            total_amount = price * days * 8  # Assuming 8 hours per day
        elif pricing_type == 'Per acre':
            total_amount = price * days  # Assuming days = acres
        else:
            total_amount = price  # Per season
        
        total_amount += transport_charge
        
        # Calculate end date
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = start + timedelta(days=days)
        end_date = end.strftime('%Y-%m-%d')
        
        # Create rental record
        conn.execute('''
            INSERT INTO rentals (user_id, listing_id, start_date, end_date, days, total_amount, status)
            VALUES (?, ?, ?, ?, ?, ?, 'Active')
        ''', (user_id, listing_id, start_date, end_date, days, total_amount))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Rental request submitted successfully!'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error processing rental: {str(e)}'
        }), 500

@app.route('/api/my_listings')
@login_required
def get_my_listings():
    """Get current user's listings"""
    user_id = session['user_id']
    conn = get_db()
    listings = conn.execute('''
        SELECT * FROM listings 
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (user_id,)).fetchall()
    conn.close()
    
    listings_data = []
    for listing in listings:
        listings_data.append({
            'id': listing['id'],
            'title': listing['title'],
            'category': listing['category'],
            'equipment_name': listing['equipment_name'],
            'brand': listing['brand'],
            'price': listing['price'],
            'pricing_type': listing['pricing_type'],
            'state': listing['state'],
            'district': listing['district'],
            'village_city': listing['village_city'],
            'main_image': listing['main_image'],
            'condition': listing['condition'],
            'power_spec': listing['power_spec'],
            'available_from': listing['available_from'],
            'available_till': listing['available_till'],
            'created_at': listing['created_at']
        })
    
    return jsonify(listings_data)

@app.route('/delete_listing/<int:listing_id>', methods=['DELETE', 'POST'])
@login_required
def delete_listing(listing_id):
    """Delete a listing"""
    try:
        user_id = session['user_id']
        conn = get_db()
        
        # Verify ownership
        listing = conn.execute('SELECT * FROM listings WHERE id = ? AND user_id = ?', (listing_id, user_id)).fetchone()
        
        if not listing:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Listing not found or you do not have permission to delete it'
            }), 404
        
        # Delete associated images if they exist
        if listing['main_image']:
            try:
                image_path = os.path.join('static', listing['main_image'])
                if os.path.exists(image_path):
                    os.remove(image_path)
            except:
                pass  # Continue even if image deletion fails
        
        if listing['additional_images']:
            try:
                for img_path in listing['additional_images'].split(','):
                    image_path = os.path.join('static', img_path.strip())
                    if os.path.exists(image_path):
                        os.remove(image_path)
            except:
                pass  # Continue even if image deletion fails
        
        # Delete listing from database
        conn.execute('DELETE FROM listings WHERE id = ? AND user_id = ?', (listing_id, user_id))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Listing deleted successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error deleting listing: {str(e)}'
        }), 500

@app.route('/edit_listing/<int:listing_id>')
@login_required
def edit_listing(listing_id):
    """Edit listing page - redirects to listing.html with edit mode"""
    user_id = session['user_id']
    conn = get_db()
    listing = conn.execute('SELECT * FROM listings WHERE id = ? AND user_id = ?', (listing_id, user_id)).fetchone()
    conn.close()
    
    if not listing:
        flash('Listing not found or you do not have permission to edit it', 'danger')
        return redirect(url_for('listdashboard'))
    
    # Store listing data in session for pre-filling form
    session['editing_listing_id'] = listing_id
    session['editing_listing_data'] = dict(listing)
    
    return redirect(url_for('listing'))


def get_mechanic_for_user(user_id):
    """Fetch mechanic profile associated with the logged-in user"""
    conn = get_db()
    mechanic = conn.execute(
        'SELECT * FROM mechanics WHERE user_id = ? ORDER BY created_at DESC LIMIT 1',
        (user_id,)
    ).fetchone()
    conn.close()
    return mechanic


@app.route('/mechanics/register', methods=['GET', 'POST'])
def mechanic_register():
    """Mechanic registration page"""
    form_data = {}
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        experience_years = request.form.get('experience_years', '').strip()
        specialization = request.form.get('specialization', '').strip()
        service_locations = request.form.get('service_locations', '').strip()
        base_charge = request.form.get('base_charge', '').strip()
        description = request.form.get('description', '').strip()
        is_available = 1 if request.form.get('is_available') == 'on' else 0
        user_id = session.get('user_id')

        form_data = {
            'full_name': full_name,
            'phone': phone,
            'email': email,
            'experience_years': experience_years,
            'specialization': specialization,
            'service_locations': service_locations,
            'base_charge': base_charge,
            'description': description,
            'is_available': 'checked' if is_available else ''
        }

        errors = []

        if not full_name:
            errors.append('Full name is required.')
        if not phone:
            errors.append('Phone or WhatsApp number is required.')
        if specialization not in MECHANIC_SPECIALIZATIONS:
            errors.append('Please select a valid specialization.')
        if not service_locations:
            errors.append('Serviceable locations are required.')
        if not base_charge:
            errors.append('Base visit charge is required.')

        if base_charge:
            try:
                float(base_charge)
            except ValueError:
                errors.append('Base visit charge must be a number.')

        if experience_years:
            try:
                int(experience_years)
            except ValueError:
                errors.append('Experience must be a whole number.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template(
                'mechanic_register.html',
                specializations=MECHANIC_SPECIALIZATIONS,
                form_data=form_data
            )

        conn = None
        try:
            conn = get_db()
            conn.execute('''
                INSERT INTO mechanics (
                    user_id, full_name, phone, email, experience_years,
                    specialization, service_locations, base_charge, description, is_available
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                full_name,
                phone,
                email if email else None,
                int(experience_years) if experience_years else None,
                specialization,
                service_locations,
                float(base_charge),
                description if description else None,
                is_available
            ))
            conn.commit()
            conn.close()
            flash('Thanks for joining the Agro-Doctor network! Your profile is live.', 'success')
            return redirect(url_for('mechanics_list'))
        except Exception as e:
            if conn:
                conn.close()
            flash('Unable to save your profile right now. Please try again.', 'danger')

    return render_template(
        'mechanic_register.html',
        specializations=MECHANIC_SPECIALIZATIONS,
        form_data=form_data
    )


@app.route('/mechanics')
def mechanics_list():
    """Mechanics listing and filter page"""
    search = request.args.get('q', '').strip()
    specialization = request.args.get('specialization', '').strip()
    available_only = request.args.get('available_only', '').strip().lower() in ('true', '1', 'on')

    query = 'SELECT * FROM mechanics WHERE 1=1'
    params = []

    if search:
        query += ' AND (LOWER(service_locations) LIKE ? OR LOWER(full_name) LIKE ?)'
        like_term = f'%{search.lower()}%'
        params.extend([like_term, like_term])

    if specialization and specialization in MECHANIC_SPECIALIZATIONS:
        query += ' AND specialization = ?'
        params.append(specialization)

    if available_only:
        query += ' AND is_available = 1'

    query += ' ORDER BY created_at DESC'

    conn = get_db()
    mechanics = conn.execute(query, params).fetchall()
    conn.close()

    return render_template(
        'mechanics_list.html',
        mechanics=mechanics,
        filters={
            'search': search,
            'specialization': specialization,
            'available_only': available_only
        },
        specializations=MECHANIC_SPECIALIZATIONS
    )


@app.route('/mechanics/<int:mechanic_id>/request', methods=['POST'])
def mechanic_service_request(mechanic_id):
    """Create a new service request for a mechanic"""
    farmer_name = request.form.get('farmer_name', '').strip()
    phone = request.form.get('phone', '').strip()
    location = request.form.get('location', '').strip()
    issue_description = request.form.get('issue_description', '').strip()

    if not farmer_name or not phone or not location or not issue_description:
        return jsonify({'success': False, 'message': 'All fields are required.'}), 400

    conn = get_db()
    try:
        mechanic = conn.execute('SELECT id FROM mechanics WHERE id = ?', (mechanic_id,)).fetchone()

        if not mechanic:
            return jsonify({'success': False, 'message': 'Mechanic not found.'}), 404

        conn.execute('''
            INSERT INTO mechanic_requests (mechanic_id, farmer_name, phone, location, issue_description)
            VALUES (?, ?, ?, ?, ?)
        ''', (mechanic_id, farmer_name, phone, location, issue_description))
        conn.commit()
    finally:
        conn.close()

    return jsonify({'success': True, 'message': 'Service request sent to the mechanic.'}), 200


@app.route('/mechanic/dashboard')
@login_required
def mechanic_dashboard():
    """Dashboard for mechanics to view and manage requests"""
    user_id = session['user_id']
    conn = get_db()
    mechanic = conn.execute(
        'SELECT * FROM mechanics WHERE user_id = ? ORDER BY created_at DESC LIMIT 1',
        (user_id,)
    ).fetchone()

    requests_data = []
    if mechanic:
        requests_data = conn.execute('''
            SELECT * FROM mechanic_requests
            WHERE mechanic_id = ?
            ORDER BY created_at DESC
        ''', (mechanic['id'],)).fetchall()

    conn.close()

    return render_template(
        'mechanic_dashboard.html',
        mechanic=mechanic,
        service_requests=requests_data,
        request_statuses=MECHANIC_REQUEST_STATUSES
    )


@app.route('/api/mechanic/availability', methods=['POST'])
@login_required
def update_mechanic_availability():
    """Toggle mechanic availability status"""
    user_id = session['user_id']
    payload = request.get_json(silent=True) or {}
    form_value = request.form.get('is_available')
    raw_value = payload.get('is_available') if payload else form_value

    is_available = 1 if str(raw_value).lower() in ('true', '1', 'on') else 0

    conn = get_db()
    mechanic = conn.execute(
        'SELECT id FROM mechanics WHERE user_id = ? ORDER BY created_at DESC LIMIT 1',
        (user_id,)
    ).fetchone()

    if not mechanic:
        conn.close()
        return jsonify({'success': False, 'message': 'Mechanic profile not found.'}), 404

    conn.execute('''
        UPDATE mechanics
        SET is_available = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (is_available, mechanic['id']))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'is_available': bool(is_available)})


@app.route('/api/mechanic/requests/<int:request_id>/status', methods=['POST'])
@login_required
def update_mechanic_request_status(request_id):
    """Update the status of a mechanic service request"""
    payload = request.get_json(silent=True) or {}
    new_status = payload.get('status') or request.form.get('status')

    if new_status not in MECHANIC_REQUEST_STATUSES:
        return jsonify({'success': False, 'message': 'Invalid status selected.'}), 400

    user_id = session['user_id']
    conn = get_db()
    mechanic = conn.execute(
        'SELECT id FROM mechanics WHERE user_id = ? ORDER BY created_at DESC LIMIT 1',
        (user_id,)
    ).fetchone()

    if not mechanic:
        conn.close()
        return jsonify({'success': False, 'message': 'Mechanic profile not found.'}), 404

    request_row = conn.execute(
        'SELECT id FROM mechanic_requests WHERE id = ? AND mechanic_id = ?',
        (request_id, mechanic['id'])
    ).fetchone()

    if not request_row:
        conn.close()
        return jsonify({'success': False, 'message': 'Request not found.'}), 404

    conn.execute('''
        UPDATE mechanic_requests
        SET status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (new_status, request_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'status': new_status})


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)

