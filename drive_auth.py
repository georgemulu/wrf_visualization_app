from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

def authenticate_drive():
    gauth = GoogleAuth()
    gauth.DEFAULT_SETTINGS['client_config_file'] = "client_secrets.json"  # Use your file here

    # Load access credentials if previously saved
    gauth.LoadCredentialsFile("credentials.json")

    if gauth.credentials is None:
        gauth.LocalWebserverAuth()  # Will prompt browser login
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()

    gauth.SaveCredentialsFile("credentials.json")  # Save session for reuse
    return GoogleDrive(gauth)
