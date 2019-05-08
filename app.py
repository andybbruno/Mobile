from flask import Flask, request
import pymongo

mongoDB = pymongo.MongoClient("mongodb://localhost:27017/")
mobile_db = mongoDB["test_db"]


app = Flask(__name__)

@app.route('/')
def homepage():
    cursor = mobile_db["testTable"].find()

    for document in cursor:
        print(document)

    return 'Dashboard'

@app.route('/machine', methods=['POST', 'DELETE'])
def machine():
    jsonReq = request.get_json(silent=True, force=True)
    #TODO : Validazione del formato json
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

app.run(host='0.0.0.0', port='3000', debug=True)
