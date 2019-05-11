from flask import Flask, request, render_template, redirect, session, url_for
import os

from json_validator import Validator

import handler
import handler.db as db


app = Flask(__name__)
app.secret_key = os.urandom(16)

#----------------------------------WEB-----------------------------------------
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


#---------------------------------IOT------------------------------------------
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
    """
    is_ok, error = handlerMachine.new_machine(request.get_json(silent=True, force=True))
    if is_ok: return 'New machine Added'
    return 'Some error occurred -> '+ error

@app.route('/machine', methods=['DELETE'])
def del_machine():
    # IDEA: non e meglio fare un end point \<ID> DELETE
    """
        Elimina la macchine con l'id specificato dalla tabella delle macchine
        JSON in entrata:
        { "ID": <int> }
    """
    if not Validator.del_machine(request.get_json(silent=True, force=True)):
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
    """
<<<<<<< HEAD
    is_ok, error = handler.register_operation(request.get_json(silent=True, force=True))
    if is_ok: return "Opertion registered"
    return "Some error occurred -> " + error
=======
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
>>>>>>> 97e9bc24bd8e49c8dd5bee470905a0267389539d


@app.route('/<int:ID>/maintenance', methods=['GET'])
def get_status(ID):
    """
        Restituisce tutte le info della macchina.
    """
    machine = machineTable.find_one({"ID": ID})
    if machine: return machine
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
    """
    is_ok, error = handler.register_order(request.get_json(silent=True, force=True))
    if is_ok: return "Transaction registered"
    return "Some error occurred -> "+ error


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
    def readTable(table):
        cursor = table.find()
        list = []
        for document in cursor:
            list.append(document)
        return list

    listMachine = readTable(db.machineTable)
    listTransaction = readTable(db.transactionTable)
    listDetection = readTable(db.detectionTable)
    listUser = readTable(db.userTable)
    listOperazion = readTable(db.operazionTable)

    if request.method == "DELETE":
        db.userTable.drop
        db.machineTable.drop
        db.transactionTable.drop
        db.detectionTable.drop

    return "Machine\n {} \n\n Transaction\n {} \n\n Detection\n {} \n\nUser\n {} \n\nOperation\n{}".format(
        str(listMachine), str(listTransaction), str(listDetection), str(listUser), str(listOperazion))

@app.route('/addUser', methods=["POST"])
def addUser():
    jsonReq = request.get_json(silent=True, force=True)
    # TODO: Aggiungere Validazione se diventa una funzione "Finale"
    userTable.insert_one(jsonReq)
    return "User Added"

#-----------------------------Telegram Bot--------------------------------------


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

app.run(host='0.0.0.0', port='3000', debug=True)
