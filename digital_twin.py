import requests, pt_hl, time, pandas, os
from dotenv import load_dotenv

load_dotenv()
player_id = str(os.getenv("PLAYER_ID"))
auth_bearer = str(os.getenv("AUTHORIZATION_BEARER"))

id_latest_record_pt = 0
id_latest_record_hl = 0
id_latest_record_trivia = 0
date_latest_record_sugarvita = 0 # TODO: SEE IF IT MAKES SENSE TO ONLY HAVE 1 DATE
date_latest_record_trivia = 0

def get_digital_twin(player_id, auth_bearer, 
                     endpoint_pt="https://api3-new.gamebus.eu/v2/players/{}/activities?gds=SUGARVITA_PLAYTHROUGH",
                     endpoint_hl="https://api3-new.gamebus.eu/v2/players/{}/activities?gds=SUGARVITA_ENGAGEMENT_LOG_1", 
                     endpoint_trivia="https://api3-new.gamebus.eu/v2/players/{}/activities?gds=ANSWER_TRIVIA_DIABETES",
                     metrics_overview_pt_sugarvita=None,
                     metrics_overview_hl_sugarvita=None,
                     metrics_overview_hl_trivia=None):
    # secrets_path = "secrets.csv"
    # df = pandas.read_csv(secrets_path)
    # secrets = df.to_numpy()

    endpoint_pt=endpoint_pt.format(player_id)
    endpoint_hl=endpoint_hl.format(player_id)
    endpoint_trivia=endpoint_trivia.format(player_id)

    payload = {}
    headers = {"Authorization": "Bearer {}".format(auth_bearer)}

    response_pt = requests.request(
        "GET", endpoint_pt, headers=headers, data=payload
    )

    response_hl = requests.request(
        "GET", endpoint_hl, headers=headers, data=payload
    )
    response_trivia = requests.request(
        "GET", endpoint_trivia, headers=headers, data=payload
    )

    parsed_metrics_from_sugarvita , parsed_last= pt_hl.parse_json_sugarvita(
        response_pt, response_hl, id_latest_record_pt, id_latest_record_hl
    )
    parsed_metrics_from_trivia = pt_hl.parse_json_trivia(
       response_trivia, id_latest_record_trivia
    )

    # parsed_metrics=pt_hl.parse_json_try(response)
    parsed_metrics_cleaned = pt_hl.remove_nan(parsed_metrics_from_sugarvita) #ONLY NEEDED FOR THE DATA THAT COMES FROM SUGARVITA

    if metrics_overview_pt_sugarvita==None and metrics_overview_hl_sugarvita==None and metrics_overview_hl_trivia==None:
        (
            metrics_overview_pt_sugarvita,
            metrics_overview_hl_sugarvita,
        ) = pt_hl.manipulate_initial_metrics_sugarvita(parsed_metrics_cleaned)
        (metrics_overview_hl_trivia
        ) = pt_hl.manipulate_initial_metrics_trivia(parsed_metrics_from_trivia)
    else:
        (
            metrics_overview_pt_sugarvita_new_data,
            metrics_overview_hl_sugarvita_new_data,
        ) = pt_hl.manipulate_initial_metrics_sugarvita(parsed_metrics_cleaned)
        (
            metrics_overview_hl_trivia_new_data
        ) = pt_hl.manipulate_initial_metrics_trivia(parsed_metrics_from_trivia)

        metrics_overview_pt_sugarvita = pt_hl.update_metrics_overview(metrics_overview_pt_sugarvita, metrics_overview_pt_sugarvita_new_data)
        metrics_overview_hl_sugarvita = pt_hl.update_metrics_overview(metrics_overview_hl_sugarvita, metrics_overview_hl_sugarvita_new_data)
        metrics_overview_hl_trivia = pt_hl.update_metrics_overview(metrics_overview_hl_trivia, metrics_overview_hl_trivia_new_data)
    
    #print(metrics_overview_pt_sugarvita)
    #print(type(metrics_overview_pt_sugarvita))

    metrics_overview_pt_sugarvita_normalized = pt_hl.normalize_metrics(
        metrics_overview_pt_sugarvita
    )
    metrics_overview_hl_sugarvita_normalized = pt_hl.normalize_metrics(
        metrics_overview_hl_sugarvita
    )
    metrics_overview_hl_trivia_normalized = pt_hl.normalize_metrics(
        metrics_overview_hl_trivia
    )
    # print(metrics_overview_normalized)
    player_types_labels = pt_hl.get_player_types(
        metrics_overview_pt_sugarvita_normalized
    )
    health_literacy_score_sugarvita = pt_hl.get_health_literacy_score_sugarvita(
        metrics_overview_hl_sugarvita_normalized
    )
    health_literacy_score_trivia = pt_hl.get_health_literacy_score_trivia(
        metrics_overview_hl_trivia_normalized
    )
    health_literacy_score = pt_hl.get_health_literacy_score_final(
        health_literacy_score_sugarvita, health_literacy_score_trivia
    )
    print(health_literacy_score_sugarvita)
    print(health_literacy_score_trivia)
    print(health_literacy_score)


    return player_types_labels, response_pt, response_hl, response_trivia, metrics_overview_pt_sugarvita, metrics_overview_hl_sugarvita, metrics_overview_hl_trivia



if __name__ == "__main__":
    # secrets_path = "secrets.csv"
    # df = pandas.read_csv(secrets_path)
    # secrets = df.to_numpy()

    payload = {}
    headers = {"Authorization": "Bearer {}".format(auth_bearer)}
    while True:
        if (
            id_latest_record_pt == 0
            and id_latest_record_hl == 0
            and id_latest_record_trivia == 0
            and date_latest_record_sugarvita == 0
            and date_latest_record_trivia == 0
        ):
            player_types_labels, response_pt, response_hl, response_trivia, metrics_overview_pt_sugarvita, metrics_overview_hl_sugarvita, metrics_overview_hl_trivia = get_digital_twin(player_id, auth_bearer)
            (
                id_latest_record_pt,
                id_latest_record_hl,
                id_latest_record_trivia,
                date_latest_record_sugarvita,
                date_latest_record_trivia
            ) = pt_hl.save_id_date_latest_record(response_pt, response_hl, response_trivia)

            print(player_types_labels)
            #print(health_literacy_score)
            time.sleep(
                1 * 60
            )  # 10*60 seconds --> 10 minutes --> it needs to be represented in seconds

        else:
            endpoint_filtered_pt = (
                "https://api3-new.gamebus.eu/v2/players/{}/activities?start="
                + str(date_latest_record_sugarvita)
                + "&gds=SUGARVITA_PLAYTHROUGH"
            )
            endpoint_pt=endpoint_filtered_pt.format(player_id)
            endpoint_filtered_hl = (
                "https://api3-new.gamebus.eu/v2/players/{}/activities?start="
                + str(date_latest_record_sugarvita)
                + "&gds=SUGARVITA_ENGAGEMENT_LOG_1"
            )
            endpoint_hl=endpoint_filtered_hl.format(player_id)
            endpoint_filtered_trivia = (
                "https://api3-new.gamebus.eu/v2/players/{}/activities?start="
                + str(date_latest_record_trivia)
                + "&gds=ANSWER_TRIVIA_DIABETES"
            )
            endpoint_trivia=endpoint_filtered_trivia.format(player_id)
            
            response_pt = requests.request(
                "GET", endpoint_pt, headers=headers, data=payload
            )
            response_hl = requests.request(
                "GET", endpoint_hl, headers=headers, data=payload
            )
            response_trivia = requests.request(
                "GET", endpoint_trivia, headers=headers, data=payload
            )

            (
                id_new_latest_pt,
                id_new_latest_hl,
                id_new_latest_trivia,
                date_new_latest_record_sugarvita,
                date_new_latest_record_trivia
            ) = pt_hl.save_id_date_latest_record(response_pt, response_hl, response_trivia)

            if (
                id_latest_record_pt != id_new_latest_pt
                and id_latest_record_hl != id_new_latest_hl
                ##and id_latest_record_trivia != id_new_latest_trivia
            ):  # if the id saved is different from the id of the latest record, then we have new data
                
                player_types_labels, health_literacy_score, response_pt, response_hl, metrics_overview_pt_sugarvita, metrics_overview_hl_sugarvita, metrics_overview_hl_trivia = get_digital_twin(player_id, auth_bearer,
                             endpoint_pt = endpoint_filtered_pt,  # endpoint pt filtered by date
                             endpoint_hl = endpoint_filtered_hl, # endpoint hl filtered by date
                             ##endpoint_trivia = endpoint_filtered_trivia, # endpoint trivia filtered by date
                             metrics_overview_pt_sugarvita = metrics_overview_pt_sugarvita,
                             metrics_overview_hl_sugarvita = metrics_overview_hl_sugarvita,
                             metrics_overview_hl_trivia = metrics_overview_hl_trivia) 
                print(player_types_labels)
                #print(health_literacy_score)
                id_latest_record_pt = id_new_latest_pt  # save the new id of the last record (will for sure change)
                id_latest_record_hl = id_new_latest_hl
                date_latest_record_sugarvita = date_new_latest_record_sugarvita
                date_latest_record_trivia = date_new_latest_record_trivia
            else:
                print("No new records")
                time.sleep(
                    1 * 60
                )  # 10*60 seconds --> 10 minutes --> it needs to be represented in seconds
                # break        