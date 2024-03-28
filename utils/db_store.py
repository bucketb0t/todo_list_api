import pymongo
from pymongo import MongoClient
from bson import ObjectId


class ToDoDBStore:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)

    def add_document(self, db_name, collection_name, document):
        db = self.client[db_name]
        collection = db[collection_name]
        collection.insert_one(document)
        return document

    def get_all_documents(self, db_name, collection_name):
        db = self.client[db_name]
        collection = db[collection_name]
        return collection

    def get_document_by_id(self, db_name, collection_name, document_id):
        db = self.client[db_name]
        collection = db[collection_name]
        return collection.find_one({"_id": document_id})

    def get_document_oid(self, db_name, collection_name, document_oid):
        db = self.client[db_name]
        collection = db[collection_name]
        return collection.find_one({"_id": ObjectId(document_oid)})
