import requests, player_types, time, json

id_latest_record = 0
date_latest_record = 0

player_id = str(input("Please input the player id: "))  # id=993
url = (
    "https://api3-new.gamebus.eu/v2/players/"
    + player_id
    + "/activities?gds=SUGARVITA_PLAYTHROUGH"
)
payload = {}
headers = {
    "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiZ2FtZWJ1c19hcGkiXSwidXNlcl9uYW1lIjoiZC52YW5laWpsQHN0dWRlbnQuZm9udHlzLm5sIiwic2NvcGUiOlsicmVhZCIsIndyaXRlIiwidHJ1c3QiXSwiZXhwIjoxNzY3OTQyODcxLCJhdXRob3JpdGllcyI6WyJERVYiLCJVU0VSIl0sImp0aSI6InQ3OUZnQm4xaGprX3BnSG1CQ0NPOVVXc3BEayIsImNsaWVudF9pZCI6ImdhbWVidXNfYmFzZV9hcHAifQ.Ey9WBijTTCoB5WdmiWb_pfrBOPUHxSh0b8jGlWzPqK3ahTbkGdGvG5alm3Tl75cse3RVSq7Y-XttuoStQSXMJpLTEMjXFCuqEbkp-wvnl-xepguWutGECaFJy0XxlGUTOfBYe8Zahl7sN6TTH3h0aZYw2LD60qHEPdcL3bpeW0NBcq4um_50E-0mHdgtxQWzblVy6fr5itjmI-4azSlr2XOYyamNYNmsjfnfHQPNq1RYhFpy-ewXc7s1svFh9EhOMd5OcWD0ht5cDRcm6Iqz6T06W6az05fIWlXN2Q9k5SzPu0Ct0YBkzr4EXxwXyJeT-nWZnCbi30wYwEd78FtsJw"
}


if __name__ == "__main__":
    while True:
        if id_latest_record == 0 and date_latest_record == 0:
            response = requests.request("GET", url, headers=headers, data=payload)
            parsed_metrics = player_types.parse_json(response, id_latest_record)
            (
                id_latest_record,
                date_latest_record,
            ) = player_types.save_id_date_latest_record(response)
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
            time.sleep(1*60) #10*60 seconds --> 10 minutes --> it needs to be represented in seconds
        
        
        else:
            url_filtered = (
                "https://api3-new.gamebus.eu/v2/players/993/activities?start="
                + str(date_latest_record)
                + "&gds=SUGARVITA_PLAYTHROUGH"
            )
            response = requests.request("GET", url, headers=headers, data=payload)
            id_new_latest, date_new_latest = player_types.save_id_date_latest_record(
                response
            )
            if (
                id_latest_record != id_new_latest
            ):  # if the id saved is different from the id of the latest record, then we have new data
                parsed_metrics = player_types.parse_json(response, id_new_latest)
                parsed_metrics_cleaned = player_types.remove_nan(parsed_metrics)
                metrics_overview_new_data = player_types.manipulate_initial_metrics(
                    parsed_metrics_cleaned
                )
                metrics_overview = player_types.update_metrics_overview(
                    metrics_overview, metrics_overview_new_data
                ) #updated metrics_overview
                metrics_overview_normalized = player_types.normalize_metrics(
                    metrics_overview
                ) #updated metrics_overview_normalized
                # print(metrics_overview_normalized)
                player_types_labels = player_types.get_player_types(
                    metrics_overview_normalized
                ) #updated labels
                print(player_types_labels)
                id_latest_record = id_new_latest  # save the new id of the last record (will for sure change)
                date_latest_record = (
                    date_new_latest  # save the date of the last record (might change)
                )
            else:
                print('No new records')
                time.sleep(1*60) #10*60 seconds --> 10 minutes --> it needs to be represented in seconds
                #break
