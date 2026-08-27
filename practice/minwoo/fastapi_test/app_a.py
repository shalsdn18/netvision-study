from fastapi import FastAPI

app = FastAPI()

items = {1: "사과", 2: "바나나"}


@app.get("/items/{item_id}")
def get_item(item_id: int):
    return {"item_id": str(item_id), "value": items.get(item_id)}
