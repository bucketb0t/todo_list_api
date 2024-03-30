from utils.db_store import ToDoDBStore
import pytest


class TestToDoDBStore:
    @pytest.fixture(scope="function")
    def mongo_driver(self):
        todo_db = ToDoDBStore()
        return todo_db

    @pytest.fixture(scope="function")
    def todo_document_fix(self):
        todo_pytest = {
            "id": 0,
            "title": "Pytest Fixture",
            "description": "First Instance",
            "completed": True
        }
        return todo_pytest

    def test_add_todo(self, mongo_driver, todo_document_fix):
        mongo_driver.delete_all_documents("todo_list_db", "todo_list_collection", {})
        result = mongo_driver.add_document("todo_list_db", "todo_list_collection", todo_document_fix)
        assert result.inserted_id is not None
        mongo_driver.delete_all_documents("todo_list_db", "todo_list_collection", {})
