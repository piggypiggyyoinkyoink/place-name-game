from fastapi import FastAPI, Cookie, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from typing import Annotated 
import sqlite3
import uuid
import json
import os
import datetime
import websockets

if not os.path.exists("gamedata"):
    os.makedirs("gamedata")

app = FastAPI(root_path="/placenamegame")

origins = [
    "http://localhost:8000",
    "http://localhost:80",
    "http://127.0.0.1:80",
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
templates = Jinja2Templates(directory="templates")

@app.get("/init")
def init(uid_json: Annotated[str | None, Cookie()] = None, type: str | None = "uk"):
    cookie = json.loads(uid_json) if uid_json else {}
    uid = cookie.get(f"uid-{type}") if cookie else None
    print(cookie)
    print("UID:", uid)
    print("Type:", type)
    with open("typemap.json", "r") as f:
        typemap = json.load(f)
    if type not in typemap:
        return JSONResponse(content={"error": "Invalid type"}, status_code=400)
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
    if not typedata:
        return JSONResponse(content={"error": "Invalid type"}, status_code=400)
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
    if not typedata:
        return JSONResponse(content={"error": "Invalid type"}, status_code=400)
    valid_counties = typedata.get("valid-counties", [])
    print("Valid counties:", valid_counties)
    if len(valid_counties) == 1:
        valid_counties.append("Penis") # fucking sqlite hates single elements in IN statements so need to add garbage
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    total = cur.execute(f"SELECT COUNT(*) FROM data WHERE county IN {tuple(valid_counties)}").fetchone()[0]
    con.close()
    return {"total": total}

@app.get("/setname")
def set_name(type: str, uid_json: Annotated[str | None, Cookie()] = None, name: str | None = "Anonymous"):
    if uid_json is None:
        return JSONResponse(content={"error": "No UID cookie"}, status_code=400)
    cookie = json.loads(uid_json)
    uid = cookie.get(f"uid-{type}")
    with open(f"gamedata/{uid}.json", "r") as f:
        content = json.load(f)
    content["name"] = name
    with open(f"gamedata/{uid}.json", "w") as f:
        json.dump(content, f)
    return JSONResponse(content={"message": "Name updated successfully", "name": name})

@app.get("/finish")
def finish(type: str,uid_json: Annotated[str | None, Cookie()] = None, name: str | None = "Anonymous"):
    if uid_json is None:
        return JSONResponse(content={"error": "No UID cookie"}, status_code=400)
    with open("typemap.json", "r") as f:
        typemap = json.load(f)
    typedata = typemap.get(type, [])
    if not typedata:
        return JSONResponse(content={"error": "Invalid type"}, status_code=400)
    cookie = json.loads(uid_json)
    uid = cookie.get(f"uid-{type}")
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(f"gamedata/{uid}.json", "r") as f:
        content = json.load(f)
    content["finished"] = True
    content["name"] = name
    content["date"] = date
    high_scores = typedata.get("high-scores", [])
    if len(high_scores) < 10 or content["count"] > min(score["count"] for score in high_scores):
        high_scores.append({"uid": uid, "name": name, "count": content["count"], "date": date})
        high_scores.sort(key=lambda x: x["count"], reverse=True)
        high_scores = high_scores[:10]
        typedata["high-scores"] = high_scores
        typemap[type] = typedata
        with open("typemap.json", "w") as f:
            json.dump(typemap, f, indent=2)
    with open(f"gamedata/{uid}.json", "w") as f:
        json.dump(content, f)
    cookie.pop(f"uid-{type}", None)
    cookie_str = json.dumps(cookie)
    response = JSONResponse(content=content)
    response.set_cookie(key="uid_json", value=cookie_str, httponly=False, samesite="lax", secure=False, max_age=99999999999)
    return response

@app.get("/reset")
def reset(type: str, uid_json: Annotated[str | None, Cookie()] = None):
    if uid_json is None:
        return JSONResponse(content={"error": "No UID cookie"}, status_code=400)
    cookie = json.loads(uid_json)
    uid = cookie.get(f"uid-{type}")
    with open(f"gamedata/{uid}.json", "r") as f:
        content = json.load(f)
    content["guesses"] = []
    content["count"] = 0
    content["finished"] = False
    with open(f"gamedata/{uid}.json", "w") as f:
        json.dump(content, f)
    response = JSONResponse(content=content)
    return response

@app.get("/check-game-exists")
def check_game_exists(type: str, uid_json: Annotated[str | None, Cookie()] = None):
    if uid_json is None:
        return JSONResponse(content={"error": "No UID cookie"}, status_code=400)
    cookie = json.loads(uid_json)
    uid = cookie.get(f"uid-{type}")
    try:
        with open(f"gamedata/{uid}.json", "r") as f:
            content = json.load(f)
            if content.get("finished") == False and content.get("type") == type:
                return JSONResponse(content={"exists": True})
    except FileNotFoundError:
        pass
    return JSONResponse(content={"exists": False})

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
def get_typemap(howmany: str | None = None):
    with open("typemap.json", "r") as f:
        typemap = json.load(f)
    if howmany:
        for type in typemap:
            count = get_total(type)["total"]
            typemap[type]["total"] = count
    return typemap

@app.get("/results")
def get_results(request: Request, uid: str):
    # try:
    with open(f"gamedata/{uid}.json", "r") as f:
        content = json.load(f)
    if content.get("finished") == False:
        return JSONResponse(content={"error": "Invalid uid"}, status_code=400)
    name = content.get("name", "Anonymous")
    count = content.get("count", 0)
    if count != 1:
        count = f"{count} places"
    else:
        count = f"{count} place"
    date = content.get("date", "Unknown")
    type = content.get("type")
    typemap = get_typemap()
    typedata = typemap.get(type, {})
    type_name = typedata.get("name", "Unknown")
    return templates.TemplateResponse("results.html", {"request": request, "name": name, "count": count, "date": date, "type": type_name, "uid": uid})
    
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/game")
def game(request: Request, type: str):
    with open("typemap.json", "r") as f:
        typemap = json.load(f)
    typedata = typemap.get(type, {})
    try:
        type_name = typedata.get("name")
        if type_name[:3] == "the":
            type_name_2 = type_name[4:]
        else:
            type_name_2 = type_name
    except KeyError:
        return JSONResponse(content={"error": "Invalid type"}, status_code=400)
    return templates.TemplateResponse("index.html", {"request": request, "type": type_name, "type2": type_name_2})

@app.get("/test")
def test():
    return {"message": "Test endpoint is working!"}

