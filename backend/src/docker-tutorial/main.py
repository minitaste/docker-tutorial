import redis
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

client = redis.StrictRedis(host='redis', port=6379, db=0)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)


class TodoItem(BaseModel):
    id: int
    content: str


class TodoItemCreate(BaseModel):
    content: str

todos: list[TodoItem] = []
id_counter = 1

def get_all_todos():
    todos = []
    for key in client.keys("todo:*"):
        todo = json.loads(client.get(key))
        todos.append(todo)
    return todos

@app.post("/todos", response_model=TodoItem)
async def create_todo(item: TodoItemCreate):
    new_id = client.incr("todo_id")
    new_todo = TodoItem(id=new_id, content=item.content)

    client.set(f"todo:{new_id}", json.dumps(new_todo.dict(), default=str))
    return new_todo

@app.get("/todos", response_model=list[TodoItem])
async def read_todos():
    todos = get_all_todos()
    return todos

@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    todo_key = f"todo:{todo_id}"
    if client.exists(todo_key):
        client.delete(todo_key)        
        return {"message": f"Delete todo {todo_id} successfully."}
    raise HTTPException(status_code=404, detail="Todo not found.")

