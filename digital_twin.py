import requests, pt_hl, time, json, os, argparse
from datetime import datetime
from dotenv import load_dotenv
from log import logger
import atexit
import signal
import sys
import csv

id_latest_record_pt = 0
id_latest_record_hl = 0
id_latest_record_trivia = 0
date_latest_record_sugarvita = 0
date_latest_record_trivia = 0

def get_digital_twin(
    player_id,
    auth_bearer,
    endpoint_pt="https://api3-new.gamebus.eu/v2/players/{}/activities?gds=SUGARVITA_PLAYTHROUGH",
    endpoint_hl="https://api3-new.gamebus.eu/v2/players/{}/activities?gds=SUGARVITA_ENGAGEMENT_LOG_1",
    endpoint_trivia="https://api3-new.gamebus.eu/v2/players/{}/activities?gds=ANSWER_TRIVIA_DIABETES",
    id_latest_record_pt=0,
    id_latest_record_trivia=0,
    metrics_overview_pt_sugarvita=None,
    metrics_overview_hl_sugarvita=None,
    metrics_overview_hl_trivia=None,
    player_types_labels=None,
    health_literacy_score_sugarvita=None,
    health_literacy_score_trivia=None,
    health_literacy_score=None,
):
    # secrets_path = "secrets.csv"
    # df = pandas.read_csv(secrets_path)
    # secrets = df.to_numpy()
    payload = {}
    headers = {"Authorization": "Bearer {}".format(auth_bearer)}

    try:
        endpoint_pt = endpoint_pt.format(player_id)
        response_pt = requests.request( 
            "GET", endpoint_pt, headers=headers, data=payload
        )
        response_pt.raise_for_status() # raise exception for HTTP errors
    except requests.exceptions.RequestException as e:
        logger.error("Failed to retrieve response_pt: %s", str(e), "\n")
    
    try:
        endpoint_hl = endpoint_hl.format(player_id)
        response_hl = requests.request(
            "GET", endpoint_hl, headers=headers, data=payload
        )
        response_hl.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error("Failed to retrieve response_hl: %s", str(e), "\n")
    
    try:
        endpoint_trivia = endpoint_trivia.format(player_id)                
        response_trivia = requests.request(
            "GET", endpoint_trivia, headers=headers, data=payload
        )
        response_trivia.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error("Failed to retrieve response_trivia: %s", str(e), "\n")


    
    if id_latest_record_pt == 0 or (
        id_latest_record_pt != int((json.loads(response_pt.text))[-1]["id"])
    ):
        parsed_metrics_from_sugarvita = pt_hl.parse_json_sugarvita(
            response_pt, response_hl, id_latest_record_pt, id_latest_record_hl
        )

        parsed_metrics_cleaned = pt_hl.remove_nan(
            parsed_metrics_from_sugarvita
        )  # ONLY NEEDED FOR THE DATA THAT COMES FROM SUGARVITA


        if (
            metrics_overview_pt_sugarvita == None
            and metrics_overview_hl_sugarvita == None
        ):
            (
                metrics_overview_pt_sugarvita,
                metrics_overview_hl_sugarvita,
            ) = pt_hl.manipulate_initial_metrics_sugarvita(parsed_metrics_cleaned)

            

        else:
            # print(id_latest_record_pt,"!=",(json.loads(response_pt.text))[-1]["id"])
            (
                metrics_overview_pt_sugarvita_new_data,
                metrics_overview_hl_sugarvita_new_data,
            ) = pt_hl.manipulate_initial_metrics_sugarvita(parsed_metrics_cleaned)
            metrics_overview_pt_sugarvita = pt_hl.update_metrics_overview(
                metrics_overview_pt_sugarvita, metrics_overview_pt_sugarvita_new_data
            )
            metrics_overview_hl_sugarvita = pt_hl.update_metrics_overview(
                metrics_overview_hl_sugarvita, metrics_overview_hl_sugarvita_new_data
            )

        metrics_overview_pt_sugarvita_normalized = pt_hl.normalize_metrics(
            metrics_overview_pt_sugarvita
        )
        metrics_overview_hl_sugarvita_normalized = pt_hl.normalize_metrics(
            metrics_overview_hl_sugarvita
        )
        player_types_labels = pt_hl.get_player_types(
            metrics_overview_pt_sugarvita_normalized
        )
        health_literacy_score_sugarvita = pt_hl.get_health_literacy_score_sugarvita(
            metrics_overview_hl_sugarvita_normalized
        )

        
    
    if id_latest_record_trivia == 0 or (
        id_latest_record_trivia != int((json.loads(response_trivia.text))[-1]["id"])
    ):
        parsed_metrics_from_trivia = pt_hl.parse_json_trivia(
            response_trivia, id_latest_record_trivia
        )
        # print(parsed_metrics_from_trivia)

        if metrics_overview_hl_trivia == None:
            metrics_overview_hl_trivia = pt_hl.manipulate_initial_metrics_trivia(
                parsed_metrics_from_trivia
            )
            # print("overview trivia:", metrics_overview_hl_trivia)

        else:
            # print(id_latest_record_trivia,"!=",(json.loads(response_trivia.text))[-1]["id"])
            metrics_overview_hl_trivia_new_data = (
                pt_hl.manipulate_initial_metrics_trivia(parsed_metrics_from_trivia)
            )
            # print("old metrics:", metrics_overview_hl_trivia)
            # print("new metrics:",  metrics_overview_hl_trivia_new_data)
            metrics_overview_hl_trivia = pt_hl.update_metrics_overview(
                metrics_overview_hl_trivia, metrics_overview_hl_trivia_new_data
            )
            # print("updated metrics:", metrics_overview_hl_trivia)

        metrics_overview_hl_trivia_normalized = pt_hl.normalize_metrics(
            metrics_overview_hl_trivia
        )
        # print("normalized metrics:", metrics_overview_hl_trivia_normalized)
        health_literacy_score_trivia = pt_hl.get_health_literacy_score_trivia(
            metrics_overview_hl_trivia_normalized
        )
        # print("trivia HL score:", health_literacy_score_trivia)
        health_literacy_score = pt_hl.get_health_literacy_score_final(
            health_literacy_score_sugarvita, health_literacy_score_trivia
        )
        # print("final HL:", health_literacy_score)
    
    elif id_latest_record_trivia == int(
        (json.loads(response_trivia.text))[-1]["id"]
    ) and (id_latest_record_pt != int((json.loads(response_pt.text))[-1]["id"])):
        health_literacy_score = pt_hl.get_health_literacy_score_final(
            health_literacy_score_sugarvita, health_literacy_score_trivia
        )
    
    return player_types_labels, health_literacy_score_sugarvita, health_literacy_score_trivia, health_literacy_score, metrics_overview_pt_sugarvita, metrics_overview_hl_sugarvita, metrics_overview_hl_trivia, response_pt, response_hl, response_trivia


def log_start():
    logger.info('Program started.')

def log_exit():
    logger.info('Program interrupted or exited.')
    

# Register a signal handler for common interrupts (e.g., Ctrl+C)
def signal_handler(sig, frame):
    log_exit()
    sys.exit(1)


parser = argparse.ArgumentParser()
parser.add_argument(
    "-o", "--output", help="Path for the output CSV file.", type=str
)
parser.add_argument(
    "-ro", "--runonce", help="For 1 result only, instead of running indefinetly", action="store_true"
)
#parser.add_argument(
#    "-i", "--input", nargs=2, help="Run the digital twin of a player by inserting PlayerId and Authorization Token", type=(int, str)
#)
parser.add_argument(
    "-t", "--time", help="Time interval, in minutes, to check for new data and possibly get new results.", type=int
)
args = parser.parse_args()


if __name__ == "__main__":
    # secrets_path = "secrets.csv"
    # df = pandas.read_csv(secrets_path)
    # secrets = df.to_numpy()
    log_start()

    load_dotenv()

    atexit.register(log_exit)
    signal.signal(signal.SIGINT, signal_handler)

    if args.output:
        output_path=args.output
    else:
        output_path="digital_twin_results.csv"

    with open(output_path, mode="w", newline='') as results:
        writer = csv.writer(results)
        writer.writerow(["Timestamp", "Health Literacy Score (SugarVita)", "Health Literacy Score (Trivia)", "Health Literacy Score", "Socializer Score", "Competitive Score", "Explorer Score"])


    player_id = str(os.getenv("PLAYER_ID"))
    auth_bearer = str(os.getenv("AUTHORIZATION_BEARER"))

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
            (
                player_types_labels,
                health_literacy_score_sugarvita,
                health_literacy_score_trivia,
                health_literacy_score,
                metrics_overview_pt_sugarvita,
                metrics_overview_hl_sugarvita,
                metrics_overview_hl_trivia,
                response_pt,
                response_hl,
                response_trivia,
            ) = get_digital_twin(player_id, auth_bearer)
            (
                id_latest_record_pt,
                id_latest_record_hl,
                id_latest_record_trivia,
                date_latest_record_sugarvita,
                date_latest_record_trivia,
            ) = pt_hl.save_id_date_latest_record(
                response_pt, response_hl, response_trivia
            )

            print((datetime.now()).strftime("%H:%M:%S"))
            print(health_literacy_score_sugarvita)
            print(health_literacy_score_trivia)
            print(health_literacy_score)
            print(player_types_labels)

            if args.output:
                output_path=args.output
            else:
                output_path="digital_twin_results.csv"

            with open(output_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    datetime.now().strftime("%H:%M:%S"),
                    health_literacy_score_sugarvita["Health Literacy Sugarvita"],
                    health_literacy_score_trivia["Health Literacy Trivia"],
                    health_literacy_score["Health Literacy"],
                    player_types_labels["Socializer"],
                    player_types_labels["Competitive"],
                    player_types_labels["Explorer"]
                ])
            
            if args.runonce:
                break
            
            if args.time:
                time.sleep(
                    args.time * 60
                )

            else:
                time.sleep(
                    1 * 60
                )  # 10*60 seconds --> 10 minutes --> it needs to be represented in seconds

            

        else:
            endpoint_filtered_pt = (
                "https://api3-new.gamebus.eu/v2/players/{}/activities?start="
                + str(date_latest_record_sugarvita)
                + "&gds=SUGARVITA_PLAYTHROUGH"
            )
            endpoint_filtered_hl = (
                "https://api3-new.gamebus.eu/v2/players/{}/activities?start="
                + str(date_latest_record_sugarvita)
                + "&gds=SUGARVITA_ENGAGEMENT_LOG_1"
            )
            endpoint_filtered_trivia = (
                "https://api3-new.gamebus.eu/v2/players/{}/activities?start="
                + str(date_latest_record_trivia)
                + "&gds=ANSWER_TRIVIA_DIABETES"
            )

            try:
                endpoint_pt = endpoint_filtered_pt.format(player_id)
                response_pt = requests.request( 
                    "GET", endpoint_pt, headers=headers, data=payload
                )
                response_pt.raise_for_status() # raise exception for HTTP errors
            except requests.exceptions.RequestException as e:
                logger.error("Failed to retrieve response_pt: %s", str(e), "\n")
            
            try:
                endpoint_hl = endpoint_filtered_hl.format(player_id)
                response_hl = requests.request(
                    "GET", endpoint_hl, headers=headers, data=payload
                )
                response_hl.raise_for_status()
            except requests.exceptions.RequestException as e:
                logger.error("Failed to retrieve response_hl: %s", str(e), "\n")
            
            try:
                endpoint_trivia = endpoint_filtered_trivia.format(player_id)                
                response_trivia = requests.request(
                    "GET", endpoint_trivia, headers=headers, data=payload
                )
                response_trivia.raise_for_status()
            except requests.exceptions.RequestException as e:
                logger.error("Failed to retrieve response_trivia: %s", str(e), "\n")


            (
                id_new_latest_pt,
                id_new_latest_hl,
                id_new_latest_trivia,
                date_new_latest_record_sugarvita,
                date_new_latest_record_trivia,
            ) = pt_hl.save_id_date_latest_record(
                response_pt, response_hl, response_trivia
            )

            if (
                (id_latest_record_pt != id_new_latest_pt
                or id_latest_record_trivia != id_new_latest_trivia) 

            ):

                (
                    player_types_labels,
                    health_literacy_score_sugarvita,
                    health_literacy_score_trivia,
                    health_literacy_score,
                    metrics_overview_pt_sugarvita,
                    metrics_overview_hl_sugarvita,
                    metrics_overview_hl_trivia,
                    response_pt,
                    response_hl,
                    response_trivia,
                ) = get_digital_twin(
                    player_id,
                    auth_bearer,
                    endpoint_pt=endpoint_filtered_pt,  # endpoint pt filtered by date
                    endpoint_hl=endpoint_filtered_hl,  # endpoint hl filtered by date
                    endpoint_trivia=endpoint_filtered_trivia,  # endpoint trivia filtered by date
                    id_latest_record_pt=id_latest_record_pt,
                    id_latest_record_trivia=id_latest_record_trivia,
                    metrics_overview_pt_sugarvita=metrics_overview_pt_sugarvita,
                    metrics_overview_hl_sugarvita=metrics_overview_hl_sugarvita,
                    metrics_overview_hl_trivia=metrics_overview_hl_trivia,
                    player_types_labels=player_types_labels,
                    health_literacy_score_sugarvita=health_literacy_score_sugarvita,
                    health_literacy_score_trivia=health_literacy_score_trivia,
                    health_literacy_score=health_literacy_score,
                )

                print((datetime.now()).strftime("%H:%M:%S"))
                print(health_literacy_score_sugarvita)
                print(health_literacy_score_trivia)
                print(health_literacy_score)
                print(player_types_labels)

                if args.output:
                    output_path=args.output
                else:
                    output_path="digital_twin_results.csv"

                with open(output_path, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        datetime.now().strftime("%H:%M:%S"),
                        health_literacy_score_sugarvita["Health Literacy Sugarvita"],
                        health_literacy_score_trivia["Health Literacy Trivia"],
                        health_literacy_score["Health Literacy"],
                        player_types_labels["Socializer"],
                        player_types_labels["Competitive"],
                        player_types_labels["Explorer"]
                    ])

                id_latest_record_pt = id_new_latest_pt  # save the new id of the last record (will for sure change)
                id_latest_record_hl = id_new_latest_hl
                id_latest_record_trivia = id_new_latest_trivia
                date_latest_record_sugarvita = date_new_latest_record_sugarvita
                date_latest_record_trivia = date_new_latest_record_trivia

                if args.time:
                    time.sleep(
                        args.time * 60
                    )
                else:
                    time.sleep(
                        1 * 60
                    )
            else:
                print("No new records", (datetime.now()).strftime("%H:%M:%S"))
                if args.time:
                    time.sleep(
                        args.time * 60
                    )
                else:
                    time.sleep(
                        1 * 60
                    )  # 10*60 seconds --> 10 minutes --> it needs to be represented in seconds
               
