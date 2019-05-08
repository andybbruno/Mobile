from flask import Flask, request


app = Flask(__name__)

@app.route('/')
def homepage():
    return 'Dashboard'

@app.route('/machine', methods=['POST', 'DELETE'])
def machine():
    if request.method == 'POST':
        return 'New machine'
    else:
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