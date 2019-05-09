from schema import Schema, And, Use, Optional

mylist = ('caffe', 'cioccolato')

# https://github.com/keleshev/schema
class Validator(object):

    def validate_order(toValidate, possible_orders):
        return Schema({
            "trnsaction_type": And(str, lambda x: x in ("rfid", "cash", "app")),
            "prodotto":  And(str, lambda x: x in possible_orders),
            "satisfaction": And(float, lambda x: x > 0 and x < 1),
            "people_detected": And(int, lambda x: x > 0)
            }).validate(toValidate)

    def validate_machine(toValidate):
        return Schema({
                "ID": int,
                'orders': Use(lambda s: True if s in mylist else False),
            }, ignore_extra_keys = True).validate(toValidate)

if __name__ == '__main__':
    #test dei validatori
    Validator.validate_machine({"ID": 67484, "orders": "caffe"})
    Validator.validate_order(
    {"trnsaction_type": "cash",
    "prodotto": "caffe",
    "satisfaction": 0.5,
    "people_detected": 1}, ["caffe","cioccolato"])
