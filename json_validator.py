from schema import Schema, And, Use

mylist = ('caffe', 'cioccolato')
new_machine = Schema({
                    'ID':       Use(lambda x: len(x) != 10),
                    'orders':   Use(lambda s: any([True if x.lower in mylist else False for x in s ])),
                    }, ignore_extra_keys = True)
