from flask import Flask, render_template, request, jsonify
import asyncio
from .dustkid_api import fetch_all_levels_all_areas, fetch_all_levels_for_area
import datetime
import pprint
import os

app = Flask(__name__)

LEVELS = {
    "Difficult1": "Repetition-13588",
    "Difficult2": "Close-13589",
    "Difficult3": "Far-13590",
    "Difficult4": "Currents-13591",
    "ForestMap1": "Mushy-Rush-13524",
    "ForestMap2": "Daisy-13525",
    "ForestMap3": "Grassy-Terrace-13526",
    "ForestMap4": "Copse-13527",
    "ForestMap5": "Twilight-Thicket-13528",
    "ForestMap6": "Viney-Underground-13529",
    "ForestMap7": "Hazy-Hideout-13530",
    "ForestMap8": "Midnight-Treetops-13531",
    "ForestMap9": "Thorny-Sunset-13532",
    "ForestMap10": "Flowerbed-13533",
    "ForestMap11": "Verdant-Ruins-13534",
    "ForestMap12": "Lamplit-Leaves-13535",
    "ForestMap13": "2-AM-Run-13536",
    "ForestMap14": "Mossy-Burrow-13537",
    "ForestMap15": "Moonlit-Canopy-13538",
    "ForestMap16": "Goodnight-Bears-13539",
    "Mountain1": "Morning-Climb-13540",
    "Mountain2": "Meltdown-13541",
    "Mountain3": "Cabin-13542",
    "Mountain4": "Stratified-13543",
    "Mountain5": "Boulder-Dash-13544",
    "Mountain6": "Mountain-Estate-13545",
    "Mountain7": "Snowcaps-13546",
    "Mountain8": "Alpine-Village-13547",
    "Mountain9": "Night-Quarry-13600",
    "Mountain10": "Precipice-13549",
    "Mountain11": "Sheer-Reflection-13550",
    "Mountain12": "Mountainside-Cavern-13551",
    "Mountain13": "Cordillera-13552",
    "Mountain14": "Treeline-13601",
    "Mountain15": "The-Peak-13554",
    "Mountain16": "Petaldrift-13555",
    "Ocean1": "Driftwood-13556",
    "Ocean2": "Beach-Bears-13557",
    "Ocean3": "Sandcastles-13558",
    "Ocean4": "Sea-Bear-13559",
    "Ocean5": "Blinkys-Castle-13560",
    "Ocean6": "Sand-Dune-13561",
    "Ocean7": "Horizon-13562",
    "Ocean8": "Grotto-13595",
    "Ocean9": "Breezy-13564",
    "Ocean10": "Rocky-Shore-13565",
    "Ocean11": "Lighthouse-13566",
    "Ocean12": "Landfall-13596",
    "Ocean13": "Phosphorescence-13568",
    "Ocean14": "Sea-Cave-13569",
    "Ocean15": "Docks-13570",
    "Ocean16": "Glacier-13571",
    "Rainlands1": "Rainsoaked-Ruins-13572",
    "Rainlands2": "Rusty-Bay-13573",
    "Rainlands3": "Misty-Lookout-13574",
    "Rainlands4": "Drizzle-Garden-13575",
    "Rainlands5": "Rainy-Canal-13576",
    "Rainlands6": "Drippy-Drains-13577",
    "Rainlands7": "Petrichor-Manor-13578",
    "Rainlands8": "Streetlights-13579",
    "Rainlands9": "Totem-Trickle-13580",
    "Rainlands10": "Ruined-Structure-13581",
    "Rainlands11": "Stonepath-13582",
    "Rainlands12": "Bluelight-13583",
    "Rainlands13": "Mapler-Factory-13584",
    "Rainlands14": "Aqueduct-13585",
    "Rainlands15": "Fluorescent-Skyway-13586",
    "Rainlands16": "Midnight-Shower-13587",
}

AREAS = {
    "Difficult": ["Difficult1", "Difficult2", "Difficult3", "Difficult4"],
    "Forest": ["ForestMap1", "ForestMap2", "ForestMap3", "ForestMap4", "ForestMap5", "ForestMap6", "ForestMap7", "ForestMap8", "ForestMap9", "ForestMap10", "ForestMap11", "ForestMap12", "ForestMap13", "ForestMap14", "ForestMap15", "ForestMap16"],
    "Mountain": ["Mountain1", "Mountain2", "Mountain3", "Mountain4", "Mountain5", "Mountain6", "Mountain7", "Mountain8", "Mountain9", "Mountain10", "Mountain11", "Mountain12", "Mountain13", "Mountain14", "Mountain15", "Mountain16"],
    "Ocean": ["Ocean1", "Ocean2", "Ocean3", "Ocean4", "Ocean5", "Ocean6", "Ocean7", "Ocean8", "Ocean9", "Ocean10", "Ocean11", "Ocean12", "Ocean13", "Ocean14", "Ocean15", "Ocean16"],
    "Rainlands": ["Rainlands1", "Rainlands2", "Rainlands3", "Rainlands4", "Rainlands5", "Rainlands6", "Rainlands7", "Rainlands8", "Rainlands9", "Rainlands10", "Rainlands11", "Rainlands12", "Rainlands13", "Rainlands14", "Rainlands15", "Rainlands16"],
}

def get_level_url(level_name, rank):
    # rank is 1-based, so subtract 1 before floor division
    if rank == "N/A" or not isinstance(rank, int):
        return f"https://dustkid.com/level/{level_name}/all/0"
    page = ((rank - 1) // 50) * 50
    return f"https://dustkid.com/level/{level_name}/all/{page}"

def format_time(ms):
    if ms == "N/A" or ms is None:
        return "N/A"
    return f"{int(ms) // 1000}.{str(int(ms) % 1000).zfill(3)}"

def map_score_letter(val):
    return {5: "S", 4: "A", 3: "B", 2: "C", 1: "D"}.get(val, "N/A")

def get_character_img(character):
    # character is 0-indexed from API, images are 1-indexed
    if isinstance(character, int) and 0 <= character <= 3:
        return f"img/head000{character+1}.png"
    return None

def time_ago(ts):
    if ts == "N/A" or ts is None:
        return "N/A"
    now = datetime.datetime.utcnow().timestamp()
    diff = now - ts
    if diff < 60:
        return f"{int(diff)} seconds ago"
    elif diff < 3600:
        return f"{int(diff//60)} minutes ago"
    elif diff < 86400:
        return f"{int(diff//3600)} hours ago"
    elif diff < 31536000:
        return f"{diff/86400:.1f} days ago"
    else:
        return f"{diff/31536000:.1f} years ago"

@app.route("/", methods=["GET", "POST"])
def index():
    leaderboard_data = {}
    user_id = None

    if request.method == "POST":
        user_id = request.form.get("user_id")
        print(f"User ID: {user_id}")
        # Fetch all levels for all areas concurrently
        grouped_results = run_async(fetch_all_levels_all_areas(AREAS, user_id, LEVELS))
        for area, results in grouped_results.items():
            area_scores = []
            area_times = []
            for level_key, result in results:
                level_name = LEVELS[level_key]
                # Scores
                rank, entry = result["score"]
                if entry:
                    rank_val = rank if isinstance(rank, int) else None
                    area_scores.append({
                        "level": level_name,
                        "level_url": get_level_url(level_name, rank_val),
                        "rank": rank,
                        "character": entry.get("character") if entry else None,
                        "character_img": get_character_img(entry.get("character")) if entry else None,
                        "score_completion": map_score_letter(entry.get("score_completion")) if entry else "N/A",
                        "score_finesse": map_score_letter(entry.get("score_finesse")) if entry else "N/A",
                        "time": format_time(entry.get("time")) if entry else "N/A",
                        "replay_id": entry.get("replay_id") if entry else None,
                        "time_off_world_record": "-",
                        "time_of_pb": time_ago(entry.get("timestamp")) if entry else "N/A",
                    })
                else:
                    area_scores.append({
                        "level": level_name,
                        "rank": "N/A",
                        "character": "N/A",
                        "score_completion": "N/A",
                        "score_finesse": "N/A",
                        "time": "N/A",
                        "time_off_world_record": "N/A",
                        "time_of_pb": "N/A",
                    })
                # Times
                rank, entry = result["time"]
                if entry:
                    rank_val = rank if isinstance(rank, int) else None
                    area_times.append({
                        "level": level_name,
                        "level_url": get_level_url(level_name, rank_val),
                        "rank": rank,
                        "character": entry.get("character") if entry else None,
                        "character_img": get_character_img(entry.get("character")) if entry else None,
                        "score_completion": map_score_letter(entry.get("score_completion")) if entry else "N/A",
                        "score_finesse": map_score_letter(entry.get("score_finesse")) if entry else "N/A",
                        "time": format_time(entry.get("time")) if entry else "N/A",
                        "replay_id": entry.get("replay_id") if entry else None,
                        "time_off_world_record": "-",
                        "time_of_pb": time_ago(entry.get("timestamp")) if entry else "N/A",
                    })
                else:
                    area_times.append({
                        "level": level_name,
                        "rank": "N/A",
                        "character": "N/A",
                        "score_completion": "N/A",
                        "score_finesse": "N/A",
                        "time": "N/A",
                        "time_off_world_record": "N/A",
                        "time_of_pb": "N/A",
                    })
            leaderboard_data[area] = {
                "scores": area_scores,
                "times": area_times,
            }
        print("Finished processing all areas.")

    return render_template(
        "leaderboard.html",
        leaderboard_data=leaderboard_data,
        user_id=user_id
    )

@app.route("/area_data", methods=["POST"])
async def area_data():
    data = request.get_json()
    area = data.get("area")
    user_id = data.get("user_id")
    if not area or not user_id or area not in AREAS:
        return jsonify({"error": "Invalid area or user_id"}), 400
    results = await fetch_all_levels_for_area(AREAS[area], user_id, LEVELS)
    area_scores = []
    area_times = []
    for level_key, result in zip(AREAS[area], results):
        level_name = LEVELS[level_key]
        # Scores
        rank, entry = result["score"]
        if entry:
            rank_val = rank if isinstance(rank, int) else None
            area_scores.append({
                "level": level_name,
                "level_url": get_level_url(level_name, rank_val),
                "rank": rank,
                "character": entry.get("character") if entry else None,
                "character_img": get_character_img(entry.get("character")) if entry else None,
                "score_completion": map_score_letter(entry.get("score_completion")) if entry else "N/A",
                "score_finesse": map_score_letter(entry.get("score_finesse")) if entry else "N/A",
                "time": format_time(entry.get("time")) if entry else "N/A",
                "replay_id": entry.get("replay_id") if entry else None,
                "time_off_world_record": "-",
                "time_of_pb": time_ago(entry.get("timestamp")) if entry else "N/A",
            })
        else:
            area_scores.append({
                "level": level_name,
                "rank": "N/A",
                "character": "N/A",
                "score_completion": "N/A",
                "score_finesse": "N/A",
                "time": "N/A",
                "time_off_world_record": "N/A",
                "time_of_pb": "N/A",
            })
        # Times
        rank, entry = result["time"]
        if entry:
            rank_val = rank if isinstance(rank, int) else None
            area_times.append({
                "level": level_name,
                "level_url": get_level_url(level_name, rank_val),
                "rank": rank,
                "character": entry.get("character") if entry else None,
                "character_img": get_character_img(entry.get("character")) if entry else None,
                "score_completion": map_score_letter(entry.get("score_completion")) if entry else "N/A",
                "score_finesse": map_score_letter(entry.get("score_finesse")) if entry else "N/A",
                "time": format_time(entry.get("time")) if entry else "N/A",
                "replay_id": entry.get("replay_id") if entry else None,
                "time_off_world_record": "-",
                "time_of_pb": time_ago(entry.get("timestamp")) if entry else "N/A",
            })
        else:
            area_times.append({
                "level": level_name,
                "rank": "N/A",
                "character": "N/A",
                "score_completion": "N/A",
                "score_finesse": "N/A",
                "time": "N/A",
                "time_off_world_record": "N/A",
                "time_of_pb": "N/A",
            })
    return jsonify({
        "area": area,
        "scores": area_scores,
        "times": area_times
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)