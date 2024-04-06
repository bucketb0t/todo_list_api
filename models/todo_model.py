from pydantic import BaseModel


class ToDoModel(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
