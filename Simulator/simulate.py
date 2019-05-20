from flask import Flask, request, render_template
import os, requests, json
from datetime import datetime as time
from random import randint

app = Flask(__name__)
app.secret_key = os.urandom(16)

import pymongo

_mongoDB = pymongo.MongoClient("mongodb://ec2-18-212-110-170.compute-1.amazonaws.com:27017/")
_mobile_db = _mongoDB["test_db"]

machineTable = _mobile_db["testTable"]
detectionTable = _mobile_db["testDetection"]



@app.route('/', methods=['GET'])
def homepage():
    return render_template("simulator.html")


@app.route('/', methods=['POST'])
def order():

    id = 33444
    url = "http://ec2-18-212-110-170.compute-1.amazonaws.com:3000/"+id+"/"


    lista = ("caffe" "cappuccino", "te", "cioccolato")
    val = ""
    man_type = ""

    order = False
    maint = False

    #--------------------------------------------Ordini------------------------- 
    if (request.form['Caffe'] is not None):
        val = "caffe"
        order = True

    if (request.form['Cioccolata'] is not None):
        val = "cioccolata"
        order = True

    if (request.form['Cappuccino'] is not None):
        val = "cappuccino"
        order = True
    
    if (request.form['Te'] is not None):
        val = "te"
        order = True

    
    #--------------------------------------------Manutenzione------------------------- 
    if (request.form['manutenzione'] is not None):
        #modifica data di manutenzione della macchina
        machineTable.update_one({"ID": id}, { "$set": { "maintenance.last_maintenance": time.timestamp(time.now()) }})
        man_type = "repair"
        maint = True

    if (request.form['refill'] is not None):
        # modifica valori dell 
        machineTable.update_one({"ID": id}, { "$set": { "maintenance.consumable_list":{
            "bicchiere": 20 + randint(-10, 10),
            "palettina": 20 + randint(-10, 10),
            "caffe": 20 + randint(-10, 10),
            "zucchero": 20 + randint(-10, 10),
            "latte": 20 + randint(-10, 10),
            "te": 20 + randint(-10, 10),
            "cioccolato": 45
        }}})
        man_type = "refill"
        maint = True

    if (request.form['fine'] is not None):
        # simulazione della fine consumabili
        machineTable.update_one({"ID": id}, { "$set": { "maintenance.consumable_list":{
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

    if (request.form['rottura'] is not None):
        # registrazione della raottura
        machineTable.update_one({"ID": id}, { "$set": { "working": False } })
        man_type = None
        maint = True


    if (order):
        data = {"transaction_type": "cash",
            "product": val,
            "satisfaction": 0.99,
            "people_detected": 99,
            "face_recognised": 99
            }
        print(requests.post(url+"order", json=json.dumps(data)))
        return render_template("simulator.html")

    if maint:
        if man_type is not None:
            data = {
                "operatorID" : 12345,
                "type" : man_type
            }

            print(requests.post(url+"order", json=json.dumps(data)))
        return render_template("simulator.html")


app.run(host='0.0.0.0', port='4000', debug=True)
