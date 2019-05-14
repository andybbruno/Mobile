from datetime import datetime as data
from random import randint

from .db import machineTable
from json_validator import Validator

def _genereteID():
    n = 5
    return randint(10**(n-1), (10**n)-1)

def new_machine(jsonReq):
    """
        Inserisce unanuova macchina nella tabella.
        Viene creato tutto il necessario per le varie funzioni del sistema e le
        statistiche.

        JSON in entrata:
        {
           *"ID": <int>,
            "orders": <json,esempio {"caffe": 0.8, "cioccolato": 1.5}>
            "position_geo": <                >
            "position_des": <str, maxlen(255), descrizione della posizione>
            "owner": <str, ente a cui sono affidate le macchiene>
            "consumable_list": <list(str>), lista degli oggetti di consumo>
        }
        * campo opzionale

        RETURN
            TRUE se la rigistrazione è avventua FALSE altrimenti
    """
    if not Validator.validate_machine(jsonReq):
        return False, "Not Valid JSON"

    ID = jsonReq.get("ID", _genereteID())
    if machineTable.find_one({"ID": ID}):
        return False, "Machine already exist"

    currTime = int(data.timestamp(data.now()))
    machine = {
        "ID": ID,
        "possible_orders": jsonReq["orders"],
        "position_geo": jsonReq.get("position_geo", None),
        "position_des": jsonReq["position_des"],
        "maintenance": {
            "consumable_list": {
            },
            "last_maintenance": currTime,
            "last_cleaning": currTime,
        },
        "management": {
            "owner": jsonReq["owner"],
            "count_orders": {
            }
        },
        "satisfaction_level": 0.5,
        "installation_date": currTime,
        "working": True,
    }

    # popolare ingredienti_levels
    to_add = {}
    [to_add.update({ingr: 0}) for ingr in jsonReq["consumable_list"]]
    machine["maintenance"]["consumable_list"].update(to_add)

    # popolare count_orders
    to_add = {}
    [to_add.update({product: 0}) for product in jsonReq["orders"].keys()]
    machine["management"]["count_orders"].update(to_add)

    machineTable.insert_one(machine)
    return True, None
