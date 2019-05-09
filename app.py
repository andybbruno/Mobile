from flask import Flask, request
import pymongo

from schema import SchemaError

from json_validator import Validator

from opsHandler import maintain

mongoDB = pymongo.MongoClient("mongodb://localhost:27017/")
mobile_db = mongoDB["test_db"]

machineTable = mobile_db["testTable"]


app = Flask(__name__)

@app.route('/')
def homepage():
    return 'Dashboard'

@app.route('/login', methods=['POST'])
def login():
    return 'login'


@app.route('/machine', methods=['POST', 'DELETE'])
def machine():
    """
        struttura macchinetta
        {
            "ID":<str, len(10)>,                                                \\ ID della macchinetta
            "orders": <list(str), can be contain ["caffe", "cioccolato", ...]>  \\ Possibili ordine che si possono fare
            "position_GEO": <                                                   \\ posizione in coordinate geografiche
            "position_Des": <str,                                               \\ Descrizione della posizione all'interno dell'edificio
        }
    """
    jsonReq = request.get_json(silent=True, force=True)
    try:
        new_machine.validate(jsonReq)# valido il json avuto
    except SchemaError  as e:
        return "Not Valid JSON"


    if request.method == 'POST':
        x = machineTable.insert_one(jsonReq)
        print("New", x)
        return 'New machine'
    else:
        x = machineTable.delete_one(jsonReq)
        print("Del", x)
        return 'Delete machine'


@app.route('/<ID>', methods=['POST', 'GET'])
def status():
    jsonReq = request.get_json(silent=True, force=True)
    if request.method == 'POST':
        # Per questa orerazione è richiesto l'ID dell'operatore
        return registerMaintainOperation()
    else:
        return getMaintainStatus()


@app.route('/<ID>/order', methods=['POST'])
def neworder():
    """
        La macchinetta utilizza questa funzione pre registrare un ordine.
        JSON in entrata:
            {
                "trnsaction_type": <str, one of (conante, contacless))
                "prodotto": <str, one of possible_orders registered>
                "satisfaction": <float, satisfaction level of customer>
                "people_detected": <int, people detected during order>
            }
        RETURN
            TRUE se la rigistrazione è avventua FALSE altrimenti
    """
    jsonReq = request.get_json(silent=True, force=True)
    Validator.new_order(jsonReq, machineTable.find_one({"ID", ID})["possible_orders"])
    return True


@app.route('/<ID>/mngt', methods=['POST', 'GET'])
def manage():
    jsonReq = request.get_json(silent=True, force=True)
    if request.method == 'POST':
        return 'Management updated'
    else:
        return 'Management returned'


# ------------------------Funzioni di Test e Gesitone -------------------------
# TODO: Da aliminare
@app.route('/allData', methods=['GET'])
def allData():
    cursor = mobile_db["testTable"].find()
    list = []
    for document in cursor:
        list.append(document)
    return str(list)

@app.route('/all', methods=['DELETE'])
def delete_():
    cursor = mobile_db["testTable"].find()
    list = []
    for document in cursor:
        list.append(document)
        mobile_db["testTable"].delete_many(document)
    return str(list)


app.run(host='0.0.0.0', port='3000', debug=True)
