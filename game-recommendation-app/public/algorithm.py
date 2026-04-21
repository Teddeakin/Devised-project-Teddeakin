import sys
import json
import io
import math
import re
import unicodedata

sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def normalize_name(name):
    name = str(name)

    # remove symbols BEFORE unicode normalization so they do not become "tm" / "r"
    name = name.replace("™", " ")
    name = name.replace("®", " ")
    name = name.replace("©", " ")

    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    name = name.lower()

    # keep letters/numbers, collapse punctuation/spaces
    name = re.sub(r"[^a-z0-9]+", " ", name)
    name = re.sub(r"\s+", " ", name).strip()

    return name


def build_user_games(user_games):
    owned_games = set()
    played_games = {}

    for game in user_games:
        name = normalize_name(game.get("name", ""))
        hours = max(0.0, float(game.get("hours", 0)))

        if not name:
            continue

        owned_games.add(name)

        # keep 0-hour games as owned so they do not get recommended back
        if hours > 0:
            played_games[name] = played_games.get(name, 0) + hours

    return owned_games, played_games


def sqrt_transform(x):
    return math.sqrt(max(0.0, x))


def log_transform(x):
    return math.log1p(max(0.0, x))


def metadata_similarity(data_a, data_b):
    genres_a = {normalize_name(g) for g in data_a.get("genres", []) if normalize_name(g)}
    genres_b = {normalize_name(g) for g in data_b.get("genres", []) if normalize_name(g)}
    tags_a = {normalize_name(t) for t in data_a.get("tags", []) if normalize_name(t)}
    tags_b = {normalize_name(t) for t in data_b.get("tags", []) if normalize_name(t)}

    shared_genres = genres_a & genres_b
    shared_tags = tags_a & tags_b

    # require at least a real overlap
    if len(shared_genres) == 0 and len(shared_tags) < 2:
        return 0.0

    genre_union = genres_a | genres_b
    tag_union = tags_a | tags_b

    genre_jaccard = (len(shared_genres) / len(genre_union)) if genre_union else 0.0
    tag_jaccard = (len(shared_tags) / len(tag_union)) if tag_union else 0.0

    # genres matter more than tags
    return (genre_jaccard * 4.0) + (tag_jaccard * 2.0)


PLAYER_PROFILES = [
    {"label": "FPS", "gameData": {
        "halo: reach": 80,
        "counter-strike 2": 150,
        "apex legends": 120,
        "valorant": 90,
        "call of duty: warzone": 140,
        "tom clancy's rainbow six siege": 110
    }},
    {"label": "Hero Shooter", "gameData": {
        "valorant": 120,
        "overwatch 2": 150,
        "apex legends": 100,
        "marvel rivals": 80,
        "team fortress 2": 70,
        "paladins": 60
    }},
    {"label": "Cozy", "gameData": {
        "stardew valley": 150,
        "animal crossing": 100,
        "unpacking": 40,
        "slime rancher": 60,
        "spiritfarer": 70,
        "a little to the left": 35,
        "assemble with care": 25
    }},
    {"label": "Life Sim / Farming", "gameData": {
        "stardew valley": 140,
        "coral island": 90,
        "disney dreamlight valley": 100,
        "my time at sandrock": 80,
        "story of seasons": 70,
        "sun haven": 75,
        "the sims 4": 55
    }},
    {"label": "Roguelike", "gameData": {
        "hades": 120,
        "slay the spire": 100,
        "dead cells": 90,
        "balatro": 80,
        "risk of rain 2": 85,
        "enter the gungeon": 70
    }},
    {"label": "Deckbuilder / Strategy Roguelike", "gameData": {
        "slay the spire": 140,
        "balatro": 110,
        "monster train": 90,
        "inscryption": 80,
        "wildfrost": 60,
        "across the obelisk": 50
    }},
    {"label": "Soulslike", "gameData": {
        "elden ring": 200,
        "dark souls iii": 100,
        "sekiro shadows die twice": 80,
        "lies of p": 70,
        "nioh 2": 75,
        "remnant ii": 55
    }},
    {"label": "Action RPG", "gameData": {
        "elden ring": 150,
        "the witcher 3": 140,
        "monster hunter world": 110,
        "nioh 2": 80,
        "dragons dogma 2": 70,
        "dark souls iii": 90
    }},
    {"label": "CRPG / Narrative RPG", "gameData": {
        "baldurs gate 3": 180,
        "divinity original sin 2": 130,
        "disco elysium": 90,
        "pillars of eternity": 70,
        "pathfinder wrath of the righteous": 60,
        "dragon age origins": 80
    }},
    {"label": "Open World RPG", "gameData": {
        "the witcher 3": 150,
        "cyberpunk 2077": 100,
        "starfield": 60,
        "the elder scrolls v skyrim": 170,
        "fallout 4": 110,
        "horizon zero dawn": 80
    }},
    {"label": "RTS", "gameData": {
        "age of empires ii": 150,
        "starcraft ii": 120,
        "manor lords": 80,
        "warcraft iii": 90,
        "command conquer remastered collection": 70,
        "company of heroes 2": 60
    }},
    {"label": "Grand Strategy / 4X", "gameData": {
        "civilization vi": 110,
        "stellaris": 130,
        "crusader kings iii": 120,
        "hearts of iron iv": 100,
        "endless legend": 70,
        "humankind": 60,
        "risk global domination": 35
    }},
    {"label": "Racing", "gameData": {
        "forza horizon 5": 100,
        "gran turismo 7": 120,
        "f1 24": 90,
        "assetto corsa": 70,
        "need for speed heat": 60,
        "dirt rally 2 0": 65
    }},
    {"label": "Sports", "gameData": {
        "ea sports fc 25": 200,
        "nba 2k25": 150,
        "madden nfl 25": 80,
        "rocket league": 120,
        "tony hawks pro skater 1 2": 50,
        "pga tour 2k23": 40
    }},
    {"label": "Horror", "gameData": {
        "resident evil 4": 60,
        "silent hill 2": 50,
        "phasmophobia": 100,
        "dead by daylight": 150,
        "outlast": 55
    }},
    {"label": "Survival / Sandbox", "gameData": {
        "minecraft": 200,
        "rust": 150,
        "ark survival ascended": 120,
        "terraria": 100,
        "valheim": 110,
        "dont starve together": 80
    }},
    {"label": "Immersive Sim", "gameData": {
        "deus ex": 80,
        "dishonored 2": 70,
        "prey": 90,
        "hitman world of assassination": 110,
        "system shock": 60,
        "deathloop": 75
    }},
    {"label": "Stealth", "gameData": {
        "hitman world of assassination": 120,
        "dishonored 2": 90,
        "metal gear solid v the phantom pain": 140,
        "tom clancys splinter cell blacklist": 70,
        "thief": 50,
        "aragami": 45
    }},
    {"label": "Platformer / Metroidvania", "gameData": {
        "ori and the blind forest": 100,
        "hollow knight": 150,
        "dead cells": 80,
        "celeste": 90,
        "metroid dread": 70,
        "blasphemous": 60
    }},
    {"label": "Creative / Building", "gameData": {
        "minecraft": 180,
        "terraria": 90,
        "cities skylines": 130,
        "planet coaster": 80,
        "satisfactory": 120,
        "factorio": 140,
        "planet zoo": 70
    }},
    {"label": "Life Sim / Creative Casual", "gameData": {
        "the sims 4": 160,
        "planet zoo": 95,
        "house flipper": 70,
        "disney dreamlight valley": 75,
        "youtubers life": 60,
        "unpacking": 35
    }},
    {"label": "Management / Park Builder", "gameData": {
        "planet zoo": 150,
        "planet coaster": 120,
        "cities skylines": 100,
        "jurassic world evolution 2": 80,
        "two point hospital": 70,
        "lets build a zoo": 55
    }},
    {"label": "Narrative / Gentle Indie", "gameData": {
        "stray": 95,
        "assemble with care": 60,
        "my child lebensborn": 70,
        "my child lebensborn remastered": 60,
        "spiritfarer": 75,
        "what remains of edith finch": 55
    }},
    {"label": "Family / LEGO Adventure", "gameData": {
        "lego harry potter years 1 4": 110,
        "lego harry potter years 5 7": 90,
        "lego star wars the skywalker saga": 95,
        "lego marvel super heroes": 70,
        "stray": 35,
        "disney dreamlight valley": 40
    }},
    {"label": "Social / Party Co-op", "gameData": {
        "lethal company": 80,
        "content warning": 70,
        "among us": 85,
        "fall guys": 75,
        "party animals": 60,
        "overcooked 2": 55
    }},
    {"label": "Shared World Shooter", "gameData": {
        "destiny 2": 120,
        "warframe": 110,
        "tom clancys the division 2": 85,
        "borderlands 3": 75,
        "remnant ii": 60,
        "the first descendant": 55
    }}
]

# normalise profile keys once
for profile in PLAYER_PROFILES:
    profile["gameData"] = {
        normalize_name(name): float(hours)
        for name, hours in profile["gameData"].items()
    }


def main(app_data):
    try:
        with open('gameCache.json', 'r', encoding='utf-8') as f:
            raw_cache = json.load(f)

        cache = {normalize_name(k): v for k, v in raw_cache.items()}

        user_games = app_data.get('Merged', {}).get('games', [])
        owned_games, _ = build_user_games(user_games)

        user_profile = {"genres": {}, "tags": {}}

        for game in user_games:
            name_key = normalize_name(game.get('name', ''))
            hours = max(0.0, float(game.get('hours', 0)))

            if hours <= 0:
                continue

            if name_key in cache:
                data = cache[name_key]

                for g in data.get('genres', []):
                    g_key = normalize_name(g)
                    user_profile["genres"][g_key] = user_profile["genres"].get(g_key, 0) + hours

                for t in data.get('tags', []):
                    t_key = normalize_name(t)
                    user_profile["tags"][t_key] = user_profile["tags"].get(t_key, 0) + (hours * 0.5)

        candidates = [
            {"name": "Halo: Reach", "genres": ["action", "shooter"], "tags": ["sci-fi", "classic"], "metacritic": 91},
            {"name": "Counter-Strike 2", "genres": ["action", "shooter"], "tags": ["competitive", "tactical"], "metacritic": 82},
            {"name": "Apex Legends", "genres": ["action", "shooter"], "tags": ["battle-royale", "movement"], "metacritic": 88},
            {"name": "Valorant", "genres": ["action", "shooter"], "tags": ["tactical", "hero-shooter"], "metacritic": 80},
            {"name": "Stardew Valley", "genres": ["rpg", "simulation", "indie"], "tags": ["relaxing", "crafting"], "metacritic": 89},
            {"name": "Animal Crossing", "genres": ["simulation"], "tags": ["relaxing", "social"], "metacritic": 90},
            {"name": "Unpacking", "genres": ["puzzle", "indie"], "tags": ["relaxing", "short"], "metacritic": 84},
            {"name": "Slime Rancher", "genres": ["adventure", "indie"], "tags": ["cute", "exploration"], "metacritic": 81},
            {"name": "Hades", "genres": ["action", "indie"], "tags": ["roguelike", "great-soundtrack"], "metacritic": 93},
            {"name": "Slay the Spire", "genres": ["strategy", "indie"], "tags": ["roguelike", "deck-builder"], "metacritic": 89},
            {"name": "Dead Cells", "genres": ["action", "indie"], "tags": ["roguelike", "metroidvania"], "metacritic": 89},
            {"name": "Balatro", "genres": ["strategy", "indie"], "tags": ["roguelike", "addictive"], "metacritic": 90},
            {"name": "Elden Ring", "genres": ["action", "rpg"], "tags": ["difficult", "open-world"], "metacritic": 96},
            {"name": "Dark Souls III", "genres": ["action", "rpg"], "tags": ["difficult", "dark-fantasy"], "metacritic": 89},
            {"name": "Sekiro: Shadows Die Twice", "genres": ["action", "adventure"], "tags": ["difficult", "stealth"], "metacritic": 90},
            {"name": "Lies of P", "genres": ["action", "rpg"], "tags": ["difficult", "souls-like"], "metacritic": 80},
            {"name": "Baldur's Gate 3", "genres": ["rpg", "strategy"], "tags": ["story-rich", "turn-based"], "metacritic": 96},
            {"name": "The Witcher 3: Wild Hunt", "genres": ["rpg", "action"], "tags": ["open-world", "story-rich"], "metacritic": 92},
            {"name": "Cyberpunk 2077", "genres": ["rpg", "action"], "tags": ["sci-fi", "open-world"], "metacritic": 86},
            {"name": "Starfield", "genres": ["rpg", "action"], "tags": ["space", "exploration"], "metacritic": 83},
            {"name": "Age of Empires II", "genres": ["strategy"], "tags": ["rts", "historical"], "metacritic": 92},
            {"name": "StarCraft II", "genres": ["strategy"], "tags": ["rts", "sci-fi"], "metacritic": 93},
            {"name": "Manor Lords", "genres": ["strategy", "simulation"], "tags": ["city-builder", "historical"], "metacritic": 84},
            {"name": "Civilization VI", "genres": ["strategy"], "tags": ["4x", "turn-based"], "metacritic": 88},
            {"name": "Forza Horizon 5", "genres": ["racing", "sports"], "tags": ["open-world", "cars"], "metacritic": 92},
            {"name": "Gran Turismo 7", "genres": ["racing", "sports"], "tags": ["simulation", "cars"], "metacritic": 87},
            {"name": "F1 24", "genres": ["racing", "sports"], "tags": ["simulation", "competitive"], "metacritic": 78},
            {"name": "Assetto Corsa", "genres": ["racing", "sports"], "tags": ["simulation", "realistic"], "metacritic": 85},
            {"name": "EA Sports FC 25", "genres": ["sports"], "tags": ["football", "competitive"], "metacritic": 76},
            {"name": "NBA 2K25", "genres": ["sports"], "tags": ["basketball", "competitive"], "metacritic": 79},
            {"name": "Madden NFL 25", "genres": ["sports"], "tags": ["american-football", "competitive"], "metacritic": 70},
            {"name": "Rocket League", "genres": ["sports", "action"], "tags": ["competitive", "multiplayer"], "metacritic": 86},
            {"name": "Resident Evil 4", "genres": ["action", "horror"], "tags": ["remake", "survival-horror"], "metacritic": 93},
            {"name": "Silent Hill 2", "genres": ["horror", "adventure"], "tags": ["psychological", "remake"], "metacritic": 86},
            {"name": "Phasmophobia", "genres": ["horror", "indie"], "tags": ["co-op", "ghosts"], "metacritic": 80},
            {"name": "Dead by Daylight", "genres": ["horror", "action"], "tags": ["asymmetrical", "survival"], "metacritic": 71},
            {"name": "Minecraft", "genres": ["sandbox", "survival"], "tags": ["crafting", "creative"], "metacritic": 93},
            {"name": "Rust", "genres": ["survival", "action"], "tags": ["pvp", "crafting"], "metacritic": 69},
            {"name": "ARK: Survival Ascended", "genres": ["survival", "action"], "tags": ["dinosaurs", "crafting"], "metacritic": 70},
            {"name": "Terraria", "genres": ["sandbox", "action"], "tags": ["crafting", "exploration"], "metacritic": 83},
            {"name": "Deus Ex", "genres": ["rpg", "shooter"], "tags": ["cyberpunk", "immersive-sim"], "metacritic": 90},
            {"name": "Dishonored 2", "genres": ["action", "adventure"], "tags": ["stealth", "immersive-sim"], "metacritic": 88},
            {"name": "Prey", "genres": ["action", "shooter"], "tags": ["sci-fi", "immersive-sim"], "metacritic": 82},
            {"name": "Hitman World of Assassination", "genres": ["action", "stealth"], "tags": ["assassin", "sandbox"], "metacritic": 87}
        ]

        genre_penalty = {
            "action": 0.65,
            "rpg": 0.65,
            "adventure": 0.75,
            "simulation": 0.8,
            "sports": 0.75,
            "strategy": 0.8,
            "shooter": 0.75
        }

        candidate_metas = [g["metacritic"] for g in candidates if g.get("metacritic") is not None]
        min_meta = min(candidate_metas) if candidate_metas else 0
        max_meta = max(candidate_metas) if candidate_metas else 100
        meta_range = max(max_meta - min_meta, 1)

        max_genre_profile = max(user_profile["genres"].values(), default=1)
        max_tag_profile = max(user_profile["tags"].values(), default=1)

        results = []

        for game in candidates:
            name_key = normalize_name(game["name"])

            if name_key in owned_games:
                continue

            genre_score_raw = 0
            genre_details = []

            for g in game['genres']:
                g_key = normalize_name(g)
                raw_value = user_profile["genres"].get(g_key, 0)
                penalty = genre_penalty.get(g_key, 1.0)
                adjusted_value = raw_value * penalty

                genre_score_raw += adjusted_value

                if raw_value > 0:
                    genre_details.append({
                        "name": g_key,
                        "raw": round(raw_value, 2),
                        "adjusted": round(adjusted_value, 2),
                        "weighted": 0
                    })

            tag_score_raw = 0
            tag_details = []

            for t in game['tags']:
                t_key = normalize_name(t)
                raw_value = user_profile["tags"].get(t_key, 0)
                tag_score_raw += raw_value

                if raw_value > 0:
                    tag_details.append({
                        "name": t_key,
                        "raw": round(raw_value, 2),
                        "weighted": 0
                    })

            genre_score = genre_score_raw / max_genre_profile if max_genre_profile > 0 else 0
            tag_score = tag_score_raw / max_tag_profile if max_tag_profile > 0 else 0
            quality = (game['metacritic'] - min_meta) / meta_range if game.get("metacritic") is not None else 0

            w1, w2, w3 = 0.50, 0.35, 0.15

            genre_weighted = genre_score * w1
            tag_weighted = tag_score * w2
            metacritic_weighted = quality * w3
            final_score = genre_weighted + tag_weighted + metacritic_weighted

            for item in genre_details:
                adjusted_normalized = (item["adjusted"] / max_genre_profile) if max_genre_profile > 0 else 0
                item["weighted"] = round(adjusted_normalized * w1, 4)

            for item in tag_details:
                normalized_tag = (item["raw"] / max_tag_profile) if max_tag_profile > 0 else 0
                item["weighted"] = round(normalized_tag * w2, 4)

            results.append({
                "name": game["name"],
                "score": round(final_score, 4),
                "breakdown": {
                    "genre_total": round(genre_weighted, 4),
                    "tag_total": round(tag_weighted, 4),
                    "metacritic_total": round(metacritic_weighted, 4)
                },
                "details": {
                    "genres": genre_details,
                    "tags": tag_details
                },
                "formula": {
                    "genre_score_raw": round(genre_score_raw, 2),
                    "tag_score_raw": round(tag_score_raw, 2),
                    "quality_raw": round(quality, 4),
                    "weights": {
                        "genre": w1,
                        "tag": w2,
                        "metacritic": w3
                    }
                }
            })

        results = sorted(results, key=lambda x: x['score'], reverse=True)
        print(json.dumps(results))

    except Exception as e:
        print(json.dumps({"error": str(e)}))


def KNN(app_data):
    try:
        user_games = app_data.get('Merged', {}).get('games', [])
        owned_games, user_games_dict = build_user_games(user_games)

        player_profiles = PLAYER_PROFILES

        total_games_list = set(owned_games)
        for p in player_profiles:
            total_games_list.update(p["gameData"].keys())
        total_games_list = sorted(list(total_games_list))

        # cosine = taste shape
        user_vector = [sqrt_transform(user_games_dict.get(t, 0)) for t in total_games_list]

        distances = []

        for p in player_profiles:
            vec = [sqrt_transform(p["gameData"].get(t, 0)) for t in total_games_list]

            dot_product = sum(user_vector[i] * vec[i] for i in range(len(total_games_list)))
            magnitude_user = math.sqrt(sum(v ** 2 for v in user_vector))
            magnitude_profile = math.sqrt(sum(v ** 2 for v in vec))

            similarity = 0
            if magnitude_user > 0 and magnitude_profile > 0:
                similarity = dot_product / (magnitude_user * magnitude_profile)

            distances.append({
                "label": p["label"],
                "similarity": round(similarity, 4),
                "data": p["gameData"]
            })

        ranked = sorted(distances, key=lambda x: x["similarity"], reverse=True)
        top_k = [n for n in ranked if n["similarity"] > 0][:6]
        if not top_k:
            top_k = ranked[:3]

        neighbor_names = [n["label"] for n in top_k]

        game_adjacency_list = []
        all_neighbor_games = set()
        for n in top_k:
            all_neighbor_games.update(n["data"].keys())

        for g_name in all_neighbor_games:
            totals = [sum(n["data"].values()) if sum(n["data"].values()) > 0 else 1 for n in top_k[:3]]
            while len(totals) < 3:
                totals.append(1)

            coords = {
                "x": (top_k[0]["data"].get(g_name, 0) / totals[0]) * 100 if len(top_k) > 0 else 0,
                "y": (top_k[1]["data"].get(g_name, 0) / totals[1]) * 100 if len(top_k) > 1 else 0,
                "z": (top_k[2]["data"].get(g_name, 0) / totals[2]) * 100 if len(top_k) > 2 else 0
            }

            owners = [p["label"] for p in player_profiles if g_name in p["gameData"]]
            active_neighbors = [n["label"] for n in top_k if g_name in n["data"]]

            pulls = [coords["x"], coords["y"], coords["z"]]
            max_pull_index = pulls.index(max(pulls))
            primary_neighbor = neighbor_names[max_pull_index] if neighbor_names else "None"

            game_adjacency_list.append({
                "name": g_name,
                "coords": coords,
                "owned": g_name in owned_games,
                "group": primary_neighbor,
                "groups": active_neighbors,
                "all_owners": ", ".join(owners),
                "strength": max(pulls)
            })

        similarity_sum = sum(n["similarity"] for n in top_k) or 1
        results = {}

        for neighbor in top_k:
            weight = neighbor["similarity"] / similarity_sum
            game_data = neighbor["data"]

            transformed_total = sum(sqrt_transform(h) for h in game_data.values()) or 1

            for title, hours in game_data.items():
                if title in owned_games:
                    continue

                neighbor_relevance = sqrt_transform(hours) / transformed_total
                final_score = neighbor_relevance * weight * 10

                if title not in results:
                    results[title] = {
                        "name": title,
                        "score": 0,
                        "contributions": {}
                    }

                results[title]["score"] += final_score
                results[title]["contributions"][neighbor["label"]] = final_score

        final = sorted(results.values(), key=lambda x: x["score"], reverse=True)

        for item in final:
            total_contribution = sum(item["contributions"].values()) or 1

            for k in item["contributions"]:
                item["contributions"][k] = round(item["contributions"][k] / total_contribution, 2)

            item["score"] = round(item["score"], 2)

        print(json.dumps({
            "recommendations": final,
            "similarities": ranked,
            "game_adjacency": game_adjacency_list,
            "neighbors": neighbor_names
        }))

    except Exception as e:
        print(json.dumps({"error": f"KNN Engine Error: {str(e)}"}))


def KNN2(app_data):
    try:
        user_games = app_data.get('Merged', {}).get('games', [])
        owned_games, user_games_dict = build_user_games(user_games)

        player_profiles = PLAYER_PROFILES

        total_games_list = set(owned_games)
        for p in player_profiles:
            total_games_list.update(p["gameData"].keys())
        total_games_list = sorted(list(total_games_list))

        # euclidean = overall play-pattern closeness, not share of total hours
        user_max = max([log_transform(h) for h in user_games_dict.values()], default=1)

        user_vector = []
        for game_name in total_games_list:
            value = log_transform(user_games_dict.get(game_name, 0))
            user_vector.append(value / user_max if user_max > 0 else 0)

        distances = []

        for p in player_profiles:
            profile_max = max([log_transform(h) for h in p["gameData"].values()], default=1)

            profile_vector = []
            for game_name in total_games_list:
                value = log_transform(p["gameData"].get(game_name, 0))
                profile_vector.append(value / profile_max if profile_max > 0 else 0)

            distance = math.sqrt(
                sum((user_vector[i] - profile_vector[i]) ** 2 for i in range(len(total_games_list)))
            )

            distances.append({
                "label": p["label"],
                "distance": round(distance, 4),
                "data": p["gameData"]
            })

        ranked = sorted(distances, key=lambda x: x["distance"])
        top_k = ranked[:6]
        neighbor_names = [n["label"] for n in top_k]

        game_adjacency_list = []
        all_neighbor_games = set()
        for n in top_k:
            all_neighbor_games.update(n["data"].keys())

        for g_name in all_neighbor_games:
            totals = [sum(n["data"].values()) if sum(n["data"].values()) > 0 else 1 for n in top_k[:3]]
            while len(totals) < 3:
                totals.append(1)

            coords = {
                "x": (top_k[0]["data"].get(g_name, 0) / totals[0]) * 100 if len(top_k) > 0 else 0,
                "y": (top_k[1]["data"].get(g_name, 0) / totals[1]) * 100 if len(top_k) > 1 else 0,
                "z": (top_k[2]["data"].get(g_name, 0) / totals[2]) * 100 if len(top_k) > 2 else 0
            }

            owners = [p["label"] for p in player_profiles if g_name in p["gameData"]]
            active_neighbors = [n["label"] for n in top_k if g_name in n["data"]]

            pulls = [coords["x"], coords["y"], coords["z"]]
            max_pull_index = pulls.index(max(pulls))
            primary_neighbor = neighbor_names[max_pull_index] if neighbor_names else "None"

            game_adjacency_list.append({
                "name": g_name,
                "coords": coords,
                "owned": g_name in owned_games,
                "group": primary_neighbor,
                "groups": active_neighbors,
                "all_owners": ", ".join(owners),
                "strength": max(pulls)
            })

        sigma = ranked[min(5, len(ranked) - 1)]["distance"] if ranked else 1
        if sigma <= 0:
            sigma = 1

        raw_weights = []
        for neighbor in top_k:
            w = math.exp(-(neighbor["distance"] ** 2) / (2 * sigma ** 2))
            raw_weights.append(w)

        total_weight = sum(raw_weights) or 1
        results = {}

        for i, neighbor in enumerate(top_k):
            weight = raw_weights[i] / total_weight
            game_data = neighbor["data"]

            transformed_total = sum(log_transform(h) for h in game_data.values()) or 1

            for title, hours in game_data.items():
                if title in owned_games:
                    continue

                neighbor_relevance = log_transform(hours) / transformed_total
                final_score = neighbor_relevance * weight * 10

                if title not in results:
                    results[title] = {
                        "name": title,
                        "score": 0,
                        "contributions": {}
                    }

                results[title]["score"] += final_score
                results[title]["contributions"][neighbor["label"]] = final_score

        final = sorted(results.values(), key=lambda x: x["score"], reverse=True)

        for item in final:
            total_contribution = sum(item["contributions"].values()) or 1

            for k in item["contributions"]:
                item["contributions"][k] = round(item["contributions"][k] / total_contribution, 2)

            item["score"] = round(item["score"], 2)

        print(json.dumps({
            "recommendations": final,
            "similarities": ranked,
            "game_adjacency": game_adjacency_list,
            "neighbors": neighbor_names
        }))

    except Exception as e:
        print(json.dumps({"error": f"KNN2 Engine Error: {str(e)}"}))


def RandomWalk(app_data):
    try:
        with open('gameCache.json', 'r', encoding='utf-8') as f:
            raw_cache = json.load(f)

        cache = {normalize_name(k): v for k, v in raw_cache.items()}

        user_games = app_data.get('Merged', {}).get('games', [])
        owned_games, user_games_dict = build_user_games(user_games)

        connected_user_games = {
            game: hours for game, hours in user_games_dict.items()
            if game in cache
        }

        # use meaningful seeds only, so tiny one-off games do not steer the walk
        seed_games = {
            game: hours for game, hours in connected_user_games.items()
            if hours >= 2
        }

        # fallback if too few survive
        if len(seed_games) < 8:
            sorted_games = sorted(
                connected_user_games.items(),
                key=lambda x: x[1],
                reverse=True
            )
            seed_games = dict(sorted_games[:12])

        graph = {}
        edge_weights = {}

        def add_edge(a, b, weight, source_type):
            if a == b or weight <= 0:
                return

            if a not in graph:
                graph[a] = {}
            if b not in graph:
                graph[b] = {}

            graph[a][b] = graph[a].get(b, 0) + weight
            graph[b][a] = graph[b].get(a, 0) + weight

            edge_key = tuple(sorted([a, b]))
            if edge_key not in edge_weights:
                edge_weights[edge_key] = {
                    "source": a,
                    "target": b,
                    "weight": 0,
                    "profiles": set()
                }

            edge_weights[edge_key]["weight"] += weight
            edge_weights[edge_key]["profiles"].add(source_type)

        universe = set(seed_games.keys())

        for owned in seed_games:
            owned_data = cache.get(owned)
            if not owned_data:
                continue

            scored = []
            for other_name, other_data in cache.items():
                if other_name == owned:
                    continue

                score = metadata_similarity(owned_data, other_data)
                if score > 0:
                    scored.append((other_name, score))

            scored.sort(key=lambda x: x[1], reverse=True)

            for other_name, score in scored[:8]:
                if score >= 0.35:
                    universe.add(other_name)

        universe = list(universe)

        for i in range(len(universe)):
            a = universe[i]
            if a not in cache:
                continue

            local_scores = []
            for j in range(len(universe)):
                if i == j:
                    continue

                b = universe[j]
                if b not in cache:
                    continue

                score = metadata_similarity(cache[a], cache[b])
                if score > 0:
                    local_scores.append((b, score))

            local_scores.sort(key=lambda x: x[1], reverse=True)

            for b, score in local_scores[:4]:
                if score >= 0.35:
                    add_edge(a, b, score, "metadata")

        all_games = set(graph.keys()) | set(owned_games)
        connected_total_hours = sum(log_transform(hours) for hours in seed_games.values())

        initial_scores = {game: 0 for game in all_games}
        if connected_total_hours > 0:
            for game, hours in seed_games.items():
                initial_scores[game] = log_transform(hours) / connected_total_hours

        scores = initial_scores.copy()
        contributions = {game: {} for game in all_games}

        if connected_total_hours > 0:
            for game, hours in seed_games.items():
                contributions[game][game] = log_transform(hours) / connected_total_hours

        alpha = 0.6
        iterations = 10

        for _ in range(iterations):
            propagated = {game: 0 for game in all_games}
            propagated_contributions = {game: {} for game in all_games}

            for game in all_games:
                neighbours = graph.get(game, {})

                if not neighbours:
                    propagated[game] += scores.get(game, 0)

                    for source_game, value in contributions.get(game, {}).items():
                        propagated_contributions[game][source_game] = (
                            propagated_contributions[game].get(source_game, 0) + value
                        )
                    continue

                total_neighbours_weight = sum(neighbours.values())
                if total_neighbours_weight == 0:
                    continue

                for neighbour, weight in neighbours.items():
                    share_ratio = weight / total_neighbours_weight
                    share_score = scores.get(game, 0) * share_ratio

                    propagated[neighbour] += share_score

                    for source_game, value in contributions.get(game, {}).items():
                        share_value = value * share_ratio
                        propagated_contributions[neighbour][source_game] = (
                            propagated_contributions[neighbour].get(source_game, 0) + share_value
                        )

            new_scores = {}
            new_contributions = {}

            for game in all_games:
                new_scores[game] = (
                    (1 - alpha) * initial_scores.get(game, 0)
                    + alpha * propagated.get(game, 0)
                )

                new_contributions[game] = {}

                for source_game, value in contributions.get(game, {}).items():
                    retained = (1 - alpha) * value
                    if retained > 0:
                        new_contributions[game][source_game] = (
                            new_contributions[game].get(source_game, 0) + retained
                        )

                for source_game, value in propagated_contributions.get(game, {}).items():
                    spread = alpha * value
                    if spread > 0:
                        new_contributions[game][source_game] = (
                            new_contributions[game].get(source_game, 0) + spread
                        )

            scores = new_scores
            contributions = new_contributions

        recommendations = []

        for game, score in scores.items():
            if game not in owned_games:
                source_breakdown = contributions.get(game, {})
                sorted_sources = sorted(source_breakdown.items(), key=lambda x: x[1], reverse=True)
                total_source = sum(source_breakdown.values())

                if total_source > 0:
                    influenced_by_percent = {
                        source: round((value / total_source) * 100, 2)
                        for source, value in sorted_sources[:5]
                    }
                else:
                    influenced_by_percent = {}

                recommendations.append({
                    "name": game,
                    "score": round(score, 4),
                    "influenced_by": influenced_by_percent
                })

        recommendations = [r for r in recommendations if r["score"] > 0.001]
        recommendations.sort(key=lambda x: x["score"], reverse=True)

        graph_nodes = []
        for game in all_games:
            graph_nodes.append({
                "id": game,
                "label": game,
                "owned": game in owned_games,
                "score": round(scores.get(game, 0), 4)
            })

        graph_edges = []
        for edge in edge_weights.values():
            graph_edges.append({
                "source": edge["source"],
                "target": edge["target"],
                "weight": round(edge["weight"], 4),
                "profiles": sorted(list(edge["profiles"]))
            })

        print(json.dumps({
            "recommendations": recommendations[:10],
            "graph_nodes": graph_nodes,
            "graph_edges": graph_edges
        }))

    except Exception as e:
        print(json.dumps({"error": f"RandomWalk Engine Error: {str(e)}"}))


if __name__ == "__main__":
    try:
        input_raw = sys.stdin.read()
        if not input_raw:
            sys.exit(0)

        app_data = json.loads(input_raw)
        algorithm_choice = app_data.get('algorithmType', 'Linear')

        if algorithm_choice == 'KNN':
            KNN(app_data)
        elif algorithm_choice == "KNN2":
            KNN2(app_data)
        elif algorithm_choice == "RandomWalk":
            RandomWalk(app_data)
        else:
            main(app_data)

    except Exception as e:
        print(json.dumps({"error": f"Gatekeeper error: {str(e)}"}))