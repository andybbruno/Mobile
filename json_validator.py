from schema import Schema, And, Or, Use, Optional, SchemaError

all_products = Schema({
    Optional('caffe'): And(Or(float, int), lambda x: x > 0),
    Optional('cioccolato'): And(Or(float, int), lambda x: x > 0),
    Optional('te'): And(Or(float, int), lambda x: x > 0),
    Optional('acqua calda'): And(Or(float, int), lambda x: x > 0),
    Optional('bicchiere vuoto'): And(Or(float, int), lambda x: x > 0),
    Optional('cappucino'): And(Or(float, int), lambda x: x > 0),
    Optional('laghine'): And(Or(float, int), lambda x: x > 0),
})

all_ingredients = ("caffe", "zucchero", "latte", "te concentrato", "cioccolato concentrato")

all_stuff = ("bicchiere", "palettina")

possible_transaction = ("rfid", "cash", "app")

# https://github.com/keleshev/schema
class Validator(object):

    def new_order(toValidate, possible_orders):
        try:
            Schema({
                    "trnsaction_type": And(str, lambda x: x in possible_transaction),
                    "prodotto":  And(str, lambda x: x in possible_orders),
                    "satisfaction": And(float, lambda x: x > 0 and x < 1),
                    "people_detected": And(int, lambda x: x > 0)
                }).validate(toValidate)
        except SchemaError as e:
            print("new_order -> ", e)
            return False
        return True

    def new_machine(toValidate):
        try:
            Schema({
                    Optional("ID"): int,
                    "orders": Use(lambda x: all_products.validate(x)),
                    Optional("position_geo"): str,
                    "position_des": And(str, lambda x: len(x) < 255),
                    "owner": str,
                    "ingredient_list": And(list, lambda x: all([True if e in all_ingredients else False for e in x])),
                    "stuff_list": And(list, lambda x: all([True if e in all_stuff else False for e in x]))
                }).validate(toValidate)
        except SchemaError as e:
            print("new_machine -> ", e)
            return False
        return True

    def del_machine(toValidate):
        try:
            Schema({
                    "ID": int,
                }).validate(toValidate)
        except SchemaError as e:
            print("new_machine -> ", e)
            return False
        return True

if __name__ == '__main__':
    #test dei validatori
    Validator.new_machine({"ID": 67484, "orders": {"caffe": 1}})
    Validator.new_order(
    {"trnsaction_type": "ash",
    "prodotto": "caffe",
    "satisfaction": 0.5,
    "people_detected": 1}, ["caffe","cioccolato"])
