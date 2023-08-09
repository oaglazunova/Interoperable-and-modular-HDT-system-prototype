import json
from statistics import mean, pstdev


def parse_json(response) -> dict:
    metrics_per_session={
    "SCORES":[], #each position of the list will represent the score achieved after a playthrough
    "PLAYTIMES":[], #each position of the list will represent how long a session took
    "DAYS_PLAYED":[],  #each position of the list will represent the amount of simulated days the player decided to select for the session
    "HOME_PATH":[], #each position of the list will represent the amount of times a player chose a Home Path Type during a session
    "WORK_PATH":[], #each position of the list will represent the amount of times a player chose a Home Path Type during a session
    "OUTDOORS_PATH":[] #each position of the list will represent the amount of times a player chose a Home Path Type during a session
    }

    parsed_response=json.loads(response.text)
    #parsed_response=parsed_response[-1] #last record

    for record in parsed_response:
        try:
            metrics_per_session['SCORES'].append(int(record['propertyInstances'][0]['value']))
        except:
            metrics_per_session['SCORES'].append('NaN')

        try:
            metrics_per_session['PLAYTIMES'].append(int(record['propertyInstances'][1]['value']))
        except:
            metrics_per_session['PLAYTIMES'].append('NaN')

        try:
            playthrough_data=record['propertyInstances'][4]['value']
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
        
    return metrics_per_session


def remove_nan(metrics) -> list: 
    # using list comprehension to perform the task
    for key, value in metrics.items():
        value_cleaned = [i for i in value if i != 'NaN']
        metrics[key]=value_cleaned
    return metrics


def manipulate_initial_metrics(metrics_cleaned) -> dict:
    metrics_overview={
        "avg_score":0, #average of the scores from all sessions played
        "sd_score":0, #standard deviation """
        "avg_playtimes":0, #average of the playtimes """
        "sd_playtimes":0, #standar deviation """
        "1_day_session":0, #total of sessions that simulated 1 day in the game
        "2_days_session":0, #"""" 2 days """
        "3_days_session":0, #""" 3 days """
        "avg_days_session":0, #average days sinulated in the game
        "sd_days_session":0, #standard deviation...
        "total_work_path":0, #total times a player as chosen a work path
        "total_home_path":0, #""" home path
        "total_outdoors_path":0 #""" outdoors path
    }

    for key, value in metrics_cleaned.items():
        if key=='SCORES':
            metrics_overview['avg_score']=round(mean(value),2)
            metrics_overview['sd_score']=round(pstdev(value),2)
        elif key=='PLAYTIMES':
            metrics_overview['avg_playtimes']=round(mean(value),2)
            metrics_overview['sd_playtimes']=round(pstdev(value),2)
        elif key=='DAYS_PLAYED':
            metrics_overview['avg_days_session']=round(mean(value),2)
            metrics_overview['sd_days_session']=round(pstdev(value),2)
            for days in value:
                if days==1:
                    metrics_overview['1_day_session']+=1
                elif days==2:
                    metrics_overview['2_days_session']+=1
                elif days==3:
                    metrics_overview['3_days_session']+=1
        elif key=="HOME_PATH":
            metrics_overview['total_home_path']=sum(value)
        elif key=="WORK_PATH":
            metrics_overview['total_work_path']=sum(value)
        elif key=='OUTDOORS_PATH':
            metrics_overview['total_outdoors_path']=sum(value)
    
    return metrics_overview