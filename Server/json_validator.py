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

all_consumable_S = Schema({
    Optional('bicchiere'): And(Or(float, int), lambda x: x > 0 and x < 100),
    Optional('palettina'): And(Or(float, int), lambda x: x > 0 and x < 100),
    Optional('caffe'): And(Or(float, int), lambda x: x > 0 and x < 100),
    Optional('zucchero'): And(Or(float, int), lambda x: x > 0 and x < 100),
    Optional('te concentrato'): And(Or(float, int), lambda x: x > 0 and x < 100),
    Optional('cioccolato concentrato'): And(Or(float, int), lambda x: x > 0 and x < 100),
})

all_consumable_L = ("bicchiere", "palettina", "caffe", "zucchero",
                    "latte", "te concentrato", "cioccolato concentrato")

possible_transaction = ("rfid", "cash", "app")
possible_operation = ("refill", "cleaning", "repair", "standard check")

# https://github.com/keleshev/schema


class Validator(object):

    def validate_order(toValidate, possible_orders):
        try:
            Schema({
                "transaction_type": And(str, lambda x: x in possible_transaction),
                "product":  And(str, lambda x: x in possible_orders),
                "satisfaction": And(float, lambda x: x > 0 and x < 1),
                "people_detected": And(int, lambda x: x >= 0),
                "face_recognised": And(int, lambda x: x >= 0),
                Optional("new_levels"): Use(lambda x: all_consumable_S.validate(x)),
            }).validate(toValidate)
        except SchemaError as e:
            print("new_order -> ", e)
            return False
        return True

    def validate_machine(toValidate):
        try:
            Schema({
                Optional("ID"): int,
                "orders": Use(lambda x: all_products.validate(x)),
                Optional("position_geo"): str,
                "position_des": And(str, lambda x: len(x) < 255),
                "owner": str,
                "consumable_list": And(list, lambda x: all([True if e in all_consumable_L else False for e in x])),
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

    def validate_operation(toValidate):
        try:
            Schema({
                "operatorID": str,
                "type": And(list, lambda x: all([True if e in all_consumable_L else False for e in x])),
            }).validate(toValidate)
        except SchemaError as e:
            print("new_machine -> ", e)
            return False
        return True


if __name__ == '__main__':
    # test dei validatori
    Validator.validate_machine({"ID": 67484, "orders": {"caffe": 1}})
    Validator.validate_order(
        {"trnsaction_type": "ash",
         "prodotto": "caffe",
         "satisfaction": 0.5,
         "people_detected": 1}, ["caffe", "cioccolato"])
