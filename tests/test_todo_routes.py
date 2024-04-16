import pytest
import json
from fastapi.testclient import TestClient
from fastapi import HTTPException
from starlette import status

from routes.todo_routes import router, todo_services
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

    def test_get_todo_all_good(self, todo_list_routes, todo_list_good):
        todo_list_routes.delete("/")
        todo_list_routes.post("/", json=todo_list_good)
        response = todo_list_routes.get("/")
        print(f"\n\033[95mRouter: \033[92mGet all todo success: \033[96m{response.json()}\033[0m\n")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert any(item == todo_list_good for item in response.json())
        todo_list_routes.delete("/")

    def test_get_todo_all_bad(self, todo_list_routes, todo_list_good):
        todo_list_routes.delete("/")
        todo_list_routes.post("/", json=todo_list_good)
        response = todo_list_routes.get("/non_existent_route")

        assert response.status_code == 405
        assert "Method Not Allowed" in response.text
        todo_list_routes.delete("/")

    def test_update_todo_route_by_id_good(self, todo_list_routes, todo_list_good, todo_list_update):
        todo_list_routes.delete("/")
        todo_list_routes.post("/", json=todo_list_good)
        response = todo_list_routes.put(f"/{todo_list_good.get('id')}", json=todo_list_update)

        print(f"\n\033[95mRouter: \033[92mUpdate todo success: \033[96m{response.json()}\033[0m\n")
        assert response.status_code == 200
        assert response.json() == {"result": f"Documents updated: 1"}

    def test_update_todo_route_by_id_bad(self, todo_list_routes, todo_list_bad, todo_list_update):
        todo_list_routes.delete("/")
        with pytest.raises(HTTPException) as exc_info:
            todo_list_routes.post("/", json=todo_list_bad)

        assert exc_info.value.status_code == 400
        assert "id: Input should be a valid integer" in exc_info.value.detail
        todo_list_routes.delete("/")

    def test_delete_todo_route_by_id_good(self, todo_list_routes, todo_list_good):
        todo_list_routes.delete("/")
        todo_list_routes.post("/", json=todo_list_good)

        # Pass a valid integer ID for input_data
        response = todo_list_routes.delete(f"/{todo_list_good.get('id')}")
        assert response.status_code == 200
        assert response.json().get("message") == f"Todo with ID {todo_list_good.get('id')} deleted successfully."
        todo_list_routes.delete("/")

    def test_delete_todo_route_by_id_bad(self, todo_list_routes, todo_list_good):
        todo_list_routes.delete("/")
        todo_list_routes.post("/", json=todo_list_good)

        existing_todo_ids = [todo.id for todo in todo_services.get_all_todos()]

        non_existing_id = max(existing_todo_ids, default=0) + 1

        with pytest.raises(HTTPException) as exc_info:
            todo_list_routes.delete(f"/{non_existing_id}")

        exception = exc_info.value
        assert exception.status_code == 404
        assert exception.detail == f"Todo with ID {non_existing_id} not found."

        todo_list_routes.delete("/")

    def test_delete_todo_all_good(self, todo_list_routes, todo_list_good):
        todo_list_routes.delete("/")
        todo_list_routes.post("/", json=todo_list_good)
        response = todo_list_routes.delete("/")
        assert response.status_code == 200
        assert response.json().get("error") is None
        assert response.json().get("result") == 'Document deleted: 1'

    def test_delete_todo_all_bad(self, todo_list_routes, todo_list_good):
        todo_list_routes.delete("/")
        todo_list_routes.post("/", json=todo_list_good)
        with pytest.raises(HTTPException) as exc_info:
            todo_list_routes.delete("/non_existent_route")
            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Document not found."
        todo_list_routes.delete("/")
