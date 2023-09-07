import json
from statistics import mean, pstdev
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime
import ast

def parse_json_trivia(
        response_trivia, id_latest_record_trivia
) -> dict:
    metrics = {
        "WITH_HINT": {"TRUE": 0, # counts the number of times questions were answered with a hint
                 "FALSE": 0}, # counts the number of times questions were answere without a hint
        "DIFFICULTY LEVEL": {"EASY": 0, # counts the number of easy questions answered 
                             "NORMAL": 0, # counts the number of normal (intermediate) questions answered
                             "HARD": 0}, # counts the number of hard questions answered
        "NO_HINT_TYPE_OF_ANSwER": {"CORRECT": 0, # of the questions answered with no hint (since the ones with the hint are always correct) we count the ones that were answered correctly
                                   "INCORRECT": 0} # of the questions answered with no hint (since the ones with the hint are always correct) we count the ones that were answered incorrectly
    }

    parsed_response_trivia = json.loads(response_trivia.text)

    for record in parsed_response_trivia:
        if record["id"] > id_latest_record_trivia:
            for element in record["propertyInstances"]:
                try:
                    if element["property"]["translationKey"] == "THROUGH_HINT":
                        metrics["WITH_HINT"]["TRUE"]+=1
                except Exception as e:
                    print("!", e, "\n")
                    


    return metrics

def parse_json_sugarvita(
    response_pt, response_hl, id_latest_record_pt, id_latest_record_hl, 
) -> dict:
    metrics_per_session = {
        "SCORES": [],  # each position of the list will represent the score achieved after a playthrough
        "PLAYTIMES": [],  # each position of the list will represent how long a session took
        "DAYS_PLAYED": [],  # each position of the list will represent the amount of simulated days the player decided to select for the session
        "HOME_PATH": [],  # each position of the list will represent the amount of times a player chose a Home Path Type during a session
        "WORK_PATH": [],  # each position of the list will represent the amount of times a player chose a Home Path Type during a session
        "OUTDOORS_PATH": [],  # each position of the list will represent the amount of times a player chose a Home Path Type during a session
        "GLUCOSE_ACCURACY": [],  # each position of the list will represent the final percentage the player was able to keep the glucose levels within a good range
        "GLUCOSE_LEVELS": [],  # each position of the list will be a list with the different levels of glucose in a session
        "SCORE_VARIATION": [],  # each position of the list will be a list with the different scores during a playthrough
        "TOTAL_TRIPS_HOSPITAL": [],  # each position of the list will represent the amount of times a player has landed on the hospital part of the board
        "GLUCOSE_CRITICAL_VALUE_RESPONSE": [],  # each position  of the list will be a list with the different scores during a playthrough
        "TURN_TIME": [],  # each position of the list will be a list with the time a turn took during a playthrough
    }

    parsed_response_pt = json.loads(response_pt.text)
    parsed_response_hl = json.loads(response_hl.text)
    # print(parsed_response_hl[-1]) #last record

    for record in parsed_response_pt:
        if record["id"] > id_latest_record_pt: 
            for element in record["propertyInstances"]:
                try:
                    if element["property"]["translationKey"] == "SCORE":
                        metrics_per_session["SCORES"].append(int(element["value"]))
                except:
                    metrics_per_session["SCORES"].append("NaN")

                try:
                    if element["property"]["translationKey"] == "PLAYTIME":
                        metrics_per_session["PLAYTIMES"].append(int(element["value"]))
                except:
                    metrics_per_session["PLAYTIMES"].append("NaN")

                try:
                    if (
                        element["property"]["translationKey"]
                        == "GLUCOSE_RANGE_PERCENTAGE"
                    ):
                        metrics_per_session["GLUCOSE_ACCURACY"].append(
                            int(element["value"])
                        )
                except:
                    continue  # not all records will have the glucose_range_percentage as this property was recently created

                try:
                    if element["property"]["translationKey"] == "PLAYTHROUGH_DATA":
                        playthrough_data = element["value"]
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

    for record in parsed_response_hl:
        current_score = []
        glucose_values_each_turn = []
        turn_time = []
        is_hospitalised = 0
        if record["id"] > id_latest_record_hl:
            for element in record["propertyInstances"]:
                try:
                    if element["property"]["translationKey"] == "ENGAGEMENT_DATA":
                        engagement_data = element["value"]
                        engagement_data = json.loads(engagement_data)
                        try:
                            if (
                                engagement_data["GameplayData"] is not None
                                and engagement_data["GameplayData"] != []
                            ):  # if len(engagement_data["Gameplay"]>1) --> there are more than 1 players!
                                # print(len(engagement_data["GameplayData"]), "\n")

                                for gameplaydata in engagement_data["GameplayData"]:
                                    gameplaydata_values = gameplaydata["Values"][
                                        0
                                    ]  # gameplaydata --> ['{...}'] --> we want to have the string to later use json loads and get the dictionary structure
                                    gameplaydata_dict = json.loads(gameplaydata_values)
                                    if (
                                        gameplaydata_dict["aborted"] == False
                                        and gameplaydata_dict["playerNr"] == 1
                                    ):  # TODO: WE ARE ASSUMING THAT OUR PLAYER IS ALWAYS THE NR.1, EVEN WHEN THERE'S MORE PLAYERS PLAYING!
                                        for turn in gameplaydata_dict["turns"]:
                                            if (
                                                turn["CurrentScore"] != 0
                                            ):  # at the end of a session, the last value of score is 0. It does not bring value to us, so we'll ignore it!
                                                current_score.append(
                                                    turn["CurrentScore"]
                                                )
                                            if turn["IsHospitalised"] == True:
                                                is_hospitalised += 1
                                            if (
                                                glucose_values_each_turn == []
                                                and turn_time == []
                                            ):
                                                glucose_values_each_turn.append(
                                                    turn["GlucoseValueStart"]
                                                )
                                                if (
                                                    turn["GlucoseValueEnd"] != 0.0
                                                ):  # at the end of a session, the last value of glucose is 0.0. It does not bring value to us, so we'll ignore it!
                                                    glucose_values_each_turn.append(
                                                        turn["GlucoseValueEnd"]
                                                    )
                                                turn_time.append(turn["MinutesStart"])
                                                if (
                                                    turn["MinutesEnd"] != 0
                                                ):  # at the end of a session, the last value of minutes is 0. It does not bring value to us, so we'll ignore it!
                                                    turn_time.append(turn["MinutesEnd"])
                                            else:
                                                glucose_values_each_turn.append(
                                                    turn["GlucoseValueEnd"]
                                                )
                                                turn_time.append(turn["MinutesEnd"])
                                if (
                                    is_hospitalised != []
                                    and current_score != []
                                    and turn_time != []
                                    and glucose_values_each_turn != []
                                ):
                                    if current_score[-1] == 0:
                                        metrics_per_session["SCORE_VARIATION"].append(
                                            current_score[:-1]
                                        )
                                    else:
                                        metrics_per_session["SCORE_VARIATION"].append(
                                            current_score
                                        )
                                    if turn_time[-1] == 0:
                                        metrics_per_session["TURN_TIME"].append(
                                            turn_time[:-1]
                                        )
                                    else:
                                        metrics_per_session["TURN_TIME"].append(
                                            turn_time
                                        )
                                    if glucose_values_each_turn[-1] == 0:
                                        metrics_per_session["GLUCOSE_LEVELS"].append(
                                            glucose_values_each_turn[:-1]
                                        )
                                    else:
                                        metrics_per_session["GLUCOSE_LEVELS"].append(
                                            glucose_values_each_turn
                                        )
                                    metrics_per_session["TOTAL_TRIPS_HOSPITAL"].append(
                                        is_hospitalised
                                    )

                        except Exception as e:
                            print("!", e, "\n")

                except Exception as e:
                    print("!", e, "\n")

    metrics_per_session[
        "GLUCOSE_CRITICAL_VALUE_RESPONSE"
    ] = get_glucose_critical_value_response(
        metrics_per_session["GLUCOSE_LEVELS"], metrics_per_session["TURN_TIME"]
    )

    return metrics_per_session


def get_glucose_critical_value_response(glucose_levels, times):
    glucose_critical_value_response = []
    # red=0

    values_to_calculate_critical_value_response = {
        "red_glucose_value": -1,
        "closest_green_glucose_value": -1,
        "time_red": -1,
        "time_closest_green": -1,
    }

    blood_glucose_colored_regions = (
        {  # we will follow the colored labels that "Do not use insulin"
            "red": [(0, 2.6), (15, 20)],
            "light_red": [(2.6, 3.3), (11, 15)],
            "yellow": [(3.3, 4.5), (8, 11)],
            "green": [(4.5, 8)],
        }
    )
    for glucose_playthrough, times_playthrough in zip(glucose_levels, times):
        for glucose_value, time in zip(glucose_playthrough, times_playthrough):
            for color, ranges in blood_glucose_colored_regions.items():
                for min_range, max_range in ranges:
                    if min_range <= glucose_value <= max_range:
                        if (
                            color == "red"
                            and values_to_calculate_critical_value_response[
                                "red_glucose_value"
                            ]
                            == -1
                        ):  # no red value
                            # red+=1
                            values_to_calculate_critical_value_response[
                                "red_glucose_value"
                            ] = glucose_value
                            values_to_calculate_critical_value_response[
                                "time_red"
                            ] = time

                        elif (
                            color == "red"
                            and values_to_calculate_critical_value_response[
                                "red_glucose_value"
                            ]
                            != -1
                        ):  # if there was already a red value, but now there's another one, we choose the worst one
                            # red+=1
                            if (
                                values_to_calculate_critical_value_response[
                                    "closest_green_glucose_value"
                                ]
                                != -1
                            ):  # if there's a new red value, but the previous critical response has not been calculated, it needs to be calculated
                                glucose_critical_value_response.append(
                                    calculate_glucose_critical_value_response(
                                        values_to_calculate_critical_value_response
                                    )
                                )
                                values_to_calculate_critical_value_response = (
                                    reset_dictionary_values(
                                        values_to_calculate_critical_value_response
                                    )
                                )
                                values_to_calculate_critical_value_response[
                                    "red_glucose_value"
                                ] = glucose_value  # set new values for red
                                values_to_calculate_critical_value_response[
                                    "time_red"
                                ] = time  # set new values for red

                            # in case there's a new red value but no closes_green_glucose_value, we need to check the worst red value and consider it (in both ranges!)
                            elif (
                                values_to_calculate_critical_value_response[
                                    "red_glucose_value"
                                ]
                                >= 15
                                and values_to_calculate_critical_value_response[
                                    "red_glucose_value"
                                ]
                                < glucose_value
                            ):
                                values_to_calculate_critical_value_response[
                                    "red_glucose_value"
                                ] = glucose_value
                                values_to_calculate_critical_value_response[
                                    "time_red"
                                ] = time

                            elif (
                                values_to_calculate_critical_value_response[
                                    "red_glucose_value"
                                ]
                                <= 2.6
                                and values_to_calculate_critical_value_response[
                                    "red_glucose_value"
                                ]
                                > glucose_value
                            ):
                                values_to_calculate_critical_value_response[
                                    "red_glucose_value"
                                ] = glucose_value
                                values_to_calculate_critical_value_response[
                                    "time_red"
                                ] = time

                        elif (
                            color == "green"
                            and values_to_calculate_critical_value_response[
                                "red_glucose_value"
                            ]
                            != -1
                        ):
                            values_to_calculate_critical_value_response[
                                "closest_green_glucose_value"
                            ] = glucose_value
                            values_to_calculate_critical_value_response[
                                "time_closest_green"
                            ] = time
                            glucose_critical_value_response.append(
                                calculate_glucose_critical_value_response(
                                    values_to_calculate_critical_value_response
                                )
                            )
                            values_to_calculate_critical_value_response = (
                                reset_dictionary_values(
                                    values_to_calculate_critical_value_response
                                )
                            )

                        elif (
                            color != "red"
                            and color != "green"
                            and values_to_calculate_critical_value_response[
                                "red_glucose_value"
                            ]
                            != -1
                        ):
                            if (
                                values_to_calculate_critical_value_response[
                                    "closest_green_glucose_value"
                                ]
                                == -1
                            ):  # if there's no value closest to green section, we just add it
                                values_to_calculate_critical_value_response[
                                    "closest_green_glucose_value"
                                ] = glucose_value
                                values_to_calculate_critical_value_response[
                                    "time_closest_green"
                                ] = time
                            elif (
                                abs(
                                    values_to_calculate_critical_value_response[
                                        "closest_green_glucose_value"
                                    ]
                                    - values_to_calculate_critical_value_response[
                                        "red_glucose_value"
                                    ]
                                )
                            ) > (
                                abs(
                                    glucose_value
                                    - values_to_calculate_critical_value_response[
                                        "red_glucose_value"
                                    ]
                                )
                            ):
                                # if the new value of glucose is closest to the green region, we have to update the values in the dictionary
                                values_to_calculate_critical_value_response[
                                    "closest_green_glucose_value"
                                ] = glucose_value
                                values_to_calculate_critical_value_response[
                                    "time_closest_green"
                                ] = time

        # at the end of a playthrough, even if the player did not reach the green area after being in the red region, the critical value response must be calculated
        if (
            values_to_calculate_critical_value_response["red_glucose_value"] != -1
            and values_to_calculate_critical_value_response[
                "closest_green_glucose_value"
            ]
            != -1
        ):
            glucose_critical_value_response.append(
                calculate_glucose_critical_value_response(
                    values_to_calculate_critical_value_response
                )
            )

        # reset values of our dictionary at the end of every analysed playthrough
        values_to_calculate_critical_value_response = reset_dictionary_values(
            values_to_calculate_critical_value_response
        )

    # print(red)
    return glucose_critical_value_response


def calculate_glucose_critical_value_response(glucose_and_times) -> float:
    glucose_critical_value_response = abs(
        (
            (
                glucose_and_times["closest_green_glucose_value"]
                - glucose_and_times["red_glucose_value"]
            )
            / (glucose_and_times["time_closest_green"] - glucose_and_times["time_red"])
        )
    )

    return glucose_critical_value_response


def reset_dictionary_values(some_dict) -> dict:
    for (
        key
    ) in (
        some_dict
    ):  # reset values of our dictionary at the end of every analysed playthrough
        some_dict[key] = -1

    return some_dict


def save_id_date_latest_record(response_pt, response_hl):
    parsed_response_pt = json.loads(response_pt.text)
    parsed_response_hl = json.loads(response_hl.text)
    ##parsed_response_trivia = json.loads(response_trivia.text)
    id_latest_record_pt = parsed_response_pt[-1]["id"]
    id_latest_record_hl = parsed_response_hl[-1]["id"]
    ##id_latest_record_trivia = parsed_response_trivia[-1]["id"]
    date_latest_record_miliseconds = parsed_response_pt[-1][
        "date"
    ]  # date in miliseconds; we want it in the format "dd-mm-yyyy"
    date_latest_record_object = datetime.fromtimestamp(
        date_latest_record_miliseconds / 1000
    )  # create a datetime object from the timestamp
    date_latest_record = date_latest_record_object.strftime(
        "%d-%m-%y"
    )  # format the datetime object into "dd-mm-yy"

    return id_latest_record_pt, id_latest_record_hl, date_latest_record


def remove_nan(metrics) -> list:
    # using list comprehension to perform the task
    for key, value in metrics.items():
        value_cleaned = [i for i in value if i != "NaN"]
        metrics[key] = value_cleaned
    return metrics


def manipulate_initial_metrics(metrics_cleaned) -> dict:
    metrics_overview_pt = {
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

    metrics_overview_hl = {
        "avg_glucose_critical_value_response": 0,  # average variation to get back to the green region (or the closes to the green region)
        "trips_to_hospital_per_game": 0,  # total trips to hospital / total number of games
        "avg_glucose_accuracy": 0,
    }

    for key, value in metrics_cleaned.items():
        # PLAYER TYPES METRICS
        if key == "SCORES":
            metrics_overview_pt["avg_score"] = round(mean(value), 2)
            metrics_overview_pt["sd_score"] = round(pstdev(value), 2)
        elif key == "PLAYTIMES":
            metrics_overview_pt["avg_playtimes"] = round(mean(value), 2)
            metrics_overview_pt["sd_playtimes"] = round(pstdev(value), 2)
        elif key == "DAYS_PLAYED":
            metrics_overview_pt["avg_days_session"] = round(mean(value), 2)
            metrics_overview_pt["sd_days_session"] = round(pstdev(value), 2)
            for days in value:
                if days == 1:
                    metrics_overview_pt["1_day_session"] += 1
                elif days == 2:
                    metrics_overview_pt["2_days_session"] += 1
                elif days == 3:
                    metrics_overview_pt["3_days_session"] += 1
        elif key == "HOME_PATH":
            metrics_overview_pt["total_home_path"] = sum(value)
        elif key == "WORK_PATH":
            metrics_overview_pt["total_work_path"] = sum(value)
        elif key == "OUTDOORS_PATH":
            metrics_overview_pt["total_outdoors_path"] = sum(value)

        # HEALTH LITERACY METRICS
        elif key == "GLUCOSE_ACCURACY":
            metrics_overview_hl["avg_glucose_accuracy"] = round(mean(value), 2)
        elif key == "TOTAL_TRIPS_HOSPITAL":
            metrics_overview_hl["trips_to_hospital_per_game"] = sum(value) / len(value)
        elif key == "GLUCOSE_CRITICAL_VALUE_RESPONSE":
            metrics_overview_hl["avg_glucose_critical_value_response"] = round(
                mean(value), 2
            )

    return metrics_overview_pt, metrics_overview_hl


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


def calculate_score(
    weights, metrics_normalized
):  # for player types and health literacy level
    score = 0
    for key, value in weights.items():
        score += value * metrics_normalized[key]
    return score


def get_health_literacy_score(metrics_overview_hl_normalized) -> float:
    health_literacy_metrics_weights = {
        "avg_glucose_critical_value_response": 0.15,
        "trips_to_hospital_per_game": 0.35,
        "avg_glucose_accuracy": 0.5,
        #"easy_level":0.1
        #"normal_level":0.2
        #"difficult_level":0.3
        #"use_hint":0.15
        #"correct":0.3
        
        
        #"incorrect":0.15
    }

    health_literacy_score = calculate_score(
        health_literacy_metrics_weights, metrics_overview_hl_normalized
    )

    health_literacy_score_dict={'Health Literacy': health_literacy_score}

    return health_literacy_score_dict


def get_player_types(metrics_overview_pt_normalized) -> dict:
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
        "Socializer": calculate_score(
            socializer_weights, metrics_overview_pt_normalized
        ),
        "Competitive": calculate_score(
            competitive_weights, metrics_overview_pt_normalized
        ),
        "Explorer": calculate_score(explorer_weights, metrics_overview_pt_normalized),
    }

    return player_types_scores


def update_metrics_overview(initial_metrics, new_metrics) -> dict:
    updated_metrics = {}
    for key in initial_metrics:
        average_value = (initial_metrics[key] + new_metrics[key]) / 2
        updated_metrics[key] = average_value

    return updated_metrics
