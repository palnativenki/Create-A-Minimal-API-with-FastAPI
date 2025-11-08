from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas, utils
from .database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Address Book API")


# Dependency: DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/addresses/", response_model=schemas.AddressOut)
def create_address(address: schemas.AddressCreate, db: Session = Depends(get_db)):
    db_address = models.Address(**address.dict())
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address


@app.get("/addresses/", response_model=List[schemas.AddressOut])
def list_addresses(db: Session = Depends(get_db)):
    return db.query(models.Address).all()


@app.get("/addresses/nearby/", response_model=List[schemas.AddressOut])
def get_nearby_addresses(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    distance_km: float = Query(..., gt=0),
    db: Session = Depends(get_db)
):
    addresses = db.query(models.Address).all()
    nearby = [
        a for a in addresses
        if utils.haversine_distance(lat, lon, a.latitude, a.longitude) <= distance_km
    ]
    return nearby


@app.get("/addresses/{address_id}", response_model=schemas.AddressOut)
def get_address(address_id: int, db: Session = Depends(get_db)):
    address = db.query(models.Address).filter(models.Address.id == address_id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address


@app.put("/addresses/{address_id}", response_model=schemas.AddressOut)
def update_address(address_id: int, updated: schemas.AddressUpdate, db: Session = Depends(get_db)):
    address = db.query(models.Address).filter(models.Address.id == address_id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    for key, value in updated.dict().items():
        setattr(address, key, value)
    db.commit()
    db.refresh(address)
    return address


@app.delete("/addresses/{address_id}", status_code=204)
def delete_address(address_id: int, db: Session = Depends(get_db)):
    address = db.query(models.Address).filter(models.Address.id == address_id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    db.delete(address)
    db.commit()
    return None

