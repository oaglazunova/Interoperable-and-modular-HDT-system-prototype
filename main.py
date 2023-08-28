import requests, player_types, time, pandas, health_literacy

if __name__ == "__main__":
    id_latest_record_pt = 0
    id_latest_record_hl = 0
    date_latest_record = 0

    secrets_path = "secrets.csv"
    df = pandas.read_csv(secrets_path)
    secrets = df.to_numpy()

    for (
        player_info
    ) in (
        secrets
    ):  # most probably we will only have 1 user at a time, but still, let's keep the for loop
        player_id = player_info[0]
        auth_bearer = player_info[1]

    endpoint_pt = "https://api3-new.gamebus.eu/v2/players/{}/activities?gds=SUGARVITA_PLAYTHROUGH".format(
        player_id
    )
    endpoint_hl = "https://api3-new.gamebus.eu/v2/players/{}/activities?gds=SUGARVITA_ENGAGEMENT_LOG_1".format(
        player_id
    )
    payload = {}
    headers = {"Authorization": "Bearer {}".format(auth_bearer)}
    while True:
        if id_latest_record_pt == 0 and id_latest_record_hl == 0 and date_latest_record == 0:
            response_pt = requests.request("GET", endpoint_pt, headers=headers, data=payload)
            response_hl = requests.request("GET", endpoint_hl, headers=headers, data=payload)

            parsed_metrics = player_types.parse_json(response_pt, response_hl, id_latest_record_pt, id_latest_record_hl)
            (
                id_latest_record_pt, 
                id_latest_record_hl,
                date_latest_record,
            ) = player_types.save_id_date_latest_record(response_pt, response_hl)
            print(parsed_metrics)
            # parsed_metrics=player_types.parse_json_try(response)
            parsed_metrics_cleaned = player_types.remove_nan(parsed_metrics)
            metrics_overview = player_types.manipulate_initial_metrics(
                parsed_metrics_cleaned
            )
            metrics_overview_normalized = player_types.normalize_metrics(
                metrics_overview
            )
            # print(metrics_overview_normalized)
            player_types_labels = player_types.get_player_types(
                metrics_overview_normalized
            )
            print(player_types_labels)
            time.sleep(
                1 * 60
            )  # 10*60 seconds --> 10 minutes --> it needs to be represented in seconds

        else:
            url_filtered = (
                "https://api3-new.gamebus.eu/v2/players/993/activities?start="
                + str(date_latest_record)
                + "&gds=SUGARVITA_PLAYTHROUGH"
            )
            response_pt = requests.request("GET", endpoint_pt, headers=headers, data=payload)
            id_new_latest_pt, id_new_latest_hl, date_new_latest = player_types.save_id_date_latest_record(
                response_pt,
                response_hl
            )
            if (
                id_latest_record_pt != id_new_latest_pt and id_latest_record_hl != id_new_latest_hl
            ):  # if the id saved is different from the id of the latest record, then we have new data
                parsed_metrics = player_types.parse_json(response_pt, response_hl, id_new_latest_pt, id_new_latest_hl)
                parsed_metrics_cleaned = player_types.remove_nan(parsed_metrics)
                metrics_overview_new_data = player_types.manipulate_initial_metrics(
                    parsed_metrics_cleaned
                )
                metrics_overview = player_types.update_metrics_overview(
                    metrics_overview, metrics_overview_new_data
                )  # updated metrics_overview
                metrics_overview_normalized = player_types.normalize_metrics(
                    metrics_overview
                )  # updated metrics_overview_normalized
                # print(metrics_overview_normalized)
                player_types_labels = player_types.get_player_types(
                    metrics_overview_normalized
                )  # updated labels
                print(player_types_labels)
                id_latest_record = id_new_latest  # save the new id of the last record (will for sure change)
                date_latest_record = (
                    date_new_latest  # save the date of the last record (might change)
                )
            else:
                print("No new records")
                time.sleep(
                    1 * 60
                )  # 10*60 seconds --> 10 minutes --> it needs to be represented in seconds
                # break
