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
            {"name": "Elden Ring", "genres": ["action", "rpg"], "tags": ["difficult", "open-world"], "metacritic": 96},
            {"name": "Stardew Valley", "genres": ["rpg", "simulation", "indie"], "tags": ["relaxing", "crafting"], "metacritic": 89},
            {"name": "Hades", "genres": ["action", "indie"], "tags": ["roguelike", "great-soundtrack"], "metacritic": 93}
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
            {"label": "Soulslike", "gameData": {"elden ring": 200, "dark souls iii": 100, "sekiro": 80, "lies of p": 70}},
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
            {"label": "Soulslike", "gameData": {"elden ring": 200, "dark souls iii": 100, "sekiro": 80, "lies of p": 70}},
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

