def admin_data_retention_tab():
    """Admin panel data retention tab"""
    import streamlit as st
    import pandas as pd
    from datetime import datetime
    import api_service
    
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
            retention_settings = api_service.APIService().run_db_command("db-check-expired")
            
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
            cleanup_result = api_service.APIService().run_db_command("db-cleanup-expired")
            
            if cleanup_result and isinstance(cleanup_result, list):
                if len(cleanup_result) > 0 and isinstance(cleanup_result[0], dict) and "error" in cleanup_result[0]:
                    st.error(f"Error: {cleanup_result[0]['error']}")
                else:
                    st.success("Expired data cleaned up successfully")
                    st.dataframe(pd.DataFrame(cleanup_result))
            else:
                st.error("Failed to clean up expired data or invalid response format")
