import pyrebase

# Standard Config
config = {
  "apiKey": "AIzaSyAiRAbssdrEqgXOWu6PnkdTZxIiomWsB-Q",
  "authDomain": "moringa-39e76.firebaseapp.com",
  "databaseURL": "",
  "storageBucket": "moringa-39e76.appspot.com"
}

# Init Pyrebase
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

# Main function to Auth
def authenticate(email, password):
  user = auth.create_user_with_email_and_password(email, password)
  return user

# Sign In With Email and Password
def signIn(email, password):
  user = auth.sign_in_with_email_and_password(email, password)
  return user

# Verify Email Just in Case
def verify(idToken):
  auth.send_email_verification(idToken)

# Password Reset using Current Email
def resetPassword(email):
  auth.send_password_reset_email(email)

# Send Account Info (Can be for If account is Verified)
def accountInfo(idToken):
  info = auth.get_account_info(idToken)
  return info
  