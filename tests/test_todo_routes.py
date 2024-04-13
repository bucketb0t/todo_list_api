import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException

from routes.todo_routes import router
from utils.db_store import ToDoDBStore


class TestToDoListRoutes:
    @pytest.fixture(scope="class")
    def todo_list_routes(self):
        return TestClient(router)

    @pytest.fixture(scope="class")
    def todo_list_db(self):
        return ToDoDBStore()

    @pytest.fixture(scope="class")
    def todo_list_good(self):
        return {
            "id": 0,
            "title": "PytestFixtureGood",
            "description": "InstanceGood",
            "completed": True
        }

    @pytest.fixture(scope="class")
    def todo_list_bad(self):
        return {
            "id": "0",
            "title": "PytestFixtureBad",
            "description": "InstanceBad",
            "completed": False,
            "bad": True
        }

    @pytest.fixture(scope="class")
    def todo_list_update(self):
        return {
            "title": "PytestFixtureUpdate",
            "description": "InstanceUpdate",
            "completed": True
        }

    def test_create_todo_good(self, todo_list_routes, todo_list_good):
        todo_list_routes.request("DELETE", "/", json=todo_list_good)
        response = todo_list_routes.post("/", json=todo_list_good)
        print(f"\n\033[95mRouter: \033[92mCreate todo success: \033[96m{response.json()}\033[0m\n")
        assert response.status_code == 200
        assert response.json().get("oid") is not None
        todo_list_routes.delete(f"/{response.json().get('oid')}")
