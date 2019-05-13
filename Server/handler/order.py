from datetime import datetime as data

from .db import machineTable, transactionTable, detectionTable
from json_validator import Validator

def register_order(ID, jsonReq):
    """
        La macchinetta utilizza questa funzione pre registrare un ordine.
        Durente la reigistrazione dell'ordine vengono registrate anche:
        - la soddisfazione del customer per il product,
        - Le persone presenti d'avanti alla macchinetta

        JSON in entrata:
            {
                "transaction_type": <str, one of (conante, contacless))
                "product": <str, one of possible_orders registered>
                "satisfaction": <float, satisfaction level of customer>
                "people_detected": <int, people detected during order>
                *"new_levels":{
                    "<consumable>": <int, new_level,
                    ...
                }
            }

        RETURN
            TRUE se la rigistrazione è avventua FALSE altrimenti
    """

    print(ID)
    print(jsonReq)
    
    timestamp = int(data.timestamp(data.now()))
    
    currMachine = machineTable.find_one({"ID": ID})
    
    if not currMachine:
        return False, "Not Valid Machine"

    if not Validator.validate_order(jsonReq, currMachine["possible_orders"].keys()):
        return False, "Not Valid JSON"

    # Inserimento transazione
    cost = currMachine["possible_orders"][jsonReq["product"]]
    transactionTable.insert_one({
        "machineID": ID,
        "transaction_type": jsonReq["transaction_type"],
        "product": jsonReq["product"],
        "cost": cost,
        "satisfaction": jsonReq["satisfaction"],
        "timestamp": timestamp
    })
    # Inserimento della people detection durante l'acquisto
    detectionTable.insert_one({
        "timestamp": timestamp,
        "machineID": ID,
        "people_detected": jsonReq["people_detected"],
        "face_recognised": jsonReq["face_recognised"]
    })
    # aggiorna il numero di vendite sulla macchnetta
    machineTable.update_one(
        {"ID": ID}, {"$inc": {"management.count_orders."+jsonReq["product"]: 1}})
    # modifica satisfaction_level della macchinetta (media armonica)
    currSat, newSat = currMachine["satisfaction_level"], jsonReq["satisfaction"]
    machineTable.update_one(
        {"ID": ID}, {"$set": {"satisfaction_level": (2*currSat*newSat)/(newSat+currSat)}})
    # modifico i livelli degli oggetti di consumo che hanno avuto ua variazione
    if jsonReq.get("new_levels", None):
        to_modify = {}
        for k, v in jsonReq["new_levels"].items():
            to_modify = {"maintenance.consumable_list."+k: v}
        machineTable.update_one({"ID": ID}, {"$set": to_modify})
    return True, None
