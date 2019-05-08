from flask import Flask, request
import pymongo

from json_validator import new_machine

from schema import SchemaError

mongoDB = pymongo.MongoClient("mongodb://localhost:27017/")
mobile_db = mongoDB["test_db"]


app = Flask(__name__)

@app.route('/')
def homepage():
    return 'Dashboard'

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

    machineTable = mobile_db["testTable"]
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
    if request.method == 'POST':
        return 'Status updated'
    else:
        return 'Status returned'


@app.route('/<ID>/order', methods=['POST'])
def neworder():
    return 'New order'


@app.route('/<ID>/mngt', methods=['POST', 'GET'])
def manage():
    if request.method == 'POST':
        return 'Management updated'
    else:
        return 'Management returned'

@app.route('/login', methods=['POST'])
def login():
    return 'login'



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
