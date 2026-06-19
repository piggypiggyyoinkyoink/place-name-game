from fastapi import FastAPI, Cookie
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated 
import sqlite3
import uuid
import json
import os

if not os.path.exists("gamedata"):
    os.makedirs("gamedata")

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

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/init")
def init(uid_json: Annotated[str | None, Cookie()] = None, type: str | None = "uk"):
    cookie = json.loads(uid_json) if uid_json else {}
    uid = cookie.get(f"uid-{type}") if cookie else None
    print(cookie)
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
    cookie[f"uid-{type}"] = uid
    cookie_str = json.dumps(cookie)
    response.set_cookie(key="uid_json", value=cookie_str, httponly=False, samesite="lax", secure=False, max_age=99999999999)
    return response


@app.get("/query")
def query(text: str, type: str, uid_json: Annotated[str | None, Cookie()] = None):
    with open("typemap.json", "r") as f:
        typemap = json.load(f)
    typedata = typemap.get(type, [])
    valid_counties = typedata.get("valid-counties", [])
    if len(valid_counties) == 1:
        valid_counties.append("Penis") # fucking sqlite hates single elements in IN statements so need to add garbage
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    text = text.replace(" ", "").replace("-", "").replace("'", "").replace(".", "").lower()
    cur.execute(f"SELECT name, lat, lon, county FROM data WHERE name_norm LIKE '%//{text}//%' AND county IN {tuple(valid_counties)}")

    results = cur.fetchall()
    con.close()
    response = {"results": [], "already_guessed": False}
    if uid_json is None:
        return JSONResponse(content={"error": "No UID cookie"}, status_code=400)
    cookie = json.loads(uid_json)
    uid = cookie.get(f"uid-{type}")
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
def get_total(type : str):
    with open("typemap.json", "r") as f:
        typemap = json.load(f)
    typedata = typemap.get(type, [])
    valid_counties = typedata.get("valid-counties", [])
    print("Valid counties:", valid_counties)
    if len(valid_counties) == 1:
        valid_counties.append("Penis") # fucking sqlite hates single elements in IN statements so need to add garbage
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    total = cur.execute(f"SELECT COUNT(*) FROM data WHERE county IN {tuple(valid_counties)}").fetchone()[0]
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

@app.get("/typemap")
def get_typemap():
    with open("typemap.json", "r") as f:
        typemap = json.load(f)
    return typemap

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