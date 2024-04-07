import pytest

from services.todo_services import ToDoServices
from models.todo_model import ToDoModel


class TestToDoServices:
    @pytest.fixture(scope="class")
    def todo_services_test(self):
        return ToDoServices()

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
            "id": 0,
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
        todo_services_test.delete_all_todos(todo_item_good)
        result = todo_services_test.add_todo(todo_model_test)
        assert result.get("oid") is not None

        todo_services_test.delete_all_todos(todo_item_good)

    def test_add_todo_bad(self, todo_services_test, todo_item_good):
        todo_services_test.delete_all_todos(todo_item_good)
        result = todo_services_test.add_todo(todo_item_good)
        assert result.get("error") is not None

        todo_services_test.delete_all_todos(todo_item_good)

    def test_get_todo_by_id(self, todo_services_test, todo_model_test, todo_item_good):
        todo_services_test.delete_all_todos(todo_item_good)
        # Add a todo item
        result = todo_services_test.add_todo(todo_model_test)

        # Retrieve the todo item by ID
        todo_model_test.id += 1
        todo_item_good["id"] = todo_model_test.id
        retrieved_todo = todo_services_test.get_todo_by_id(todo_model_test.id)

        print(f"Retrieved Todo: {retrieved_todo}")
        # Ensure the retrieved todo item is not None
        assert retrieved_todo is not None, "Retrieved todo item is None"

        # Ensure the retrieved todo item has the correct ID
        assert retrieved_todo.get("id") == todo_item_good.get("id"), "Incorrect todo ID"

        # Ensure the retrieved todo item has the correct title, description, and completion status
        assert retrieved_todo.get("title") == todo_model_test.title, "Incorrect todo title"
        assert retrieved_todo.get("description") == todo_model_test.description, "Incorrect todo description"
        assert retrieved_todo.get("completed") == todo_model_test.completed, "Incorrect todo completion status"
