from pydantic import BaseModel
from sqlalchemy import text
from db import engine
from uuid import uuid4, UUID
from typing import List

import pprint

class Zone(BaseModel):
    id: UUID
    park_id: UUID
    name: str
    free: int
    total:int

class ParkingLot(BaseModel):
    id: UUID 
    name: str
    zones: List[Zone]



def append_parking_lot(parking_lot:ParkingLot):
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(
                text("INSERT INTO parking_lots (id, name) VALUES (:id, :name)"),
                {"id": parking_lot.id, "name":parking_lot.name}
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
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(text("DELETE FROM parking_lots"))
            conn.execute(text("DELETE FROM zones"))

def del_parking_lot(parking_lot_id):
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
    prompt ="""
    SELECT 
        park.id::text,
        park.name,
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
                    "zone_name":zone[3],
                    "zone_free":zone[4],
                    "zone_total":zone[5]
                    }
                if zone[0] in park_dict:
                    park_dict[zone[0]]["zones"].append(app_zone)
                else:
                    park_dict[zone[0]] = {"park_name": zone[1], "zones":[app_zone]}
            return park_dict

def get_park_lot(park_lot_name) -> ParkingLot:
    promt = """
    SELECT
        parking.id::text,
        parking.name,
        zone.id::text,
        zone.name,
        zone.free,
        zone.total 
    FROM zones zone
    JOIN parking_lots parking ON parking.id=zone.park_id
    WHERE parking.name = :namee
    """
    with engine.connect() as conn:
        result = conn.execute(text(promt), {"namee":park_lot_name})

        data = result.fetchall()

        ####### обработка данных для отправки######
        zone_list = [Zone(id=zone[2], 
                          park_id=data[0][0], 
                          name=zone[-3],
                          free=zone[-2],
                          total=zone[-1]
                          ) 
                     for zone in data
                     ]
        parking_lot = ParkingLot(id=data[0][0], name=data[0][1], zones=zone_list)
        return parking_lot

def update_parking_lot_free_value(parking_lot: ParkingLot):
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


# park_id1, park_id2 = uuid4(), uuid4()

# zone1 = Zone(id=uuid4(), park_id=park_id1, name="центр", free=80, total=100)
# zone2 = Zone(id="b2e12384-e640-4046-bbe4-0816dd7a9077", park_id=park_id2, name="север", free=5, total=120)
# zone3 = Zone(id="9a3a5294-e827-4497-8bf7-f3f8090ba22e", park_id=park_id2, name="центр", free=5, total=80)
# zone4 = Zone(id="b76af911-ba49-426e-a7b9-b4fb4c044056", park_id=park_id2, name="юг", free=5, total=100)

# parking_lot1 = ParkingLot(id=park_id1, name="ИРИТ-РТФ", zones=[zone1])
# parking_lot2 = ParkingLot(id=park_id2, name="ГРИНВИЧ", zones=[zone2, zone3, zone4])

# append_parking_lot(parking_lot1)
# append_parking_lot(parking_lot2)

#pprint.pprint(get_all())