import aiohttp
import asyncio
import logging

# Configure logging for this module
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
)

async def fetch_leaderboard_page(session, level_id, page_number):
    url = f"https://dustkid.com/json/level/{level_id}/all/{page_number}"
    async with session.get(url) as resp:
        return await resp.json()

async def fetch_user_leaderboard_for_level(session, level_id, user_id, semaphore):
    async with semaphore:
        # Scores
        user_score_entry = None
        user_score_rank = None
        all_scores = []
        page = 0
        while True:
            data = await fetch_leaderboard_page(session, level_id, page)
            scores = list(data.get("scores", {}).values())
            if not scores:
                break
            all_scores.extend(scores)
            page += 1
        for rank, entry in enumerate(all_scores, 1):
            if str(entry.get("user")) == str(user_id):
                user_score_rank = rank
                user_score_entry = entry
                break

        # Times
        user_time_entry = None
        user_time_rank = None
        all_times = []
        page = 0
        while True:
            data = await fetch_leaderboard_page(session, level_id, page)
            times = list(data.get("times", {}).values())
            if not times:
                break
            all_times.extend(times)
            page += 1
        for rank, entry in enumerate(all_times, 1):
            if str(entry.get("user")) == str(user_id):
                user_time_rank = rank
                user_time_entry = entry
                break

        return {
            "score": (user_score_rank, user_score_entry),
            "time": (user_time_rank, user_time_entry)
        }

async def fetch_all_levels_for_area(level_keys, user_id, levels_dict):
    semaphore = asyncio.Semaphore(16)  # Limit to 16 concurrent requests
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_user_leaderboard_for_level(session, levels_dict[level_key], user_id, semaphore)
            for level_key in level_keys if level_key in levels_dict
        ]
        return await asyncio.gather(*tasks)

async def fetch_all_levels_all_areas(areas_dict, user_id, levels_dict):
    semaphore = asyncio.Semaphore(32)  # Increase concurrency if desired
    async with aiohttp.ClientSession() as session:
        tasks = []
        level_area_pairs = []
        for area, level_keys in areas_dict.items():
            for level_key in level_keys:
                if level_key in levels_dict:
                    tasks.append(fetch_user_leaderboard_for_level(session, levels_dict[level_key], user_id, semaphore))
                    level_area_pairs.append((area, level_key))
        results = await asyncio.gather(*tasks)
        # Group results by area
        grouped = {area: [] for area in areas_dict}
        for (area, level_key), result in zip(level_area_pairs, results):
            grouped[area].append((level_key, result))
        return grouped