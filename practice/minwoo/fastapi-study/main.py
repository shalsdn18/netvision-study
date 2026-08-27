from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
import subprocess

import socket

from database import get_db
from models import Camera as CameraModel
from schemas import CameraCreate, CameraResponse

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello REST API"}


@app.get("/cameras", response_model=list[CameraResponse])
def get_cameras(db: Session = Depends(get_db)):
    return db.query(CameraModel).all()


@app.get("/cameras/{camera_id}", response_model=CameraResponse)
def get_camera(
    camera_id: int,
    db: Session = Depends(get_db)
):
    camera = db.query(CameraModel).filter(
        CameraModel.id == camera_id
    ).first()

    if not camera:
        raise HTTPException(
            status_code=404,
            detail="Camera not found"
        )

    return camera


@app.post("/cameras", response_model=CameraResponse)
def create_camera(
    camera: CameraCreate,
    db: Session = Depends(get_db)
):
    new_camera = CameraModel(
        name=camera.name,
        ip=camera.ip
    )

    db.add(new_camera)
    db.commit()
    db.refresh(new_camera)

    return new_camera


@app.put("/cameras/{camera_id}", response_model=CameraResponse)
def update_camera(
    camera_id: int,
    camera: CameraCreate,
    db: Session = Depends(get_db)
):
    existing_camera = db.query(CameraModel).filter(
        CameraModel.id == camera_id
    ).first()

    if not existing_camera:
        raise HTTPException(
            status_code=404,
            detail="Camera not found"
        )

    existing_camera.name = camera.name
    existing_camera.ip = camera.ip

    db.commit()
    db.refresh(existing_camera)

    return existing_camera


@app.delete("/cameras/{camera_id}")
def delete_camera(
    camera_id: int,
    db: Session = Depends(get_db)
):
    camera = db.query(CameraModel).filter(
        CameraModel.id == camera_id
    ).first()

    if not camera:
        raise HTTPException(
            status_code=404,
            detail="Camera not found"
        )

    db.delete(camera)
    db.commit()

    return {"message": "Camera deleted"}

@app.get("/cameras/{camera_id}/port-check")
def check_camera_port(
    camera_id: int,
    port: int = 554,
    db: Session = Depends(get_db)
):
    camera = db.query(CameraModel).filter(
        CameraModel.id == camera_id
    ).first()

    if not camera:
        raise HTTPException(
            status_code=404,
            detail="Camera not found"
        )

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)

        result = sock.connect_ex((camera.ip, port))
        sock.close()

        return {
            "camera_id": camera.id,
            "name": camera.name,
            "ip": camera.ip,
            "port": port,
            "open": result == 0
        }

    except Exception as e:
        return {
            "camera_id": camera.id,
            "name": camera.name,
            "ip": camera.ip,
            "port": port,
            "open": False,
            "error": str(e)
        }


@app.get("/cameras/{camera_id}/ping")
def ping_camera(
    camera_id: int,
    db: Session = Depends(get_db)
):
    camera = db.query(CameraModel).filter(
        CameraModel.id == camera_id
    ).first()

    if not camera:
        raise HTTPException(
            status_code=404,
            detail="Camera not found"
        )

    try:
        result = subprocess.run(
            ["ping", "-n", "1", "-w", "2000", camera.ip],
            capture_output=True,
            text=True
        )

        return {
            "camera_id": camera.id,
            "name": camera.name,
            "ip": camera.ip,
            "reachable": result.returncode == 0
        }

    except Exception as e:
        return {
            "camera_id": camera.id,
            "name": camera.name,
            "ip": camera.ip,
            "reachable": False,
            "error": str(e)
        }

@app.get("/cameras/{camera_id}/port-check")
def check_camera_port(
    camera_id: int,
    port: int = 554,
    db: Session = Depends(get_db)
):
    camera = db.query(CameraModel).filter(
        CameraModel.id == camera_id
    ).first()

    if not camera:
        raise HTTPException(
            status_code=404,
            detail="Camera not found"
        )

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)

        result = sock.connect_ex((camera.ip, port))
        sock.close()

        return {
            "camera_id": camera.id,
            "name": camera.name,
            "ip": camera.ip,
            "port": port,
            "open": result == 0
        }

    except Exception as e:
        return {
            "camera_id": camera.id,
            "name": camera.name,
            "ip": camera.ip,
            "port": port,
            "open": False,
            "error": str(e)
        }