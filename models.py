from database import Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "Users"
    idUser = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    dateOfBirth = Column(String, nullable=False)
    phoneNumber = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    sessionKey = Column(String, nullable=True)
    pending = Column(Boolean, nullable=False)
    languange = Column(String, nullable=False)
    timeCreated = Column(DateTime(timezone=True), server_default=func.now())

class Notification(Base):
    __tablename__ = "Notification"
    idNotification = Column(Integer, primary_key=True, nullable=False)
    idUser = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    seen = Column(Boolean, nullable=False)
    timeCreated = Column(DateTime(timezone=True), server_default=func.now())

class Centra(Base):
    __tablename__ = "Centra"
    idCentra = Column(Integer, primary_key=True, nullable=False)
    manager = Column(String, nullable=False)
    phone = Column(Integer, nullable=False)
    location = Column(String, nullable=False)
    geoCodeX = Column(Float, nullable=False)
    geoCodeY = Column(Float, nullable=False)
    timeCreated = Column(DateTime(timezone=True), server_default=func.now())

class WetLeaves(Base):
    __tablename__ = "WetLeaves"
    idWet = Column(Integer, primary_key=True, nullable=False)
    idCentra = Column(Integer, nullable=False)
    expired = Column(Boolean, nullable=False)
    weight = Column(Integer, nullable=False)
    timeToExpired = Column(DateTime, nullable=False)
    timeCreated = Column(DateTime(timezone=True), server_default=func.now())

class DryLeaves(Base):
    __tablename__ = "DryLeaves"
    idDry = Column(Integer, primary_key=True ,nullable=False)
    idCentra = Column(Integer, nullable=False)
    idMachine = Column(Integer, nullable=False)
    weight = Column(Integer, nullable=False)
    timeToExpired = Column(DateTime, nullable=False)
    timeCreated = Column(DateTime(timezone=True), server_default=func.now())

class Flour(Base):
    __tablename__ = "Flour"
    idFlour = Column(Integer, primary_key=True, nullable=False)
    idCentra = Column(Integer, nullable=False)
    idMachine = Column(Integer, nullable=False)
    weight = Column(Integer, nullable=False)
    timeToExpired = Column(DateTime, nullable=False)
    timeCreated = Column(DateTime(timezone=True), server_default=func.now())

class Shipment(Base):
    __tablename__ = "Shipments"
    idShipment = Column(Integer, primary_key=True, nullable=False)
    idCentra = Column(Integer, nullable=False)
    orderNumber = Column(String, nullable=False)
    address = Column(String, nullable=False)
    status = Column(String, nullable=False)
    weight = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    estimated = Column(DateTime, nullable=False)
    orderDetails = Column(String, nullable=False)
    stage = Column(Integer, nullable=False)
    timeCreated = Column(DateTime(timezone=True), server_default=func.now())

class Storage(Base):
    __tablename__ = "Storage"
    idStorage = Column(Integer, primary_key=True, nullable=False)
    idShipment = Column(Integer, nullable=False)
    provider = Column(String, nullable=False)
    weight = Column(Integer, nullable=False)
    arrival = Column(DateTime, nullable=True)
    isRescaled = Column(Boolean, nullable=False)
    rescaledDate = Column(DateTime, nullable=False)
    expiredDate = Column(DateTime, nullable=False)
    timeCreated = Column(DateTime(timezone=True), server_default=func.now())

# class Tasks(Base):
#     __tablename__ = "Tasks"
#     id = Column(Integer, primary_key=True, nullable=False)
#     title = Column(String, nullable=False)
#     description = Column(String, nullable=False)
#     checked = Column(Boolean, nullable=False)
#     timeCreated = Column(DateTime(timezone=True), server_default=func.now())
    