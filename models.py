from pydantic import BaseModel, Field, model_validator
from sqlalchemy import text
from db import engine
from uuid import uuid4, UUID
from typing import List

import pprint

class Zone(BaseModel):
    id: UUID
    park_id: UUID
    name: str
    free: int = Field(ge=0)
    total:int = Field(gt=0)

    @model_validator(mode='after')
    def check_total_gt_free(self):
        """
        Валидация free и total(total всегда > free)
        """
        if self.total <= self.free:
            raise ValueError('поле total должно быть больше чем поле free')
        return self

class ParkingLot(BaseModel):
    id: UUID 
    name: str
    zones: List[Zone]
    description : str
    last_update: str
    


def append_parking_lot(parking_lot:ParkingLot):
    """
    Добавление в таблицу новой парковки и новых 
    зон(от этой парковки) в таблицу zones
    """
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(
                text("INSERT INTO parking_lots "
                "(id, name, description, last_update) " \
                "VALUES (:id, :name, :description, NOW())"),
                {"id": parking_lot.id, "name":parking_lot.name, "description":parking_lot.description}
            )

            prompt = """
                    INSERT INTO
                    zones (id, park_id, name, total, free)
                    VALUES (:id, :park_id, :name, :total, :free)
                    """
            for zone in parking_lot.zones:
                    values = {
                        "id": zone.id, 
                        "park_id": zone.park_id, 
                        "name": zone.name, 
                        "total": zone.total,
                        "free": zone.free
                        }
                    
                    conn.execute(text(prompt), values)

def clear_ALL_data():
    """
    Удаление вообще всего из обеих таблиц
    """
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(text("DELETE FROM parking_lots"))
            conn.execute(text("DELETE FROM zones"))

def del_parking_lot(parking_lot_id):
    """
    удаление конкретной парковки(по ее uuid) вместе со всеми ее зонами
    """
    try:
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(text(
                    "DELETE FROM parking_lots WHERE id= :parkk_id"), 
                    {"parkk_id":parking_lot_id})
                
                conn.execute(text(
                    "DELETE FROM zones WHERE park_id= :parkk_id"), 
                    {"parkk_id":parking_lot_id})
    except:
        raise Exception

def get_all() -> dict: 
    """возвращает список всех парковок со списками зон для каждой"""
    prompt ="""
    SELECT 
        park.id::text,
        park.name,
        park.description,
        park.last_update::text,
        zone.id::text,
        zone.name,
        zone.free,
        zone.total 
    FROM zones zone
    JOIN parking_lots park ON park.id=zone.park_id
    """
    with engine.connect() as conn:
        with conn.begin():
            result = conn.execute(text(prompt))
            data = result.fetchall()

            ####### обработка данных для отправки######
            park_dict = {}
            for zone in data:
                app_zone = {
                    "zone_name":zone[5],
                    "zone_free":zone[6],
                    "zone_total":zone[7]
                    }
                if zone[0] in park_dict:
                    park_dict[zone[0]]["zones"].append(app_zone)
                else:
                    park_dict[zone[0]] = {
                        "park_name": zone[1],
                        "description": zone[2],
                        "zones":[app_zone],
                        "last_update":zone[3]
                        }
            return park_dict

def get_park_lot(park_lot_name) -> ParkingLot:
    """
    возвращает одну конкретную парковку по имени(со списком зон этой парковки)
    """
    prompt = """
    SELECT
        parking.id::text,
        parking.name,
        parking.description,
        parking.last_update::text,
        zone.id::text,
        zone.name,
        zone.free,
        zone.total 
    FROM zones zone
    JOIN parking_lots parking ON parking.id=zone.park_id
    WHERE parking.name = :namee
    """
    with engine.connect() as conn:
        result = conn.execute(text(prompt), {"namee":park_lot_name})

        data = result.fetchall()

        ####### обработка данных для отправки######
        zone_list = [Zone(id=zone[-4], 
                          park_id=data[0][0], 
                          name=zone[-3],
                          free=zone[-2],
                          total=zone[-1]
                          ) 
                     for zone in data
                     ]
        parking_lot = ParkingLot(
            id=data[0][0], 
            name=data[0][1],
            description=data[0][2],
            last_update=data[0][3], 
            zones=zone_list)
        return parking_lot

def update_parking_lot_free_value(parking_lot: ParkingLot):
    """
    принимает на вход схему парковки(класс ParkingLot)
    в котором храняться новые значения free(новая информация о том
    сколько мест в каждой зоне свободно(список зон передается в классе
    ParkingLot в списке zones, в котором каждый элемент является объектом
    класса Zone))
    затем обновляет данные в таблице zones исходя из новых данных
    """
    try:
        prompt = """
        UPDATE zones SET free= :new_value WHERE id = :zone_id
        """

        values = [
            {"new_value":zone.free, "zone_id":zone.id}
            for zone in parking_lot.zones      
                  ]
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(text(prompt), values)
    except: 
        raise Exception



##данные для тестов(создадутся 2 парковки в бд с указанными зонами)
# park_id1, park_id2 = uuid4(), uuid4()

# zone1 = Zone(id=uuid4(), park_id=park_id1, name="центр", free=80, total=100)
# zone2 = Zone(id=uuid4(), park_id=park_id2, name="север", free=5, total=120)
# zone3 = Zone(id=uuid4(), park_id=park_id2, name="центр", free=5, total=80)
# zone4 = Zone(id=uuid4(), park_id=park_id2, name="юг", free=5, total=100)

# parking_lot1 = ParkingLot(
#     id=park_id1, 
#     name="ИРИТ-РТФ", 
#     zones=[zone1], 
#     description="парковка великого РТФ шампиньона",
#     last_update="вчера"
#     )
# parking_lot2 = ParkingLot(
#     id=park_id2, 
#     name="ГРИНВИЧ", 
#     zones=[zone2, zone3, zone4],
#     description="крутая такая",
#     last_update="вчера"
#     )

# append_parking_lot(parking_lot1)
# append_parking_lot(parking_lot2)
