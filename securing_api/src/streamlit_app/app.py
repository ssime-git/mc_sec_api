import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# Import our custom modules
from api_service import APIService
import ui_components as ui

# Initialize API service
api_service = APIService()

# Session state initialization
if 'token' not in st.session_state:
    st.session_state.token = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'refresh_users' not in st.session_state:
    st.session_state.refresh_users = True
if 'refresh_logs' not in st.session_state:
    st.session_state.refresh_logs = True
if 'refresh_db' not in st.session_state:
    st.session_state.refresh_db = True
if 'refresh_predictions' not in st.session_state:
    st.session_state.refresh_predictions = True
if 'refresh_retention' not in st.session_state:
    st.session_state.refresh_retention = True
if 'last_refresh_time' not in st.session_state:
    st.session_state.last_refresh_time = {}

# Page configuration
st.set_page_config(
    page_title="GDPR-Compliant API Dashboard",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Debug information (after page config)
st.sidebar.write(f"Using Security API URL: {api_service.security_api_url}")
st.sidebar.write(f"Using Prediction API URL: {api_service.prediction_api_url}")

# Add API connection test to sidebar
ui.connection_test()

def sidebar():
    """Sidebar navigation"""
    st.sidebar.title("Navigation")
    
    if st.session_state.token:
        st.sidebar.write(f"Logged in as: **{st.session_state.username}**")
        
        if st.session_state.is_admin:
            st.sidebar.write("**Admin privileges enabled**")
        
        page = st.sidebar.radio(
            "Select Page",
            ["Home", "Make Prediction", "Manage Consents", "My Data", "Admin Panel"] if st.session_state.is_admin else ["Home", "Make Prediction", "Manage Consents", "My Data"]
        )
        
        if st.sidebar.button("Logout"):
            st.session_state.token = None
            st.session_state.username = None
            st.session_state.is_admin = False
            st.experimental_rerun()
            
        return page
    else:
        page = st.sidebar.radio("Select Page", ["Login", "Register"])
        return page

def login_page():
    """Login page"""
    ui.login_form()

def register_page():
    """Registration page"""
    ui.register_form()

def home_page():
    """Home page"""
    st.title("GDPR-Compliant API Dashboard")
    
    st.markdown("""
    ## Welcome to the GDPR-Compliant API System
    
    This dashboard allows you to interact with our GDPR-compliant API system, which includes:
    
    - **Secure Authentication**: Your credentials are safely stored and verified
    - **Consent Management**: Control how your data is used
    - **Data Access**: View and export your personal data
    - **Pseudonymized Predictions**: Get predictions without exposing your personal data
    
    Use the sidebar to navigate between different sections of the dashboard.
    """)
    
    # Show user information if logged in
    if st.session_state.token:
        st.success(f"You are logged in as {st.session_state.username}")
        
        # Quick links
        st.subheader("Quick Links")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Make a Prediction"):
                # Store the navigation choice in session state
                st.session_state['navigation_choice'] = "Make Prediction"
                st.experimental_rerun()
        
        with col2:
            if st.button("Manage Consents"):
                # Store the navigation choice in session state
                st.session_state['navigation_choice'] = "Manage Consents"
                st.experimental_rerun()
        
        with col3:
            if st.button("View My Data"):
                # Store the navigation choice in session state
                st.session_state['navigation_choice'] = "My Data"
                st.experimental_rerun()

def prediction_page():
    """Prediction page"""
    st.title("Make a Prediction")
    
    st.markdown("""
    This page allows you to make predictions using our machine learning model.
    Your data is pseudonymized before being sent to the prediction API, ensuring your privacy.
    """)
    
    ui.prediction_form()

def consents_page():
    """Consent management page"""
    st.title("Consent Management")
    
    st.markdown("""
    ## Manage Your Data Consents
    
    Under GDPR, you have the right to control how your data is processed and stored.
    Use this page to manage your consent preferences.
    
    - **Data Processing**: Allows us to process your data for predictions
    - **Data Storage**: Allows us to store your data for future use
    """)
    
    ui.consent_management()

def user_data_page():
    """User data page"""
    st.title("Your Data")
    
    st.markdown("""
    ## Access Your Personal Data
    
    Under GDPR, you have the right to access your personal data.
    This page allows you to view and export your data.
    """)
    
    ui.user_data_view()

def admin_panel():
    """Admin panel for managing users and viewing logs"""
    st.title("Admin Panel")
    
    if not st.session_state.is_admin:
        st.error("You do not have permission to access this page")
        return
    
    st.markdown("""
    ## Admin Panel
    
    This panel provides administrative functions for managing the GDPR-compliant API system.
    """)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Users", "Audit Logs", "Prediction History", "Database Management", "Data Retention"])
    
    with tab1:
        ui.admin_users_tab()
    
    with tab2:
        ui.admin_audit_logs_tab()
    
    with tab3:
        ui.admin_predictions_tab()
    
    with tab4:
        ui.admin_database_tab()
    
    with tab5:
        ui.admin_data_retention_tab()

def main():
    """Main application"""
    # Check if there's a navigation choice from quick links
    if 'navigation_choice' in st.session_state:
        page = st.session_state['navigation_choice']
        # Clear the navigation choice after using it
        del st.session_state['navigation_choice']
    else:
        # Get current page from sidebar
        page = sidebar()
    
    # Display appropriate page based on selection
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
    elif page == "My Data":
        user_data_page()
    elif page == "Admin Panel":
        admin_panel()

if __name__ == "__main__":
    main()
