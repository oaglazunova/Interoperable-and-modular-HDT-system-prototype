import json
from statistics import mean, pstdev
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime


def parse_json(response, id_latest_record) -> dict:
    metrics_per_session = {
        "SCORES": [],  # each position of the list will represent the score achieved after a playthrough
        "PLAYTIMES": [],  # each position of the list will represent how long a session took
        "DAYS_PLAYED": [],  # each position of the list will represent the amount of simulated days the player decided to select for the session
        "HOME_PATH": [],  # each position of the list will represent the amount of times a player chose a Home Path Type during a session
        "WORK_PATH": [],  # each position of the list will represent the amount of times a player chose a Home Path Type during a session
        "OUTDOORS_PATH": [],  # each position of the list will represent the amount of times a player chose a Home Path Type during a session
    }

    parsed_response = json.loads(response.text)
    # print(parsed_response[-1]) #last record

    for record in parsed_response:
        if (record["id"] > id_latest_record):
            try:
                metrics_per_session["SCORES"].append(
                    int(record["propertyInstances"][0]["value"])
                )
            except:
                metrics_per_session["SCORES"].append("NaN")

            try:
                metrics_per_session["PLAYTIMES"].append(
                    int(record["propertyInstances"][1]["value"])
                )
            except:
                metrics_per_session["PLAYTIMES"].append("NaN")

            try:
                playthrough_data = record["propertyInstances"][4]["value"]
                playthrough_data = json.loads(
                    playthrough_data
                )  # converts the "dictionary" string into a dictionary
                metrics_per_session["DAYS_PLAYED"].append(
                    playthrough_data["daysPlayed"]
                )

                home_path, outdoors_path, work_path = 0, 0, 0

                for turn in playthrough_data["turns"]:
                    if turn["DestinationPathType"] == 1:
                        home_path += 1
                    elif turn["DestinationPathType"] == 2:
                        outdoors_path += 1
                    elif turn["DestinationPathType"] == 3:
                        work_path += 1

                metrics_per_session["HOME_PATH"].append(home_path)
                metrics_per_session["WORK_PATH"].append(work_path)
                metrics_per_session["OUTDOORS_PATH"].append(outdoors_path)

            except:
                metrics_per_session["HOME_PATH"].append("NaN")
                metrics_per_session["WORK_PATH"].append("NaN")
                metrics_per_session["OUTDOORS_PATH"].append("NaN")
                metrics_per_session["DAYS_PLAYED"].append("NaN")

    return metrics_per_session


def save_id_date_latest_record(response):
    parsed_response = json.loads(response.text)
    id_latest_record = parsed_response[-1]["id"]
    date_latest_record_miliseconds = parsed_response[-1][
        "date"
    ]  # date in miliseconds; we want it in the format "dd-mm-yyyy"
    date_latest_record_object = datetime.fromtimestamp(
        date_latest_record_miliseconds / 1000
    )  # create a datetime object from the timestamp
    date_latest_record = date_latest_record_object.strftime(
        "%d-%m-%y"
    )  # format the datetime object into "dd-mm-yy"

    return id_latest_record, date_latest_record


def remove_nan(metrics) -> list:
    # using list comprehension to perform the task
    for key, value in metrics.items():
        value_cleaned = [i for i in value if i != "NaN"]
        metrics[key] = value_cleaned
    return metrics


def manipulate_initial_metrics(metrics_cleaned) -> dict:
    metrics_overview = {
        "avg_score": 0,  # average of the scores from all sessions played
        "sd_score": 0,  # standard deviation """
        "avg_playtimes": 0,  # average of the playtimes """
        "sd_playtimes": 0,  # standard deviation """
        "1_day_session": 0,  # total of sessions that simulated 1 day in the game
        "2_days_session": 0,  # """" 2 days """
        "3_days_session": 0,  # """ 3 days """
        "avg_days_session": 0,  # average days simulated in the game
        "sd_days_session": 0,  # standard deviation...
        "total_work_path": 0,  # total times a player as chosen a work path
        "total_home_path": 0,  # """ home path
        "total_outdoors_path": 0,  # """ outdoors path
    }

    for key, value in metrics_cleaned.items():
        if key == "SCORES":
            metrics_overview["avg_score"] = round(mean(value), 2)
            metrics_overview["sd_score"] = round(pstdev(value), 2)
        elif key == "PLAYTIMES":
            metrics_overview["avg_playtimes"] = round(mean(value), 2)
            metrics_overview["sd_playtimes"] = round(pstdev(value), 2)
        elif key == "DAYS_PLAYED":
            metrics_overview["avg_days_session"] = round(mean(value), 2)
            metrics_overview["sd_days_session"] = round(pstdev(value), 2)
            for days in value:
                if days == 1:
                    metrics_overview["1_day_session"] += 1
                elif days == 2:
                    metrics_overview["2_days_session"] += 1
                elif days == 3:
                    metrics_overview["3_days_session"] += 1
        elif key == "HOME_PATH":
            metrics_overview["total_home_path"] = sum(value)
        elif key == "WORK_PATH":
            metrics_overview["total_work_path"] = sum(value)
        elif key == "OUTDOORS_PATH":
            metrics_overview["total_outdoors_path"] = sum(value)

    return metrics_overview


def normalize_metrics(metrics_overview) -> dict:
    values = [
        [value] for value in metrics_overview.values()
    ]  # converting the values to a 2D array for the scaling
    scaler = MinMaxScaler()  # initializing the scaler
    normalized_values = scaler.fit_transform(values)  # normalization
    normalized_dict = {
        key: normalized_value[0]
        for key, normalized_value in zip(metrics_overview.keys(), normalized_values)
    }  # converting the normalized values back to a dictionary

    return normalized_dict


def calculate_score_for_player_types(player_type_weights, metrics_overview_normalized):
    score = 0
    for key, value in player_type_weights.items():
        score += value * metrics_overview_normalized[key]
    return score


def get_player_types(metrics_overview_normalized) -> dict:
    socializer_weights = {
        "avg_score": 0,
        "sd_score": 0,
        "avg_playtimes": 0,
        "sd_playtimes": 0,
        "1_day_session": 0,
        "2_days_session": 0,
        "3_days_session": 0,
        "avg_days_session": 0,
        "sd_days_session": 0,
        "total_work_path": 0.5,
        "total_home_path": 0,
        "total_outdoors_path": 0.5,
    }

    competitive_weights = {
        "avg_score": 0.3,
        "sd_score": 0.05,
        "avg_playtimes": 0,
        "sd_playtimes": 0,
        "1_day_session": 0.2,
        "2_days_session": 0.1,
        "3_days_session": 0,
        "avg_days_session": 0.1,
        "sd_days_session": 0.05,
        "total_work_path": 0.1,
        "total_home_path": 0.05,
        "total_outdoors_path": 0.05,
    }

    explorer_weights = {
        "avg_score": 0,
        "sd_score": 0,
        "avg_playtimes": 0.3,
        "sd_playtimes": 0.05,
        "1_day_session": 0,
        "2_days_session": 0.1,
        "3_days_session": 0.15,
        "avg_days_session": 0.15,
        "sd_days_session": 0.05,
        "total_work_path": 0.05,
        "total_home_path": 0.05,
        "total_outdoors_path": 0.1,
    }

    player_types_scores = {
        "Socializer": calculate_score_for_player_types(
            socializer_weights, metrics_overview_normalized
        ),
        "Competitive": calculate_score_for_player_types(
            competitive_weights, metrics_overview_normalized
        ),
        "Explorer": calculate_score_for_player_types(
            explorer_weights, metrics_overview_normalized
        ),
    }

    return player_types_scores


def update_metrics_overview(initial_metrics, new_metrics) -> dict:
    updated_metrics = {}
    for key in initial_metrics:
        average_value = (initial_metrics[key] + new_metrics[key]) / 2
        updated_metrics[key] = average_value

    return updated_metrics


"""
def get_property_value(json_loads, translation_key):
    try:
        for property in json_loads['PropertyInstances']:
            if property['property']['translationKey']== translation_key:
                try:
                    return int(property['value'])
                except:
                    return property['value']
    except:
        return 'NaN'


def parse_json_try(response) -> dict: #to not have indexes hardcoded
    metrics_per_session={
    "SCORES":[], #each position of the list will represent the score achieved after a playthrough
    "PLAYTIMES":[], #each position of the list will represent how long a session took
    "DAYS_PLAYED":[],  #each position of the list will represent the amount of simulated days the player decided to select for the session
    "HOME_PATH":[], #each position of the list will represent the amount of times a player chose a Home Path Type during a session
    "WORK_PATH":[], #each position of the list will represent the amount of times a player chose a Home Path Type during a session
    "OUTDOORS_PATH":[] #each position of the list will represent the amount of times a player chose a Home Path Type during a session
    }

    parsed_response=json.loads(response.text)
    #print(parsed_response[-1]) #last record
    
    
    for record in parsed_response:
        #print(record)
        score=get_property_value(record,'SCORE')
        print(score)
        playtime=get_property_value(record,'PLAYTIME')
        playthrough_data=get_property_value(record,'PLAYTHROUGH_DATA')
        metrics_per_session['SCORES'].append(score)
        metrics_per_session['PLAYTIMES'].append(playtime)

        try:
            playthrough_data=json.loads(playthrough_data) #converts the "dictionary" string into a dictionary
            metrics_per_session['DAYS_PLAYED'].append(playthrough_data['daysPlayed'])
            
            home_path, outdoors_path, work_path = 0, 0, 0

            for turn in playthrough_data['turns']:
                if turn['DestinationPathType'] == 1:
                    home_path+=1
                elif turn['DestinationPathType'] == 2:
                    outdoors_path+=1
                elif turn['DestinationPathType']==3:
                    work_path+=1

            metrics_per_session['HOME_PATH'].append(home_path)
            metrics_per_session['WORK_PATH'].append(work_path)
            metrics_per_session['OUTDOORS_PATH'].append(outdoors_path)
        
        except:
            metrics_per_session['HOME_PATH'].append('NaN')
            metrics_per_session['WORK_PATH'].append('NaN')
            metrics_per_session['OUTDOORS_PATH'].append('NaN')
            metrics_per_session['DAYS_PLAYED'].append('NaN')
        
        break
        
    return metrics_per_session
"""
