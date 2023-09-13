from flask import Flask, jsonify, request
import digital_twin as dt

app = Flask(__name__)

@app.route("/get_scores/<int:playerID>", methods=["GET"])
def get_scores(playerID):
    headers = request.headers
    bearer_token = headers.get(
        "Authorization"
    )  # Extract the bearer token from the request headers --> Bearer Token
    token = bearer_token.split()[1]  # JUST THE TOKEN (without "Bearer")

    (player_types_labels, 
     health_literacy_score_sugarvita, 
     health_literacy_score_trivia, 
     health_literacy_score, 
     metrics_overview_pt_sugarvita,
     metrics_overview_hl_sugarvita,
     metrics_overview_hl_trivia,
     response_pt,
     response_hl,
     response_trivia) = dt.get_digital_twin(playerID, token)

    scores={
        "player_types_labels": player_types_labels,
        "health_literacy_score_sugarvita": health_literacy_score_sugarvita,
        "health_literacy_score_trivia": health_literacy_score_trivia,
        "health_literacy_score": health_literacy_score
    }
    return jsonify(scores), 200