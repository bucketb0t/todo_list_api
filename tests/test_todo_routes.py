import pytest

from fastapi.testclient import TestClient
from fastapi import HTTPException

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

    def test_get_todo_by_id_good(self, todo_list_routes, todo_list_good):
        todo_list_routes.delete("/")
        todo_list_routes.post("/", json=todo_list_good)
        response = todo_list_routes.get("/", params={"id": todo_list_good.get("id")})
        print(f"\n\033[95mRouter: \033[92mGet all todo_by_id success: \033[96m{response.json()}\033[0m\n")

        assert response.status_code == 200
        for key, value in todo_list_good.items():
            assert response.json()[todo_list_good.get("id") - 1].get(key) == value

        todo_list_routes.delete("/")

    def test_get_todo_by_id_bad(self, todo_list_routes, todo_list_good):
        todo_list_routes.delete("/")
        todo_list_routes.post("/", json=todo_list_good)

        bad_id = 999

        with pytest.raises(HTTPException) as exc_info:
            todo_list_routes.get(f"/{bad_id}", params={"id": bad_id})

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == f"Todo with ID {bad_id} not found."

    def test_get_todo_by_query_good(self, todo_list_routes, todo_list_good):
        todo_list_routes.delete("/")
        todo_list_routes.post("/", json=todo_list_good)

        query_params = {"completed": True}
        response = todo_list_routes.get("/", params=query_params)
        print(f"\n\033[95mRouter: \033[92mGet all todo_by_query success: \033[96m{response.json()}\033[0m\n")

        assert response.status_code == 200
        assert len(response.json()) > 0

    def test_get_todo_by_query_bad(self, todo_list_routes, todo_list_good):
        todo_list_routes.delete("/")
        todo_list_routes.post("/", json=todo_list_good)

        # Test for a query that doesn't match any todos
        query_bad = {"bad": True}
        response = todo_list_routes.get("/query", params=query_bad)

        try:
            assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
            response_json = response.json()
            assert "message" in response_json
            assert "retrieved_todo" in response_json
            assert len(response_json["retrieved_todo"]) == 0
        except AssertionError as e:
            raise AssertionError(f"Test failed: {e}")

    def test_get_todo_all_good(self, todo_list_routes, todo_list_good):
        todo_list_routes.delete("/")
        todo_list_routes.post("/", json=todo_list_good)
        response = todo_list_routes.get("/")
        print(f"\n\033[95mRouter: \033[92mGet all todo success: \033[96m{response.json()}\033[0m\n")

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert any(item == todo_list_good for item in response.json())
        todo_list_routes.delete("/")

    def test_get_todo_all_bad(self, todo_list_routes, monkeypatch):
        # Mocking the todo_services.get_all_todos method to raise an exception
        def mock_get_all_todos():
            raise Exception("Database connection error occurred")

        monkeypatch.setattr(todo_services, "get_all_todos", mock_get_all_todos)

        with pytest.raises(HTTPException) as exc_info:
            todo_list_routes.get("/")

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Database connection error occurred"

    def test_update_todo_by_id_good(self, todo_list_routes, todo_list_good, todo_list_update):
        todo_list_routes.delete("/")
        todo_list_routes.post("/", json=todo_list_good)
        response = todo_list_routes.put(f"/{todo_list_good.get('id')}", json=todo_list_update)

        print(f"\n\033[95mRouter: \033[92mUpdate todo success: \033[96m{response.json()}\033[0m\n")
        assert response.status_code == 200
        assert response.json() == {"result": f"Documents updated: 1"}

    def test_update_todo_by_id_bad(self, todo_list_routes, todo_list_bad, todo_list_update):
        todo_list_routes.delete("/")
        with pytest.raises(HTTPException) as exc_info:
            todo_list_routes.post("/", json=todo_list_bad)

        assert exc_info.value.status_code == 400
        assert "id: Input should be a valid integer" in exc_info.value.detail
        todo_list_routes.delete("/")

    def test_delete_todo_by_id_good(self, todo_list_routes, todo_list_good):
        todo_list_routes.delete("/")
        todo_list_routes.post("/", json=todo_list_good)
        response = todo_list_routes.delete(f"/{todo_list_good.get('id')}")

        print(f"\n\033[95mRouter: \033[92mDelete todo_by_id success: \033[96m{response.json()}\033[0m\n")
        assert response.status_code == 200
        assert response.json().get("message") == f"Todo with ID {todo_list_good.get('id')} deleted successfully."
        todo_list_routes.delete("/")

    def test_delete_todo_by_id_bad(self, todo_list_routes, todo_list_good):
        todo_list_routes.delete("/")
        todo_list_routes.post("/", json=todo_list_good)

        existing_todo_ids = [todo.get("id") for todo in todo_list_routes.get("/").json()]

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

        print(f"\n\033[95mRouter: \033[92mDelete todos success: \033[96m{response.json()}\033[0m\n")
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
