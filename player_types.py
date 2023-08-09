import requests, json

metrics={
    "SCORES":[], #each position of the list will represent the score achieved after a playthrough
    "PLAYTIMES":[], #each position of the list will represent how long a session took
    "DAYS_PLAYED":[],  #each position of the list will represent the amount of simulated days the player decided to select for the session
    "HOME_PATH":[], #each position of the list will represent the amount of times a player chose a Home Path Type during a session
    "WORK_PATH":[], #each position of the list will represent the amount of times a player chose a Home Path Type during a session
    "OUTDOORS_PATH":[] #each position of the list will represent the amount of times a player chose a Home Path Type during a session
    } 

url = "https://api3-new.gamebus.eu/v2/players/993/activities?gds=SUGARVITA_PLAYTHROUGH"

payload={}
headers = {
  'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiZ2FtZWJ1c19hcGkiXSwidXNlcl9uYW1lIjoiZC52YW5laWpsQHN0dWRlbnQuZm9udHlzLm5sIiwic2NvcGUiOlsicmVhZCIsIndyaXRlIiwidHJ1c3QiXSwiZXhwIjoxNzY3OTQyODcxLCJhdXRob3JpdGllcyI6WyJERVYiLCJVU0VSIl0sImp0aSI6InQ3OUZnQm4xaGprX3BnSG1CQ0NPOVVXc3BEayIsImNsaWVudF9pZCI6ImdhbWVidXNfYmFzZV9hcHAifQ.Ey9WBijTTCoB5WdmiWb_pfrBOPUHxSh0b8jGlWzPqK3ahTbkGdGvG5alm3Tl75cse3RVSq7Y-XttuoStQSXMJpLTEMjXFCuqEbkp-wvnl-xepguWutGECaFJy0XxlGUTOfBYe8Zahl7sN6TTH3h0aZYw2LD60qHEPdcL3bpeW0NBcq4um_50E-0mHdgtxQWzblVy6fr5itjmI-4azSlr2XOYyamNYNmsjfnfHQPNq1RYhFpy-ewXc7s1svFh9EhOMd5OcWD0ht5cDRcm6Iqz6T06W6az05fIWlXN2Q9k5SzPu0Ct0YBkzr4EXxwXyJeT-nWZnCbi30wYwEd78FtsJw'
  }

response = requests.request("GET", url, headers=headers, data=payload)
parsed_response=json.loads(response.text)
print(type(parsed_response))
parsed_response=parsed_response[-1] #last record

metrics['SCORES'].append(parsed_response['propertyInstances'][0]['value'])
metrics['PLAYTIMES'].append(parsed_response['propertyInstances'][1]['value'])
playthrough_data=parsed_response['propertyInstances'][4]['value']
#print(type(playthrough_data)) #"dictonary" string
playthrough_data=json.loads(playthrough_data) #converts the "dictionary" string into a dictionary
#print(type(playthrough_data)) #dictonary
metrics['DAYS_PLAYED'].append(playthrough_data['daysPlayed'])

home_path, outdoors_path, work_path = 0, 0, 0

for turn in playthrough_data['turns']:
    if turn['DestinationPathType'] == 1:
        home_path+=1
    elif turn['DestinationPathType'] == 2:
        outdoors_path+=1
    elif turn['DestinationPathType']==3:
        work_path+=1

metrics['HOME_PATH'].append(home_path)
metrics['WORK_PATH'].append(work_path)
metrics['OUTDOORS_PATH'].append(outdoors_path)

print(metrics)


                          



#id_player=parsed_response['creator']['id']
#timestamp=parsed_response['date']
#activities=parsed_response['propertyInstances'] #activities[0]-> related to the type of emotions; activities[1] -> related to the intensity.
#type_emotion=(activities[0]['value'])
#intensity_emotion=(activities[1]['value'])
#print(id_player, timestamp, type_emotion, intensity_emotion)
