from typing import List, Dict, Any, Optional, Union
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
        # Attempt to parse the todo_data dictionary into an instance of the ToDoModel class
        todo_model = parse_obj_as(ToDoModel, todo_data)

        # Call a function to add the todo_model instance to the database or perform other actions
        result = todo_services.add_todo(todo_model)

        # Convert the value associated with the key "oid" in the result dictionary to a string
        result["oid"] = str(result["oid"])

        # Check if the result is a dictionary and if it contains a key "error" with a non-None value
        if isinstance(result, dict) and result.get("error") is not None:
            # If an error is detected, raise an HTTPException with a status code of 400 and the error detail
            raise HTTPException(status_code=400, detail=result.get("error"))

        # If no errors occur during processing, return the result dictionary
        return result

    # Catch any ValidationError exceptions that occur during parsing or processing
    except ValidationError as e:
        # Initialize an empty list to store individual error messages
        error_messages = []

        # Iterate over the list of validation errors contained in the ValidationError object
        for error in e.errors():
            # Construct a string for each error message and append it to the error_messages list
            error_messages.append(f"{error['loc'][0]}: {error['msg']}")

        # Join all error messages into a single string separated by newline characters
        error_detail = "\n".join(error_messages)

        # Raise an HTTPException with a status code of 400 and the concatenated error detail
        raise HTTPException(status_code=400, detail=error_detail)


@router.get("/", response_model=Union[List[ToDoModel], Dict[str, Any]])
async def get_todo_route() -> Union[List[ToDoModel], Dict[str, Any]]:
    try:
        results = todo_services.get_all_todos()
        if isinstance(results, list) and any(isinstance(result, dict) and result.get("error") for result in results):
            error_messages = ", ".join(result["error"] for result in results if result.get("error"))
            raise HTTPException(status_code=400, detail=error_messages)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{input_data}", response_model=Dict[str, Any])
async def update_todo_route(input_data: int, body_data: dict) -> Dict[str, Any]:
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


@router.delete("/", response_model=Dict[str, Any])
async def delete_todo_route() -> Dict[str, Any]:
    try:
        result = todo_services.delete_all_todos()
        if isinstance(result, dict) and result.get("error") is not None:
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
