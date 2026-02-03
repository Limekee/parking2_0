from fastapi import FastAPI, HTTPException
import uvicorn

from models import *

app = FastAPI()


@app.get("/parking_lots")
def get_parking_lots():
    return get_all()

@app.get("/parking_lots/{pl_name}")
def get_parking_lot(pl_name:str):
    try:
        print(pl_name)
        return get_park_lot(park_lot_name=pl_name)
    except:
        raise HTTPException(status_code=404, detail="парковка не найдена")

@app.post("/parking_lots")
def create_parking_lot(parking_lot:ParkingLot):
    try:
        append_parking_lot(parking_lot=parking_lot)
        
    except:
        raise HTTPException(status_code=404, detail="такая парковка уже есть(id занят)")
    return {"success": True}

@app.delete("/parking_lots/{parking_lot_id}")
def delete_parking_lot(parking_lot_id:str):
    try:
        del_parking_lot(parking_lot_id)
    except:
        raise HTTPException(status_code=404, detail="парковка не найдена")
    return {"success":True}

@app.delete("/parking_lots")
def delete_ALL():
    try:
        clear_ALL_data()
    except:
        raise HTTPException(status_code=404, detail="что то пошло не так")
    return {"success": True}
@app.put("/parking_lots")
def update_parking_lot(parking_lot: ParkingLot):
    try:
        update_parking_lot_free_value(parking_lot)
    except:
        raise HTTPException(status_code=404, detail="парковка не найдена")
    return {"success":True}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)