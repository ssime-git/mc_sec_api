"""
OAuth2 Demo Launcher

This script launches all three servers (Auth, Resource, and Client) in parallel
using multiprocessing. It also provides a clean shutdown mechanism.
"""

import multiprocessing
import sys
import time
import webbrowser
import signal
import logging
from auth_server.auth_server import app as auth_app
from resource_server.resource_server import app as resource_app
from client_app.client_app import app as client_app

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [LAUNCHER] %(message)s'
)
logger = logging.getLogger(__name__)

def run_auth_server():
    """Run the Authorization Server on port 5050"""
    logger.info("Starting Authorization Server on port 5050")
    auth_app.run(port=5050)

def run_resource_server():
    """Run the Resource Server on port 5051"""
    logger.info("Starting Resource Server on port 5051")
    resource_app.run(port=5051)

def run_client_app():
    """Run the Client Application on port 5052"""
    logger.info("Starting Client Application on port 5052")
    client_app.run(port=5052)

def main():
    # Create processes for each server
    auth_process = multiprocessing.Process(target=run_auth_server)
    resource_process = multiprocessing.Process(target=run_resource_server)
    client_process = multiprocessing.Process(target=run_client_app)
    
    # List to keep track of all processes
    processes = [auth_process, resource_process, client_process]
    
    try:
        logger.info("=== Starting OAuth2 Demo ===")
        
        # Start all processes
        for p in processes:
            p.start()
            time.sleep(1)  # Small delay to ensure orderly startup
        
        logger.info("All servers are running!")
        logger.info("Authorization Server: http://localhost:5050")
        logger.info("Resource Server: http://localhost:5051")
        logger.info("Client Application: http://localhost:5052")
        
        # Open the client app in the default browser
        webbrowser.open('http://localhost:5052')
        
        logger.info("\nPress Ctrl+C to stop all servers...")
        
        # Wait for all processes
        for p in processes:
            p.join()
            
    except KeyboardInterrupt:
        logger.info("\nShutting down all servers...")
        
        # Terminate all processes
        for p in processes:
            if p.is_alive():
                p.terminate()
                p.join()
        
        logger.info("All servers stopped successfully!")
        sys.exit(0)

if __name__ == '__main__':
    # Improve handling of Ctrl+C
    signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))
    main()