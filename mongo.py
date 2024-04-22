from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017")
db = client["jus"]

jurisprudencias = db.get_collection("jurisprudencia")
logs = db.get_collection("logs")
pages = db.get_collection("pages")


def remove_duplicates():
    pipeline = [
        {
            "$group": {
                "_id": "$numero_peticao",
                "duplicates": {"$push": "$_id"},
                "count": {"$sum": 1}
            }
        },
        {
            "$match": {
                "count": {"$gt": 1}
            }
        }
    ]
    duplicates = list(jurisprudencias.aggregate(pipeline))
    print(f"Found {len(duplicates)} duplicates")
    for duplicate in duplicates:
        del duplicate["duplicates"][0]
    for duplicate in duplicates:
        jurisprudencias.delete_many({"_id": {"$in": duplicate["duplicates"]}})
    return duplicates

