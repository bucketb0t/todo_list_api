from typing import List, Dict, Any, Optional, Union
from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from models.todo_model import ToDoModel
from services.todo_services import ToDoServices

router = APIRouter()
todo_services = ToDoServices()


@router.post("/", response_model=Dict[str, Any])
async def create_todo_route(todo_data: dict) -> Dict[str, Any]:
    try:
        result = todo_services.add_todo(ToDoModel(**todo_data))
        result["oid"] = str(result["oid"])
        if isinstance(result, dict) and result.get("error") is not None:
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
