from flask import Flask, request, render_template, redirect, session
import pymongo, os
from datetime import datetime as data
from random import randint
from json_validator import Validator
from opsHandler import maintain

mongoDB = pymongo.MongoClient("mongodb://localhost:27017/")
mobile_db = mongoDB["test_db"]

machineTable = mobile_db["testTable"]
transactionTable = mobile_db["testTransaction"]
detectionTable = mobile_db["testDetection"]
userTable = mobile_db["testUser"]

app = Flask(__name__)
app.secret_key = os.urandom(16)

@app.route('/')
def homepage():
    if ('username' in session):
        return render_template('index.html', username=session['username'])
    else:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if userTable.find_one({"username": username, "password": password}):
            session['username'] = username
            return redirect('/')
        else:
            return render_template('login.html', error="Incorrect username or password")
    else:
        return render_template('login.html')


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
            "consumable_list": <list(str>), lista degli oggetti di consumo>
        }
        * campo opzionale

        RETURN
            TRUE se la rigistrazione è avventua FALSE altrimenti
    """
    jsonReq = request.get_json(silent=True, force=True)
    if not Validator.validate_machine(jsonReq):
        return "Not Valid JSON"

    ID = jsonReq.get("ID", genereteID())
    if machineTable.find_one({"ID": ID}):
        return "Machine already exist"

    currTime = (int) (data.timestamp(data.now()))
    machine = {
        "ID": ID,
        "possible_orders": jsonReq["orders"],
        "position_geo": jsonReq.get("position_geo", None),
        "position_des": jsonReq["position_des"],
        "maintenance": {
            "consumable_list":{
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
    }

    # popolare ingredienti_levels
    to_add = {}
    [to_add.update({ingr: 0}) for ingr in jsonReq["consumable_list"]]
    machine["maintenance"]["consumable_list"].update(to_add)

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


@app.route('/<int:ID>/order', methods=['POST'])
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
                *"new_levels":{
                    "<consumable>": <int, new_level,
                    ...
                }
            }
        RETURN
            TRUE se la rigistrazione è avventua FALSE altrimenti
    """
    jsonReq = request.get_json(silent=True, force=True)
    timestamp = (int) (data.timestamp(data.now()))
    currMachine = machineTable.find_one({"ID": ID})
    if not currMachine:
        return "Not Valid Machine"

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
        "people_detected": jsonReq["people_detected"]
    })
    # aggiorna il numero di vendite sulla macchnetta
    machineTable.update_one({"ID": ID}, {"$inc":{"management.count_orders."+jsonReq["product"]: 1}})
    # modifica satisfaction_level della macchinetta (media armonica)
    currSat, newSat = currMachine["satisfaction_level"], jsonReq["satisfaction"]
    machineTable.update_one({"ID": ID}, {"$set":{"satisfaction_level": (2*currSat*newSat)/(newSat+currSat)}})
    # modifico i livelli degli oggetti di consumo che hanno avuto ua variazione
    if jsonReq.get("new_levels", None):
        to_modify = {}
        for k, v in jsonReq["new_levels"].items():
            to_modify = {"maintenance.consumable_list."+k: v}
        machineTable.update_one({"ID": ID}, {"$set": to_modify})
    return "Transaction registered"

@app.route('/<int:ID>/mngt', methods=['POST', 'GET'])
def manage():
    jsonReq = request.get_json(silent=True, force=True)
    if request.method == 'POST':
        return 'Management updated'
    else:
        return 'Management returned'


# ------------------------Funzioni di Test e Gesitone -------------------------
# TODO: Da aliminare
@app.route('/all', methods=['GET', "DELETE"])
def allData():
    def readTable(table):
        curso = machineTable.find()
        list = []
        for document in cursor:
            list.append(document)
        return list

    listMachine = readTable(machineTable)
    listTransaction = readTable(transactionTable)
    listDetection = readTable(detectionTable)
    listUser = readTable(userTable)

    if request.method == "DELETE":
        machineTable.delete_many(listMachine)
        transactionTable.delete_many(listTransaction)
        detectionTable.delete_many(listDetection)
        userTable.delete_many(listUser)

    return "Machine\n "+listMachine+" \n\n Transaction\n "+listTransaction+" \n\n Detection\n "+listDetection+" \n\nUser\n "+listUser+" \n\n"

#IDEA: bot telegram
#TODO:

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

app.run(host='127.0.0.1', port='5000', debug=True)
