import pytest
import pymongo

from services.todo_services import ToDoServices
from models.todo_model import ToDoModel
from utils.db_store import ToDoDBStore


class TestToDoServices:
    @pytest.fixture(scope="class")
    def todo_services_test(self):
        return ToDoServices()

    @pytest.fixture(scope="class")
    def todo_db_store(self):
        return ToDoDBStore()

    @pytest.fixture(scope="class")
    def todo_model_test(self, todo_item_good):
        return ToDoModel(**todo_item_good)

    @pytest.fixture(scope="class")
    def todo_item_good(self):
        return {
            "id": 0,
            "title": "PytestFixtureGood",
            "description": "InstanceGood",
            "completed": True
        }

    @pytest.fixture(scope="class")
    def todo_item_bad(self):
        return {
            "id": "0",
            "title": "PytestFixtureBad",
            "description": "InstanceBad",
            "completed": False,
            "bad": True
        }

    @pytest.fixture(scope="class")
    def todo_item_update(self):
        return {
            "title": "PytestFixtureUpdate",
            "description": "InstanceUpdate",
            "completed": False,
        }

    def test_add_todo_good(self, todo_services_test, todo_model_test, todo_item_good):
        todo_services_test.delete_all_todos()
        result = todo_services_test.add_todo(todo_model_test)
        assert result.get("oid") is not None

        todo_services_test.delete_all_todos()

    def test_add_todo_bad(self, todo_services_test, todo_item_good):
        todo_services_test.delete_all_todos()
        result = todo_services_test.add_todo(todo_item_good)
        assert result.get("error") is not None

        todo_services_test.delete_all_todos()

    def test_get_todo_by_id(self, todo_services_test, todo_model_test, todo_item_good):
        todo_services_test.delete_all_todos()
        todo_services_test.add_todo(todo_model_test)

        # Retrieve the todo item by ID
        todo_model_test.id += 1
        todo_item_good["id"] = todo_model_test.id
        result = todo_services_test.get_todo_by_id(todo_model_test.id)

        # Ensure the retrieved todo item is not None
        assert result is not None, "Retrieved todo item is None"

        # Ensure the retrieved todo item has the correct ID
        assert result.get("id") == todo_item_good.get("id")

        # Ensure the retrieved todo item has the correct title, description, and completion status
        assert result.get("title") == todo_model_test.title
        assert result.get("description") == todo_model_test.description
        assert result.get("completed") == todo_model_test.completed

        todo_services_test.delete_all_todos()

    def test_get_todo_by_id_bad(self, todo_services_test, todo_model_test, todo_item_good, todo_item_bad):
        todo_services_test.delete_all_todos()
        todo_services_test.add_todo(todo_model_test)

        todo_model_test.id = todo_item_bad.get("id")
        result = todo_services_test.get_todo_by_id(todo_model_test.id)

        # Debugging statements
        print(f"Result: {result}")
        print(f"Todo item bad ID: {todo_model_test.id}")

        # Ensure the retrieved todo item is not None
        assert result is not None, "Retrieved todo item is None"

        # Ensure the retrieved todo item has the correct ID
        assert result.get("id") != todo_item_good.get("id")

        assert result.get("error") is not None

        todo_services_test.delete_all_todos()

    def test_get_todo_by_query(self, todo_services_test, todo_model_test, todo_item_good):

        todo_services_test.delete_all_todos()
        todo_services_test.add_todo(todo_model_test)

        todo_model_test.id += 1
        todo_item_good["id"] = todo_model_test.id

        result = todo_services_test.get_todo_by_query(todo_item_good)

        assert result is not None, "Retrieved todo item is None"
        assert isinstance(result, list), "Result is not a list"
        assert len(result) == 1, "Result length is not 1"
        assert getattr(result[0], "id") == todo_item_good.get("id")

        for key, value in todo_item_good.items():
            for todo in result:
                assert getattr(todo, key) == value

        todo_services_test.delete_all_todos()

    def test_get_todo_by_query_bad(self, todo_services_test, todo_db_store, todo_item_bad):

        todo_services_test.delete_all_todos()
        todo_db_store.add_document("todo_list_db", "todo_list_collection", todo_item_bad)

        result = todo_services_test.get_todo_by_query({"id": 0})

        assert result is not None, "Retrieved todo item list is None"
        for todo_item in result:
            assert todo_item.get("error") is not None, "Expected error in todo item"

        todo_services_test.delete_all_todos()

    def test_update_todo_by_id(self, todo_services_test, todo_item_good, todo_model_test, todo_item_update):

        todo_services_test.delete_all_todos()
        todo_services_test.add_todo(todo_model_test)

        todo_item_good["id"] += 1

        result = todo_services_test.update_todo_by_id(todo_item_good.get("id"), todo_item_update)
        result = todo_services_test.get_todo_by_id(todo_item_good.get("id"))

        assert result.get("error") is None
        for key, value in todo_item_update.items():
            assert result.get(key) == value

        todo_services_test.delete_all_todos()

    def test_update_todo_by_id_bad(self, todo_services_test, todo_db_store, todo_item_bad, todo_item_update):
        todo_services_test.delete_all_todos()
        todo_db_store.add_document("todo_list_db", "todo_list_collection", todo_item_bad)

        result = todo_services_test.update_todo_by_id(todo_item_bad.get("id"), todo_item_update)
        result = todo_services_test.get_todo_by_query({"id": 0})

        assert result is not None, "Retrieved todo item list is None"
        for todo_item in result:
            assert todo_item.get("error") is not None, "Expected error in todo item"

        todo_services_test.delete_all_todos()

    def test_delete_todo_by_id(self, todo_services_test, todo_item_good, todo_model_test):

        todo_services_test.delete_all_todos()
        todo_services_test.add_todo(todo_model_test)

        todo_model_test.id += 1
        todo_item_good["id"] = todo_model_test.id

        result = todo_services_test.delete_todo_by_id(todo_item_good.get("id"))
        assert result == {"result": f"Documents deleted: 1"}

        todo_services_test.delete_all_todos()

    def test_delete_todo_by_id_bad(self, todo_services_test, todo_item_bad, todo_model_test, todo_db_store):

        todo_services_test.delete_all_todos()
        todo_db_store.add_document("todo_list_db", "todo_list_collection", todo_item_bad)

        result = todo_services_test.delete_todo_by_id(todo_model_test)
        assert result.get("error") is not None

        todo_services_test.delete_all_todos()

    def test_delete_all_todos(self, todo_services_test, todo_item_good, todo_model_test):

        todo_services_test.delete_all_todos()
        todo_services_test.add_todo(todo_model_test)

        count_before_deletion = len(todo_services_test.get_todo_by_query({}))

        result = todo_services_test.delete_all_todos()
        deleted_count = int(result["result"].split(":")[1].strip())

        count_after_deletion = len(todo_services_test.get_todo_by_query({}))

        assert count_before_deletion - deleted_count == count_after_deletion
        assert result is not None, "Result of deletion operation is None"
        assert "result" in result, "Result does not contain deletion information"
        assert "Document deleted" in result["result"], "Deletion information is not provided"


