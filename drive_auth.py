from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

def authenticate_drive():
    gauth = GoogleAuth(settings={
        "client_config_backend": "file",
        "client_config_file": "client_secrets.json",

        "save_credentials": True,
        "save_credentials_backend": "file",
        "save_credentials_file": "credentials.json",

        "oauth_scope": [
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/drive.file"
        ],
        "get_refresh_token": True,  # 🔁 Important!
        "oauth_flow_params": {
            "access_type": "offline",  # 🔁 CRITICAL!
            "prompt": "consent"        # 🔁 Forces fresh consent to get refresh_token
        }
    })

    try:
        gauth.LoadCredentialsFile("credentials.json")
    except:
        pass

    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()

    gauth.SaveCredentialsFile("credentials.json")

    return GoogleDrive(gauth)
