from random import randint

baseUser = [{"name": "Michael Bengawan", "password": "12345678", "role": "admin", "dateOfBirth": "31/12/2003", "email": "michael.bengawan@moringa.com", "id": 3}]
# Create a new ID
def getNewID(baseUser):
    newNumber = randint(1, 5)
    check = False
    for x in baseUser:
        if x['id'] == newNumber:
           check = True 
    if check == False:
        return newNumber 
    else:
        return getNewID(baseUser)
    
# Create a new Email
def getNewEmail(baseUser, username):
    formattedUsername = username.lower().replace(" ", ".")
    newEmail = formattedUsername + "@moringa.com"
    check = False
    for x in baseUser:
        if x['email'] == newEmail:
            check = True
    if check == True:
        extraDigit = randint(1, 10)
        formattedUsername = formattedUsername + extraDigit.__str__()
        return getNewEmail(baseUser, formattedUsername)
    else:
        return newEmail