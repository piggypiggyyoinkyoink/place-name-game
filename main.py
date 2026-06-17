from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI()

origins = [
    "http://localhost:*",
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="client"), name="static")

@app.get("/query")
async def query(text: str):
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    text = text.replace(" ", "").replace("-", "").replace("'", "").replace(".", "").lower()
    cur.execute(f"SELECT name, lat, lon FROM data WHERE name_norm LIKE '%//{text}//%'")

    results = cur.fetchall()
    con.close()
    response = {"results": []}
    for result in results:
        res_json = {"name": result[0], "lat": result[1], "lon": result[2]}
        response["results"].append(res_json)
    return response