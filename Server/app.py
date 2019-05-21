from flask import Flask, request, render_template, redirect, session, url_for, jsonify
import os
from werkzeug.utils import secure_filename
from json_validator import Validator
import handler
import handler.db as db
import json
import random
from datetime import datetime


app = Flask(__name__)
app.secret_key = os.urandom(16)
# app.config['UPLOAD_FOLDER'] = "Server/static/live/"
app.config['UPLOAD_FOLDER'] = "static/live/"


# ----------------------------------WEB-----------------------------------------ù

def renderWith(renderedContent):
    if ('username' in session) and ('logged' in session):
        return render_template('index.html',
                               username=session['username'],
                               content=renderedContent)
    else:
        return redirect('/login')


@app.route('/')
def homepage():
    id = db.machineTable.distinct('ID')

    id_1 = id[0]
    id_2 = id[1]

    tmp_1 = db.machineTable.find_one(
        {'ID': id_1})['maintenance']['consumable_list']
    lbl_1 = list(tmp_1.keys())
    val_1 = list(tmp_1.values())

    tmp_2 = db.machineTable.find_one(
        {'ID': id_2})['maintenance']['consumable_list']
    lbl_2 = list(tmp_2.keys())
    val_2 = list(tmp_2.values())

    img1 = "/static/live/" + str(id_1) + ".jpg"
    img2 = "/static/live/" + str(id_2) + ".jpg"

    content = render_template("main-panel/dashboard.html",
                              ID1=id_1,
                              ID2=id_2,
                              imgID1=img1,
                              imgID2=img2,
                              val_1=val_1,
                              val_2=val_2,
                              lbl_1=lbl_1,
                              lbl_2=lbl_2)

    return renderWith(content)


@app.route('/statistics')
def statistics():
    id = db.machineTable.distinct('ID')

    id_1 = id[0]
    id_2 = id[1]

    tmp_1 = db.machineTable.find_one(
        {'ID': id_1})['management']['count_orders']
    lbl_1 = list(tmp_1.keys())
    val_1 = list(tmp_1.values())

    tmp_2 = db.machineTable.find_one(
        {'ID': id_2})['management']['count_orders']
    lbl_2 = list(tmp_2.keys())
    val_2 = list(tmp_2.values())

    content = render_template("main-panel/stats.html",
                              ID1=id_1,
                              ID2=id_2,
                              val_1=val_1,
                              val_2=val_2,
                              lbl_1=lbl_1,
                              lbl_2=lbl_2)

    return renderWith(content)


@app.route('/<int:machineID>/people')
def people(machineID):
    people = db.detectionTable.find({'machineID': machineID}).sort([('timestamp', -1)]).limit(1).next()['people_detected']
    return jsonify(machineID=machineID, people_detected=people)


@app.route('/machines')
def machinelist():

    machines = []
    machine_list = db.machineTable.find()

    for mac in machine_list:
        order = mac["working"]
        order_badge = None
        if not order:
            order = "Out of order"
            order_badge = "danger"
        elif any([e < 20 for e in mac["maintenance"]["consumable_list"].values()]):
            order = "To refill"
            order_badge = "warning"
        else:
            order = "Working"
            order_badge = "success"

        sat = mac["satisfaction_level"]
        sat_badge = None
        if sat > 0.8:
            sat_badge = "success"
        elif sat < 0.4:
            sat_badge = "danger"
        else:
            sat_badge = "warning"

        dSat = (random.random() * 2)-1
        badge_dSat = "danger" if dSat >= 0 else "success"
        arrow = "down" if dSat >= 0 else "up"

        machines.append({
            "id": mac["ID"],
            "owner": mac["management"]["owner"],
            "satisfaction": "%.4f" % sat,
            "badge_sat": sat_badge,
            "delta_satisfaction": "%.4f" % dSat,
            "badge_dSat": badge_dSat,
            "arrow": arrow,
            "operarion": order,
            "badge_ops": order_badge,
        })

    return renderWith(render_template("main-panel/listMachines.html", machines=machines))


@app.route('/<int:ID>/maintenance', methods=['GET'])
def get_status(ID):
    """
        Renderizza la pagina con tutte le info della macchina.
    """
    mac = db.machineTable.find_one({"ID": ID})
    if not mac:
        return renderWith(render_template("main-panel/not_found.html"))

    order = mac["working"]
    order_badge = None
    if not order:
        order = "Out of order"
        order_badge = "danger"
    elif any([e < 20 for e in mac["maintenance"]["consumable_list"].values()]):
        order = "To Refill"
        order_badge = "warning"
    else:
        order = "Working"
        order_badge = "success"

    tmp_1 = db.machineTable.find_one(
        {'ID': ID})['maintenance']['consumable_list']
    lbl_1 = list(tmp_1.keys())
    val_1 = list(tmp_1.values())

    tmp_2 = db.machineTable.find_one({'ID': ID})['management']['count_orders']
    lbl_2 = list(tmp_2.keys())
    val_2 = list(tmp_2.values())

    all_info = {
        "owner": mac["management"]["owner"],
        "tot_owner": "Zio",
        "delta_revenue": "Zio",
        "tot_revenue": "Zio",
        "delta_satisfaction": "Zio",
        "satisfaction": "%.4f" % mac["satisfaction_level"],
        "state": order,
        "next_ops": 3,

        "id": mac["ID"],
        "imgID": "/static/live/" + str(ID) + ".jpg",
        "position_des": mac["position_des"],
        "position_geo": mac["position_geo"],
        "last_maintenance": datetime.fromtimestamp(mac["maintenance"]["last_maintenance"]),
        "last_cleaning": datetime.fromtimestamp(mac["maintenance"]["last_cleaning"]),
        "off_time_range": mac["management"]["off_time_range"],
        "installation_date": datetime.fromtimestamp(mac["installation_date"]),

        # grafico consumabili
        "val_1": val_1,
        "lbl_1": lbl_1,
        "val_2": val_2,
        "lbl_2": lbl_2,
    }
    content = render_template("main-panel/infoMachine.html", **all_info)
    return renderWith(content)


@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect('/')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']
        # TODO inserire un id personalizzato all'utente
        if db.userTable.find_one({"username": username}):
            return render_template('register.html', error='Username already in use!')
        if password1 != password2:
            return render_template('register.html', error="Please check the passwords")
        if (username == ""):
            return render_template('register.html', error="Please enter a valid username")
        if (password1 == "") or (password2 == ""):
            return render_template('register.html', error="Please enter a valid password")
        else:
            db.userTable.insert_one(
                {"username": username, "password": password1})
            session['username'] = username
            return redirect('/reg')
    else:
        return render_template('register.html')


@app.route('/reg', methods=['GET'])
def reg_complete():
    # print(session['username'])
    return render_template('regcomplete.html', user=session['username'])


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if db.userTable.find_one({"username": username, "password": password}):
            session['username'] = username
            session['logged'] = True
            return redirect('/')
        else:
            return render_template('login.html', error="Incorrect username or password")
    else:
        return render_template('login.html')


# ---------------------------------IOT------------------------------------------
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
    is_ok, error = handler.new_machine(
        request.get_json(silent=True, force=True))
    if is_ok:
        return 'New machine Added'
    return 'Some error occurred -> ' + error


@app.route('/<int:machineID>', methods=['DELETE'])
def del_machine(machineID):
    # IDEA: non e meglio fare un end point \<ID> DELETE
    """
        Elimina la macchine con l'id specificato dalla tabella delle macchine
        JSON in entrata:
        { "ID": <int> }
    """

    return 'Machine deleteed' + str(db.machineTable.delete_one({'ID': machineID}))


@app.route('/<int:machineID>/live', methods=['POST'])
def live(machineID):
    if 'frame' in request.files:
        file = request.files['frame']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return '200', 200
    else:
        return '404', 404


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
    var = request.get_json(silent=True, force=True)
    print(var, type(var))
    is_ok, error = handler.register_operation(
        machineID, var)
    if is_ok:
        return "Opertion registered"
    return "Some error occurred -> " + error


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
                "face_recognised": <int, number of face recognised>
                *"new_levels":{
                    "<consumable>": <int, new_level,
                    ...
                }
            }
    """
    is_ok, error = handler.register_order(
        ID, json.loads(request.get_json(silent=True, force=True)))
    if is_ok:
        return "Transaction registered"
    return "Some error occurred -> " + error


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

    return "Machine</br> {} </br></br> Transaction</br> {} </br></br> Detection</br> {} </br></br>User</br> {} </br></br>Operation</br>{}".format(
        str(listMachine), str(listTransaction), str(listDetection), str(listUser), str(listOperazion))


@app.route('/addUser', methods=["POST"])
def addUser():
    jsonReq = request.get_json(silent=True, force=True)
    # TODO: Aggiungere Validazione se diventa una funzione "Finale"
    db.userTable.insert_one(jsonReq)
    return "User Added"

# -----------------------------Telegram Bot--------------------------------------


@app.errorhandler(404)
def page_not_found(e):
     # note that we set the 404 status explicitly
    return renderWith(render_template("main-panel/not_found.html"))


app.run(host='0.0.0.0', port='3000', debug=True)
