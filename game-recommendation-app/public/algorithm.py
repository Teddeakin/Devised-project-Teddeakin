import sys
import json
import os
import io
import math

sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main(app_data):
    try:

        with open('gameCache.json', 'r', encoding='utf-8') as f:
            cache = json.load(f)

        user_games = app_data.get('Merged', {}).get('games', [])
        
        user_profile = {"genres": {}, "tags": {}}
        total_hours = 0

        for game in user_games:
            name_key = game['name'].lower().strip() # normalise the name(s)
            hours = float(game.get('hours', 0)) # get playtime as a number
            total_hours += hours 
            
            if name_key in cache:
                data = cache[name_key] # looking through teh cache to find the data for the namekey

                for g in data.get('genres', []): # go through the genres assigned to the namekey
                    user_profile["genres"][g] = user_profile["genres"].get(g, 0) + hours # tells it work on the current genre its looping through and add the hours that are here

                for t in data.get('tags', []):
                    user_profile["tags"][t] = user_profile["tags"].get(t, 0) + (hours * 0.5) # does the same for tags but is half the value

        candidates = [
            {"name": "Halo Reach", "genres": ["action", "shooter"], "tags": ["sci-fi", "classic"], "metacritic": 91},
            {"name": "Counter-Strike 2", "genres": ["action", "shooter"], "tags": ["competitive", "tactical"], "metacritic": 82},
            {"name": "Apex Legends", "genres": ["action", "shooter"], "tags": ["battle-royale", "movement"], "metacritic": 88},
            {"name": "Valorant", "genres": ["action", "shooter"], "tags": ["tactical", "hero-shooter"], "metacritic": 80},
            {"name": "Stardew Valley", "genres": ["rpg", "simulation", "indie"], "tags": ["relaxing", "crafting"], "metacritic": 89},
            {"name": "Animal Crossing", "genres": ["simulation"], "tags": ["relaxing", "social"], "metacritic": 90},
            {"name": "Unpacked", "genres": ["puzzle", "indie"], "tags": ["relaxing", "short"], "metacritic": 84},
            {"name": "Slime Rancher", "genres": ["adventure", "indie"], "tags": ["cute", "exploration"], "metacritic": 81},
            {"name": "Hades", "genres": ["action", "indie"], "tags": ["roguelike", "great-soundtrack"], "metacritic": 93},
            {"name": "Slay the Spire", "genres": ["strategy", "indie"], "tags": ["roguelike", "deck-builder"], "metacritic": 89},
            {"name": "Dead Cells", "genres": ["action", "indie"], "tags": ["roguelike", "metroidvania"], "metacritic": 89},
            {"name": "Balatro", "genres": ["strategy", "indie"], "tags": ["roguelike", "addictive"], "metacritic": 90},
            {"name": "Elden Ring", "genres": ["action", "rpg"], "tags": ["difficult", "open-world"], "metacritic": 96},
            {"name": "Dark Souls III", "genres": ["action", "rpg"], "tags": ["difficult", "dark-fantasy"], "metacritic": 89},
            {"name": "sekiro: shadows die twice", "genres": ["action", "adventure"], "tags": ["difficult", "stealth"], "metacritic": 90},
            {"name": "Lies of P", "genres": ["action", "rpg"], "tags": ["difficult", "souls-like"], "metacritic": 80},
            {"name": "Baldurs Gate 3", "genres": ["rpg", "strategy"], "tags": ["story-rich", "turn-based"], "metacritic": 96},
            {"name": "The Witcher 3", "genres": ["rpg", "action"], "tags": ["open-world", "story-rich"], "metacritic": 92},
            {"name": "Cyberpunk 2077", "genres": ["rpg", "action"], "tags": ["sci-fi", "open-world"], "metacritic": 86},
            {"name": "Starfield", "genres": ["rpg", "action"], "tags": ["space", "exploration"], "metacritic": 83},
            {"name": "Age of Empires II", "genres": ["strategy"], "tags": ["rts", "historical"], "metacritic": 92},
            {"name": "Starcraft II", "genres": ["strategy"], "tags": ["rts", "sci-fi"], "metacritic": 93},
            {"name": "Manor Lords", "genres": ["strategy", "simulation"], "tags": ["city-builder", "historical"], "metacritic": 84},
            {"name": "Civilization VI", "genres": ["strategy"], "tags": ["4x", "turn-based"], "metacritic": 88},
            {"name": "Forza Horizon 5", "genres": ["racing", "sports"], "tags": ["open-world", "cars"], "metacritic": 92},
            {"name": "Gran Turismo 7", "genres": ["racing", "sports"], "tags": ["simulation", "cars"], "metacritic": 87},
            {"name": "F1 24", "genres": ["racing", "sports"], "tags": ["simulation", "competitive"], "metacritic": 78},
            {"name": "Assetto Corsa", "genres": ["racing", "sports"], "tags": ["simulation", "realistic"], "metacritic": 85},
            {"name": "FC 25", "genres": ["sports"], "tags": ["football", "competitive"], "metacritic": 76},
            {"name": "NBA 2K25", "genres": ["sports"], "tags": ["basketball", "competitive"], "metacritic": 79},
            {"name": "Madden NFL 25", "genres": ["sports"], "tags": ["american-football", "competitive"], "metacritic": 70},
            {"name": "Rocket League", "genres": ["sports", "action"], "tags": ["competitive", "multiplayer"], "metacritic": 86},
            {"name": "Resident Evil 4", "genres": ["action", "horror"], "tags": ["remake", "survival-horror"], "metacritic": 93},
            {"name": "Silent Hill 2", "genres": ["horror", "adventure"], "tags": ["psychological", "remake"], "metacritic": 86},
            {"name": "Phasmophobia", "genres": ["horror", "indie"], "tags": ["co-op", "ghosts"], "metacritic": 80},
            {"name": "Dead by Daylight", "genres": ["horror", "action"], "tags": ["asymmetrical", "survival"], "metacritic": 71},
            {"name": "Minecraft", "genres": ["sandbox", "survival"], "tags": ["crafting", "creative"], "metacritic": 93},
            {"name": "Rust", "genres": ["survival", "action"], "tags": ["pvp", "crafting"], "metacritic": 69},
            {"name": "Ark Survival Ascended", "genres": ["survival", "action"], "tags": ["dinosaurs", "crafting"], "metacritic": 70},
            {"name": "Terraria", "genres": ["sandbox", "action"], "tags": ["crafting", "exploration"], "metacritic": 83},
            {"name": "Deus Ex", "genres": ["rpg", "shooter"], "tags": ["cyberpunk", "immersive-sim"], "metacritic": 90},
            {"name": "Dishonored 2", "genres": ["action", "adventure"], "tags": ["stealth", "immersive-sim"], "metacritic": 88},
            {"name": "Prey", "genres": ["action", "shooter"], "tags": ["sci-fi", "immersive-sim"], "metacritic": 82},
            {"name": "Hitman 3", "genres": ["action", "stealth"], "tags": ["assassin", "sandbox"], "metacritic": 87}
    ]

        results = []

        for game in candidates: # look through each of potential candidates

            genre_score = 0
            for g in game['genres']: # look at the genres in the candidates
                genre_score += user_profile["genres"].get(g, 0) # finding the genre in user profiles and adding the genre score calculated earlier (increases for both genres)
  
            tag_score = 0
            for t in game['tags']:
                tag_score += user_profile["tags"].get(t, 0)
            
            w1, w2, w3 = 0.5, 0.3, 0.2
            quality = game['metacritic'] / 10 # looking for the metacritic score for that game
            
            final_score = (genre_score * w1) + (tag_score * w2) + (quality * w3)
            
            results.append({"name": game['name'], "score": round(final_score, 2)}) 

        # Sort by highest score
        results = sorted(results, key=lambda x: x['score'], reverse=True)
        print(json.dumps(results))

    except Exception as e:
        print(json.dumps({"error": str(e)}))


def KNN(app_data):
    try:
        with open('gameCache.json', 'r', encoding='utf-8') as f:
            cache = json.load(f)

        user_games = app_data.get('Merged', {}).get('games', [])

        user_games_normalized = {n["name"].lower().strip() for n in user_games}
        user_games_dict = {n["name"].lower().strip(): float(n.get("hours", 0)) for n in user_games}

        player_profiles = [
            {"label": "FPS", "gameData": {"halo reach": 80, "counter-strike 2": 150, "apex legends": 120, "valorant": 90}},
            {"label": "Cozy", "gameData": {"stardew valley": 150, "animal crossing": 100, "unpacked": 40, "slime rancher": 60}},
            {"label": "Roguelike", "gameData": {"hades": 120, "slay the spire": 100, "dead cells": 90, "balatro": 80}},
            {"label": "Soulslike", "gameData": {"elden ring": 200, "dark souls iii": 100, "sekiro: shadows die twice": 80, "lies of p": 70, "dead cells": 90, "Ori and the Blind Forest": 1.9}},
            {"label": "RPG", "gameData": {"baldurs gate 3": 180, "the witcher 3": 150, "cyberpunk 2077": 100, "starfield": 60}},
            {"label": "RTS", "gameData": {"age of empires ii": 150, "starcraft ii": 120, "manor lords": 80, "civilization vi": 110}},
            {"label": "Racing", "gameData": {"forza horizon 5": 100, "gran turismo 7": 120, "f1 24": 90, "assetto corsa": 70}},
            {"label": "Sports", "gameData": {"fc 25": 200, "nba 2k25": 150, "madden nfl 25": 80, "rocket league": 120}},
            {"label": "Horror", "gameData": {"resident evil 4": 60, "silent hill 2": 50, "phasmophobia": 100, "dead by daylight": 150, "dead cells": 90,}},
            {"label": "Survival/Sandbox", "gameData": {"minecraft": 200, "rust": 150, "ark survival ascended": 120, "terraria": 100}},
            {"label": "Immersive Sim", "gameData": {"deus ex": 80, "dishonored 2": 70, "prey": 90, "hitman 3": 110}}
        ]

        total_games_list = set(user_games_normalized)

        for p in player_profiles:
            total_games_list.update(p["gameData"].keys())

        total_games_list = sorted(list(total_games_list))

        vector = []
        total = sum(user_games_dict.values())

        for t in total_games_list:
            game_hours = user_games_dict.get(t, 0) / total if total > 0 else 0
            vector.append(game_hours)

        distances = []

        for p in player_profiles:
            total_p = sum(p["gameData"].values())

            vec = []
            for t in total_games_list:
                value = p["gameData"].get(t, 0) / total_p if total_p > 0 else 0
                vec.append(value)

            dot_product = sum(vector[i] * vec[i] for i in range(len(total_games_list)))

            magnitude_user = math.sqrt(sum(vector[i] ** 2 for i in range(len(total_games_list))))
            magnitude_profile = math.sqrt(sum(vec[i] ** 2 for i in range(len(total_games_list))))

            if magnitude_user > 0 and magnitude_profile > 0:
                similarity = dot_product / (magnitude_user * magnitude_profile)
            else:
                similarity = 0

            distances.append({
                "label": p["label"],
                "similarity": similarity,
                "data": p["gameData"]
            })

        ranked = sorted(distances, key=lambda x: x["similarity"], reverse=True)
        top_k = ranked[:3]

        game_adjacency_list = []
        neighbor_names = [n["label"] for n in top_k]

        all_neighbor_games = set()
        for n in top_k:
            all_neighbor_games.update(n["data"].keys())

        for g_name in all_neighbor_games:

            total_n1 = sum(top_k[0]["data"].values()) if len(top_k) > 0 else 1
            total_n2 = sum(top_k[1]["data"].values()) if len(top_k) > 1 else 1
            total_n3 = sum(top_k[2]["data"].values()) if len(top_k) > 2 else 1

            coords = {
                "x": (top_k[0]["data"].get(g_name, 0) / total_n1) * 100,
                "y": (top_k[1]["data"].get(g_name, 0) / total_n2) * 100,
                "z": (top_k[2]["data"].get(g_name, 0) / total_n3) * 100
            }
            owners = [p["label"] for p in player_profiles if g_name.lower().strip() in {k.lower().strip() for k in p["gameData"].keys()}]

            active_neighbors = [n["label"] for n in top_k if g_name.lower().strip() in {k.lower().strip() for k in n["data"].keys()}]

            game_adjacency_list.append({
                "name": g_name,
                "coords": coords,
                "owned": g_name.lower().strip() in user_games_normalized,
                "group": active_neighbors[0] if active_neighbors else "None",
                "all_owners": ", ".join(owners) 
            })

            pulls = [coords["x"], coords["y"], coords["z"]]
            max_pull_index = pulls.index(max(pulls))
            primary_neighbor = neighbor_names[max_pull_index]

            strength = max(coords["x"], coords["y"], coords["z"])

            game_adjacency_list.append({
                "name": g_name,
                "coords": coords,
                "owned": g_name.lower().strip() in user_games_normalized,
                "group": primary_neighbor, 
                "all_owners": ", ".join(owners), 
                "strength": strength
            })

        results = {}

        for rank, neighbor in enumerate(top_k):
            weight = 1 - (rank * 0.2)

            game_data = neighbor["data"]
            total_neighbor = sum(game_data.values())

            for title, hours in game_data.items():
                name_key = title.lower().strip()

                if name_key not in user_games_normalized:

                    neighbor_relevance = (hours / total_neighbor) * 10

                    final_score = neighbor_relevance * weight

                    if name_key not in results: 
                        results[name_key] = {
                            "name": title,
                            "score": 0,
                            "contributions": {}
                        }      
                    results[name_key]["score"] += final_score
                    results[name_key]["contributions"][neighbor["label"]] = final_score

        final = sorted(results.values(), key=lambda x: x["score"], reverse=True)

        for item in final:
            total = sum(item["contributions"].values())

            if total > 0:
                for k in item["contributions"]:
                    item["contributions"][k] /= total

            for k in item["contributions"]:
                item["contributions"][k] = round(item["contributions"][k], 2)

            item["score"] = round(item["score"], 2)

        print(json.dumps({"recommendations": final, "similarities": ranked, "game_adjacency": game_adjacency_list, "neighbors": neighbor_names}))

    except Exception as e:
        print(json.dumps({"error": f"KNN Engine Error: {str(e)}"}))



def KNN2(app_data):
    try:
        import json
        import math

        with open('gameCache.json', 'r', encoding='utf-8') as f:
            cache = json.load(f)

        user_games = app_data.get('Merged', {}).get('games', [])
        user_profile = {"genres": {}, "tags": {}}

        user_games_normalized = {n["name"].lower().strip() for n in user_games}
        user_games_dict = {n["name"].lower().strip(): float(n.get("hours", 0)) for n in user_games}

        # Build user profile (genres + tags)
        for name, hours in user_games_dict.items():
            if name in cache:
                data = cache[name]

                for g in data.get("genres", []):
                    user_profile["genres"][g] = user_profile["genres"].get(g, 0) + hours

                for t in data.get("tags", []):
                    user_profile["tags"][t] = user_profile["tags"].get(t, 0) + (hours * 0.5)

        player_profiles = [
            {"label": "FPS", "gameData": {"halo reach": 80, "counter-strike 2": 150, "apex legends": 120, "valorant": 90}},
            {"label": "Cozy", "gameData": {"stardew valley": 150, "animal crossing": 100, "unpacked": 40, "slime rancher": 60}},
            {"label": "Roguelike", "gameData": {"hades": 120, "slay the spire": 100, "dead cells": 90, "balatro": 80}},
            {"label": "Soulslike", "gameData": {"elden ring": 200, "dark souls iii": 100, "sekiro: shadows die twice": 80, "lies of p": 70}},
            {"label": "RPG", "gameData": {"baldurs gate 3": 180, "the witcher 3": 150, "cyberpunk 2077": 100, "starfield": 60}},
            {"label": "RTS", "gameData": {"age of empires ii": 150, "starcraft ii": 120, "manor lords": 80, "civilization vi": 110}},
            {"label": "Racing", "gameData": {"forza horizon 5": 100, "gran turismo 7": 120, "f1 24": 90, "assetto corsa": 70}},
            {"label": "Sports", "gameData": {"fc 25": 200, "nba 2k25": 150, "madden nfl 25": 80, "rocket league": 120}},
            {"label": "Horror", "gameData": {"resident evil 4": 60, "silent hill 2": 50, "phasmophobia": 100, "dead by daylight": 150}},
            {"label": "Survival/Sandbox", "gameData": {"minecraft": 200, "rust": 150, "ark survival ascended": 120, "terraria": 100}},
            {"label": "Immersive Sim", "gameData": {"deus ex": 80, "dishonored 2": 70, "prey": 90, "hitman 3": 110}}
        ]

        total_games_list = set(user_games_normalized)

        for p in player_profiles:
            total_games_list.update(p["gameData"].keys())

        total_games_list = sorted(list(total_games_list))

        vector = []
        total = sum(user_games_dict.values())

        for t in total_games_list:
            game_hours = user_games_dict.get(t, 0) / total if total > 0 else 0
            vector.append(game_hours)

        distances = []

        for p in player_profiles:
            total_p = sum(p["gameData"].values())

            vec = []
            for t in total_games_list:
                value = p["gameData"].get(t, 0) / total_p if total_p > 0 else 0
                vec.append(value)

            dist = math.sqrt(sum((vector[i] - vec[i]) ** 2 for i in range(len(total_games_list))))

            distances.append({
                "label": p["label"],
                "distance": dist,
                "data": p["gameData"]
            })

        ranked = sorted(distances, key=lambda x: x["distance"])
        top_k = ranked[:3]

        results = {}

        for rank, neighbor in enumerate(top_k):
            weight = 1 - (rank * 0.2)

            game_data = neighbor["data"]
            total_neighbor = sum(game_data.values())

            for title, hours in game_data.items():
                name_key = title.lower().strip()

                if name_key not in user_games_normalized:

                    # Taste score (same as before but scaled)
                    neighbor_relevance = (hours / total_neighbor) * 10

                    # Get cache data
                    game_info = cache.get(name_key, {})

                    # Quality score
                    quality = game_info.get("metacritic", 70) / 10

                    # Genre bonus
                    genre_bonus = 0
                    for g in game_info.get("genres", []):
                        if g in user_profile["genres"]:
                            genre_bonus += 1.0

                    # Final weighted score
                    w1, w2, w3 = 0.6, 0.2, 0.2
                    base_score = (neighbor_relevance * w1) + (quality * w2) + (min(genre_bonus, 2) * w3)
                    final_score = base_score * weight

                    if name_key in results:
                        results[name_key]["score"] += final_score
                    else:
                        results[name_key] = {
                            "name": title,
                            "score": final_score
                        }

        final = sorted(results.values(), key=lambda x: x["score"], reverse=True)

        for item in final:
            item["score"] = round(item["score"], 2)

        print(json.dumps(final[:10]))

    except Exception as e:
        print(json.dumps({"error": f"KNN Engine Error: {str(e)}"}))

if __name__ == "__main__":
    try:
        input_raw = sys.stdin.read()
        if not input_raw:
            sys.exit(0) 

        app_data = json.loads(input_raw)
        # l;oad in the cache here asw

        algorithm_choice = app_data.get('algorithmType', 'Linear')

        if algorithm_choice == 'KNN':
            KNN(app_data)
        elif algorithm_choice == "KNN2":
            KNN2(app_data)
        else:
            main(app_data)

    except Exception as e:
        print(json.dumps({"error": f"Gatekeeper error: {str(e)}"}))

