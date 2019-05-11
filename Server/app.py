from flask import Flask, request, render_template, redirect, session, url_for
import pymongo
import requests
import os
import json
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
operazionTable = mobile_db["testOperation"]

app = Flask(__name__)
app.secret_key = os.urandom(16)


@app.route('/')
def homepage():
    if ('username' in session) and ('logged' in session):
        return render_template('index.html',
                               username=session['username'],

                               )
    else:
        return redirect('/login')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']

        if userTable.find_one({"username": username}):
            return render_template('register.html', error='Username already in use!')
        elif password1 != password2:
            return render_template('register.html', error="Please check the passwords")
        else:
            userTable.insert_one({"username": username, "password": password1})
            session['username'] = username
            return redirect('/reg')
    else:
        return render_template('register.html')


@app.route('/reg', methods=['GET'])
def reg_complete():
    print(session['username'])
    return render_template('regcomplete.html', user=session['username'])


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if userTable.find_one({"username": username, "password": password}):
            session['username'] = username
            session['logged'] = True
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
        return "You must specify ID of machine to delete"
    return 'Machine deleteed'


@app.route('/<int:machineID>/maintenance', methods=['POST'])
def new_operation(machineID):
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
    jsonReq = request.get_json(silent=True, force=True)
    # Per questa orerazione è richiesto l'ID dell'operatore
    if not Validator.validate_operation(jsonReq):
        return "Not Valid JSON"

    operatorID = int(jsonReq["operatorID"])
    if machineTable.find_one({"ID": machineID}):
        return "Machine ID not valid"
    if userTable.find_one({"ID": operatorID}):
        return "Operator ID not valid"

    op_type = jsonReq["type"]
    currTime = int(data.timestamp(data.now()))
    operazionTable.insert_one({
        "operatorID": operatorID,
        "machineID": machineID,
        "type": op_type,
        "timestamp": currTime
    })

    if op_type == "refill":
        # TODO richiedere i nuovi livelli alla macchinetta se è stato fatto un refill
        #new_level = request_to_macchientta()
        new_level = {"bicchiere": 50, "palettina": 50, "caffe": 50,
                     "cioccolato concentrato": 50, "zucchero": 50}
        to_modify = {}
        for k, v in new_levels.items():
            to_modify = {"maintenance.consumable_list."+k: v}
        machineTable.update_one({"ID": ID}, {"$set": to_modify})
    if op_type == "cleaning":
        machineTable.update_one(
            {"ID": machineID}, {"$set": {"maintenance.last_cleaning": currTime}})
    if op_type in ["repair", "standard check"]:
        machineTable.update_one(
            {"ID": machineID}, {"$set": {"maintenance.last_maintenance": currTime}})

    return "Operarione registrata"


@app.route('/<int:ID>/maintenance', methods=['GET'])
def get_status(ID):
    """
        Restituisce tutte le info della macchina.
    """
    operatorID = int(jsonReq["operatorID"])
    machine = machineTable.find_one({"ID": machineID})
    if machine:
        return machine
    else:
        return "Machine ID not valid"


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
    timestamp = int(data.timestamp(data.now()))
    currMachine = machineTable.find_one({"ID": ID})
    if not currMachine:
        return "Not Valid Machine"

    if not Validator.validate_order(jsonReq, currMachine["possible_orders"].keys()):
        return "Not Valid JSON"

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
        "people_detected": jsonReq["people_detected"]
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
    return "Transaction registered"


@app.route('/<int:ID>/mngt', methods=['POST', 'GET'])
def manage():
    jsonReq = request.get_json(silent=True, force=True)
    if request.method == 'POST':
        return 'Management updated'
    else:
        return 'Management returned'


# ------------------------Funzioni di Test e Gesitone -------------------------

def readTable(table):
    cursor = table.find()
    list = []
    for document in cursor:
        list.append(document)
    return list


# TODO: Da aliminare
@app.route('/all', methods=['GET', "DELETE"])
def allData():

    if request.method == "DELETE":
        userTable.drop
        machineTable.drop
        transactionTable.drop
        detectionTable.drop
        return "All deleted!"
    else:
        listMachine = readTable(machineTable)
        listTransaction = readTable(transactionTable)
        listDetection = readTable(detectionTable)
        listUser = readTable(userTable)
        listOperazion = readTable(operazionTable)

        ret = "Machine\n " + str(listMachine) + " \n\n Transaction\n " + str(listTransaction) + " \n\n Detection\n " + \
            str(listDetection) + " \n\nUser\n " + str(listUser) + " \n\nOperation\n" + str(listOperazion)

        return ret


@app.route('/addUser', methods=["POST"])
def addUser():
    jsonReq = request.get_json(silent=True, force=True)
    # TODO: Aggiungere Validazione se diventa una funzione "Finale"
    userTable.insert_one(jsonReq)
    return "User Added"

# IDEA: bot telegram


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


app.run(host='0.0.0.0', port='3000', debug=True)
