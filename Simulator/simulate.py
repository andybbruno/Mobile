
"""
Script per la simulazione del di un interazione intensa tra utenti e macchinetta
"""
server = None #TODO creare il collegameno al vero server
#TODO simulare anche il collegameto con il rasp per la richesta dei livelli

#Cancello tutto quello che c'è nel database per partire da zero
server.delete("/all")
# Ripopolo il Database con dati fittizi

server.post("/addUser", json = {})

#Creo gli operatori
server.post("/addUser", json = {
    "ID": "1",
    "role": "operator"
    "username": "Fesso"
    "password": "pw"
})

#Creo le macchinette
server.post("/machine", json = {
"ID": "111"
"orders": {"caffe": 0.8, "cioccolato": 1},
"position_des": "Infondo a destra c'è il cesso!",
"owner": "TuaMa srl",
"consumable_list": ["bicchiere", "palettina", "caffe", "cioccolato concentrato", "zucchero"],
"operatorID": "Oper_1"
})

server.post("/machine", json = {
"ID": "222"
"orders": {"caffe": 0.6, "cioccolato": 1.1, "te": 0.7, "bicchere vuoto": 0.2},
"position_des": "Infondo a destra c'è il cesso!",
"owner": "TuaMa srl",
"consumable_list": ["bicchiere", "palettina", "caffe", "cioccolato concentrato", "zucchero"],
"operatorID": "Oper_1"
})

#simulo lapulizia e il refill
server.post("/111/maintenance", json = {
    "operatorID": 1,
    "type": "cleaning"
})
server.post("/111/maintenance", json = {
    "operatorID": 1,
    "type": "refill"
})
server.post("/222/maintenance", json = {
    "operatorID": 1,
    "type": "cleaning"
})
server.post("/222/maintenance", json = {
    "operatorID": 1,
    "type": "refill"
})

#simulo degli ordini fatti sulle due macchinette
server.post("/", json = {})
server.post("/addUser", json = {})


server.post("/challenge", data={"runs":[1]}, follow_redirects=True)
