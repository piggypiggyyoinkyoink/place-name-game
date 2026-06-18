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
def init(uid: Annotated[str | None, Cookie()] = None, type: str | None = None):
    print("UID:", uid)
    print("Type:", type)
    if uid is not None:
        try:
            with open(f"gamedata/{uid}.json", "r") as f:
                content = json.load(f)
                if content.get("finished") == False and content.get("type") == type:
                    response = JSONResponse(content=content)
                    return response
        except FileNotFoundError:
            print("File not found")
    
    uid = str(uuid.uuid4())
    init_content = {"uid": uid, "guesses":[], "count": 0, "name": "Anonymous", "date": "Unknown", "finished": False, "type": type}
    with open(f"gamedata/{uid}.json", "w") as f:
        json.dump(init_content, f)
    response = JSONResponse(content=init_content)
    response.set_cookie(key="uid", value=uid, httponly=False, samesite="lax", secure=False)
    return response


@app.get("/query")
def query(text: str, type: str, uid: Annotated[str | None, Cookie()] = None):
    with open("typemap.json", "r") as f:
        typemap = json.load(f)
    valid_counties = typemap.get(type, [])
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    text = text.replace(" ", "").replace("-", "").replace("'", "").replace(".", "").lower()
    cur.execute(f"SELECT name, lat, lon, county FROM data WHERE name_norm LIKE '%//{text}//%' AND county IN {tuple(valid_counties)}")

    results = cur.fetchall()
    con.close()
    response = {"results": [], "already_guessed": False}
    with open(f"gamedata/{uid}.json", "r") as f:
        content = json.load(f)
    for result in results:
        res_json = {"name": result[0], "lat": result[1], "lon": result[2], "county": result[3]}
        if res_json not in content["guesses"]:
            content["guesses"].append(res_json)
            content["count"] += 1
            response["results"].append(res_json)
        else:
            response["already_guessed"] = True
    with open(f"gamedata/{uid}.json", "w") as f:
        json.dump(content, f)
    return response

@app.get("/howmany")
def get_total():
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    total = cur.execute("SELECT COUNT(*) FROM data").fetchone()[0]
    con.close()
    return {"total": total}

@app.get("/data/{uid}")
def get_data(uid: str):
    try:
        with open(f"gamedata/{uid}.json", "r") as f:
            content = json.load(f)
            response = JSONResponse(content=content)
            return response
    except:
        return JSONResponse(content={"error": "Data not found"}, status_code=404)

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