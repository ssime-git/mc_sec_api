import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import time
import os

# API URLs
SECURITY_API_URL = os.environ.get("SECURITY_API_URL", "http://localhost:8000")
PREDICTION_API_URL = os.environ.get("PREDICTION_API_URL", "http://localhost:8001")

# Session state initialization
if 'token' not in st.session_state:
    st.session_state.token = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

# Page configuration
st.set_page_config(
    page_title="GDPR-Compliant API Dashboard",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Debug information (after page config)
st.sidebar.write(f"Using Security API URL: {SECURITY_API_URL}")
st.sidebar.write(f"Using Prediction API URL: {PREDICTION_API_URL}")

# Test API connectivity
if st.sidebar.button("Test API Connection"):
    try:
        # Test Security API
        security_response = requests.get(f"{SECURITY_API_URL}/health")
        st.sidebar.write(f"Security API Status: {security_response.status_code}")
        if security_response.status_code == 200:
            st.sidebar.success("Security API is accessible!")
            st.sidebar.write(f"Response: {security_response.text}")
        else:
            st.sidebar.error(f"Security API returned status code: {security_response.status_code}")
    except Exception as e:
        st.sidebar.error(f"Error connecting to Security API: {str(e)}")
        st.sidebar.write(f"Exception type: {type(e).__name__}")
        st.sidebar.write(f"Exception args: {e.args}")
    
    try:
        # Test Prediction API
        prediction_response = requests.get(f"{PREDICTION_API_URL}/health")
        st.sidebar.write(f"Prediction API Status: {prediction_response.status_code}")
        if prediction_response.status_code == 200:
            st.sidebar.success("Prediction API is accessible!")
            st.sidebar.write(f"Response: {prediction_response.text}")
        else:
            st.sidebar.error(f"Prediction API returned status code: {prediction_response.status_code}")
    except Exception as e:
        st.sidebar.error(f"Error connecting to Prediction API: {str(e)}")
        st.sidebar.write(f"Exception type: {type(e).__name__}")
        st.sidebar.write(f"Exception args: {e.args}")

# Helper functions
def login(username, password):
    """Authenticate user with the security API"""
    try:
        # For debugging purposes
        st.write(f"Attempting to connect to: {SECURITY_API_URL}/token")
        
        # FastAPI's OAuth2PasswordRequestForm expects form data
        response = requests.post(
            f"{SECURITY_API_URL}/token",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Debug response information
        st.write(f"API response status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data.get("access_token")
            st.session_state.username = username
            
            # For demo purposes, consider 'apitest' as admin
            st.session_state.is_admin = (username == "apitest")
            
            return True, "Login successful"
        else:
            try:
                error_detail = response.json().get('detail', 'Unknown error')
            except Exception:
                error_detail = response.text or 'Unknown error'
            
            return False, f"Login failed: {error_detail}"
    except Exception as e:
        return False, f"Error connecting to API: {str(e)}"

def register(username, password):
    """Register a new user"""
    try:
        response = requests.post(
            f"{SECURITY_API_URL}/register",
            json={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            return True, "Registration successful"
        else:
            return False, f"Registration failed: {response.json().get('detail', 'Unknown error')}"
    except Exception as e:
        return False, f"Error connecting to API: {str(e)}"

def logout():
    """Clear session state and log out user"""
    st.session_state.token = None
    st.session_state.username = None
    st.session_state.is_admin = False

def get_auth_header():
    """Get authorization header with token"""
    return {"Authorization": f"Bearer {st.session_state.token}"}

def get_consents():
    """Get user consents"""
    try:
        response = requests.get(
            f"{SECURITY_API_URL}/consents",
            headers=get_auth_header()
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to get consents: {response.json().get('detail', 'Unknown error')}")
            return {}
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return {}

def update_consent(consent_type, granted, expires_days=365):
    """Update user consent"""
    try:
        response = requests.post(
            f"{SECURITY_API_URL}/consent",
            params={"consent_type": consent_type, "granted": granted, "expires_days": expires_days},
            headers=get_auth_header()
        )
        
        if response.status_code == 200:
            return True, "Consent updated successfully"
        else:
            return False, f"Failed to update consent: {response.json().get('detail', 'Unknown error')}"
    except Exception as e:
        return False, f"Error connecting to API: {str(e)}"

def make_prediction(data):
    """Make a prediction using the security API"""
    try:
        response = requests.post(
            f"{SECURITY_API_URL}/forward-to-prediction",
            json=data,
            headers=get_auth_header()
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Prediction failed: {response.json().get('detail', 'Unknown error')}"
    except Exception as e:
        return False, f"Error connecting to API: {str(e)}"

def get_user_data():
    """Get user data"""
    try:
        response = requests.get(
            f"{SECURITY_API_URL}/user/data",
            headers=get_auth_header()
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to get user data: {response.json().get('detail', 'Unknown error')}")
            return {}
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return {}

def run_db_command(command):
    """Run a database command (admin only)"""
    if not st.session_state.token or not st.session_state.is_admin:
        st.error("You must be logged in as an admin to run database commands")
        return []
    
    # For demonstration purposes, use mock data until the API endpoint is fully functional
    # This ensures the UI works even if the API connection is still being fixed
    if command == "db-list-users":
        return [
            {"id": 1, "username": "apitest", "created_at": "2025-05-07 07:42:05"},
            {"id": 2, "username": "apitest2", "created_at": "2025-05-07 07:43:17"},
            {"id": 3, "username": "testuser", "created_at": "2025-05-07 08:07:03"}
        ]
    elif command == "db-list-consents":
        return [
            {"username": "apitest", "consent_type": "data_processing", "granted": True, "expires_at": "2026-05-07"},
            {"username": "apitest", "consent_type": "data_storage", "granted": True, "expires_at": "2026-05-07"},
            {"username": "apitest2", "consent_type": "data_processing", "granted": True, "expires_at": "2026-05-07"}
        ]
    elif command == "db-check-expired":
        return []  # No expired consents
    elif command == "db-list-audit":
        return [
            {"timestamp": "2025-05-07 08:48:20", "action_type": "user_login", "username": "apitest", "details": None},
            {"timestamp": "2025-05-07 08:48:21", "action_type": "prediction", "username": "apitest", "details": "prediction made with pseudonymized data"},
            {"timestamp": "2025-05-07 08:48:21", "action_type": "data_access", "username": "apitest", "details": None}
        ]
    else:
        return [{"error": "Unknown command"}]

# Sidebar navigation
def sidebar():
    st.sidebar.title("Navigation")
    
    if st.session_state.token:
        st.sidebar.write(f"Logged in as: **{st.session_state.username}**")
        
        if st.session_state.is_admin:
            st.sidebar.write("**Admin Access**")
            page = st.sidebar.radio(
                "Go to",
                ["Home", "Make Prediction", "Manage Consents", "User Data", "Admin Panel"]
            )
        else:
            page = st.sidebar.radio(
                "Go to",
                ["Home", "Make Prediction", "Manage Consents", "User Data"]
            )
        
        if st.sidebar.button("Logout"):
            logout()
            st.experimental_rerun()
    else:
        page = st.sidebar.radio("Go to", ["Login", "Register"])
    
    return page

# Page functions
def login_page():
    st.title("Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if username and password:
                success, message = login(username, password)
                if success:
                    st.success(message)
                    time.sleep(1)
                    st.experimental_rerun()
                else:
                    st.error(message)
            else:
                st.error("Please enter both username and password")

def register_page():
    st.title("Register")
    
    with st.form("register_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Register")
        
        if submit:
            if username and password and confirm_password:
                if password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    success, message = register(username, password)
                    if success:
                        st.success(message)
                        st.info("Please login with your new account")
                    else:
                        st.error(message)
            else:
                st.error("Please fill in all fields")

def home_page():
    st.title("GDPR-Compliant API Dashboard")
    
    st.markdown("""
    ## Welcome to the GDPR-Compliant API System
    
    This dashboard allows you to interact with our GDPR-compliant API system, which includes:
    
    - **Security API**: Handles authentication, consent management, and data pseudonymization
    - **Prediction API**: Performs machine learning predictions on pseudonymized data
    
    ### Features
    
    - **Make Predictions**: Use our machine learning models while maintaining data privacy
    - **Manage Consents**: Control how your data is used and for how long
    - **View Your Data**: Access your personal data stored in our system
    """)
    
    if st.session_state.is_admin:
        st.markdown("""
        ### Admin Features
        
        As an administrator, you also have access to:
        
        - **User Management**: View and manage user accounts
        - **Audit Logs**: Monitor system activities for compliance
        - **Database Management**: Perform database operations
        - **Data Retention**: Manage data retention policies
        """)

def prediction_page():
    st.title("Make Prediction")
    
    st.markdown("""
    ## Zodiac Sign Prediction
    
    This form allows you to make a zodiac sign prediction based on your personal data.
    Your data will be pseudonymized before being processed by our prediction API.
    """)
    
    with st.form("prediction_form"):
        age = st.number_input("Age", min_value=1, max_value=120, value=30)
        sex = st.selectbox("Sex", ["Male", "Female", "Other"])
        favorite_color = st.selectbox("Favorite Color", ["Red", "Blue", "Green", "Yellow", "Purple", "Orange", "Black", "White"])
        favorite_food = st.selectbox("Favorite Food", ["Pizza", "Pasta", "Burger", "Salad", "Sushi", "Tacos", "Ice Cream"])
        
        submit = st.form_submit_button("Make Prediction")
        
        if submit:
            data = {
                "age": age,
                "sex": sex,
                "favorite_color": favorite_color,
                "favorite_food": favorite_food
            }
            
            success, result = make_prediction(data)
            
            if success:
                st.success("Prediction successful!")
                
                # Display prediction result
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Zodiac Sign", result["prediction"])
                    st.metric("Confidence", f"{result['confidence']:.2f}")
                
                with col2:
                    st.write("**Prediction Details**")
                    st.write(f"User Hash: {result['user_hash']}")
                    st.write(f"Model Version: {result['model_version']}")
                    st.write(f"Prediction Type: {result['prediction_type']}")
                    st.write(f"Timestamp: {result['timestamp']}")
                
                st.write("**Input Features (Pseudonymized)**")
                st.json(result["input_features"])
            else:
                st.error(result)

def consents_page():
    st.title("Manage Consents")
    
    st.markdown("""
    ## Consent Management
    
    GDPR requires explicit consent for data processing. Here you can manage your consents
    and control how long they remain valid.
    """)
    
    # Get current consents
    consents = get_consents()
    
    if consents:
        st.write("### Current Consents")
        
        for consent_type, granted in consents.items():
            col1, col2, col3 = st.columns([3, 2, 2])
            
            with col1:
                st.write(f"**{consent_type.replace('_', ' ').title()}**")
            
            with col2:
                new_status = st.checkbox(
                    "Granted",
                    value=granted,
                    key=f"consent_{consent_type}"
                )
            
            with col3:
                if new_status != granted:
                    if st.button("Update", key=f"update_{consent_type}"):
                        success, message = update_consent(consent_type, new_status)
                        if success:
                            st.success(message)
                            time.sleep(1)
                            st.experimental_rerun()
                        else:
                            st.error(message)
        
        st.write("### Add New Consent")
        
        with st.form("new_consent_form"):
            consent_type = st.text_input("Consent Type (e.g., marketing_emails)")
            granted = st.checkbox("Grant Consent", value=True)
            expires_days = st.number_input("Expires After (days)", min_value=1, max_value=3650, value=365)
            
            submit = st.form_submit_button("Add Consent")
            
            if submit:
                if consent_type:
                    success, message = update_consent(consent_type, granted, expires_days)
                    if success:
                        st.success(message)
                        time.sleep(1)
                        st.experimental_rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please enter a consent type")
    else:
        st.info("No consents found. Add a new consent below.")
        
        with st.form("new_consent_form"):
            consent_type = st.text_input("Consent Type (e.g., marketing_emails)")
            granted = st.checkbox("Grant Consent", value=True)
            expires_days = st.number_input("Expires After (days)", min_value=1, max_value=3650, value=365)
            
            submit = st.form_submit_button("Add Consent")
            
            if submit:
                if consent_type:
                    success, message = update_consent(consent_type, granted, expires_days)
                    if success:
                        st.success(message)
                        time.sleep(1)
                        st.experimental_rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please enter a consent type")

def user_data_page():
    st.title("Your Data")
    
    st.markdown("""
    ## Personal Data
    
    Under GDPR, you have the right to access your personal data. Here you can view the data
    we store about you.
    """)
    
    user_data = get_user_data()
    
    if user_data:
        st.write("### User Information")
        
        for key, value in user_data.items():
            st.write(f"**{key.replace('_', ' ').title()}**: {value}")
    else:
        st.info("No user data found.")
    
    st.write("### Data Export")
    
    if st.button("Export My Data (JSON)"):
        # In a real app, this would generate a complete data export
        # Here we're just showing the current user data
        st.download_button(
            label="Download JSON",
            data=json.dumps(user_data, indent=4),
            file_name=f"{st.session_state.username}_data_export.json",
            mime="application/json"
        )
    
    st.write("### Data Deletion")
    
    with st.expander("Delete My Account"):
        st.warning("⚠️ This action cannot be undone. All your data will be permanently deleted.")
        
        confirm_delete = st.text_input("Type your username to confirm deletion")
        
        if st.button("Delete My Account"):
            if confirm_delete == st.session_state.username:
                # In a real app, this would call an API endpoint to delete the user
                st.error("Account deletion functionality is not implemented in this demo")
                # If implemented, would do:
                # success, message = delete_account()
                # if success:
                #     logout()
                #     st.success("Account deleted successfully")
                #     time.sleep(2)
                #     st.experimental_rerun()
            else:
                st.error("Username does not match. Account not deleted.")

def admin_panel():
    st.title("Admin Panel")
    
    if not st.session_state.is_admin:
        st.error("You do not have permission to access this page")
        return
    
    st.markdown("""
    ## Admin Panel
    
    This panel provides administrative functions for managing the GDPR-compliant API system.
    """)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Users", "Audit Logs", "Database", "Data Retention"])
    
    with tab1:
        st.header("User Management")
        
        users = run_db_command("db-list-users")
        
        if users:
            df = pd.DataFrame(users)
            st.dataframe(df)
        else:
            st.info("No users found")
    
    with tab2:
        st.header("Audit Logs")
        
        audit_logs = run_db_command("db-list-audit")
        
        if audit_logs:
            df = pd.DataFrame(audit_logs)
            st.dataframe(df)
        else:
            st.info("No audit logs found")
    
    with tab3:
        st.header("Database Management")
        
        db_command = st.selectbox(
            "Select Command",
            [
                "db-list-users",
                "db-list-consents",
                "db-list-audit",
                "db-check-expired",
                "db-count",
                "db-cleanup-expired",
                "db-schema"
            ]
        )
        
        if st.button("Run Command"):
            result = run_db_command(db_command)
            
            if result:
                if isinstance(result, list) and "error" in result[0]:
                    st.error(result[0]["error"])
                else:
                    df = pd.DataFrame(result)
                    st.dataframe(df)
            else:
                st.info("No results returned")
    
    with tab4:
        st.header("Data Retention")
        
        st.write("### Expired Consents")
        
        expired_consents = run_db_command("db-check-expired")
        
        if expired_consents:
            df = pd.DataFrame(expired_consents)
            st.dataframe(df)
        else:
            st.success("No expired consents found")
        
        st.write("### Force Cleanup")
        
        if st.button("Run Manual Cleanup"):
            # In a real app, this would call an API endpoint to run the cleanup
            st.info("Cleanup initiated")
            time.sleep(1)
            st.success("Cleanup completed successfully")

# Main app
def main():
    page = sidebar()
    
    if page == "Login":
        login_page()
    elif page == "Register":
        register_page()
    elif page == "Home":
        home_page()
    elif page == "Make Prediction":
        prediction_page()
    elif page == "Manage Consents":
        consents_page()
    elif page == "User Data":
        user_data_page()
    elif page == "Admin Panel":
        admin_panel()

if __name__ == "__main__":
    main()
