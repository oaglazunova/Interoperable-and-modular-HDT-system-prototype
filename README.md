# Human Digital Twins for diabetic patients: a player type and health literacy profiling approach

![License](https://img.shields.io/github/license/catolivetree/dissertation)
![Version](https://img.shields.io/badge/version-v0.1.0-blue?style=for-the-badge)

By collecting data from an educational diabetes game (**SUGARVITA**), we are able to profile a diabetic patient in 3 player types: **Social, Competitive, Explorer**. <br>
Additionally, based on a patient's performance within the educational game, as well as a trivia mini-game, a **health literacy score** regarding diabetes is also obtained. <br>
This project is ready to be running as a command-line tool, as well as it is web-server ready.

## Repository structure
- **digital_twin.py**: is our human digital twin: <br>
  -Definition of command line arguments to run the twin. <br>
  -Logging exceptions. <br>
  -All the logic behind getting the player types and health literacy scores periodically.
- **pt_hl.py**: definition of functions to: <br>
  -Parse the data coming from SUGARVITA and the trivia mini-game. <br>
  -Remove null values. <br>
  -Transform features for profiling of the player types and health literacy level. <br>
  -Normalize data. <br>
  -Assign weights to the features. <br>
  -Calculate the final scores for: Health Literacy (overall), Health Literacy (based on SUGARVITA's performance), Health Literacy (based on trivia mini-game), Social, Competitive, and Explorer. <br>
  -Return the id's and dates of the latest records coming from SUGARVITA, as well as the trivia mini-game. <br>
  -Update the values of the features when there's new data. <br>
  
- **log.py**: configuration of the logging system.
  
- **app.py**: definition of the API
- **test_api.py**: definition of the test functions (scenarios) to assess the API.

- **offline_testing**: to simulate new data from SUGARVITA, even without playing it online. For more information, there's another readme file inside this folder.
  
## Before you begin
Run `pip install -r requirements.text`

## Usage (command line)
Run `python digital_twin.py -h` or `python digital_twin.py --help`
Usage: `digital_twin.py [-h] [-o OUTPUT] [-ro] [-id PLAYERID] [-tk TOKEN] [-t TIME]`

Options: <br>
`-h, --help show this help message and exit` <br>
`-o OUTPUT, --output OUTPUT path for the output CSV file` <br>
`-ro, --runonce for 1 results only, instead of running indefinetly` <br>
`-id PLAYERID, --playerid PLAYERID input the playerID to get the digital twin results` <br>
`-tk TOKEN, --token TOKEN input the secret token to get the digital twin results` <br>
`-t TIME, --time TIME interval, in minutes, to check for new data and possibly get new results` <br>

## Usage (API)
Run `python -m flask run` <br>
Open the Postman app: <br>
- Add the bearer token (for a player), in the authorization tab
- Define the GET request as it follows: `http://localhost:5000/get_scores/PLAYERID` (where PLAYERID is the real playerID)
- Send request
- Get results for that player

### Test functions
Run `python -m pytest`
