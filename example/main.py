# ABOUTME: Minimal FastAPI example app for testing ApiLens locally.
# ABOUTME: Run `apilens generate spec.json` or `apilens serve` from the example/ directory.

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Example API", version="1.0.0")


class Item(BaseModel):
    id: int
    name: str
    price: float


class CreateItemRequest(BaseModel):
    name: str
    price: float


@app.get("/items", response_model=list[Item])
def list_items():
    return []


@app.post("/items", response_model=Item, status_code=201)
def create_item(body: CreateItemRequest):
    return Item(id=1, **body.model_dump())


@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    return Item(id=item_id, name="Example", price=9.99)


@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    pass
