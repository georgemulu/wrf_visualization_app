from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

def authenticate_drive():
    gauth = GoogleAuth()
    
    # Configure settings properly
    settings = {
        "client_config_file": "client_secrets.json",
        "save_credentials": True,
        "save_credentials_backend": "file",
        "save_credentials_file": "credentials.json",  # Explicit file path
        "get_refresh_token": True,
        "oauth_scope": ["https://www.googleapis.com/auth/drive"]
    }
    
    # Apply settings
    gauth.settings.update(settings)
    
    # Force offline access and consent for refresh token
    gauth.CommandLineAuth()  # Alternative to LocalWebserverAuth
    
    # Try to load existing credentials
    try:
        gauth.LoadCredentialsFile("credentials.json")
    except:
        pass  # Ignore if file doesn't exist
    
    # Authenticate if needed
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()  # This will open browser for auth
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    
    # Save credentials properly
    gauth.SaveCredentialsFile("credentials.json")
    return GoogleDrive(gauth)