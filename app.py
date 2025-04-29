from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import bcrypt
import json

# Custom JSON encoder for ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key')
app.json_encoder = JSONEncoder

# Session configuration
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
app.config['SESSION_COOKIE_SECURE'] = False  # Changed to False for development
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# MongoDB configuration
try:
    client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
    db = client['finance_tracker']
    # Test the connection
    client.server_info()
    print("✅ MongoDB connection successful!")
except Exception as e:
    print("❌ MongoDB connection failed:", str(e))

# Add test route
@app.route('/test-db')
def test_db():
    try:
        # Try to access the database
        db.list_collections()
        return jsonify({
            "status": "success",
            "message": "MongoDB connection is working!",
            "database": "finance_tracker",
            "collections": list(db.list_collection_names())
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Add this route after the test-db route
@app.route('/check-db')
def check_db():
    try:
        # Get all users and convert ObjectId to string
        users = list(db.users.find({}, {'password': 0}))
        # Convert ObjectId to string for each user
        for user in users:
            user['_id'] = str(user['_id'])
        
        return jsonify({
            "status": "success",
            "database": db.name,
            "collections": db.list_collection_names(),
            "users_count": len(users),
            "users": users
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Flask-Login configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.email = user_data['email']
    
    def get_id(self):
        return str(self.id)
    
    @staticmethod
    def get(user_id):
        try:
            user_data = db.users.find_one({'_id': ObjectId(user_id)})
            if user_data:
                return User(user_data)
            return None
        except:
            return None

@login_manager.user_loader
def load_user(user_id):
    try:
        user_data = db.users.find_one({'_id': ObjectId(user_id)})
        if user_data:
            return User(user_data)
        return None
    except:
        return None

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        print("\n=== Login Attempt ===")
        print(f"Email: {email}")
        
        try:
            # Find user by email
            user = db.users.find_one({'email': email})
            print(f"User found: {user is not None}")
            
            if user:
                print(f"User data: {user}")
                print(f"Stored password hash: {user['password']}")
                
                # Check password
                password_matches = bcrypt.checkpw(
                    password.encode('utf-8'),
                    user['password']
                )
                print(f"Password matches: {password_matches}")
                
                if password_matches:
                    print("✅ Password matches")
                    # Create user object
                    user_obj = User(user)
                    print(f"Created user object with ID: {user_obj.id}")
                    
                    # Login user
                    login_user(user_obj, remember=True)
                    print("✅ User logged in successfully")
                    
                    # Set session as permanent
                    session.permanent = True
                    
                    # Verify login
                    print(f"Current user authenticated: {current_user.is_authenticated}")
                    print(f"Current user ID: {current_user.get_id()}")
                    
                    return redirect(url_for('dashboard'))
                else:
                    print("❌ Password does not match")
                    flash('Invalid email or password')
            else:
                print("❌ User not found")
                flash('Invalid email or password')
                
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            flash('Login failed. Please try again.')
        
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Debug: Print registration attempt and database info
        print("\n=== Registration Attempt ===")
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Database name: {db.name}")
        print(f"Current collections: {db.list_collection_names()}")
        
        try:
            # Check if users collection exists
            if 'users' not in db.list_collection_names():
                print("Creating users collection...")
                db.create_collection('users')
            
            # Check if email exists with more detailed logging
            existing_user = db.users.find_one({'email': email})
            print(f"Existing user check result: {existing_user}")
            
            if existing_user:
                print("❌ Registration failed: Email already exists")
                print(f"Found existing user: {existing_user}")
                flash('Email already registered')
                return redirect(url_for('register'))
            
            # Hash password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Create user document
            user_data = {
                'username': username,
                'email': email,
                'password': hashed_password
            }
            
            # Insert user into database
            print("\nAttempting to insert user...")
            result = db.users.insert_one(user_data)
            print(f"✅ Insert result: {result.inserted_id}")
            
            # Verify the insertion
            print("\nVerifying insertion...")
            inserted_user = db.users.find_one({'_id': result.inserted_id})
            if inserted_user:
                print("✅ User data verified in database")
                print(f"Stored user data: {inserted_user}")
                # Don't print the password hash
                print(f"Username: {inserted_user['username']}")
                print(f"Email: {inserted_user['email']}")
            else:
                print("❌ User data not found after insertion")
            
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
            
        except Exception as e:
            print(f"\n❌ Error during registration: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            flash('Registration failed. Please try again.')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's transactions
    transactions = list(db.transactions.find({'user_id': current_user.id}))
    
    # Convert ObjectId to string for JSON serialization
    for transaction in transactions:
        transaction['_id'] = str(transaction['_id'])
        if 'date' in transaction:
            transaction['date'] = transaction['date'].strftime('%Y-%m-%d')
    
    # Calculate totals
    total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
    total_expenses = sum(t['amount'] for t in transactions if t['type'] == 'expense')
    total_savings = total_income - total_expenses
    
    return render_template('dashboard.html',
                         total_income=total_income,
                         total_expenses=total_expenses,
                         total_savings=total_savings,
                         transactions=transactions)

@app.route('/add_transaction', methods=['POST'])
@login_required
def add_transaction():
    transaction = {
        'user_id': current_user.id,
        'type': request.form.get('type'),
        'amount': float(request.form.get('amount')),
        'category': request.form.get('category'),
        'date': datetime.strptime(request.form.get('date'), '%Y-%m-%d'),
        'notes': request.form.get('notes')
    }
    
    db.transactions.insert_one(transaction)
    flash('Transaction added successfully!')
    return redirect(url_for('dashboard'))

@app.route('/delete_transaction/<transaction_id>')
@login_required
def delete_transaction(transaction_id):
    try:
        # Convert string ID to ObjectId
        result = db.transactions.delete_one({
            '_id': ObjectId(transaction_id),
            'user_id': current_user.id
        })
        
        if result.deleted_count > 0:
            flash('Transaction deleted successfully!')
        else:
            flash('Transaction not found or you do not have permission to delete it.')
            
    except Exception as e:
        print(f"Error deleting transaction: {str(e)}")
        flash('Error deleting transaction. Please try again.')
        
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 