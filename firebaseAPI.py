import firebase_admin.auth
import pyrebase
import firebase_admin

class firebaseAPIObject():
  def __init__(self):
     # Standard Config for Pyrebase
    self.config = {
      "apiKey": "AIzaSyAiRAbssdrEqgXOWu6PnkdTZxIiomWsB-Q",
      "authDomain": "moringa-39e76.firebaseapp.com",
      "databaseURL": "",
      "storageBucket": "moringa-39e76.appspot.com"
    }
    # Init Pyrebase
    self.firebase = pyrebase.initialize_app(self.config)
    self.auth = self.firebase.auth()

    # Creds for Firebase Admin
    self.creds = firebase_admin.credentials.Certificate('moringa-39e76-firebase-adminsdk-3xdw4-b741d945f3.json')
    self.firebaseAdmin = firebase_admin.initialize_app(self.creds)

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
  
  def setSessions(self, idToken):
    sessionToken = firebase_admin.auth.create_session_cookie(id_token=idToken)
    return sessionToken
  
  def verifySession(self, sessionCookie):
    verifiedUser = firebase_admin.auth.verify_session_cookie(session_cookie=sessionCookie)
    print(verifiedUser)