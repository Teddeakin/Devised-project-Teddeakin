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

        with open ('gameCache.json', 'r', encoding='utf-8') as f:
            Cache = json.load(f)

        User_games = []
        User_games_names = []
        User_games_hr= []
        
        User_games = app_data.get('Merged', {}).get('games', []) # fyi app_data.get('Merged', {}).get(games['name'], []) also works

        for games in User_games:
            User_games_names.append(games['name'])

        for games in User_games:
            User_games_hr.append(games['hours'])

        Test_users = [ # add .lower and .strip to somewhere asp
            {
                "name": "FPS",
                "gameData": {"halo: reach": 80, "counter-strike": 100, "apex legends": 200, }
            },
            {
                "name": "Cozy",
                "gameData": {"stardew valley": 100, "baldur's gate 3": 120, "slime rancher": 40, "minecraft": 123}
            } 
            # make some more 
        ]

        all_unique_games = set(User_games_names) # get rid of user games names probably

        for person in Test_users:
            for game_name in person["gameData"].keys(): # .keys only gets the names(first thing in the object)
                all_unique_games.add(game_name)

        total_game_list = sorted(list(all_unique_games))


        user_updated_list = [] # Update the user list to include the games present in other users library
        # user_lookup = {g['name']: float(g['hours']) for g in User_games}
        user_lookup = {g['name'].lower().strip(): float(g['hours']) for g in User_games}
        for game in total_game_list:
            user_updated_list.append(user_lookup.get(game, 0))
        
        Test_users_list = []
        for person in Test_users:
            vector = []
            for game in total_game_list:
                vector.append(person["gameData"].get(game, 0))
            Test_users_list.append({"name": person["name"], "vector": vector})
        
        distances = []

        for testUser in Test_users_list:
            sum_of_squares = 0

            for i in range(len(total_game_list)): # range assigns numbered list
                diff = user_updated_list[i] - testUser["vector"][i]
                sum_of_squares += diff ** 2
            
            distance = math.sqrt(sum_of_squares)
            distances.append({"name": testUser["name"], "distance": round(distance, 2)})
        
        distances = sorted(distances, key=lambda x: x['distance'])

        nearest_neighbor_name = distances[0]["name"]

        neighbor_data = next(person for person in Test_users if person["name"] == nearest_neighbor_name)

        recommendations = []

        for game_name, play_hours in neighbor_data["gameData"].items():
            # Check if the user owns this game
            if game_name.lower().strip() not in [n.lower().strip() for n in User_games_names]:
                # calculate a Recommendation Score
                recommendations.append({
                    "name": game_name,
                    "score": play_hours,
                })
        
        recommendations = sorted(recommendations, key=lambda x: x['score'], reverse=True)

        print(json.dumps(recommendations))

        # print(json.dumps(distances))
    except Exception as e:
        print(json.dumps({"error": str(e)}))



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
        else:
            main(app_data)

    except Exception as e:
        print(json.dumps({"error": f"Gatekeeper error: {str(e)}"}))

