from utils.db_store import ToDoDBStore
from models.todo_model import ToDoModel


class ToDoServices:
    def __init__(self):
        self.db = ToDoDBStore()

    def add_todo(self, todo_model: ToDoModel):
        try:
            todo = self.db.add_document("todo_list_db", "todo_list_collection", todo_model.dict())
            print(f"ToDo successfully added: {todo.inserted_id}")
            return {"oid": todo.inserted_id}
        except Exception as e:
            return {"error": str(e)}

    def get_todo_by_id(self, todo_id: int):
        try:
            todo = self.db.get_document_by_id("todo_list_db", "todo_list_collection", todo_id)
            if todo is None:
                raise ValueError(f"Document with id {todo_id} not found.")
            return todo
        except Exception as e:
            return {"error": str(e)}

    def get_todo_by_query(self, todo_query: dict):
        try:
            todos = self.db.get_document_by_query("todo_list_db", "todo_list_collection", todo_query)
            result = []
            for todo in todos:
                result.append(ToDoModel(**todo))
            print(f"All Todos successfully retrieved: {result}")
            return result
        except Exception as e:
            return {"error": str(e)}

    def get_all_todos(self):
        try:
            todos = self.db.get_all_documents("todo_list_db", "todo_list_collection")
            results = []
            for todo in todos:
                results.append(ToDoModel(**todo))
            print(f"All Todos successfully retrieved: {todos}")
            return results
        except Exception as e:
            return {"error": str(e)}

    def update_todo_by_id(self, todo_id: int, todo_dict: dict):
        try:
            todo = self.db.update_document_by_id("todo_list_db", "todo_list_collection", todo_id, todo_dict)
            return {"result": f"Documents updated: {todo.modified_count}"}
        except Exception as e:
            return {"error": str(e)}

    def delete_todo_by_id(self, todo_id: int):
        try:
            todo = self.db.delete_document_by_id("todo_list_db", "todo_list_collection", todo_id)
            return {"result": f"Documents deleted: {todo.deleted_count}"}
        except Exception as e:
            return {"error": f"{e}"}

    def delete_all_todos(self):
        try:
            todos = self.db.delete_all_documents("todo_list_db", "todo_list_collection", {})
            return {"result": f"Document deleted: {todos.deleted_count}"}
        except Exception as e:
            return {"error": f"{e}"}
