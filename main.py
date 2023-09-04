import requests, player_types, time, pandas, os
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()

    id_latest_record_pt = 0
    id_latest_record_hl = 0
    date_latest_record = 0

    # secrets_path = "secrets.csv"
    # df = pandas.read_csv(secrets_path)
    # secrets = df.to_numpy()

    player_id = str(os.getenv("PLAYER_ID"))
    auth_bearer = str(os.getenv("AUTHORIZATION_BEARER"))

    endpoint_pt = "https://api3-new.gamebus.eu/v2/players/{}/activities?gds=SUGARVITA_PLAYTHROUGH".format(
        player_id
    )
    endpoint_hl = "https://api3-new.gamebus.eu/v2/players/{}/activities?gds=SUGARVITA_ENGAGEMENT_LOG_1".format(
        player_id
    )
    payload = {}
    headers = {"Authorization": "Bearer {}".format(auth_bearer)}
    while True:
        if (
            id_latest_record_pt == 0
            and id_latest_record_hl == 0
            and date_latest_record == 0
        ):
            response_pt = requests.request(
                "GET", endpoint_pt, headers=headers, data=payload
            )
            response_hl = requests.request(
                "GET", endpoint_hl, headers=headers, data=payload
            )

            parsed_metrics = player_types.parse_json(
                response_pt, response_hl, id_latest_record_pt, id_latest_record_hl
            )
            (
                id_latest_record_pt,
                id_latest_record_hl,
                date_latest_record,
            ) = player_types.save_id_date_latest_record(response_pt, response_hl)
            print(parsed_metrics)
            # parsed_metrics=player_types.parse_json_try(response)
            parsed_metrics_cleaned = player_types.remove_nan(parsed_metrics)
            (
                metrics_overview_pt,
                metrics_overview_hl,
            ) = player_types.manipulate_initial_metrics(parsed_metrics_cleaned)
            metrics_overview_pt_normalized = player_types.normalize_metrics(
                metrics_overview_pt
            )
            metrics_overview_hl_normalized = player_types.normalize_metrics(
                metrics_overview_hl
            )
            # print(metrics_overview_normalized)
            player_types_labels = player_types.get_player_types(
                metrics_overview_pt_normalized
            )
            health_literacy_score = player_types.get_health_literacy_score(
                metrics_overview_hl
            )
            print(player_types_labels)
            print(health_literacy_score)
            time.sleep(
                1 * 60
            )  # 10*60 seconds --> 10 minutes --> it needs to be represented in seconds

        else:
            endpoint_filtered_pt = (
                "https://api3-new.gamebus.eu/v2/players/{}/activities?start="
                + str(date_latest_record)
                + "&gds=SUGARVITA_PLAYTHROUGH"
            )
            endpoint_filtered_hl = (
                "https://api3-new.gamebus.eu/v2/players/{}/activities?start="
                + str(date_latest_record)
                + "&gds=SUGARVITA_ENGAGEMENT_LOG_1"
            )
            response_pt = requests.request(
                "GET", endpoint_pt, headers=headers, data=payload
            )
            response_hl = requests.request(
                "GET", endpoint_hl, headers=headers, data=payload
            )
            (
                id_new_latest_pt,
                id_new_latest_hl,
                date_new_latest,
            ) = player_types.save_id_date_latest_record(response_pt, response_hl)
            if (
                id_latest_record_pt != id_new_latest_pt
                and id_latest_record_hl != id_new_latest_hl
            ):  # if the id saved is different from the id of the latest record, then we have new data
                parsed_metrics = player_types.parse_json(
                    response_pt, response_hl, id_new_latest_pt, id_new_latest_hl
                )
                parsed_metrics_cleaned = player_types.remove_nan(parsed_metrics)
                (
                    metrics_overview_pt_new_data,
                    metrics_overview_hl_new_data,
                ) = player_types.manipulate_initial_metrics(parsed_metrics_cleaned)
                metrics_pt_overview = player_types.update_metrics_overview(
                    metrics_overview_pt, metrics_overview_pt_new_data
                )  # updated metrics_overview
                metrics_hl_overview = player_types.update_metrics_overview(
                    metrics_overview_hl, metrics_overview_hl_new_data
                )  # updated metrics_overview
                metrics_overview_pt_normalized = player_types.normalize_metrics(
                    metrics_pt_overview
                )  # updated metrics_overview_pt_normalized
                metrics_overview_hl_normalized = player_types.normalize_metrics(
                    metrics_hl_overview
                )  # updated metrics_overview_hl_normalized
                # print(metrics_overview_normalized)
                player_types_labels = player_types.get_player_types(
                    metrics_overview_pt_normalized
                )  # updated labels
                health_literacy_score = player_types.get_health_literacy_score(
                    metrics_overview_hl_normalized
                )
                print(player_types_labels)
                print(health_literacy_score)
                id_latest_record_pt = id_new_latest_pt  # save the new id of the last record (will for sure change)
                id_latest_record_hl = id_new_latest_hl
                date_latest_record = (
                    date_new_latest  # save the date of the last record (might change)
                )
            else:
                print("No new records")
                time.sleep(
                    1 * 60
                )  # 10*60 seconds --> 10 minutes --> it needs to be represented in seconds
                # break
