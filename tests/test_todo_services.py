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
            "completed": True,
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

        todo_services_test.delete_all_todos(todo_item_good)

    def test_get_todo_by_id_bad(self, todo_services_test, todo_model_test, todo_item_good, todo_item_bad):
        todo_services_test.delete_all_todos(todo_item_good)
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

        todo_services_test.delete_all_todos(todo_item_good)

    def test_get_todo_by_query(self, todo_services_test, todo_model_test, todo_item_good):

        todo_services_test.delete_all_todos(todo_item_good)
        todo_services_test.add_todo(todo_model_test)

        todo_model_test.id += 1
        todo_item_good["id"] = todo_model_test.id

        result = todo_services_test.get_todo_by_query(todo_item_good)

        assert result is not None, "Retrieved todo item is None"
        assert isinstance(result, list), "Result is not a list"
        assert len(result) == 1, "Result length is not 1"
        assert getattr(result[0],"id") == todo_item_good.get("id")

        for key, value in todo_item_good.items():
            for todo in result:
                assert getattr(todo, key) == value

        todo_services_test.delete_all_todos(todo_item_good)