"""Helper script to obtain Gmail API refresh token."""

import os
import json
import socket
import webbrowser
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from urllib.parse import urlparse

def is_port_in_use(port):
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return False
        except OSError:
            return True

def get_redirect_uris(client_secrets_file):
    """Extract redirect URIs from client secrets file."""
    try:
        with open(client_secrets_file, 'r') as f:
            config = json.load(f)
        return config['web']['redirect_uris']
    except Exception as e:
        print(f"Error reading redirect URIs: {e}")
        return []

def get_gmail_token(client_secrets_file):
    """Get Gmail API refresh token using OAuth 2.0 flow."""
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    # Read registered redirect URIs first
    redirect_uris = get_redirect_uris(client_secrets_file)
    if not redirect_uris:
        print("⚠️ No redirect URIs found in client secrets file!")
        print("Please make sure your client secrets file is valid and contains web.redirect_uris")
        return
    
    print("\nRegistered redirect URIs in your client secrets file:")
    for uri in redirect_uris:
        print(f"  - {uri}")
    
    # Try to find an available port from the registered URIs
    available_uri = None
    available_port = None
    
    for uri in redirect_uris:
        try:
            port = int(urlparse(uri).port)
            if not is_port_in_use(port):
                available_uri = uri
                available_port = port
                break
        except:
            continue
    
    if available_port is None:
        print("\n⚠️ All registered ports are in use! Let's try a random available port.")
        # Try some other ports
        for port in range(8090, 8110):
            if not is_port_in_use(port):
                available_port = port
                print(f"Found available port: {available_port}")
                print(f"⚠️ Warning: Using port {available_port}, which is NOT in your registered URIs!")
                print(f"You need to add http://localhost:{available_port} to your Google Cloud Console")
                print("before proceeding. Would you like to:")
                print("1. Continue anyway (likely to fail)")
                print("2. Exit and update Google Cloud Console first")
                
                choice = input("Enter choice (1/2): ").strip()
                if choice != "1":
                    print("Exiting. Please update your Google Cloud Console and try again.")
                    return
                break
        
        if available_port is None:
            print("❌ Could not find any available port. Please close some applications and try again.")
            return
    else:
        print(f"\nFound available registered port: {available_port}")
        print(f"Using redirect URI: {available_uri}")
    
    try:
        # Start OAuth 2.0 flow
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_file,
            SCOPES
        )
        
        # Run local server for auth with the port from redirect URI
        creds = flow.run_local_server(port=available_port)
        
        # Get the refresh token
        refresh_token = creds.refresh_token
        
        # Load client secrets to get client_id and client_secret
        with open(client_secrets_file, 'r') as f:
            client_config = json.load(f)
        
        web_config = client_config['web']
        
        print("\n✅ Authentication successful!")
        print("\nGmail API Credentials:")
        print("-" * 50)
        print(f"Client ID: {web_config['client_id']}")
        print(f"Client Secret: {web_config['client_secret']}")
        print(f"Refresh Token: {refresh_token}")
        print("-" * 50)
        print("\nAdd these as secrets in your GitHub repository or environment variables:")
        print("1. GMAIL_CLIENT_ID")
        print("2. GMAIL_CLIENT_SECRET") 
        print("3. GMAIL_REFRESH_TOKEN")
        print("4. GMAIL_FROM_EMAIL (add your Gmail address)")
        
    except Exception as e:
        print(f"\n❌ Error obtaining token: {str(e)}")
        
        if "redirect_uri_mismatch" in str(e):
            print("\nREDIRECT URI MISMATCH ERROR")
            print("-" * 50)
            print("The redirect URI in your code doesn't match what's in Google Cloud Console.")
            print(f"Attempted to use: http://localhost:{available_port}/")
            print("\nFollow these steps to fix it:")
            print("\nOption 1: Update Google Cloud Console (Recommended)")
            print("1. Go to https://console.cloud.google.com/apis/credentials")
            print("2. Find and edit your OAuth 2.0 Client ID")
            print(f"3. Add 'http://localhost:{available_port}/' to the list of Authorized redirect URIs")
            print("4. Click Save and try running this script again")
        else:
            print("\nTroubleshooting steps:")
            print("1. Verify OAuth consent screen is properly configured")
            print("2. Make sure Gmail API is enabled in your Google Cloud project")
            print("3. Verify you're using a Web application OAuth client ID")
            print("4. Check that your email is added as a test user")
            print("\nAdditional debugging info:")
            print(f"Used port: {available_port}")

if __name__ == '__main__':
    print("Gmail Token Generator")
    print("=" * 50)
    print("\nThis script will help you obtain the necessary Gmail API credentials for the website tracker.")
    
    # Suggest killing any local development servers
    print("\nTIP: If you have web servers or other services running on ports 8080-8085,")
    print("you might want to stop them before proceeding.")
    
    client_secrets_path = input("\nEnter path to client secrets JSON file: ").strip()
    
    if os.path.exists(client_secrets_path):
        get_gmail_token(client_secrets_path)
    else:
        print(f"\n❌ Error: File not found at {client_secrets_path}")
        print("\nPlease make sure you've downloaded the client secrets JSON file from Google Cloud Console:")
        print("1. Go to https://console.cloud.google.com/apis/credentials")
        print("2. Click on the download icon next to your OAuth 2.0 Client ID")
        print("3. Save the file and provide the correct path")
