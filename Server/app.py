from flask import Flask, request, render_template
import pymongo
from datetime import datetime as data
from random import randint

from json_validator import Validator

from opsHandler import maintain

mongoDB = pymongo.MongoClient("mongodb://localhost:27017/")
mobile_db = mongoDB["test_db"]

machineTable = mobile_db["testTable"]
transactionTable = mobile_db["testTransaction"]
detectionTable = mobile_db["testDetection"]

app = Flask(__name__)

logged_in = False;

@app.route('/')
def homepage():
    if (logged_in):
        return render_template('index.html')
    else:
        return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    return 'Login'

def genereteID():
    n = 5
    return randint(10**(n-1), (10**n)-1)

@app.route('/machine', methods=['POST'])
def new_machine():
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
            "ingredient_list": <list(str>), lista degli ingrdienti>
            "stuff_list": <list(str), lista degli oggetti>
        }
        * campo opzionale

        RETURN
            TRUE se la rigistrazione è avventua FALSE altrimenti
    """
    jsonReq = request.get_json(silent=True, force=True)
    if not Validator.validate_machine(jsonReq):
        return "Not Valid JSON"

    currTime = (int) (data.timestamp(data.now()))
    machine = {
        "ID": jsonReq.get("ID", genereteID()),
        "possible_orders": jsonReq["orders"],
        "position_geo": jsonReq.get("position_geo", None),
        "position_des": jsonReq["position_des"],
        "maintenance": {
            "ingredient_levels":{
            },
            "stuff_levels": {
            },
            "last_maintenance": currTime,
            "last_cleaning": currTime,
        },
        "management": {
            "owner": jsonReq["owner"],
            "count_orders": {
            }
        },
        "installation_date": currTime,
    }

    # popolare ingredienti_levels
    to_add = {}
    [to_add.update({ingr: 0}) for ingr in jsonReq["ingredient_list"]]
    machine["maintenance"]["ingredient_levels"].update(to_add)

    # popolare  stuff_levels
    to_add = {}
    [to_add.update({stuff: 0}) for stuff in jsonReq["stuff_list"]]
    machine["maintenance"]["stuff_levels"].update(to_add)

    # popolare count_orders
    to_add = {}
    [to_add.update({product: 0}) for product in jsonReq["orders"].keys()]
    machine["management"]["count_orders"].update(to_add)

    print("New", machine)
    machineTable.insert_one(machine)
    return 'New machine Adder'

@app.route('/machine', methods=['DELETE'])
def del_machine():
    # IDEA: non e meglio fare un end point \<ID> DELETE
    """
        Elimina la macchine con l'id specificato dalla tabella delle macchine
        JSON in entrata:
        {
            "ID": <int>
        }

        RETURN
            TRUE se la rigistrazione è avventua FALSE altrimenti
    """
    jsonReq = request.get_json(silent=True, force=True)

    if not Validator.del_machine(jsonReq):
        return "Not Valid JSON"

    print("Del", machineTable.delete_one(jsonReq))
    return 'Delete machine'


# @app.route('/<ID>', methods=['POST', 'GET'])
# def status():
#     jsonReq = request.get_json(silent=True, force=True)
#     if request.method == 'POST':
#         # Per questa orerazione è richiesto l'ID dell'operatore
#         return registerMaintainOperation()
#     else:
#         return getMaintainStatus()


@app.route('/<ID>/order', methods=['POST'])
def new_order(ID):
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
            }
        RETURN
            TRUE se la rigistrazione è avventua FALSE altrimenti
    """
    jsonReq = request.get_json(silent=True, force=True)
    timestamp = (int) (data.timestamp(data.now()))
    currMachine = machineTable.find_one({"ID", ID})

    if not Validator.validate_order(jsonReq, currMachine["possible_orders"].keys()):
        return "Not Valid JSON"

    #Inserimento transazione
    cost = currMachine["possible_orders"][jsonReq["product"]]
    transactionTable.insert_one({
        "timestamp": timestamp,
        "id_machine": ID,
        "transaction_type": jsonReq["transaction_type"],
        "product": jsonReq["product"],
        "cost": cost,
        "satisfaction": jsonReq["satisfaction"]
    })
    #Inserimento della people detection durante l'acquisto
    detectionTable.insert_one({
        "timestamp": timestamp,
        "machineID": ID,
        "people_detected": jsonReq["people_detected"]})
    # TODO aggiornare il numero di vendite sulla macchnetta
    # TODO modificare satisfaction_level della macchinetta in base a questo
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


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

app.run(host='0.0.0.0', port='3000', debug=True)
