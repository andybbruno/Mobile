from schema import Schema, And, Use, Optional

mylist = ('caffe', 'cioccolato')

# https://github.com/keleshev/schema
class Validator(object):

    def new_order(toValidate, possible_orders):
        return Schema({
            "trnsaction_type": And(str, lambda x: x in ("rfid", "cash", "app")),
            "prodotto":  And(str, lambda x: x in possible_orders),
            "satisfaction": And(float, lambda x: x > 0 and x < 1),
            "people_detected": And(int, lambda x: x > 0)
            }).validate(toValidate)

    def new_machine(toValidate):
        return Schema({
                "ID": int,
                'orders': Use(lambda s: any([True if x.lower in mylist else False for x in s ])),
            }, ignore_extra_keys = True).validate(toValidate)

if __name__ == '__main__':
    #test dei validatori
    Validator.new_machine({"ID": 67484, "orders": ["caffe"]})
    Validator.new_order(
    {"trnsaction_type": "cash",
    "prodotto": "caffe",
    "satisfaction": 0.5,
    "people_detected": 1}, ["caffe","cioccolato"])
