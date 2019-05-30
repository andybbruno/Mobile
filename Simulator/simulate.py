import pymongo
from flask import Flask, request, render_template
import os
import requests
import json
from datetime import datetime as time
from random import randint

app = Flask(__name__)
app.secret_key = os.urandom(16)


_mongoDB = pymongo.MongoClient(
    "mongodb://ec2-18-212-110-170.compute-1.amazonaws.com:27017/")
_mobile_db = _mongoDB["test_db"]

machineTable = _mobile_db["testTable"]
detectionTable = _mobile_db["testDetection"]


@app.route('/', methods=['GET'])
def homepage():
    return render_template("simulator.html")


@app.route('/', methods=['POST'])
def order():

    id = 33444
    url = "http://ec2-18-212-110-170.compute-1.amazonaws.com:3000/"+str(id)+"/"

    lista = ("caffe" "cappucino", "te", "cioccolato")
    val = ""
    man_type = ""

    order = False
    maint = False

    # --------------------------------------------Ordini-------------------------
    if ("Caffe" in request.form.keys()):
        val = "caffe"
        order = True

    elif ("Cioccolata" in request.form.keys()):
        val = "cioccolato"
        order = True

    elif ("Te" in request.form.keys()):
        val = "te"
        order = True

    elif ("Acquacalda" in request.form.keys()):
        val = "acqua calda"
        order = True

    if (order):
        data = {
                "transaction_type": "cash",
                "product": val,
                "satisfaction": 0.99,
                "people_detected": 99,
                "face_recognised": 99,
                "new_levels": {
                    str(val) : 1
                } 
            }
        msg = requests.post(url+"order", json=json.dumps(data))
        return render_template("simulator.html", message="<" + str(msg.status_code) + "> - " + msg.text)

    # --------------------------------------------Manutenzione-------------------------
    if ("manutenzione" in request.form.keys()):
        # modifica data di manutenzione della macchina
        machineTable.update_one({"ID": id}, {
                                "$set": {"maintenance.last_maintenance": time.timestamp(time.now()), "working": True}})
        man_type = "repair"
        maint = True

    elif ("fine" in request.form.keys()):
        # modifica valori dell
        machineTable.update_one({"ID": id}, {"$set": {"maintenance.consumable_list": {
            "bicchiere": 10 + randint(-10, 10),
            "palettina": 10 + randint(-10, 10),
            "caffe": 10 + randint(-10, 10),
            "zucchero": 10 + randint(-10, 10),
            "latte": 10 + randint(-10, 10),
            "te": 10 + randint(-10, 10),
            "cioccolato": 10 + randint(-10, 10)
        }}})
        man_type = "refill"
        maint = True

    elif ("refill" in request.form.keys()):
        # simulazione della fine consumabili
        machineTable.update_one({"ID": id}, {"$set": {"maintenance.consumable_list": {
            "bicchiere": 100,
            "palettina": 100,
            "caffe": 100,
            "zucchero": 100,
            "latte": 100,
            "te": 100,
            "cioccolato": 100
        }}})
        man_type = None
        maint = True

    elif ("rottura" in request.form.keys()):
        # registrazione della raottura
        machineTable.update_one({"ID": id}, {"$set": {"working": False}})
        man_type = None
        maint = True

    if (maint):
        if man_type is not None:
            data = {
                "operatorID": 12345,
                "type": str(man_type)
            }

            msg = requests.post(url+"maintenance", json=json.dumps(data))
            return render_template("simulator.html", message="<" + str(msg.status_code) + "> - " + msg.text)
        else:
            return render_template("simulator.html", message="<200> - Updated")


app.run(host='0.0.0.0', port='4000', debug=True)
