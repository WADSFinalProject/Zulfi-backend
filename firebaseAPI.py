import pyrebase
class firebaseAPIObject():
  def __init__(self):
     # Standard Config
    self.config = {
      "apiKey": "AIzaSyAiRAbssdrEqgXOWu6PnkdTZxIiomWsB-Q",
      "authDomain": "moringa-39e76.firebaseapp.com",
      "databaseURL": "",
      "storageBucket": "moringa-39e76.appspot.com"
    }
    # Init Pyrebase
    self.firebase = pyrebase.initialize_app(self.config)
    self.auth = self.firebase.auth()

  # Main function to Auth
  def createAuth(self, email, password):
    user = self.auth.create_user_with_email_and_password(email, password)
    return user

  # Sign In With Email and Password
  def signIn(self, email, password):
    user = self.auth.sign_in_with_email_and_password(email, password)
    return user

  # Verify Email Just in Case
  def verify(self, idToken):
    self.auth.send_email_verification(idToken)

  # Password Reset using Current Email
  def resetPassword(self, email):
    self.auth.send_password_reset_email(email)

  # Send Account Info (Can be for If account is Verified)
  def accountInfo(self, idToken):
    info = self.auth.get_account_info(idToken)
    return info
  