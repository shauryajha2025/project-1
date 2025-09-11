import streamlit as st
import re
import hashlib
import sqlite3
from datetime import datetime
import base64

# Page configuration
st.set_page_config(
    page_title="Capital Compass",
    page_icon="🧭",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Set background image with NYC Manhattan
def set_bg_image():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .main {{
            background-color: rgba(14, 17, 23, 0.95);
            color: #fafafa;
            padding: 2rem;
            border-radius: 10px;
            margin: 2rem auto;
            max-width: 500px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        }}
        .stTextInput>div>div>input {{
            background-color: #262730 !important;
            color: #fafafa !important;
            border: 1px solid #4a4a4a !important;
            border-radius: 4px;
            padding: 0.5rem;
        }}
        .stTextInput>div>div>input:focus {{
            border-color: #6a6a6a !important;
            box-shadow: 0 0 0 1px #6a6a6a;
        }}
        .stTextInput label {{
            color: #fafafa !important;
            font-weight: bold;
        }}
        .stButton>button {{
            background-color: #4a4a4a;
            color: #fafafa;
            border: none;
            padding: 0.75rem 1rem;
            border-radius: 4px;
            transition: all 0.3s ease;
            width: 100%;
            font-weight: bold;
        }}
        .stButton>button:hover {{
            background-color: #5a5a5a;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        .success {{
            color: #4caf50;
            font-weight: bold;
        }}
        .error {{
            color: #f44336;
            font-weight: bold;
        }}
        .header {{
            text-align: center;
            margin-bottom: 2rem;
        }}
        .compass-icon {{
            font-size: 4rem;
            margin-bottom: 1rem;
        }}
        .footer {{
            text-align: center;
            margin-top: 3rem;
            color: #7e7e7e;
            font-size: 0.8rem;
        }}
        .toggle-container {{
            display: flex;
            justify-content: center;
            margin-bottom: 1.5rem;
            background-color: #262730;
            border-radius: 50px;
            padding: 5px;
            width: 80%;
            margin-left: auto;
            margin-right: auto;
        }}
        .toggle-option {{
            padding: 10px 20px;
            border-radius: 50px;
            cursor: pointer;
            width: 50%;
            text-align: center;
            transition: all 0.3s ease;
        }}
        .toggle-active {{
            background-color: #4a4a4a;
            font-weight: bold;
        }}
        .form-container {{
            animation: fadeIn 0.5s ease-in;
            background-color: rgba(38, 39, 48, 0.95);
            padding: 2rem;
            border-radius: 10px;
            margin-top: 1rem;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(-10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .stCheckbox label {{
            color: #fafafa !important;
        }}
        .stCheckbox>div>div {{
            background-color: #262730;
            border: 1px solid #4a4a4a;
        }}
        .stExpander {{
            border: 1px solid #4a4a4a;
            border-radius: 4px;
        }}
        .stExpander>div {{
            background-color: #262730;
        }}
        .stExpander>div>p {{
            color: #fafafa;
            font-weight: bold;
        }}
        </style>
        """, 
        unsafe_allow_html=True
    )

set_bg_image()

# Database setup
def init_db():
    conn = sqlite3.connect('capital_compass.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Password validation
def validate_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter"
    if not re.search(r"[0-9]", password):
        return "Password must contain at least one number"
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        return "Password must contain at least one special character"
    return None

# User registration
def register_user(username, password):
    conn = sqlite3.connect('capital_compass.db')
    c = conn.cursor()
    
    # Check if username already exists
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    if c.fetchone():
        conn.close()
        return "Username already exists"
    
    # Hash password and store user
    password_hash = hash_password(password)
    c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
              (username, password_hash))
    conn.commit()
    conn.close()
    return None

# User authentication
def authenticate_user(username, password):
    conn = sqlite3.connect('capital_compass.db')
    c = conn.cursor()
    
    # Get user by username
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    
    if user and user[2] == hash_password(password):
        return True, "Login successful!"
    else:
        return False, "Invalid username or password"

# Main application
def main():
    # Initialize database
    init_db()
    
    # Header section
    st.markdown('<div class="header">', unsafe_allow_html=True)
    st.markdown('<div class="compass-icon">🧭</div>', unsafe_allow_html=True)
    st.title("Capital Compass")
    st.subheader("Navigate Your Financial Future")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Toggle between login and registration
    st.markdown('<div class="toggle-container">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Create New Account", key="register_btn"):
            st.session_state.form_mode = "register"
    with col2:
        if st.button("Already Registered", key="login_btn"):
            st.session_state.form_mode = "login"
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Initialize form mode in session state
    if "form_mode" not in st.session_state:
        st.session_state.form_mode = "register"
    
    # Highlight active toggle option
    st.markdown(
        f"""
        <style>
        #register_btn {{
            background-color: {"#4a4a4a" if st.session_state.form_mode == "register" else "transparent"};
            color: #fafafa;
            border: none;
            border-radius: 50px;
            font-weight: {"bold" if st.session_state.form_mode == "register" else "normal"};
        }}
        #login_btn {{
            background-color: {"#4a4a4a" if st.session_state.form_mode == "login" else "transparent"};
            color: #fafafa;
            border: none;
            border-radius: 50px;
            font-weight: {"bold" if st.session_state.form_mode == "login" else "normal"};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Display appropriate form based on mode
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    if st.session_state.form_mode == "register":
        with st.form("registration_form"):
            st.markdown("### Create Your Account")
            
            username = st.text_input("Username", placeholder="Enter your username", key="reg_username")
            password = st.text_input("Password", type="password", 
                                    placeholder="Create a strong password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", 
                                            placeholder="Re-enter your password", key="reg_confirm")
            
            # Terms and conditions
            agree = st.checkbox("I agree to the Terms and Conditions", key="reg_agree")
            
            submitted = st.form_submit_button("Register")
            
            if submitted:
                # Validate inputs
                if not username:
                    st.error("Username is required", icon="🚨")
                elif len(username) < 4:
                    st.error("Username must be at least 4 characters long", icon="🚨")
                elif not password:
                    st.error("Password is required", icon="🚨")
                elif password != confirm_password:
                    st.error("Passwords do not match", icon="🚨")
                elif not agree:
                    st.error("You must agree to the Terms and Conditions", icon="🚨")
                else:
                    # Validate password strength
                    password_error = validate_password(password)
                    if password_error:
                        st.error(password_error, icon="🚨")
                    else:
                        # Register user
                        error = register_user(username, password)
                        if error:
                            st.error(error, icon="🚨")
                        else:
                            st.success("Account created successfully! You can now log in.", icon="✅")
                            # Reset form
                            st.session_state.form_mode = "login"
                            st.experimental_rerun()
        
        # Password guidelines
        with st.expander("Password Requirements"):
            st.write("""
            - At least 8 characters long
            - Contains at least one uppercase letter (A-Z)
            - Contains at least one lowercase letter (a-z)
            - Contains at least one number (0-9)
            - Contains at least one special character (!@#$%^&* etc.)
            """)
    
    else:  # Login form
        with st.form("login_form"):
            st.markdown("### Login to Your Account")
            
            username = st.text_input("Username", placeholder="Enter your username", key="login_username")
            password = st.text_input("Password", type="password", 
                                    placeholder="Enter your password", key="login_password")
            
            remember_me = st.checkbox("Remember me", key="login_remember")
            
            submitted = st.form_submit_button("Login")
            
            if submitted:
                if not username:
                    st.error("Username is required", icon="🚨")
                elif not password:
                    st.error("Password is required", icon="🚨")
                else:
                    # Authenticate user
                    success, message = authenticate_user(username, password)
                    if success:
                        st.success(message, icon="✅")
                        # Store login state in session
                        st.session_state.logged_in = True
                        st.session_state.username = username
                    else:
                        st.error(message, icon="🚨")
        
        # Forgot password option
        st.markdown("<div style='text-align: center; margin-top: 1rem;'>"
                   "<a href='#' style='color: #7e7e7e;'>Forgot your password?</a>"
                   "</div>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    st.markdown("© 2023 Capital Compass • All Rights Reserved")
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
