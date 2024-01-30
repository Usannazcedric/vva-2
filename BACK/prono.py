
# equipe1 = "Scotland"
# equipe2 = "England"
# ville_du_match = "Asadabad"  
# date_du_match = "2017-05-07"  

from flask import Flask, request, jsonify
from flask_cors import CORS 
import pandas as pd
import json

app = Flask(__name__)
CORS(app)  

data_matchs = pd.read_csv('rugby_dataset.csv')
with open('daily_weather3co.json', 'r') as json_file:
    data_meteo = json.load(json_file)

def calculer_resultats(equipe1, equipe2, date_du_match, ville_du_match):
    data_matchs['date'] = pd.to_datetime(data_matchs['date'])

    date_debut = pd.to_datetime('2013-01-01')
    date_fin = pd.to_datetime('now')

    historique_matchs = data_matchs[(data_matchs['date'] >= date_debut) & (data_matchs['date'] <= date_fin) &
                                   ((data_matchs['home_team'] == equipe1) & (data_matchs['away_team'] == equipe2) |
                                    (data_matchs['home_team'] == equipe2) & (data_matchs['away_team'] == equipe1))]
    
    victoires_equipe1 = len(historique_matchs[(historique_matchs['home_team'] == equipe1) &
                                              (historique_matchs['home_score'] > historique_matchs['away_score'])]) + \
                        len(historique_matchs[(historique_matchs['away_team'] == equipe1) &
                                              (historique_matchs['away_score'] > historique_matchs['home_score'])])

    victoires_equipe2 = len(historique_matchs[(historique_matchs['home_team'] == equipe2) &
                                              (historique_matchs['home_score'] > historique_matchs['away_score'])]) + \
                        len(historique_matchs[(historique_matchs['away_team'] == equipe2) &
                                              (historique_matchs['away_score'] > historique_matchs['home_score'])])

    total_matchs = len(historique_matchs)
    pourcentage_victoires_equipe1 = (victoires_equipe1 / total_matchs) * 100
    pourcentage_victoires_equipe2 = (victoires_equipe2 / total_matchs) * 100

    prob_equipe1 = pourcentage_victoires_equipe1 / 100
    prob_equipe2 = pourcentage_victoires_equipe2 / 100

    cote_equipe1 = 1 / prob_equipe1
    cote_equipe2 = 1 / prob_equipe2

    timestamp_date_du_match = pd.to_datetime(date_du_match).timestamp()

    donnees_meteo_match = [entry for entry in data_meteo if entry['city_name'] == ville_du_match and
                           entry['date'] == timestamp_date_du_match]

    if donnees_meteo_match:
        precipitation_mm = donnees_meteo_match[0]['precipitation_mm']
        condition_meteo = "pluvieux" if precipitation_mm > 0 else "sec"
    else:
        condition_meteo = "données non disponibles"

    resultat = {
        "pourcentage_victoires_equipe1": pourcentage_victoires_equipe1,
        "pourcentage_victoires_equipe2": pourcentage_victoires_equipe2,
        "cote_equipe1": cote_equipe1,
        "cote_equipe2": cote_equipe2,
        "condition_meteo": condition_meteo
    }

    return resultat

@app.route('/resultats', methods=['POST'])
def obtenir_resultats():
    data = request.json
    equipe1 = data.get('equipe1')
    equipe2 = data.get('equipe2')
    date_du_match = data.get('date')
    ville_du_match = data.get('ville')

    resultat = calculer_resultats(equipe1, equipe2, date_du_match, ville_du_match)
    return jsonify(resultat)

if __name__ == '__main__':
    app.run(debug=True)
