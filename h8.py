import streamlit as st
import re
import sqlite3
import hashlib
import time
from datetime import datetime
import os

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
    .database-info {
        background-color: #1E1E1E;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #FF4B4B;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# Database setup - Using a separate SQLite database file
def init_database():
    # Create a separate database file in a different location
    db_path = "C:/CapitalCompass/capital_compass_users.db"  # Windows path example
    # For cross-platform compatibility, you can use:
    # db_path = os.path.join(os.path.expanduser("~"), "CapitalCompass", "capital_compass_users.db")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
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
            account_status TEXT DEFAULT 'active'
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
            country TEXT DEFAULT 'USA',
            risk_tolerance TEXT CHECK(risk_tolerance IN ('low', 'medium', 'high')),
            investment_experience TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # Create indexes
    c.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
    
    conn.commit()
    return conn, db_path

# Password hashing function
def hash_password(password):
    salt = "capital_compass_salt_2023"
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
    
    try:
        c.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                  (username, email, password_hash))
        user_id = c.lastrowid
        conn.commit()
        return user_id, True
    except sqlite3.IntegrityError:
        return None, False
    except Exception as e:
        return None, False

# App header
st.markdown('<h1 class="main-header">Capital Compass</h1>', unsafe_allow_html=True)
st.markdown('<h2 class="sub-header">Navigate Your Financial Future</h2>', unsafe_allow_html=True)

# Initialize database
try:
    conn, db_path = init_database()
    db_connected = True
except Exception as e:
    st.error(f"Database connection error: {str(e)}")
    db_connected = False
    conn = None
    db_path = "Not available"

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
        <li>💼 Advanced investment tools and calculators</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# Registration form
with st.form("registration_form"):
    st.write("### Create Your Account")
    
    # User inputs
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Username", placeholder="Choose a unique username (min. 3 chars)")
    with col2:
        email = st.text_input("Email Address", placeholder="Your active email address")
    
    col3, col4 = st.columns(2)
    with col3:
        password = st.text_input("Password", type="password", placeholder="Create a strong password")
    with col4:
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
    
    # Additional optional fields
    with st.expander("Additional Information (Optional)"):
        col5, col6 = st.columns(2)
        with col5:
            first_name = st.text_input("First Name")
        with col6:
            last_name = st.text_input("Last Name")
        
        country = st.selectbox("Country", ["USA", "Canada", "UK", "Australia", "Germany", "Other"])
    
    agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy", value=False)
    newsletter = st.checkbox("Subscribe to investment insights newsletter", value=True)
    
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
    
    # Check database connection
    if not db_connected:
        errors.append("Database connection unavailable. Please try again later.")
    
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
    if db_connected and user_exists(conn, username, email):
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
            user_id, success = save_user(conn, username, email, password)
            if success:
                st.markdown('<div class="success-message">✅ Account created successfully!</div>', unsafe_allow_html=True)
                
                # Display success information
                st.write("### Welcome to Capital Compass!")
                st.write(f"**Username:** {username}")
                st.write(f"**Email:** {email}")
                st.write(f"**User ID:** {user_id}")
                st.write("**Registration Date:**", datetime.now().strftime("%Y-%m-%d %H:%M"))
                
                if newsletter:
                    st.info("📧 You've been subscribed to our investment insights newsletter!")
                
                st.success("Your account data has been securely stored in our database.")
                
            else:
                st.markdown('<div class="error-message">Error creating account. Please try again.</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.markdown(f'<div class="error-message">Error creating account: {str(e)}</div>', unsafe_allow_html=True)

# Database information section (only showing the connection details)
with st.expander("Database Connection Information", expanded=False):
    st.markdown("""
    <div class="database-info">
    <h4>📊 Database Connection Details:</h4>
    <p><strong>Database Type:</strong> SQLite</p>
    <p><strong>Database Path:</strong> {}</p>
    <p><strong>Tables:</strong> users, user_profiles</p>
    <p><strong>Status:</strong> {}</p>
    </div>
    """.format(db_path, "Connected" if db_connected else "Disconnected"), unsafe_allow_html=True)
    
    st.info("""
    ℹ️ User data is securely stored in a separate SQL database with hashed passwords.
    The database is located at the path shown above and is not accessible via web interface.
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "© 2023 Capital Compass. All rights reserved. | "
    "<a href='#' style='color: #4F8BF9;'>Terms of Service</a> | "
    "<a href='#' style='color: #4F8BF9;'>Privacy Policy</a> | "
    "<a href='#' style='color: #4F8BF9;'>Security</a>"
    "</div>", 
    unsafe_allow_html=True
)

# Close database connection
if conn:
    conn.close()
