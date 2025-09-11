import streamlit as st
import re
import hashlib
import sqlite3
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Capital Compass",
    page_icon="🧭",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Set background image with NYC night skyline
def set_bg_image():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("https://images.unsplash.com/photo-1485871981521-5b1fd3805eee?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .main {{
            background-color: rgba(0, 0, 0, 0.85);
            color: #ffffff;
            padding: 2rem;
            border-radius: 10px;
            margin: 2rem auto;
            max-width: 500px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.7);
            border: 1px solid #444;
        }}
        .stTextInput>div>div>input {{
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 2px solid #cccccc !important;
            border-radius: 6px;
            padding: 0.75rem;
            font-size: 1rem;
        }}
        .stTextInput>div>div>input:focus {{
            border-color: #4a90e2 !important;
            box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.2);
        }}
        .stTextInput label {{
            color: #ffffff !important;
            font-weight: bold;
            font-size: 1.1rem;
        }}
        .stButton>button {{
            background-color: #4a90e2;
            color: #ffffff;
            border: none;
            padding: 0.75rem 1rem;
            border-radius: 6px;
            transition: all 0.3s ease;
            width: 100%;
            font-weight: bold;
            font-size: 1.1rem;
        }}
        .stButton>button:hover {{
            background-color: #3a80d2;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        .success {{
            color: #4caf50;
            font-weight: bold;
        }}
        .error {{
            color: #ff5252;
            font-weight: bold;
        }}
        .header {{
            text-align: center;
            margin-bottom: 2rem;
        }}
        .compass-icon {{
            font-size: 4rem;
            margin-bottom: 1rem;
            color: #4a90e2;
            text-shadow: 0 0 10px rgba(74, 144, 226, 0.5);
        }}
        .footer {{
            text-align: center;
            margin-top: 3rem;
            color: #bbbbbb;
            font-size: 0.8rem;
        }}
        .toggle-container {{
            display: flex;
            justify-content: center;
            margin-bottom: 1.5rem;
            background-color: #222222;
            border-radius: 50px;
            padding: 5px;
            width: 80%;
            margin-left: auto;
            margin-right: auto;
            border: 1px solid #444;
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
            background-color: #4a90e2;
            font-weight: bold;
        }}
        .form-container {{
            animation: fadeIn 0.5s ease-in;
            background-color: rgba(0, 0, 0, 0.7);
            padding: 2rem;
            border-radius: 10px;
            margin-top: 1rem;
            border: 1px solid #444;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(-10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .stCheckbox label {{
            color: #ffffff !important;
            font-weight: normal;
        }}
        .stCheckbox>div>div {{
            background-color: #ffffff;
            border: 2px solid #cccccc;
        }}
        .stExpander {{
            border: 1px solid #444;
            border-radius: 6px;
            background-color: rgba(0, 0, 0, 0.7);
        }}
        .stExpander>div {{
            background-color: rgba(0, 0, 0, 0.7);
        }}
        .stExpander>div>p {{
            color: #ffffff;
            font-weight: bold;
        }}
        .stExpander>div>div>div {{
            color: #ffffff;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #ffffff;
        }}
        p, div {{
            color: #ffffff;
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
            background-color: {"#4a90e2" if st.session_state.form_mode == "register" else "transparent"};
            color: #ffffff;
            border: none;
            border-radius: 50px;
            font-weight: {"bold" if st.session_state.form_mode == "register" else "normal"};
        }}
        #login_btn {{
            background-color: {"#4a90e2" if st.session_state.form_mode == "login" else "transparent"};
            color: #ffffff;
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
                   "<a href='#' style='color: #bbbbbb; text-decoration: none;'>Forgot your password?</a>"
                   "</div>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    st.markdown("© 2023 Capital Compass • All Rights Reserved")
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
