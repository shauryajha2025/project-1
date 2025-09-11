def save_user_to_google_sheets(username, email, password):
    # This would be the actual implementation for Google Sheets
    import gspread
    from google.oauth2.service_account import Credentials
    
    # Define the scope
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    
    # Load credentials (you would store these securely in Streamlit secrets)
    creds = Credentials.from_service_account_info(st.secrets["google_credentials"], scopes=scope)
    client = gspread.authorize(creds)
    
    # Open the Google Sheet
    spreadsheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1sxQBudLlJxycUCgxVt5A_y71iktGqWob5rGz6jxc-PM/edit#gid=0')
    worksheet = spreadsheet.get_worksheet(0)
    
    # Append data
    password_hash = hash_password(password)
    registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    worksheet.append_row([username, email, password_hash, registration_date])
    
    return True
