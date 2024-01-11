import time
from datetime import datetime, timedelta
from flask import Flask
from flask import render_template
import requests
import pytz
us_timezone = pytz.timezone('America/New_York')



app = Flask(__name__)

def get_game_data():
    yesterday = (datetime.now(us_timezone) - timedelta(days=1)).strftime('%Y-%m-%d')
    today = (datetime.now(us_timezone)).strftime('%Y-%m-%d')

    # API endpoint URL parameters
    games_url = f'https://www.balldontlie.io/api/v1/games?start_date={yesterday}&end_date={today}&per_page={500}'

    # recup data
    response = requests.get(games_url)
    return response.json()['data']


def get_game_stats():
    yesterday = (datetime.now(us_timezone) - timedelta(days=1)).strftime('%Y-%m-%d')
    today = (datetime.now(us_timezone)).strftime('%Y-%m-%d')
    stats_url = f"https://www.balldontlie.io/api/v1/stats?start_date={yesterday}&end_date={today}&per_page={500}"
    stats_response = requests.get(stats_url)
    return stats_response.json()["data"]


def get_result(game_data, game_stats):
    
    basketball_games = {'today': [], 'yesterday': []}
    
    # key game id
    iter = 0
    
    for game in game_data:
        iter += 1
        game_id = game['id']
        
        top_performer = None
        
        for game_state in game_stats:
            s_game_id = game_state['game']['id']
            if (game_id) == (s_game_id):
                if game_state['player']== None : continue
                player_name = game_state['player']['first_name'] + " " + game_state['player']['last_name']
                    
                pts = game_state['pts']
                ast = game_state['ast']
                reb = game_state['reb']
                if top_performer == None or pts > top_performer[1]:
                    top_performer = (player_name, pts, ast, reb)
                    
        game_day = datetime.strptime(game['date'], "%Y-%m-%dT%H:%M:%S.%fZ").day
        if game['home_team_score'] == game['visitor_team_score'] == 0:
            notification_message = (
                        "\n" + "=" * 38 + "\n"
                        f" **This game will be played later!**\n"
                        f":basketball: **{game['home_team']['full_name']}**\n"
                        f":basketball: **{game['visitor_team']['full_name']} **\n"
                        "\n" + "=" * 38 + "\n"
                    )
        elif top_performer:
            notification_message = (
                        "\n" + "=" * 38 + "\n"
                        f":basketball: **{game['home_team']['full_name']} {game['home_team_score']}**\n"
                        f":basketball: **{game['visitor_team']['full_name']} {game['visitor_team_score']}**\n"
                        f":trophy: ** {top_performer[0]}, {top_performer[1]}pts / {top_performer[2]} ast / {top_performer[3]} reb**\n"
                        "\n" + "=" * 38 + "\n"
                    )

            
        if datetime.now(us_timezone).day == game_day:
            basketball_games['today'].append(notification_message)
        else:
            basketball_games['yesterday'].append(notification_message)
    return basketball_games
        
        
    
    
@app.route("/send")
def send():
    
    game_data = get_game_data()  #game data yesterday and today
    print("getting data")
    
    game_stats =  get_game_stats()  #stats yesterday and today
    print("getting state")
    
    basketball_games = get_result(game_data, game_stats)
    print("getting basket ball")
    
    webhook_url = 'https://discord.com/api/webhooks/1194944310852993075/STEHCw3REgL8QCUENXMQO79hea-4ScYy8Kv0xzJ94fl9fvw76UeH8TBLzyydn6bipXqV'
    # Calculate yesterday, today
    
    yesterday = (datetime.now(us_timezone) - timedelta(days=1)).strftime('%Y-%m-%d')
    today = datetime.now(us_timezone).strftime('%Y-%m-%d')
    
    
    # Yesterday's basketball games
    # Post the date time(Yesterday)
    requests.post(webhook_url, json={'content':f"\n\n\n:calendar: **{yesterday}**\n"})
    
    
    # print(basketball_games['today'])
    for game in basketball_games['yesterday']:
        data = {'content': game}
        requests.post(webhook_url, json=data)
        # print(response.status_code)

    # Today's basketball games
    # Post the date time(Today)
    requests.post(webhook_url, json={'content':f"\n\n\n:calendar: **{today}**\n"})
    for game in basketball_games['today']:
        data = {'content': game}
        requests.post(webhook_url, json=data)
        # print(response.status_code)
    print("Done")
    return 'Message sent to discord Posting channel!'
    





@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
    
