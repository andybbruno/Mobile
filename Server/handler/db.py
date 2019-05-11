import pymongo

_mongoDB = pymongo.MongoClient("mongodb://localhost:27017/")
_mobile_db = _mongoDB["test_db"]

machineTable = _mobile_db["testTable"]
transactionTable = _mobile_db["testTransaction"]
detectionTable = _mobile_db["testDetection"]
userTable = _mobile_db["testUser"]
operazionTable = _mobile_db["testOperation"]
