from fastapi import FastAPI, HTTPException
import uvicorn

from models import *

app = FastAPI()


@app.get("/parking_lots")
def get_parking_lots():
    """
    ручка для отправления списка всех парковок со списками зон для каждой
    """
    try:
        return get_all()
    except:
        raise HTTPException(detail="что то пошло не так")

@app.get("/parking_lots/{pl_name}")
def get_parking_lot(pl_name:str):
    """
    ручка для отправления одной парковки(ищем ее по имени) со списком всех ее зон
    """
    try:
        return get_park_lot(park_lot_name=pl_name)
    except:
        raise HTTPException(status_code=404, detail="парковка не найдена")

@app.post("/parking_lots")
def create_parking_lot(parking_lot:ParkingLot):
    """
    ручка для создания одной парковки со всеми ее зонами(по схеме ParkingLot)
    """
    try:
        append_parking_lot(parking_lot=parking_lot)
        
    except:
        raise HTTPException(status_code=404, detail="такая парковка уже есть(id занят)")
    return {"success": True}

@app.delete("/parking_lots/{parking_lot_id}")
def delete_parking_lot(parking_lot_id:str):
    """
    ручка для удаления одной конкретной парковки со всеми ее зонами
    (ищем парковку по uuid)
    """
    try:
        del_parking_lot(parking_lot_id)
    except:
        raise HTTPException(status_code=404, detail="парковка не найдена")
    return {"success":True}

@app.delete("/parking_lots")
def delete_ALL():
    """
    ручка для удаления вообще всех даннх из обеих таблиц
    """
    try:
        clear_ALL_data()
    except:
        raise HTTPException(status_code=404, detail="что то пошло не так")
    return {"success": True}

@app.put("/parking_lots")
def update_parking_lot(parking_lot: ParkingLot):
    """
    ручка для обнавления данных о свободных местах 
    в каждой зоне одной конкретной парковки
    (ищем зоны по uuid указаном в схеме ParkingLot)
    """
    try:
        update_parking_lot_free_value(parking_lot)
    except:
        raise HTTPException(status_code=404, detail="парковка не найдена")
    return {"success":True}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)