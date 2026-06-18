from fastapi import FastAPI, Cookie
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated 
import sqlite3
import uuid
import json

app = FastAPI()

origins = [
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


@app.get("/init")
def init(uid: Annotated[str | None, Cookie()] = None):
    
    if uid is not None:
        try:
            with open(f"gamedata/{uid}.json", "r") as f:
                content = json.load(f)
                response = JSONResponse(content=content)
                return response
        except FileNotFoundError:pass
    
    uid = str(uuid.uuid4())
    init_content = {"uid": uid, "guesses":[]}
    with open(f"gamedata/{uid}.json", "w") as f:
        json.dump(init_content, f)
    response = JSONResponse(content=init_content)
    response.set_cookie(key="uid", value=uid, httponly=False, samesite="lax", secure=False)
    return response


@app.get("/query")
def query(text: str, uid: Annotated[str | None, Cookie()] = None):
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    text = text.replace(" ", "").replace("-", "").replace("'", "").replace(".", "").lower()
    cur.execute(f"SELECT name, lat, lon, county FROM data WHERE name_norm LIKE '%//{text}//%'")

    results = cur.fetchall()
    con.close()
    response = {"results": []}
    with open(f"gamedata/{uid}.json", "r") as f:
        content = json.load(f)
    for result in results:
        res_json = {"name": result[0], "lat": result[1], "lon": result[2], "county": result[3]}
        if res_json not in content["guesses"]:
            content["guesses"].append(res_json)
            response["results"].append(res_json)
    with open(f"gamedata/{uid}.json", "w") as f:
        json.dump(content, f)
    return response

@app.get("/all")
def all():
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute(f"SELECT name, lat, lon, county FROM data")

    results = cur.fetchall()
    con.close()
    response = {"results": []}
    for result in results:
        res_json = {"name": result[0], "lat": result[1], "lon": result[2], "county": result[3]}
        response["results"].append(res_json)
    return response