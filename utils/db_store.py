import pymongo
from pymongo import MongoClient
from bson import ObjectId


class ToDoDBStore:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)

    def initialize_db(self, db_name: str, db_collection: str):
        db = self.client[db_name]
        collection = db[db_collection]
        test_document = {
            "id": 0,
            "title": "First Initialization",
            "description": "First Instance",
            "completed": True
        }
        test_update_document = {
            "id": 1,
            "title": "Updated Initialization",
            "description": "Updated Instance",
            "completed": True
        }

        result = self.add_document(db_name, db_collection, test_document)
        test_document_id = test_document['id']
        result = self.get_all_documents(db_name, db_collection)
        result = self.get_document_by_id(db_name, db_collection, test_document_id)
        result = self.get_documents_by_query(db_name, db_collection, {"id": test_document_id})
        result = self.update_document_by_id(db_name, db_collection, test_document_id, test_update_document)
        result = self.delete_document_by_id(db_name, db_collection, test_document_id)
        result = self.delete_all_documents(db_name, db_collection, {"id": test_document_id})

    def get_next_id(self, db_name, db_collection):
        collection = self.client[db_name][db_collection]

        if collection.count_documents({}) == 0:
            return 1
        else:
            return collection.find_one({}, sort=[("id", pymongo.ASCENDING)])["id"] + 1

    def add_document(self, db_name: str, collection_name: str, document: dict):
        db = self.client[db_name]
        collection = db[collection_name]
        document['id'] = self.get_next_id(db_name, collection_name)
        return collection.insert_one(document)

    def get_all_documents(self, db_name: str, collection_name: str):
        db = self.client[db_name]
        collection = db[collection_name]
        return list(collection.find())

    def get_document_by_id(self, db_name: str, collection_name: str, task_id: int):
        db = self.client[db_name]
        collection = db[collection_name]
        return collection.find_one({"id": task_id})

    def get_documents_by_query(self, db_name: str, collection_name: str, query: dict):
        db = self.client[db_name]
        collection = db[collection_name]
        return collection.find(query)

    def update_document_by_id(self, db_name: str, collection_name: str, task_id: int, document: dict):
        db = self.client[db_name]
        collection = db[collection_name]
        collection.update_one({"_id": ObjectId(str(task_id))}, {"$set": document})
        return document

    def delete_document_by_id(self, db_name: str, collection_name: str, task_id: int):
        db = self.client[db_name]
        collection = db[collection_name]
        return collection.delete_one({"id": task_id})

    def delete_all_documents(self, db_name: str, collection_name: str, query: dict):
        db = self.client[db_name]
        collection = db[collection_name]
        return collection.delete_many(query)
