import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from api_service import APIService

# Initialize API service
api_service = APIService()

def connection_test():
    """Test connection to APIs and display results in sidebar"""
    with st.sidebar.expander("API Connection Status"):
        connection_results = api_service.test_connection()
        
        # Security API status
        security_status = connection_results.get("security_api", {}).get("status", "unknown")
        if security_status == "connected":
            st.sidebar.success("✅ Security API: Connected")
        else:
            st.sidebar.error("❌ Security API: Not connected")
            details = connection_results.get("security_api", {}).get("details", "Unknown error")
            st.sidebar.write(f"Details: {details}")
        
        # Prediction API status
        prediction_status = connection_results.get("prediction_api", {}).get("status", "unknown")
        if prediction_status == "connected":
            st.sidebar.success("✅ Prediction API: Connected")
        else:
            st.sidebar.error("❌ Prediction API: Not connected")
            details = connection_results.get("prediction_api", {}).get("details", "Unknown error")
            st.sidebar.write(f"Details: {details}")

def login_form():
    """Display login form"""
    st.header("Login")
    
    # Add debug information in an expander
    with st.expander("Debug Information"):
        st.write(f"API URL: {api_service.security_api_url}")
        st.write(f"Current session state keys: {list(st.session_state.keys())}")
    
    # Add default login credentials hint
    st.info("For testing, you can use the following credentials:\n" +
            "Username: apitest\n" +
            "Password: password")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if not username or not password:
                st.error("Please enter both username and password")
                return
            
            # First get the token
            try:
                response = requests.post(
                    f"{api_service.security_api_url}/token",
                    data={"username": username, "password": password},
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    token = data.get("access_token")
                    
                    if token:
                        # Store token in session state
                        st.session_state.token = token
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.is_admin = (username == "apitest")  # For demo, apitest is admin
                        st.session_state.navigation = "home"
                        
                        st.success("Login successful!")
                        st.experimental_rerun()
                    else:
                        st.error("Authentication failed: No token received")
                else:
                    try:
                        error_detail = response.json().get('detail', 'Unknown error')
                    except Exception:
                        error_detail = response.text or 'Unknown error'
                    
                    st.error(f"Authentication failed: {error_detail}")
            except Exception as e:
                st.error(f"Error connecting to authentication service: {str(e)}")

def register_form():
    """Display registration form"""
    st.header("Register")
    
    with st.form("register_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Register")
        
        if submit:
            if not username or not password or not confirm_password:
                st.error("Please fill in all fields")
                return
            
            if password != confirm_password:
                st.error("Passwords do not match")
                return
            
            success, message = api_service.register(username, password)
            if success:
                st.success(message)
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.is_admin = False
                st.session_state.navigation = "home"
                st.experimental_rerun()
            else:
                st.error(message)

def navigation_sidebar():
    """Display navigation sidebar"""
    with st.sidebar:
        st.title("GDPR-Compliant API")
        
        if st.session_state.logged_in:
            st.write(f"Logged in as: **{st.session_state.username}**")
            
            st.subheader("Navigation")
            
            if st.button("Home", key="nav_home"):
                st.session_state.navigation = "home"
                st.experimental_rerun()
                
            if st.button("My Data", key="nav_data"):
                st.session_state.navigation = "data"
                st.experimental_rerun()
                
            if st.button("Consents", key="nav_consents"):
                st.session_state.navigation = "consents"
                st.experimental_rerun()
                
            if st.button("Predictions", key="nav_predictions"):
                st.session_state.navigation = "predictions"
                st.experimental_rerun()
                
            # Admin panel only for admin users
            if st.session_state.is_admin:
                if st.button("Admin Panel", key="nav_admin"):
                    st.session_state.navigation = "admin"
                    st.experimental_rerun()
            
            if st.button("Logout", key="nav_logout"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.session_state.logged_in = False
                st.session_state.navigation = "login"
                st.experimental_rerun()
        else:
            if st.button("Login", key="nav_login"):
                st.session_state.navigation = "login"
                st.experimental_rerun()
                
            if st.button("Register", key="nav_register"):
                st.session_state.navigation = "register"
                st.experimental_rerun()

def home_page():
    """Display home page"""
    st.title("Welcome to GDPR-Compliant API")
    
    st.write("""
    This application demonstrates a GDPR-compliant API system with the following features:
    - User authentication and authorization
    - Consent management
    - Data pseudonymization
    - Prediction API with ML model
    - Admin panel for monitoring and management
    """)
    
    st.subheader("Quick Links")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("My Data", key="quick_data"):
            st.session_state.navigation = "data"
            st.experimental_rerun()
    
    with col2:
        if st.button("Manage Consents", key="quick_consents"):
            st.session_state.navigation = "consents"
            st.experimental_rerun()
    
    with col3:
        if st.button("Make Predictions", key="quick_predictions"):
            st.session_state.navigation = "predictions"
            st.experimental_rerun()

def my_data_page():
    """Display user data page"""
    st.title("My Data")
    
    # Get user data
    user_data = api_service.get_user_data()
    
    if user_data and "error" not in user_data:
        st.subheader("Personal Information")
        st.json(user_data)
        
        # Option to download data
        if st.button("Download My Data"):
            st.download_button(
                label="Download JSON",
                data=str(user_data),
                file_name=f"user_data_{st.session_state.username}.json",
                mime="application/json"
            )
        
        # Option to delete account
        st.subheader("Delete Account")
        st.warning("This action cannot be undone. All your data will be permanently deleted.")
        
        if st.button("Delete My Account"):
            if st.session_state.username == "apitest":
                st.error("Cannot delete demo admin account")
            else:
                success, message = api_service.delete_account()
                if success:
                    st.success(message)
                    # Log out the user
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.session_state.logged_in = False
                    st.session_state.navigation = "login"
                    st.experimental_rerun()
                else:
                    st.error(message)
    else:
        if user_data and "error" in user_data:
            st.error(f"Error: {user_data['error']}")
        else:
            st.info("No data available")

def consents_page():
    """Display consents management page"""
    st.title("Consent Management")
    
    # Get current consents
    consents = api_service.get_consents()
    
    if consents and "error" not in consents:
        st.subheader("Your Current Consents")
        
        # Convert to DataFrame for better display
        df = pd.DataFrame(consents)
        st.dataframe(df)
        
        # Form to update consents
        st.subheader("Update Consents")
        
        with st.form("consent_form"):
            consent_types = ["data_processing", "data_storage"]
            selected_consents = []
            
            for consent_type in consent_types:
                # Check if consent is already granted
                is_granted = False
                for consent in consents:
                    if consent.get("consent_type") == consent_type and consent.get("granted"):
                        is_granted = True
                        break
                
                if st.checkbox(f"I consent to {consent_type.replace('_', ' ')}", value=is_granted, key=f"consent_{consent_type}"):
                    selected_consents.append(consent_type)
            
            # Expiration period
            expiration_days = st.number_input("Consent valid for (days)", min_value=1, max_value=365, value=30)
            
            submit = st.form_submit_button("Update Consents")
            
            if submit:
                success, message = api_service.update_consents(selected_consents, expiration_days)
                if success:
                    st.success(message)
                    st.experimental_rerun()  # Refresh to show updated consents
                else:
                    st.error(message)
    else:
        # If consents is not a valid list or is empty
        st.info("No consent data available")

def predictions_page():
    """Display predictions page"""
    st.title("Make Predictions")
    
    # Check if user has necessary consents
    consents = api_service.get_consents()
    has_consents = False
    
    if consents and "error" not in consents:
        for consent in consents:
            if consent.get("consent_type") in ["data_processing", "data_storage"] and consent.get("granted"):
                has_consents = True
    
    if not has_consents:
        st.warning("You need to grant necessary consents before making predictions.")
        if st.button("Go to Consents Page"):
            st.session_state.navigation = "consents"
            st.experimental_rerun()
        return
    
    # Prediction form
    st.subheader("Enter Information for Prediction")
    
    with st.form("prediction_form"):
        age = st.number_input("Age", min_value=0, max_value=120, value=30)
        sex = st.selectbox("Sex", ["Male", "Female"])
        favorite_color = st.selectbox("Favorite Color", ["Red", "Blue", "Green", "Yellow", "Purple"])
        favorite_food = st.selectbox("Favorite Food", ["Pizza", "Pasta", "Burger", "Sushi", "Salad", "Ice Cream"])
        
        submit = st.form_submit_button("Get Prediction")
        
        if submit:
            prediction_data = {
                "age": age,
                "sex": sex,
                "favorite_color": favorite_color,
                "favorite_food": favorite_food
            }
            
            result = api_service.make_prediction(prediction_data)
            
            if result and "error" not in result:
                st.success("Prediction successful!")
                st.json(result)
            else:
                if result and "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.error("Unknown error occurred")

# Add the missing functions that app.py is trying to use
def prediction_form():
    """Display prediction form"""
    # Check if user has necessary consents
    consents = api_service.get_consents()
    has_consents = False
    
    # Check if consents is a valid list of dictionaries
    if isinstance(consents, list) and consents:
        # Check if the first item is an error message
        if len(consents) == 1 and "error" in consents[0]:
            st.error(f"Error retrieving consents: {consents[0]['error']}")
        else:
            # Process valid consents
            for consent in consents:
                if isinstance(consent, dict) and \
                   consent.get("consent_type") in ["data_processing", "data_storage"] and \
                   consent.get("granted"):
                    has_consents = True
    
    if not has_consents:
        st.warning("You need to grant necessary consents before making predictions.")
        if st.button("Go to Consents Page"):
            st.session_state.navigation = "consents"
            st.experimental_rerun()
        return
    
    # Prediction form
    st.subheader("Enter Information for Prediction")
    
    with st.form("prediction_form"):
        age = st.number_input("Age", min_value=0, max_value=120, value=30)
        sex = st.selectbox("Sex", ["Male", "Female"])
        favorite_color = st.selectbox("Favorite Color", ["Red", "Blue", "Green", "Yellow", "Purple"])
        favorite_food = st.selectbox("Favorite Food", ["Pizza", "Pasta", "Burger", "Sushi", "Salad", "Ice Cream"])
        
        submit = st.form_submit_button("Get Prediction")
        
        if submit:
            prediction_data = {
                "age": age,
                "sex": sex,
                "favorite_color": favorite_color,
                "favorite_food": favorite_food
            }
            
            result = api_service.make_prediction(prediction_data)
            
            if result and "error" not in result:
                st.success("Prediction successful!")
                st.json(result)
            else:
                if result and "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.error("Unknown error occurred")

def consent_management():
    """Display consent management form"""
    # Get current consents
    consents = api_service.get_consents()
    
    # Check if consents is a valid list of dictionaries
    if isinstance(consents, list) and consents:
        # Check if the first item is an error message
        if len(consents) == 1 and "error" in consents[0]:
            st.error(f"Error retrieving consents: {consents[0]['error']}")
            return
        
        st.subheader("Your Current Consents")
        
        # Convert to DataFrame for better display
        df = pd.DataFrame(consents)
        st.dataframe(df)
        
        # Form to update consents
        st.subheader("Update Consents")
        
        with st.form("consent_form"):
            consent_types = ["data_processing", "data_storage"]
            selected_consents = []
            
            for consent_type in consent_types:
                # Check if consent is already granted
                is_granted = False
                for consent in consents:
                    if consent.get("consent_type") == consent_type and consent.get("granted"):
                        is_granted = True
                        break
                
                if st.checkbox(f"I consent to {consent_type.replace('_', ' ')}", value=is_granted, key=f"consent_{consent_type}"):
                    selected_consents.append(consent_type)
            
            # Expiration period
            expiration_days = st.number_input("Consent valid for (days)", min_value=1, max_value=365, value=30)
            
            submit = st.form_submit_button("Update Consents")
            
            if submit:
                success, message = api_service.update_consents(selected_consents, expiration_days)
                if success:
                    st.success(message)
                    st.experimental_rerun()  # Refresh to show updated consents
                else:
                    st.error(message)
    else:
        # If consents is not a valid list or is empty
        st.info("No consent data available")

def user_data_view():
    """Display user data view"""
    # Get user data
    user_data = api_service.get_user_data()
    
    # Check if user_data is a valid dictionary
    if isinstance(user_data, dict):
        # Check if it contains an error message
        if "error" in user_data:
            st.error(f"Error retrieving user data: {user_data['error']}")
            return
        
        st.subheader("Personal Information")
        st.json(user_data)
        
        # Option to download data
        if st.button("Download My Data"):
            st.download_button(
                label="Download JSON",
                data=str(user_data),
                file_name=f"user_data_{st.session_state.username}.json",
                mime="application/json"
            )
        
        # Option to delete account
        st.subheader("Delete Account")
        st.warning("This action cannot be undone. All your data will be permanently deleted.")
        
        if st.button("Delete My Account"):
            if st.session_state.username == "apitest":
                st.error("Cannot delete demo admin account")
            else:
                success, message = api_service.delete_account()
                if success:
                    st.success(message)
                    # Log out the user
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.session_state.logged_in = False
                    st.session_state.navigation = "login"
                    st.experimental_rerun()
                else:
                    st.error(message)
    else:
        if user_data and "error" in user_data:
            st.error(f"Error: {user_data['error']}")
        else:
            st.info("No data available")

def admin_panel():
    """Admin panel"""
    if not st.session_state.is_admin:
        st.error("You don't have permission to access this page")
        return
    
    st.title("Admin Panel")
    
    # Initialize refresh states if not present
    if "refresh_users" not in st.session_state:
        st.session_state.refresh_users = True
    if "refresh_logs" not in st.session_state:
        st.session_state.refresh_logs = True
    if "refresh_predictions" not in st.session_state:
        st.session_state.refresh_predictions = True
    if "refresh_db" not in st.session_state:
        st.session_state.refresh_db = False
    if "db_command" not in st.session_state:
        st.session_state.db_command = "db-list-users"
    if "last_refresh_time" not in st.session_state:
        st.session_state.last_refresh_time = {}
    
    # Admin tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Users", "Audit Logs", "Predictions", "Database"])
    
    with tab1:
        admin_users_tab()
    
    with tab2:
        admin_audit_logs_tab()
    
    with tab3:
        admin_predictions_tab()
    
    with tab4:
        admin_database_tab()

def admin_users_tab():
    """Admin panel users tab"""
    st.header("User Management")
    
    # Add debug information
    st.write(f"API URL: {api_service.security_api_url}")
    st.write(f"Authentication token present: {bool(st.session_state.token)}")
    st.write(f"Admin privileges: {st.session_state.is_admin}")
    
    if st.button("Refresh Users", key="refresh_users_button"):
        st.session_state.refresh_users = True
        st.session_state.last_refresh_time['users'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if st.session_state.refresh_users:
        with st.spinner("Fetching users..."):
            users = api_service.run_db_command("db-list-users")
            st.session_state.users = users
            st.session_state.refresh_users = False
            st.session_state.last_refresh_time['users'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        users = st.session_state.get('users', [])
    
    # Display the raw response for debugging
    with st.expander("Debug: Raw Response"):
        st.write(users)
    
    if users and isinstance(users, list) and len(users) > 0 and isinstance(users[0], dict) and "error" not in users[0]:
        try:
            df = pd.DataFrame(users)
            st.dataframe(df)
            
            # Add timestamp to show when the data was last refreshed
            if 'users' in st.session_state.last_refresh_time:
                st.caption(f"Last refreshed: {st.session_state.last_refresh_time['users']}")
        except Exception as e:
            st.error(f"Error creating dataframe: {str(e)}")
            st.write("Raw data:", users)
    else:
        if users and isinstance(users, list) and len(users) > 0 and isinstance(users[0], dict) and "error" in users[0]:
            st.error(f"Error: {users[0]['error']}")
        else:
            st.info("No users found or invalid response format")

def admin_audit_logs_tab():
    """Admin panel audit logs tab"""
    st.header("Audit Logs")
    
    # Add debug information in an expander
    with st.expander("Debug Information"):
        st.write(f"API URL: {api_service.security_api_url}")
        st.write(f"Authentication token present: {bool(st.session_state.token)}")
        st.write(f"Admin privileges: {st.session_state.is_admin}")
        st.write(f"Current session state keys: {list(st.session_state.keys())}")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Recent Activity")
    with col2:
        if st.button("🔄 Refresh Logs", key="refresh_logs_button"):
            st.session_state.refresh_logs = True
            st.session_state.last_refresh_time['logs'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if st.session_state.refresh_logs:
        with st.spinner("Fetching audit logs..."):
            audit_logs = api_service.run_db_command("db-list-audit")
            st.session_state.audit_logs = audit_logs
            st.session_state.refresh_logs = False
            st.session_state.last_refresh_time['logs'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        audit_logs = st.session_state.get('audit_logs', [])
    
    # Display the raw response for debugging
    with st.expander("Debug: Raw Response"):
        st.write(audit_logs)
    
    if audit_logs and isinstance(audit_logs, list) and len(audit_logs) > 0 and isinstance(audit_logs[0], dict) and "error" not in audit_logs[0]:
        try:
            df = pd.DataFrame(audit_logs)
            st.dataframe(df)
            
            # Always show the current timestamp for last refresh
            if 'logs' in st.session_state.last_refresh_time:
                st.caption(f"Last refreshed: {st.session_state.last_refresh_time['logs']}")
            else:
                st.session_state.last_refresh_time['logs'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                st.caption(f"Last refreshed: {st.session_state.last_refresh_time['logs']}")
        except Exception as e:
            st.error(f"Error creating dataframe: {str(e)}")
            st.write("Raw data:", audit_logs)
    else:
        if audit_logs and isinstance(audit_logs, list) and len(audit_logs) > 0 and isinstance(audit_logs[0], dict) and "error" in audit_logs[0]:
            st.error(f"Error: {audit_logs[0]['error']}")
        else:
            st.info("No audit logs found or invalid response format")

def admin_predictions_tab():
    """Admin panel predictions tab"""
    st.header("Prediction History")
    
    # Add debug information in an expander
    with st.expander("Debug Information"):
        st.write(f"API URL: {api_service.security_api_url}")
        st.write(f"Authentication token present: {bool(st.session_state.token)}")
        st.write(f"Admin privileges: {st.session_state.is_admin}")
        st.write(f"Current session state keys: {list(st.session_state.keys())}")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Recent Predictions")
    with col2:
        if st.button("🔄 Refresh Predictions", key="refresh_predictions_button"):
            st.session_state.refresh_predictions = True
            st.session_state.last_refresh_time['predictions'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if st.session_state.refresh_predictions:
        with st.spinner("Fetching prediction history..."):
            predictions = api_service.run_db_command("db-list-predictions")
            st.session_state.predictions = predictions
            st.session_state.refresh_predictions = False
            st.session_state.last_refresh_time['predictions'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        predictions = st.session_state.get('predictions', [])
    
    # Display the raw response for debugging
    with st.expander("Debug: Raw Response"):
        st.write(f"Type of predictions: {type(predictions)}")
        st.write(f"Content of predictions: {predictions}")
    
    # Handle empty predictions case
    if not predictions or not isinstance(predictions, list) or len(predictions) == 0:
        st.info("No prediction history found")
        if 'predictions' in st.session_state.last_refresh_time:
            st.caption(f"Last refreshed: {st.session_state.last_refresh_time['predictions']}")
        return
    
    # Handle error case
    if isinstance(predictions, list) and len(predictions) > 0:
        if isinstance(predictions[0], dict) and "error" in predictions[0]:
            st.error(f"Error: {predictions[0]['error']}")
            if 'predictions' in st.session_state.last_refresh_time:
                st.caption(f"Last refreshed: {st.session_state.last_refresh_time['predictions']}")
            return
    
    # Process valid predictions
    try:
        # Process the predictions data to extract more information
        processed_predictions = []
        
        for pred in predictions:
            if not isinstance(pred, dict):
                continue
                
            details = pred.get('details', '')
            # Extract prediction method and result if available
            method = 'unknown'
            result = 'unknown'
            if details and isinstance(details, str) and 'using method:' in details:
                method_part = details.split('using method:')[1].strip()
                if ', result:' in method_part:
                    method = method_part.split(', result:')[0].strip()
                    result = method_part.split(', result:')[1].strip()
            
            processed_predictions.append({
                'timestamp': pred.get('timestamp', ''),
                'username': pred.get('username', ''),
                'action_type': pred.get('action_type', 'unknown'),
                'prediction_method': method,
                'prediction_result': result
            })
        
        # Create a DataFrame and display it
        if processed_predictions:
            df = pd.DataFrame(processed_predictions)
            st.dataframe(df)
            
            # Add timestamp to show when the data was last refreshed
            if 'predictions' in st.session_state.last_refresh_time:
                st.caption(f"Last refreshed: {st.session_state.last_refresh_time['predictions']}")
        else:
            st.info("No prediction data to display")
            if 'predictions' in st.session_state.last_refresh_time:
                st.caption(f"Last refreshed: {st.session_state.last_refresh_time['predictions']}")
            
    except Exception as e:
        st.error(f"Error processing prediction data: {str(e)}")
        st.write("Raw data:", predictions)
        if 'predictions' in st.session_state.last_refresh_time:
            st.caption(f"Last refreshed: {st.session_state.last_refresh_time['predictions']}")

def admin_data_retention_tab():
    """Admin panel data retention tab"""
    st.header("Data Retention Policy")
    
    # Initialize session state variables if they don't exist
    if 'refresh_retention' not in st.session_state:
        st.session_state.refresh_retention = False
    if 'last_refresh_time' not in st.session_state:
        st.session_state.last_refresh_time = {}
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh Policies", key="refresh_retention_button"):
            st.session_state.refresh_retention = True
            st.session_state.last_refresh_time['retention'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Data retention settings
    st.subheader("Current Data Retention Settings")
    
    # Get current data retention settings
    if st.session_state.refresh_retention:
        with st.spinner("Loading data retention settings..."):
            # Fetch data retention settings from API
            retention_settings = api_service.run_db_command("db-check-expired")
            
            if retention_settings and isinstance(retention_settings, list):
                if len(retention_settings) > 0 and isinstance(retention_settings[0], dict) and "error" in retention_settings[0]:
                    st.error(f"Error: {retention_settings[0]['error']}")
                else:
                    # Display data retention settings
                    st.dataframe(pd.DataFrame(retention_settings))
                    
                    # Show last refresh time
                    if 'retention' in st.session_state.last_refresh_time:
                        st.caption(f"Last refreshed: {st.session_state.last_refresh_time['retention']}")
            else:
                st.info("No data retention settings found or invalid response format")
    
    # Data cleanup options
    st.subheader("Data Cleanup Options")
    
    if st.button("Clean Up Expired Data", key="cleanup_button"):
        with st.spinner("Cleaning up expired data..."):
            # Run cleanup command
            cleanup_result = api_service.run_db_command("db-cleanup-expired")
            
            if cleanup_result and isinstance(cleanup_result, list):
                if len(cleanup_result) > 0 and isinstance(cleanup_result[0], dict) and "error" in cleanup_result[0]:
                    st.error(f"Error: {cleanup_result[0]['error']}")
                else:
                    st.success("Expired data cleaned up successfully")
                    st.dataframe(pd.DataFrame(cleanup_result))
            else:
                st.error("Failed to clean up expired data or invalid response format")

def admin_database_tab():
    """Admin panel database tab"""
    st.header("Database Management")
    
    # Initialize session state variables if they don't exist
    if 'db_command' not in st.session_state:
        st.session_state.db_command = "db-list-users"
    if 'refresh_db' not in st.session_state:
        st.session_state.refresh_db = False
    if 'db_results' not in st.session_state:
        st.session_state.db_results = []
    
    col1, col2 = st.columns([3, 1])
    with col1:
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
            ],
            index=0
        )
    with col2:
        if st.button("🔄 Run Command", key="run_db_command_button"):
            st.session_state.refresh_db = True
            st.session_state.db_command = db_command
            if 'last_refresh_time' not in st.session_state:
                st.session_state.last_refresh_time = {}
            st.session_state.last_refresh_time['db'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if st.session_state.refresh_db:
        with st.spinner(f"Running command: {st.session_state.db_command}"):
            db_results = api_service.run_db_command(st.session_state.db_command)
            st.session_state.db_results = db_results
            st.session_state.refresh_db = False
            st.session_state.last_refresh_time['db'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        db_results = st.session_state.get('db_results', [])
    
    # Display results
    if db_results and isinstance(db_results, list) and len(db_results) > 0:
        if "error" not in db_results[0]:
            try:
                df = pd.DataFrame(db_results)
                st.dataframe(df)
            except Exception as e:
                st.error(f"Error creating dataframe: {str(e)}")
                st.write("Raw results:", db_results)
        else:
            st.error(f"Error: {db_results[0]['error']}")
    elif db_results and isinstance(db_results, dict):
        st.json(db_results)
    else:
        st.info("No results to display")
    
    # Add timestamp to show when the command was last run
    if 'db' in st.session_state.last_refresh_time:
        st.caption(f"Last run: {st.session_state.last_refresh_time['db']}")
