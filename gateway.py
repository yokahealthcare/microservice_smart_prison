from fastapi import FastAPI
from fastapi.responses import RedirectResponse

import util

app = FastAPI()


@app.get("/")
def index():
    return RedirectResponse(url="/docs")


@app.get("/add_camera")
def add_camera(name: str, source: str, fight_engine: bool, pray_engine: bool, city: str, gpu: int, port: int):
    if util.create_camera(name, source, fight_engine, pray_engine, city, gpu, port):
        return "OK"
    else:
        return "FAILED"


@app.get("/delete_camera")
def stop_camera(name: str):
    if util.delete_camera(name):
        return "OK"
    else:
        return "FAILED"


@app.get("/delete_all_camera")
def delete_all_camera():
    if util.delete_all_camera():
        return "OK"
    else:
        return "FAILED"


@app.get("/info")
def info(camera_name=None):
    if camera_name is None:
        success, data = util.get_info_all_camera()
        if not success:
            return "FAILED"

        return data
    else:
        success, data = util.get_info_camera(camera_name)
        if not success:
            return "FAILED"

        return data
