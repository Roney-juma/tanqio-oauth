#!/usr/bin/env python
"""
OAuth Test Client
This script demonstrates how to use the OAuth server as a client application.
"""
import requests
import webbrowser
from urllib.parse import urlencode, parse_qs, urlparse
import http.server
import socketserver
import threading
from urllib.parse import urlparse, parse_qs

class OAuthTestClient:
    def __init__(self, client_id, client_secret, base_url='http://localhost:8000'):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self.redirect_uri = 'http://localhost:8080/callback'
        self.authorization_code = None
        
    def get_authorization_url(self):
        """Generate the authorization URL"""
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'read write',
            'state': 'random-state-string'
        }
        
        auth_url = f"{self.base_url}/o/authorize/?" + urlencode(params)
        return auth_url
    
    def exchange_code_for_token(self, authorization_code):
        """Exchange authorization code for access token"""
        token_url = f"{self.base_url}/o/token/"
        
        data = {
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Token exchange failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    
    def test_protected_endpoint(self, access_token):
        """Test accessing a protected API endpoint"""
        api_url = f"{self.base_url}/api/protected/"
        
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None

def start_callback_server():
    """Start a simple server to handle OAuth callback"""
    authorization_code = None
    
    class CallbackHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            nonlocal authorization_code
            
            if self.path.startswith('/callback'):
                # Parse the authorization code from the callback URL
                parsed_url = urlparse(self.path)
                query_params = parse_qs(parsed_url.query)
                
                if 'code' in query_params:
                    authorization_code = query_params['code'][0]
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'''
                    <html><body>
                    <h2>Authorization Successful!</h2>
                    <p>You can close this window and return to the terminal.</p>
                    <script>setTimeout(function(){window.close();}, 3000);</script>
                    </body></html>
                    ''')
                else:
                    self.send_response(400)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'<html><body><h2>Authorization Failed!</h2></body></html>')
            else:
                self.send_response(404)
                self.end_headers()
    
    with socketserver.TCPServer(("", 8080), CallbackHandler) as httpd:
        print("🌐 Callback server started on http://localhost:8080")
        httpd.handle_request()  # Handle one request then stop
        return authorization_code

def main():
    print("🧪 OAuth Test Client")
    print("=" * 40)
    
    # You'll need to replace these with actual values after running setup_oauth.py
    print("ℹ️  Make sure you have:")
    print("   1. Run python setup_oauth.py")
    print("   2. Started your Django server (python manage.py runserver)")
    print("   3. Have the OAuth application credentials")
    print()
    
    client_id = input("Enter OAuth Client ID: ").strip()
    if not client_id:
        print("❌ Client ID is required")
        return
    
    client_secret = input("Enter OAuth Client Secret: ").strip()
    if not client_secret:
        print("❌ Client Secret is required")
        return
    
    # Create OAuth client
    oauth_client = OAuthTestClient(client_id, client_secret)
    
    # Step 1: Get authorization URL
    auth_url = oauth_client.get_authorization_url()
    print(f"🔗 Authorization URL: {auth_url}")
    print()
    
    # Step 2: Open browser and start callback server
    print("🚀 Opening browser for authorization...")
    print("📡 Starting callback server...")
    
    # Start the callback server in a separate thread
    server_thread = threading.Thread(target=lambda: start_callback_server())
    server_thread.daemon = True
    server_thread.start()
    
    # Open the authorization URL in browser
    webbrowser.open(auth_url)
    
    # Wait for the callback
    server_thread.join()
    
    # Get the authorization code (this is a simplified approach)
    authorization_code = input("Enter the authorization code from the callback: ").strip()
    
    if not authorization_code:
        print("❌ Authorization code is required")
        return
    
    # Step 3: Exchange code for token
    print("🔄 Exchanging authorization code for access token...")
    token_response = oauth_client.exchange_code_for_token(authorization_code)
    
    if token_response:
        print("✅ Token exchange successful!")
        print(f"📋 Token Response: {token_response}")
        
        access_token = token_response.get('access_token')
        
        if access_token:
            # Step 4: Test protected endpoint
            print("🧪 Testing protected API endpoint...")
            api_response = oauth_client.test_protected_endpoint(access_token)
            
            if api_response:
                print("✅ Protected API access successful!")
                print(f"📋 API Response: {api_response}")
            else:
                print("❌ Protected API access failed!")
        else:
            print("❌ No access token received!")
    else:
        print("❌ Token exchange failed!")

if __name__ == '__main__':
    main()
