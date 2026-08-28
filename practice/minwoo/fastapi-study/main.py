import subprocess
import socket
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Camera as CameraModel
from schemas import CameraCreate, CameraResponse


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)


def get_camera_or_404(camera_id: int, db: Session) -> CameraModel:
    camera = db.get(CameraModel, camera_id)
    if camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera


@app.get("/")
def root():
    return {"message": "Hello REST API"}


@app.get("/cameras", response_model=list[CameraResponse])
def get_cameras(db: Session = Depends(get_db)):
    return db.query(CameraModel).all()


@app.get("/cameras/{camera_id}", response_model=CameraResponse)
def get_camera(
    camera_id: int,
    db: Session = Depends(get_db),
):
    return get_camera_or_404(camera_id, db)


@app.post("/cameras", response_model=CameraResponse)
def create_camera(
    camera: CameraCreate,
    db: Session = Depends(get_db),
):
    new_camera = CameraModel(name=camera.name, ip=camera.ip)

    db.add(new_camera)
    db.commit()
    db.refresh(new_camera)

    return new_camera


@app.put("/cameras/{camera_id}", response_model=CameraResponse)
def update_camera(
    camera_id: int,
    camera: CameraCreate,
    db: Session = Depends(get_db),
):
    existing_camera = get_camera_or_404(camera_id, db)

    existing_camera.name = camera.name
    existing_camera.ip = camera.ip

    db.commit()
    db.refresh(existing_camera)

    return existing_camera


@app.delete("/cameras/{camera_id}")
def delete_camera(
    camera_id: int,
    db: Session = Depends(get_db),
):
    camera = get_camera_or_404(camera_id, db)

    db.delete(camera)
    db.commit()

    return {"message": "Camera deleted"}


@app.get("/cameras/{camera_id}/port-check")
def check_camera_port(
    camera_id: int,
    port: int = 554,
    db: Session = Depends(get_db),
):
    camera = get_camera_or_404(camera_id, db)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(2)
            result = sock.connect_ex((camera.ip, port))

        return {
            "camera_id": camera.id,
            "name": camera.name,
            "ip": camera.ip,
            "port": port,
            "open": result == 0,
        }

    except OSError as error:
        return {
            "camera_id": camera.id,
            "name": camera.name,
            "ip": camera.ip,
            "port": port,
            "open": False,
            "error": str(error),
        }


@app.get("/cameras/{camera_id}/ping")
def ping_camera(
    camera_id: int,
    db: Session = Depends(get_db),
):
    camera = get_camera_or_404(camera_id, db)

    try:
        result = subprocess.run(
            ["ping", "-n", "1", "-w", "2000", camera.ip],
            capture_output=True,
            text=True,
            timeout=3,
        )

        return {
            "camera_id": camera.id,
            "name": camera.name,
            "ip": camera.ip,
            "reachable": result.returncode == 0,
        }

    except (OSError, subprocess.TimeoutExpired) as error:
        return {
            "camera_id": camera.id,
            "name": camera.name,
            "ip": camera.ip,
            "reachable": False,
            "error": str(error),
        }
