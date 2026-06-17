from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import sqlite3

app = FastAPI()

app.mount("/static", StaticFiles(directory="client"), name="static")

@app.get("/query")
async def query(text: str):
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    text = text.replace(" ", "").replace("-", "").replace("'", "").replace(".", "").lower()
    cur.execute(f"SELECT name, lat, lon FROM data WHERE name_norm LIKE '%//{text}//%'")

    results = cur.fetchall()
    con.close()
    if not results:
        return None
    return {"results": results}