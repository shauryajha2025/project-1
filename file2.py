import streamlit as st
import re
import hashlib
import time
from datetime import datetime
import requests
import base64
import json

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
    .github-info {
        background-color: #1E1E1E;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #6e5494;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# GitHub configuration
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "your_github_token_here")
REPO_OWNER = "shauryajha2025"
REPO_NAME = "project-1"
FILE_PATH = "data.sql"
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"

# Password hashing function
def hash_password(password):
    salt = "capital_compass_salt_2023"
    return hashlib.sha256((password + salt).encode()).hexdigest()

# Get current file content from GitHub
def get_github_file_content():
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(GITHUB_API_URL, headers=headers)
        if response.status_code == 200:
            content = response.json()["content"]
            return base64.b64decode(content).decode("utf-8"), response.json()["sha"]
        else:
            return "", ""
    except:
        return "", ""

# Update GitHub file with new user data
def update_github_file(new_content, sha):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "message": f"Add new user registration - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "content": base64.b64encode(new_content.encode("utf-8")).decode("utf-8"),
        "sha": sha
    }
    
    try:
        response = requests.put(GITHUB_API_URL, headers=headers, json=data)
        return response.status_code == 200
    except:
        return False

# Save user data to GitHub SQL file
def save_user_to_github(username, email, password):
    password_hash = hash_password(password)
    registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Get current file content
    current_content, sha = get_github_file_content()
    
    # Create SQL insert statement
    sql_insert = f"INSERT INTO users (username, email, password_hash, created_at) VALUES ('{username}', '{email}', '{password_hash}', '{registration_date}');\n"
    
    # Add to existing content
    new_content = current_content + sql_insert
    
    # Update file on GitHub
    return update_github_file(new_content, sha)

# Check if user exists in GitHub file
def user_exists_in_github(username, email):
    current_content, _ = get_github_file_content()
    return f"'{username}'" in current_content or f"'{email}'" in current_content

# App header
st.markdown('<h1 class="main-header">Capital Compass</h1>', unsafe_allow_html=True)
st.markdown('<h2 class="sub-header">Navigate Your Financial Future</h2>', unsafe_allow_html=True)

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
    if user_exists_in_github(username, email):
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
        
        # Save user to GitHub
        try:
            success = save_user_to_github(username, email, password)
            if success:
                st.markdown('<div class="success-message">✅ Account created successfully!</div>', unsafe_allow_html=True)
                
                # Display minimal success information
                st.write("### Welcome to Capital Compass!")
                st.write(f"**Username:** {username}")
                st.write("**Registration Status:** Complete")
                st.write("**Data Storage:** Securely saved to GitHub repository")
                
                if newsletter:
                    st.info("📧 You've been subscribed to our investment insights newsletter!")
                
                st.success("Your account data has been securely stored in our GitHub repository.")
                
            else:
                st.markdown('<div class="error-message">Error creating account. Please try again.</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.markdown(f'<div class="error-message">Error creating account: {str(e)}</div>', unsafe_allow_html=True)

# GitHub information section
with st.expander("Data Storage Information", expanded=False):
    st.markdown(f"""
    <div class="github-info">
    <h4>📊 Data Storage Details:</h4>
    <p><strong>Storage Platform:</strong> GitHub</p>
    <p><strong>Repository:</strong> {REPO_OWNER}/{REPO_NAME}</p>
    <p><strong>File:</strong> {FILE_PATH}</p>
    <p><strong>Data Format:</strong> SQL Insert Statements</p>
    <p><strong>Security:</strong> Password Hashing (SHA-256)</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("""
    ℹ️ User data is securely stored in a GitHub repository with hashed passwords.
    No personal data is displayed on this webpage - all information is sent directly to secure storage.
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
