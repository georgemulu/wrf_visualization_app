from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

def authenticate_drive():
    gauth = GoogleAuth()

    # ✅ SETUP BACKEND CONFIGURATION HERE
    gauth.settings['client_config_backend'] = 'file'
    gauth.settings['client_config_file'] = 'client_secrets.json'  # Must match your filename

    # Optional but recommended: set location to save credentials
    gauth.settings['save_credentials'] = True
    gauth.settings['save_credentials_backend'] = 'file'
    gauth.settings['save_credentials_file'] = 'credentials.json'

    # ✅ Now load saved credentials if available
    try:
        gauth.LoadCredentialsFile("credentials.json")
    except:
        pass  # Skip error if file doesn't exist

    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()

    gauth.SaveCredentialsFile("credentials.json")

    return GoogleDrive(gauth)
