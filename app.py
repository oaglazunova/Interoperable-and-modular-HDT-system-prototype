from flask import Flask, jsonify
import main

app=Flask(__name__)

@app.route('/get_player_type', methods=['GET'])
def get_player_type():
    player_types_labels = pt_hl.get_player_types(metrics_overview_pt_normalized)
    
    # Converts the result to a JSON response
    response = {
        'player_types_labels': player_types_labels
    }
    return jsonify(response)