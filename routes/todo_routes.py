from typing import List, Dict, Any, Union
from fastapi import APIRouter, HTTPException
from pydantic import ValidationError, parse_obj_as

from models.todo_model import ToDoModel
from services.todo_services import ToDoServices

router = APIRouter()
todo_services = ToDoServices()


@router.post("/", response_model=Dict[str, Any])
async def create_todo_route(todo_data: dict) -> Dict[str, Any]:
    """
    Define a route handler for handling HTTP POST requests at the root URL ("/") with a response model of Dict[str, Any].

    Parameters:
    - todo_data (dict): The data representing the todo item to be created.

    Returns:
    - dict: The result of the todo creation operation.

    Raises:
    - HTTPException: If an error occurs during parsing or processing, an HTTPException with status code 400 and the error detail will be raised.
    """
    try:
        todo_model = parse_obj_as(ToDoModel, todo_data)
        result = todo_services.add_todo(todo_model)
        result["oid"] = str(result["oid"])
        if isinstance(result, dict) and result.get("error") is not None:
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result
    except ValidationError as e:
        error_messages = []
        for error in e.errors():
            error_messages.append(f"{error['loc'][0]}: {error['msg']}")
        error_detail = "\n".join(error_messages)
        raise HTTPException(status_code=400, detail=error_detail)


@router.get("/{id}", response_model=Dict[str, Any])
async def get_todo_route_by_id(id: int) -> Dict[str, Any]:
    try:
        index_to_get = None
        for i, todo in enumerate(todo_services.get_all_todos()):
            if todo.id == id:
                index_to_get = i
                break
        if index_to_get is None:
            raise HTTPException(status_code=404, detail=f"Todo with ID {id} not found.")

        retrieved_todo = todo_services.get_todo_by_id(id)

    except ValueError:
        raise HTTPException(status_code=400, detail="Error! 'id' parameter is not an integer value instance")

    return {"message": f"Todo with ID {id} retrieved successfully.", "update_todo": retrieved_todo}


@router.get("/", response_model=Union[List[ToDoModel], Dict[str, Any]])
async def get_todo_route_all() -> Union[List[ToDoModel], Dict[str, Any]]:
    try:
        results = todo_services.get_all_todos()
        if not results:
            raise HTTPException(status_code=404, detail="No todos found")
        if any(isinstance(result, dict) and result.get("error") for result in results):
            error_messages = ", ".join(result.get("error") for result in results)
            raise HTTPException(status_code=400, detail=error_messages)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{input_data}", response_model=Dict[str, Any])
async def update_todo_route_by_id(input_data: int, body_data: dict) -> Dict[str, Any]:
    try:
        if "id" in body_data and not isinstance(body_data.get("id"), int):
            raise HTTPException(status_code=400, detail="Error! 'id' parameter is not a integer value instance")
        if "title" in body_data and not isinstance(body_data.get("title"), str):
            raise HTTPException(status_code=400, detail="Error! 'title' parameter is not a string value instance")
        if "description" in body_data and not isinstance(body_data.get("description"), str):
            raise HTTPException(status_code=400, detail="Error! 'description' parameter is not a string value instance")
        if "completed" in body_data and not isinstance(body_data.get("completed"), bool):
            raise HTTPException(status_code=400, detail="Error! 'completed' parameter is not a boolean value instance")

        result = todo_services.update_todo_by_id(input_data, body_data)
        if isinstance(result, dict) and result.get("error") is not None:
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{input_data}", response_model=Dict[str, Any])
async def delete_todo_route_by_id(input_data: Union[int, str]) -> Dict[str, Any]:
    try:
        input_id = int(input_data)  # Ensure the ID is an integer
    except ValueError:
        raise HTTPException(status_code=400, detail="Error! 'id' parameter is not an integer value instance")

    todos = todo_services.get_all_todos()

    # Find the index of the todo item with the provided ID
    index_to_delete = None
    for i, todo in enumerate(todos):
        if todo.id == input_id:
            index_to_delete = i
            break

    if index_to_delete is None:
        raise HTTPException(status_code=404, detail=f"Todo with ID {input_id} not found.")

    # Delete the todo item
    deleted_todo = todos.pop(index_to_delete)

    return {"message": f"Todo with ID {input_id} deleted successfully.", "deleted_todo": deleted_todo}


@router.delete("/", response_model=Dict[str, Any])
async def delete_todo_route_all() -> Dict[str, Any]:
    try:
        result = todo_services.delete_all_todos()
        if isinstance(result, dict) and result.get("error") is not None:
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
