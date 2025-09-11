import streamlit as st
import re
import sqlite3
import hashlib
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Capital Compass - Registration",
    page_icon="🧭",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Apply dark theme with custom CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .stTextInput>div>div>input, .stTextInput>div>div>input:focus {
        background-color: #262730;
        color: white;
        border-color: #4F8BF9;
    }
    .main-header {
        font-size: 3rem;
        color: #4F8BF9;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #4F8BF9;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #00cc00;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    .error-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #ff4d4d;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #262730;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4F8BF9;
        margin: 1rem 0;
    }
    .password-feedback {
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    .stProgress > div > div > div > div {
        background-color: #4F8BF9;
    }
    .database-section {
        background-color: #1E1E1E;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #FF4B4B;
    }
</style>
""", unsafe_allow_html=True)

# Database setup with multiple tables
def init_database():
    conn = sqlite3.connect('capital_compass.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_verified INTEGER DEFAULT 0,
            verification_token TEXT
        )
    ''')
    
    # User profiles table
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            first_name TEXT,
            last_name TEXT,
            date_of_birth DATE,
            phone_number TEXT,
            country TEXT,
            risk_tolerance TEXT CHECK(risk_tolerance IN ('low', 'medium', 'high')),
            investment_goals TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # Accounts table
    c.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            account_type TEXT CHECK(account_type IN ('checking', 'savings', 'investment', 'retirement')),
            account_number TEXT UNIQUE NOT NULL,
            balance DECIMAL(15, 2) DEFAULT 0.00,
            currency TEXT DEFAULT 'USD',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # Transactions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            transaction_type TEXT CHECK(transaction_type IN ('deposit', 'withdrawal', 'transfer', 'dividend', 'fee')),
            amount DECIMAL(15, 2) NOT NULL,
            description TEXT,
            category TEXT,
            transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'completed',
            FOREIGN KEY (account_id) REFERENCES accounts (id) ON DELETE CASCADE
        )
    ''')
    
    # Investments table
    c.execute('''
        CREATE TABLE IF NOT EXISTS investments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            symbol TEXT NOT NULL,
            name TEXT NOT NULL,
            quantity DECIMAL(15, 6) NOT NULL,
            purchase_price DECIMAL(15, 2) NOT NULL,
            current_price DECIMAL(15, 2),
            purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sector TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # Create indexes for better performance
    c.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_transactions_account_id ON transactions(account_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_investments_user_id ON investments(user_id)')
    
    conn.commit()
    return conn

# Password hashing function
def hash_password(password):
    salt = "capital_compass_salt_2023"  # In production, use a unique salt per user
    return hashlib.sha256((password + salt).encode()).hexdigest()

# Check if username or email already exists
def user_exists(conn, username, email):
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email))
    return c.fetchone() is not None

# Save user to database
def save_user(conn, username, email, password):
    password_hash = hash_password(password)
    c = conn.cursor()
    
    # Generate a verification token
    verification_token = hashlib.sha256(f"{username}{email}{datetime.now()}".encode()).hexdigest()
    
    c.execute('INSERT INTO users (username, email, password_hash, verification_token) VALUES (?, ?, ?, ?)',
              (username, email, password_hash, verification_token))
    
    user_id = c.lastrowid
    
    # Create a default account for the user
    account_number = f"CC{user_id:08d}"
    c.execute('INSERT INTO accounts (user_id, account_type, account_number) VALUES (?, ?, ?)',
              (user_id, 'checking', account_number))
    
    conn.commit()
    return user_id, account_number

# Display database info
def display_database_info(conn):
    c = conn.cursor()
    
    # Get table counts
    c.execute("SELECT COUNT(*) FROM users")
    user_count = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM accounts")
    account_count = c.fetchone()[0]
    
    st.markdown('<div class="database-section">', unsafe_allow_html=True)
    st.write("### Database Information")
    st.write(f"**Total Users:** {user_count}")
    st.write(f"**Total Accounts:** {account_count}")
    
    if user_count > 0:
        st.write("### Recent Registrations")
        c.execute("SELECT id, username, email, created_at FROM users ORDER BY created_at DESC LIMIT 5")
        recent_users = c.fetchall()
        
        for user in recent_users:
            st.write(f"User #{user[0]}: {user[1]} ({user[2]}) - {user[3]}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# App header
st.markdown('<h1 class="main-header">Capital Compass</h1>', unsafe_allow_html=True)
st.markdown('<h2 class="sub-header">Navigate Your Financial Future</h2>', unsafe_allow_html=True)

# Initialize database
conn = init_database()

# Information section
with st.expander("Why Create an Account?", expanded=True):
    st.markdown("""
    <div class="info-box">
    <p>Join <strong>Capital Compass</strong> to access exclusive features:</p>
    <ul>
        <li>📊 Personalized investment portfolio tracking</li>
        <li>📈 Real-time market data and analytics</li>
        <li>🎯 AI-powered financial recommendations</li>
        <li>🔔 Custom alerts for market movements</li>
        <li>📱 Sync across all your devices</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# Registration form
with st.form("registration_form"):
    st.write("### Create Your Account")
    
    # User inputs
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Username", placeholder="Choose a unique username")
    with col2:
        email = st.text_input("Email Address", placeholder="Your email address")
    
    col3, col4 = st.columns(2)
    with col3:
        password = st.text_input("Password", type="password", placeholder="Create a strong password")
    with col4:
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
    
    agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
    
    # Password strength indicator
    if password:
        strength = 0
        feedback = []
        
        # Check password criteria
        if len(password) >= 8:
            strength += 1
        else:
            feedback.append("❌ At least 8 characters")
            
        if re.search(r"[A-Z]", password):
            strength += 1
        else:
            feedback.append("❌ At least one uppercase letter")
            
        if re.search(r"[a-z]", password):
            strength += 1
        else:
            feedback.append("❌ At least one lowercase letter")
            
        if re.search(r"[0-9]", password):
            strength += 1
        else:
            feedback.append("❌ At least one number")
            
        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            strength += 1
        else:
            feedback.append("❌ At least one special character")
        
        # Display strength bar and feedback
        st.markdown("**Password Strength**")
        st.progress(strength/5)
        
        if strength < 5:
            for item in feedback:
                st.markdown(f'<div class="password-feedback">{item}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="password-feedback">✅ Strong password!</div>', unsafe_allow_html=True)
    
    # Submit button
    submitted = st.form_submit_button("Create Account", use_container_width=True)

# Form validation and processing
if submitted:
    errors = []
    
    # Validate inputs
    if not username:
        errors.append("Username is required")
    elif len(username) < 3:
        errors.append("Username must be at least 3 characters")
    elif not re.match(r"^[a-zA-Z0-9_]+$", username):
        errors.append("Username can only contain letters, numbers, and underscores")
        
    if not email:
        errors.append("Email is required")
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        errors.append("Please enter a valid email address")
        
    if not password:
        errors.append("Password is required")
    elif len(password) < 8:
        errors.append("Password must be at least 8 characters")
    elif password != confirm_password:
        errors.append("Passwords do not match")
        
    if not agree_terms:
        errors.append("You must agree to the Terms of Service and Privacy Policy")
    
    # Check if user already exists
    if user_exists(conn, username, email):
        errors.append("Username or email already exists")
    
    # Display errors or success
    if errors:
        for error in errors:
            st.markdown(f'<div class="error-message">{error}</div>', unsafe_allow_html=True)
    else:
        # Simulate account creation process
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for percent_complete in range(100):
            time.sleep(0.01)
            progress_bar.progress(percent_complete + 1)
            status_text.text(f"Creating account... {percent_complete+1}%")
        
        status_text.empty()
        progress_bar.empty()
        
        # Save user to database
        try:
            user_id, account_number = save_user(conn, username, email, password)
            st.markdown('<div class="success-message">✅ Account created successfully!</div>', unsafe_allow_html=True)
            
            # Display user info
            st.write("### Welcome to Capital Compass!")
            st.write(f"**User ID:** {user_id}")
            st.write(f"**Username:** {username}")
            st.write(f"**Email:** {email}")
            st.write(f"**Account Number:** {account_number}")
            st.write("**Account Created:**", datetime.now().strftime("%Y-%m-%d %H:%M"))
            
            st.info("A verification email has been sent to your email address. Please verify to access all features.")
            
        except Exception as e:
            st.markdown(f'<div class="error-message">Error creating account: {str(e)}</div>', unsafe_allow_html=True)

# Display database information
display_database_info(conn)

# Close database connection
conn.close()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "© 2023 Capital Compass. All rights reserved. | "
    "<a href='#' style='color: #4F8BF9;'>Terms of Service</a> | "
    "<a href='#' style='color: #4F8BF9;'>Privacy Policy</a>"
    "</div>", 
    unsafe_allow_html=True
)
