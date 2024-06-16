from fastapi import FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
from random import randint
from .firebaseAPI import firebaseAPIObject
from . import models
from .database import engine, get_db
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import datetime

# Users

class User(BaseModel):
    email: str
    password: str
    name: str
    role: str
    dateOfBirth: str 

class UpdateUser(BaseModel):
    email: str
    password: str
    name: str
    role: str
    dateOfBirth: str
    phoneNumber: int
    gender: str
    sessionKey: str
    pending: bool
    languange: str
    
models.Base.metadata.create_all(bind=engine)
app = FastAPI()
firebase = firebaseAPIObject()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
    
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

@app.post("/users", status_code=status.HTTP_201_CREATED, tags=["Users"])
def add_user(data: User, db: Session = Depends(get_db)):
    userDict = data.model_dump()
    user = firebase.createAuth(userDict["email"], userDict.pop("password"))

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
def update_user(id: int, user: User,  db: Session = Depends(get_db)):
    getUser = db.query(models.User).filter(models.User.idUser == id)
    selectedUser = getUser.first()
    if selectedUser == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"user with id: {id} was not found")
    getUser.update(user.model_dump(), synchronize_session=False)

    db.commit()
    return {"Updated User" : getUser.first()}

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
    newNotif = models.Notification(*NotifDict)
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
    getShipment = db.query(models.Shipment).filter(models.Shipment.id == id)
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
    isRescaled: bool
    rescaledDate: datetime.datetime
    expiredDate: datetime.datetime
    timeCreated: datetime.datetime

@app.get("/storages", tags=["Storages"])
def get_all_storages(db: Session = Depends(get_db)):
    storageAll = db.query(models.Storage).all()
    return {"all_storage": storageAll}

@app.get("/storages/{id}", tags=["Storages"])
def get_storage(id: int, db: Session = Depends(get_db)):
    storage = db.query(models.Storage).filter(models.Storage.id == id).first()
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

@app.put("/storages/{id}", tags=["Storages"])
def update_storage(id: int, storage: Storage,  db: Session = Depends(get_db)):
    getStorage = db.query(models.Storage).filter(models.Storage.id == id)
    selectedStorage = getStorage.first()
    if selectedStorage == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"storage with id: {id} was not found")
    getStorage.update(storage.model_dump(), synchronize_session=False)

    db.commit()
    return {"Updated Storage" : getStorage.first()}