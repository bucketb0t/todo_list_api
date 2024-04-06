import pytest

from utils.db_store import ToDoDBStore
from services.todo_services import ToDoServices
from models.todo_model import ToDoModel


class TestToDoServices:
    @pytest.fixture(scope="class")
    def todo_services_test(self):
        return ToDoServices()

    @pytest.fixture(scope="class")
    def todo_model_test(self, todo_item):
        return ToDoModel(**todo_item)

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