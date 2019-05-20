from flask import Flask, request, render_template
import os, requests, json

app = Flask(__name__)
app.secret_key = os.urandom(16)



@app.route('/', methods=['GET'])
def homepage():
    return render_template("simulator.html")


@app.route('/', methods=['POST'])
def order():


    url = "http://ec2-18-212-110-170.compute-1.amazonaws.com:3000/11222/order"


    lista = ("caffe" "cappuccino", "te", "cioccolato")
    val = ""
    man_type = ""

    order = False
    maint = False

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

    if (request.form['manutenzione'] is not None):
        man_type = "repair"
        maint = True

    if (request.form['refill'] is not None):
        man_type = "refill"
        maint = True

    if (request.form['fine'] is not None):
        # TODO: RINO FAI QUESTA COSA 
        man_type = "fine"
        maint = True

    if (request.form['manutenzione'] is not None):
        # TODO: RINO FAI QUESTA COSA 
        man_type = "repair"
        maint = True

    

    if (order):
        data = {"transaction_type": "cash",
            "product": val,
            "satisfaction": 0.99,
            "people_detected": 99,
            "face_recognised": 99
            }
        print(requests.post(url, json=json.dumps(data)))
        return render_template("simulator.html")

    if maint:
        data = {
            "operatorID" : 12345
            "type" : man_type
        }

        return render_template("simulator.html")





app.run(host='0.0.0.0', port='4000', debug=True)
