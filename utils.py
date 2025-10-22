from bson import ObjectId


def replace_mongo_id(doc):
    if not doc:
        return doc

    # Handle the root '_id'
    if "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]

    # Convert any nested ObjectId fields (like 'user_id')
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)
        elif isinstance(value, dict):
            doc[key] = replace_mongo_id(value)
        elif isinstance(value, list):
            doc[key] = [
                (
                    replace_mongo_id(v)
                    if isinstance(v, dict)
                    else str(v) if isinstance(v, ObjectId) else v
                )
                for v in value
            ]

    return doc
