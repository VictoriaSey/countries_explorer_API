def replace_mongo_id(document):
    # Replaces the BSON ObjectId with a string representation._id -> id
    if document and "_id" in document:
        document["id"] = str(document.pop("_id"))
    return document
