from datetime import datetime as data

from .db import machineTable, userTable, operazionTable
from json_validator import Validator

def register_operation(machineID, jsonReq):
    """
        Elimina la macchine con l'id specificato dalla tabella delle macchine
        JSON in entrata:
        {
            "operatorID": <str>
            "type": <str, in ["refill", "cleaning", "repair", "standard check"]>
        }

        RETURN
            TRUE se la rigistrazione è avventua FALSE altrimenti
    """

    if not Validator.validate_operation(jsonReq):
        return False, "Not Valid JSON"

    operatorID = int(jsonReq["operatorID"])
    if not machineTable.find_one({"ID": machineID}):
        return False, "Machine ID not valid"
    if not userTable.find_one({"ID": operatorID}):
        return False, "Operator ID not valid"

    op_type = jsonReq["type"]
    currTime = int(data.timestamp(data.now()))
    operazionTable.insert_one({
        "operatorID": operatorID,
        "machineID": machineID,
        "type": op_type,
        "timestamp": currTime
    })

    # if op_type == "refill":
        # ci si aspetta che la macchinetta invia new_level \ID\new_levels
    if op_type == "cleaning":
        machineTable.update_one({"ID": machineID}, {"$set":{"maintenance.last_cleaning":currTime}})
    if op_type in ["repair", "standard check"]:
        machineTable.update_one({"ID": machineID}, {"$set":{"maintenance.last_maintenance":currTime}})

    return True, None

#
# #TODO richiedere i nuovi livelli alla macchinetta se è stato fatto un refill
# #new_level = request_to_macchientta()
# new_level = {"bicchiere":50, "palettina":50, "caffe":50, "cioccolato concentrato":50, "zucchero":50}
# to_modify = {}
# for k, v in new_levels.items():
#     to_modify = {"maintenance.consumable_list."+k: v}
# machineTable.update_one({"ID": ID}, {"$set": to_modify})
#
