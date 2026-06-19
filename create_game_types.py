import json, os

UK_COUNTIES=["Greater London","Suffolk","Essex","Wiltshire","East Sussex","Staffordshire","Cambridgeshire", "Somerset", "Pembrokeshire", "Cheshire", "Lincolnshire", "Surrey", "Hampshire", "West Sussex", "Hertfordshire", "West Yorkshire", "West Midlands", "Norfolk", "Cumbria", "Isle of Wight", "Cornwall", "Devon", "Oxfordshire", "Berkshire", "Buckinghamshire", "Gloucestershire", "Bedfordshire", "Monmouthshire", "Ceredigion", "Dorset", "Leicestershire", "South Lanarkshire", "Highland", "Warwickshire", "Northamptonshire", "Glasgow City", "Worcestershire", "Northumberland", "Kent", "North Yorkshire", "East Riding of Yorkshire", "Tyne and Wear", "Herefordshire", "Midlothian", "East Lothian", "South Yorkshire", "Rutland", "Flintshire", "City of Edinburgh", "Derbyshire", "East Dunbartonshire","Stirling","Carmarthenshire","Durham","Dumfries and Galloway","Gwynedd","Wrexham","South Ayrshire","Aberdeenshire","Swansea","Shropshire","Anglesey","Perth and Kinross","Dundee City","Merseyside","Lancashire","Angus","Fife","Moray","Nottinghamshire","Greater Manchester","Scottish Borders","Fermanagh","West Dunbartonshire","Renfrewshire","North Ayrshire","Argyll and Bute","Clackmannanshire","West Lothian","Falkirk","Newport","East Ayrshire","Inverclyde","Torfaen","Blaenau Gwent","Caerphilly","Rhondda Cynon Taf","Vale of Glamorgan","Bridgend","Neath Port Talbot","Powys","Denbighshire","Conwy","East Renfrewshire","Western Isles","North Lanarkshire","Orkney","Merthyr Tydfil","Down","Antrim","Londonderry","Shetland Islands","Tyrone","Armagh","Cardiff","Bristol"]
ENGLAND_COUNTIES = ["Greater London","Suffolk","Essex","Wiltshire","East Sussex","Staffordshire","Cambridgeshire", "Somerset", "Cheshire", "Lincolnshire", "Surrey", "Hampshire", "West Sussex", "Hertfordshire", "West Yorkshire", "West Midlands", "Norfolk", "Cumbria", "Isle of Wight", "Cornwall", "Devon", "Oxfordshire", "Berkshire", "Buckinghamshire", "Gloucestershire", "Bedfordshire", "Monmouthshire", "Ceredigion", "Dorset", "Leicestershire", "South Lanarkshire", "Highland", "Warwickshire", "Northamptonshire", "Glasgow City", "Worcestershire", "Northumberland", "Kent", "North Yorkshire", "East Riding of Yorkshire", "Tyne and Wear", "Herefordshire", "South Yorkshire", "Rutland", "Derbyshire", "Durham", "Shropshire", "Merseyside", "Lancashire", "Nottinghamshire", "Greater Manchester", "Bristol"]
WALES_COUNTIES = ["Pembrokeshire", "Monmouthshire", "Ceredigion", "Gwynedd", "Swansea", "Torfaen", "Blaenau Gwent", "Caerphilly", "Rhondda Cynon Taf", "Vale of Glamorgan", "Bridgend", "Neath Port Talbot", "Powys", "Denbighshire", "Conwy", "Cardiff", "Anglesey", "Merthyr Tydfil", "Carmarthenshire", "Flintshire", "Wrexham", "Newport"]
SCOTLAND_COUNTIES = ["South Lanarkshire", "Highland", "Midlothian", "East Lothian", "Glasgow City", "North Lanarkshire", "Dundee City", "Angus", "Fife", "Moray", "Scottish Borders", "West Dunbartonshire", "Renfrewshire", "North Ayrshire", "Argyll and Bute", "Clackmannanshire", "West Lothian", "Falkirk", "East Ayrshire", "Inverclyde", "Western Isles", "Orkney", "Shetland Islands", "Stirling", "Perth and Kinross", "Aberdeenshire","City of Edinburgh","East Dunbartonshire", "South Ayrshire", "Dumfries and Galloway", "Aberdeen City", "East Renfrewshire"]
NI_COUNTIES = ["Fermanagh","Down","Antrim","Londonderry","Shetland Islands","Tyrone","Armagh"]

OUT_DIR = "static/geo"

if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)
with open("uk-counties.geojson", "r", encoding="utf-8") as f:
    data = json.load(f)

typemap_json = {}

uk_geodata = {"type": "FeatureCollection", "features": []}
england_geodata = {"type": "FeatureCollection", "features": []}
wales_geodata = {"type": "FeatureCollection", "features": []}
scotland_geodata = {"type": "FeatureCollection", "features": []}
ni_geodata = {"type": "FeatureCollection", "features": []}

for feature in data["features"]:
    county = feature["properties"]["county"]
    geodata = {"type": "FeatureCollection", "features": [feature]}
    if county in UK_COUNTIES:
        uk_geodata["features"].append(feature)
    if county in ENGLAND_COUNTIES:
        england_geodata["features"].append(feature)
    if county in WALES_COUNTIES:
        wales_geodata["features"].append(feature)
    if county in SCOTLAND_COUNTIES:
        scotland_geodata["features"].append(feature)
    if county in NI_COUNTIES:
        ni_geodata["features"].append(feature)

    name = county.replace(" ", "").replace("-", "").replace("'", "").replace(".", "").replace("(", "").replace(")", "").replace(",", "").lower()
    with open(f"{OUT_DIR}/{name}.geojson", "w", encoding="utf-8") as outfile:
        json.dump(geodata, outfile)
    display_name = county
    if county in ["Western Isles", "West Midlands", "Isle of Wight", "East Riding of Yorkshire", "City of Edinburgh", "Scottish Borders"]:
        display_name = "the " + county
    # if county in ["Durham", "Antrim", "Derry", "Down", "Fermanagh", "Tyrone", "Armagh"]:
    #     display_name = "County " + county
    typemap_json[name] = {"geofile": f"{name}.geojson", "name": display_name, "valid-counties": [county]}
    print(name)


with open(f"{OUT_DIR}/uk.geojson", "w", encoding="utf-8") as outfile:
    json.dump(uk_geodata, outfile)
with open(f"{OUT_DIR}/england.geojson", "w", encoding="utf-8") as outfile:
    json.dump(england_geodata, outfile)
with open(f"{OUT_DIR}/wales.geojson", "w", encoding="utf-8") as outfile:
    json.dump(wales_geodata, outfile)
with open(f"{OUT_DIR}/scotland.geojson", "w", encoding="utf-8") as outfile:
    json.dump(scotland_geodata, outfile)
with open(f"{OUT_DIR}/ni.geojson", "w", encoding="utf-8") as outfile:
    json.dump(ni_geodata, outfile)

typemap_json["uk"] = {"geofile": "uk.geojson", "name": "the United Kingdom", "valid-counties": UK_COUNTIES}
typemap_json["england"] = {"geofile": "england.geojson", "name": "England", "valid-counties": ENGLAND_COUNTIES}
typemap_json["wales"] = {"geofile": "wales.geojson", "name": "Wales", "valid-counties": WALES_COUNTIES}
typemap_json["scotland"] = {"geofile": "scotland.geojson", "name": "Scotland", "valid-counties": SCOTLAND_COUNTIES}
typemap_json["ni"] = {"geofile": "ni.geojson", "name": "Northern Ireland", "valid-counties": NI_COUNTIES}


with open("typemap.json", "w") as f:
    json.dump(typemap_json, f, indent=2)