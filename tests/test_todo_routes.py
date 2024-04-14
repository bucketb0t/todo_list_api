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
    def todo_list_good(self, request):
        last_id = getattr(request.cls, "last_id", 0)
        new_id = last_id + 1
        request.cls.last_id = new_id
        return {
            "id": new_id,
            "title": "PytestFixtureGood",
            "description": "InstanceGood",
            "completed": True
        }

    @pytest.fixture(scope="class")
    def todo_list_bad(self):
        return {
            "id": None,
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
        todo_list_routes.delete("/")
        response = todo_list_routes.post("/", json=todo_list_good)
        print(f"\n\033[95mRouter: \033[92mCreate todo success: \033[96m{response.json()}\033[0m\n")
        assert response.status_code == 200
        assert response.json().get("oid") is not None
        todo_list_routes.delete("/")

    def test_create_todo_bad(self, todo_list_routes, todo_list_bad):
        todo_list_routes.delete("/")

        with pytest.raises(HTTPException) as exc_info:
            response = todo_list_routes.post("/", json=todo_list_bad)
            assert exc_info.value.status_code == 400
            assert response.json().get("error") is not None
        todo_list_routes.delete("/")

    def test_get_todo(self, todo_list_routes, todo_list_good):
        todo_list_routes.delete("/")
        todo_list_routes.post("/", json=todo_list_good)
        response = todo_list_routes.get("/")
        print(f"\n\033[95mRouter: \033[92mGet all todo success: \033[96m{response.json()}\033[0m\n")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert any(item == todo_list_good for item in response.json())
        todo_list_routes.delete("/")

    def test_get_todo_bad(self, todo_list_routes, todo_list_good):
        # Clean up any existing todos
        todo_list_routes.delete("/")
        todo_list_routes.post("/", json=todo_list_good)
        response = todo_list_routes.get("/non_existent_route")
        assert response.status_code == 404
        todo_list_routes.delete("/")