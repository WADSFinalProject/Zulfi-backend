from fastapi import FastAPI, Response, status, HTTPException, Depends, Cookie
from pydantic import BaseModel
from random import randint
from firebaseAPI import firebaseAPIObject
import models
from database import engine, get_db
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import datetime
from uuid import UUID
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
from fastapi_sessions.session_verifier import SessionVerifier
from fastapi import HTTPException
from uuid import uuid4
from fastapi import FastAPI, Response
from fastapi import Depends
from typing import Optional

# Rest of the code...


# Users

class User(BaseModel):
    email: str
    password: str
    name: str
    role: str
    dateOfBirth: str 

class UpdateUser(BaseModel):
    email: Optional[str]
    name: Optional[str]
    role: Optional[str]
    dateOfBirth: Optional[str]

class LogInUser(BaseModel):
    email: str
    password: str

class EmailUser(BaseModel):
    email: str
    
models.Base.metadata.create_all(bind=engine)
app = FastAPI()
firebase = firebaseAPIObject()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000", "https://test-backend-k9s7.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def setting(response: Response, refreshToken, sessionToken):
    response.set_cookie(key= refreshToken, value= sessionToken, httponly=True)
    return True

def reading(refresh_token = Cookie(None)):
    return refresh_token
    
# Create a new Email
def getNewEmail(baseUser, username):
    formattedUsername = username.lower().replace(" ", ".")
    newEmail = formattedUsername + "@moringa.com"
    check = False
    for x in baseUser:
        if x.email == newEmail:
            check = True
    if check == True:
        extraDigit = randint(1, 10)
        formattedUsername = formattedUsername + extraDigit.__str__()
        return getNewEmail(baseUser, formattedUsername)
    else:
        return newEmail

@app.get("/users", tags=["Users"])
def get_all_users(db: Session = Depends(get_db)):
    userAll = db.query(models.User).all()
    return {"all_user": userAll}

@app.get("/users/{id}", tags=["Users"] )
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.idUser == id).first()
    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {id} was not found")
    return {"user": user}

@app.post("/users/email/", tags=["Users"] )
def get_user(data: EmailUser, db: Session = Depends(get_db)):
    dataDict = data.model_dump()
    user = db.query(models.User).filter(models.User.email == dataDict['email']).first()
    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with email: {dataDict['email']} was not found")
    return {"user": user}

@app.post("/users", status_code=status.HTTP_201_CREATED, tags=["Users"])
def add_user(data: User, db: Session = Depends(get_db)):
    userDict = data.model_dump()
    user = firebase.createAuth(userDict["email"], userDict.pop("password"))
    print(user)

    userDict["phoneNumber"] = None
    userDict["gender"] = None
    userDict["sessionKey"] = None
    userDict["pending"] = True
    userDict["languange"] = "English"
    
    newUser = models.User(**userDict)
    db.add(newUser)
    db.commit()
    db.refresh(newUser)

    return {"User has been added" : newUser}

@app.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Users"])
def delete_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.idUser == id)
    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"user with id: {id} was not found")
    user.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/users/{id}", tags=["Users"])
def update_user(id: int, user: UpdateUser,  db: Session = Depends(get_db)):
    print(user)
    getUser = db.query(models.User).filter(models.User.idUser == id)
    selectedUser = getUser.first()
    if selectedUser == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"user with id: {id} was not found")
    getUser.update(user.model_dump(), synchronize_session=False)

    db.commit()
    return {"Updated User" : getUser.first()}

class PendingUser(BaseModel):
    pending: bool

@app.put("/users/pending/{id}", tags=["Users"])
def update_user(id: int, user: PendingUser,  db: Session = Depends(get_db)):
    print(user)
    getUser = db.query(models.User).filter(models.User.idUser == id)
    selectedUser = getUser.first()
    if selectedUser == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"user with id: {id} was not found")
    getUser.update(user.model_dump(), synchronize_session=False)

    db.commit()
    return {"Updated User" : getUser.first()}


@app.post("/logins", status_code=status.HTTP_200_OK, tags=["Users"])
def add_user(data: LogInUser, db: Session = Depends(get_db)):
    stuff = data.model_dump()
    user = firebase.signIn(stuff['email'], stuff['password'])
    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "user was not found")
    return {
            "User has been auth" : user['email'],
            "registered": user['registered'] 
            }

# Sessions

class SessionData(BaseModel):
    username: str

cookie_params = CookieParameters(
    secure=False,
    httponly=True,
    samesite= 'none'
)

cookie = SessionCookie(
    cookie_name="cookie",
    identifier="general_verifier",
    auto_error=True,
    secret_key="DONOTUSE",
    cookie_params=cookie_params,
)

backend = InMemoryBackend[UUID, SessionData]()

class BasicVerifier(SessionVerifier[UUID, SessionData]):
    def __init__(
        self,
        *,
        identifier: str,
        auto_error: bool,
        backend: InMemoryBackend[UUID, SessionData],
        auth_http_exception: HTTPException,
    ):
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception

    @property
    def identifier(self):
        return self._identifier

    @property
    def backend(self):
        return self._backend

    @property
    def auto_error(self):
        return self._auto_error

    @property
    def auth_http_exception(self):
        return self._auth_http_exception

    def verify_session(self, model: SessionData) -> bool:
        """If the session exists, it is valid"""
        return True


verifier = BasicVerifier(
    identifier="general_verifier",
    auto_error=True,
    backend=backend,
    auth_http_exception=HTTPException(status_code=403, detail="invalid session"),
)

@app.post("/create_session/{name}", tags=["Sessions"])
async def create_session(name: str, response: Response):

    session = uuid4()
    data = SessionData(username=name)

    await backend.create(session, data)
    cookie.attach_to_response(response, session)

    return f"created session for {name}"

@app.post("/whoami", dependencies=[Depends(cookie)], tags=["Sessions"])
async def whoami(session_data: SessionData = Depends(verifier)):
    return session_data

@app.post("/delete_session", tags=["Sessions"])
async def del_session(response: Response, session_id: UUID = Depends(cookie)):
    await backend.delete(session_id)
    cookie.delete_from_response(response)
    return "deleted session"

# Notification

class Notification(BaseModel):
    idUser: int
    title: str
    description: str
    seen: bool

@app.get("/notifications/{id}", tags=["Notifications"])
def get_notification(id: int, db: Session = Depends(get_db)):
    notifs = db.query(models.Notification).filter(models.Notification.idUser == id).all()
    if notifs == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"notification with id: {id} was not found")
    return {"notification": notifs}

@app.post("/notifications", status_code=status.HTTP_201_CREATED, tags=["Notifications"])
def add_notification(data: Notification, db: Session = Depends(get_db)):
    NotifDict = data.model_dump()
    print(NotifDict)
    newNotif = models.Notification(**NotifDict)
    db.add(newNotif)
    db.commit()
    db.refresh(newNotif)

    return {"Notif has been Created" : newNotif}

# Centra

class Centra(BaseModel):
    manager: str
    phone: int
    location: str
    geoCodeX: float
    geoCodeY: float

@app.get("/centras", tags=["Centras"])
def get_all_centras(db: Session = Depends(get_db)):
    centraAll = db.query(models.Centra).all()
    return {"all_centra": centraAll}

@app.post("/centras", status_code=status.HTTP_201_CREATED, tags=["Centras"])
def add_centra(data: Centra, db: Session = Depends(get_db)):
    centraDict = data.model_dump()
    newCentra = models.Centra(**centraDict)
    db.add(newCentra)
    db.commit()
    db.refresh(newCentra)

    return {"Centra has been added" : newCentra}

@app.delete("/centras/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Centras"])
def delete_centra(id: int, db: Session = Depends(get_db)):
    centra = db.query(models.Centra).filter(models.Centra.idCentra == id)
    if centra == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"centra with id: {id} was not found")
    centra.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/centras/{id}", tags=["Centras"])
def update_centra(id: int, centra: Centra,  db: Session = Depends(get_db)):
    getCentra = db.query(models.Centra).filter(models.Centra.id == id)
    selectedCentra = getCentra.first()
    if selectedCentra == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"centra with id: {id} was not found")
    getCentra.update(centra.model_dump(), synchronize_session=False)

    db.commit()
    return {"Updated Centra" : getCentra.first()}

# WetLeaves

class WetLeaves(BaseModel):
    idCentra: int
    expired: bool
    weight: int
    timeToExpired: datetime.datetime

@app.get("/wetleaves", tags=["WetLeaves"])
def get_all_wetleaves(db: Session = Depends(get_db)):
    wetleaveAll = db.query(models.WetLeaves).all()
    return {"all_wet": wetleaveAll}

@app.post("/wetleaves", status_code=status.HTTP_201_CREATED, tags=["WetLeaves"])
def add_wet(data: WetLeaves, db: Session = Depends(get_db)):
    wetleaveDict = data.model_dump()
    newWetLeaf = models.WetLeaves(**wetleaveDict)
    db.add(newWetLeaf)
    db.commit()
    db.refresh(newWetLeaf)
    return {"WetLeaf has been added" : newWetLeaf}

@app.delete("/wetleaves/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["WetLeaves"])
def delete_wetleaf(id: int, db: Session = Depends(get_db)):
    wetleaf = db.query(models.WetLeaves).filter(models.WetLeaves.idWet == id)
    if wetleaf == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"wetleaf with id: {id} was not found")
    wetleaf.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/wetleaves/{id}", tags=["WetLeaves"])
def update_wetleaf(id: int, wet: WetLeaves,  db: Session = Depends(get_db)):
    getWetLeaves = db.query(models.WetLeaves).filter(models.WetLeaves.idWet == id)
    selectedWet = getWetLeaves.first()
    if selectedWet == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"wetleaf with id: {id} was not found")
    getWetLeaves.update(wet.model_dump(), synchronize_session=False)

    db.commit()
    return {"Updated Wet Leaves" : getWetLeaves.first()}

# Dry Leaves

class DryLeaves(BaseModel):
    idCentra: int
    idMachine: int
    weight: int
    timeToExpired: datetime.datetime

@app.get("/dryleaves", tags=["DryLeaves"])
def get_all_Dryleaves(db: Session = Depends(get_db)):
    DryleaveAll = db.query(models.DryLeaves).all()
    return {"all_dry": DryleaveAll}

@app.post("/dryleaves", status_code=status.HTTP_201_CREATED, tags=["DryLeaves"])
def add_Dry(data: DryLeaves, db: Session = Depends(get_db)):
    DryleaveDict = data.model_dump()
    newDryLeaf = models.DryLeaves(**DryleaveDict)
    db.add(newDryLeaf)
    db.commit()
    db.refresh(newDryLeaf)
    return {"DryLeaf has been added" : newDryLeaf}

@app.delete("/dryleaves/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["DryLeaves"])
def delete_Dryleaf(id: int, db: Session = Depends(get_db)):
    Dryleaf = db.query(models.DryLeaves).filter(models.DryLeaves.idDry == id)
    if Dryleaf == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Dryleaf with id: {id} was not found")
    Dryleaf.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/dryleaves/{id}", tags=["DryLeaves"])
def update_Dryleaf(id: int, Dry: DryLeaves,  db: Session = Depends(get_db)):
    getDryLeaves = db.query(models.DryLeaves).filter(models.DryLeaves.idDry == id)
    selectedDry = getDryLeaves.first()
    if selectedDry == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Dryleaf with id: {id} was not found")
    getDryLeaves.update(Dry.model_dump(), synchronize_session=False)

    db.commit()
    return {"Updated Dry Leaves" : getDryLeaves.first()}

# Flour

class Flour(BaseModel):
    idCentra: int
    idMachine: int
    weight: int
    timeToExpired: datetime.datetime

@app.get("/flours", tags=["Flour"])
def get_all_Flours(db: Session = Depends(get_db)):
    FlourleaveAll = db.query(models.Flour).all()
    return {"all_Flour": FlourleaveAll}

@app.post("/flours", status_code=status.HTTP_201_CREATED, tags=["Flour"])
def add_Flour(data: Flour, db: Session = Depends(get_db)):
    FlourleaveDict = data.model_dump()
    newFlour = models.Flour(**FlourleaveDict)
    db.add(newFlour)
    db.commit()
    db.refresh(newFlour)
    return {"Flour has been added" : newFlour}

@app.delete("/flours/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Flour"])
def delete_Flour(id: int, db: Session = Depends(get_db)):
    Flour = db.query(models.Flour).filter(models.Flour.idFlour == id)
    if Flour == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Flour with id: {id} was not found")
    Flour.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/flours/{id}", tags=["Flour"])
def update_Flour(id: int, Flour: Flour,  db: Session = Depends(get_db)):
    getFlours = db.query(models.Flour).filter(models.Flour.idFlour == id)
    selectedFlour = getFlours.first()
    if selectedFlour == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Flour with id: {id} was not found")
    getFlours.update(Flour.model_dump(), synchronize_session=False)

    db.commit()
    return {"Updated Flour " : getFlours.first()}

# Shipment

class Shipment(BaseModel):
    idCentra: int
    orderNumber: str
    address: str
    status: str
    weight: int
    provider: str
    estimated: datetime.datetime
    orderDetails: str
    stage: int

@app.get("/shipments", tags=["Shipments"])
def get_all_shipments(db: Session = Depends(get_db)):
    shipmentAll = db.query(models.Shipment).all()
    return {"all_shipment": shipmentAll}

@app.post("/shipments", status_code=status.HTTP_201_CREATED, tags=["Shipments"])
def add_shipment(data: Shipment, db: Session = Depends(get_db)):
    shipmentDict = data.model_dump()
    newShipment = models.Shipment(**shipmentDict)
    db.add(newShipment)
    db.commit()
    db.refresh(newShipment)

    return {"Shipment has been added" : newShipment}

@app.delete("/shipments/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Shipments"])
def delete_shipment(id: int, db: Session = Depends(get_db)):
    shipment = db.query(models.Shipment).filter(models.Shipment.idShipment == id)
    if shipment == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"shipment with id: {id} was not found")
    shipment.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/shipments/{id}", tags=["Shipments"])
def update_shipment(id: int, shipment: Shipment,  db: Session = Depends(get_db)):
    getShipment = db.query(models.Shipment).filter(models.Shipment.idShipment == id)
    selectedShipment = getShipment.first()
    if selectedShipment == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"shipment with id: {id} was not found")
    getShipment.update(shipment.model_dump(), synchronize_session=False)

    db.commit()
    return {"Updated Shipment" : getShipment.first()}

# Storage

class Storage(BaseModel):
    idShipment: int
    provider: str
    weight: int
    arrival: datetime.datetime
    isRescaled: bool = False
    rescaledDate: datetime.datetime
    expiredDate: datetime.datetime

class StorageWeightUpdate(BaseModel):
    weight: int
    isRescaled: Optional[bool] = True

@app.get("/storages", tags=["Storages"])
def get_all_storages(db: Session = Depends(get_db)):
    storageAll = db.query(models.Storage).all()
    return {"all_storage": storageAll}

@app.get("/storages/{id}", tags=["Storages"])
def get_storage(id: int, db: Session = Depends(get_db)):
    storage = db.query(models.Storage).filter(models.Storage.idStorage == id).first()
    if storage == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"storage with id: {id} was not found")
    return {"storage": storage}

@app.post("/storages", status_code=status.HTTP_201_CREATED, tags=["Storages"])
def add_storage(data: Storage, db: Session = Depends(get_db)):
    storageDict = data.model_dump()
    newStorage = models.Storage(**storageDict)
    db.add(newStorage)
    db.commit()
    db.refresh(newStorage)

    return {"Storage has been added" : newStorage}

@app.delete("/storages/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Storages"])
def delete_storage(id: int, db: Session = Depends(get_db)):
    storage = db.query(models.Storage).filter(models.Storage.idStorage == id)
    if storage == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"storage with id: {id} was not found")
    storage.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/storages/put/{id}", tags=["Storages"])
def update_storage_weight(id: int, storage: StorageWeightUpdate, db: Session = Depends(get_db)):
    selected_storage = db.query(models.Storage).filter(models.Storage.idStorage == id).first()
    if selected_storage is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Storage with id: {id} was not found")

    # Update weight and isRescaled
    db.query(models.Storage).filter(models.Storage.idStorage == id).update({
        "weight": storage.weight,
        "isRescaled": True
    }, synchronize_session=False)
    db.commit()

    # Fetch and return the updated storage
    updated_storage = db.query(models.Storage).filter(models.Storage.idStorage == id).first()
    return {"Updated Storage": updated_storage}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=True)