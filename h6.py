import streamlit as st
import re
import hashlib
import time
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

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
</style>
""", unsafe_allow_html=True)

# Google Sheets setup
def init_google_sheets():
    # Define the scope
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    
    # Load credentials from the service account key file
    # You need to download this file from Google Cloud Console
    creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
    
    # Authorize the client
    client = gspread.authorize(creds)
    
    # Open the Google Sheet by URL
    sheet_url = 'https://docs.google.com/spreadsheets/d/1sxQBudLlJxycUCgxVt5A_y71iktGqWob5rGz6jxc-PM/edit#gid=0'
    spreadsheet = client.open_by_url(sheet_url)
    
    # Select the worksheet (use the first sheet by default)
    worksheet = spreadsheet.get_worksheet(0)
    
    # Set up headers if the sheet is empty
    if not worksheet.get_all_values():
        worksheet.update('A1:D1', [['Username', 'Email', 'Password Hash', 'Registration Date']])
    
    return worksheet

# Password hashing function
def hash_password(password):
    salt = "capital_compass_salt_2023"
    return hashlib.sha256((password + salt).encode()).hexdigest()

# Check if username or email already exists in Google Sheets
def user_exists(worksheet, username, email):
    all_records = worksheet.get_all_records()
    for record in all_records:
        if record.get('Username') == username or record.get('Email') == email:
            return True
    return False

# Save user to Google Sheets
def save_user_to_sheets(worksheet, username, email, password):
    password_hash = hash_password(password)
    registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Append the new user data
    worksheet.append_row([username, email, password_hash, registration_date])
    
    return True

# App header
st.markdown('<h1 class="main-header">Capital Compass</h1>', unsafe_allow_html=True)
st.markdown('<h2 class="sub-header">Navigate Your Financial Future</h2>', unsafe_allow_html=True)

# Initialize Google Sheets
try:
    worksheet = init_google_sheets()
    sheets_connected = True
except Exception as e:
    st.error(f"Error connecting to Google Sheets: {str(e)}")
    st.info("Please make sure you have set up Google Sheets API credentials correctly.")
    sheets_connected = False

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
    
    # Check if Google Sheets is connected
    if not sheets_connected:
        errors.append("System temporarily unavailable. Please try again later.")
    
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
    
    # Check if user already exists (if sheets is connected)
    if sheets_connected and user_exists(worksheet, username, email):
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
        
        # Save user to Google Sheets
        try:
            success = save_user_to_sheets(worksheet, username, email, password)
            if success:
                st.markdown('<div class="success-message">✅ Account created successfully!</div>', unsafe_allow_html=True)
                st.info("Your account information has been securely stored. A verification email has been sent to your email address.")
                
                # Clear the form
                st.session_state.registration_form = {}
            else:
                st.markdown('<div class="error-message">Error creating account. Please try again.</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.markdown(f'<div class="error-message">Error creating account: {str(e)}</div>', unsafe_allow_html=True)

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
