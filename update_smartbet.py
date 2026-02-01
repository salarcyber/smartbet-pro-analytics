"""
SmartBet Pro Analytics - Main Update Script
Fetches data, runs models, generates HTML from Jinja2 template
"""

import os
import json
import requests
from datetime import datetime
import pytz
from jinja2 import Environment, FileSystemLoader

# Import our Elo engine
from elo_engine import EloEngine

print("🚀 SmartBet Pro Analytics Starting...")
print("=" * 60)

# Initialize Elo engines
soccer_elo = EloEngine(sport='soccer')
nba_elo = EloEngine(sport='basketball')

# Get API keys from environment
ODDS_API_KEY = os.getenv('ODDS_API_KEY')
FOOTBALL_DATA_KEY = os.getenv('FOOTBALL_DATA_KEY')
API_FOOTBALL_KEY = os.getenv('API_FOOTBALL_KEY')

print("✅ API keys loaded")
print(f"✅ Odds API: {'Connected' if ODDS_API_KEY else 'Missing'}")
print(f"✅ Football Data: {'Connected' if FOOTBALL_DATA_KEY else 'Missing'}")
print(f"✅ API Football: {'Connected' if API_FOOTBALL_KEY else 'Missing'}")

# Fetch today's Premier League fixtures
def fetch_pl_fixtures():
    """Fetch Premier League fixtures from Football-Data.org"""
    try:
        url = "https://api.football-data.org/v4/competitions/PL/matches"
        headers = {'X-Auth-Token': FOOTBALL_DATA_KEY}
        
        # Fetch ALL games from today (no status filter)
        params = {
            'dateFrom': datetime.now().strftime('%Y-%m-%d'),
            'dateTo': datetime.now().strftime('%Y-%m-%d')
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            fixtures = data.get('matches', [])
            print(f"✅ Found {len(fixtures)} Premier League fixtures today")
            return fixtures
        else:
            print(f"⚠️  Football-Data API returned status {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error fetching fixtures: {e}")
        return []

# Fetch betting odds
def fetch_odds():
    """Fetch betting odds from The Odds API"""
    try:
        url = "https://api.the-odds-api.com/v4/sports/soccer_epl/odds/"
        params = {
            'apiKey': ODDS_API_KEY,
            'regions': 'us,uk',
            'markets': 'h2h,totals',
            'oddsFormat': 'decimal'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Fetched odds for {len(data)} matches")
            return data
        else:
            print(f"⚠️  Odds API returned status {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error fetching odds: {e}")
        return []

# Generate HTML from template
def generate_html(matches_data):
    """Generate HTML from Jinja2 template with match data"""
    
    try:
        # Set up Jinja2 environment
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('base.html')
        
        # Get current time
        current_time = datetime.now(pytz.UTC)
        
        # Prepare template data
        template_data = {
            'current_date': current_time.strftime('%A, %B %d, %Y'),
            'current_time': current_time.strftime('%Y-%m-%d %H:%M:%S UTC'),
            'soccer_matches': matches_data,
            'nba_matches': []  # TODO: Add NBA later
        }
        
        # Render template
        html_output = template.render(**template_data)
        
        # Write to index.html
        with open('index.html', 'w') as f:
            f.write(html_output)
        
        print(f"✅ Generated HTML successfully")
        print(f"   Date: {template_data['current_date']}")
        print(f"   Time: {template_data['current_time']}")
        print(f"   Matches: {len(matches_data)}")
        return True
        
    except Exception as e:
        print(f"❌ Error generating HTML: {e}")
        import traceback
        traceback.print_exc()
        return False

# Main execution
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("📊 STARTING DATA FETCH")
    print("=" * 60)
    
    # Fetch fixtures
    fixtures = fetch_pl_fixtures()
    
    # Fetch odds
    odds = fetch_odds()
    
    # Process matches and generate predictions
    matches_data = []
    
    if fixtures:
        print("\n" + "=" * 60)
        print("🧮 GENERATING PREDICTIONS")
        print("=" * 60)
        
        for fixture in fixtures:  # Process ALL fixtures
            home_team = fixture['homeTeam']['name']
            away_team = fixture['awayTeam']['name']
            
            print(f"\n🎯 Analyzing: {home_team} vs {away_team}")
            
            # Get Elo prediction
            prediction = soccer_elo.predict_match(home_team, away_team)
            
            print(f"   Home Elo: {prediction['home_rating']}")
            print(f"   Away Elo: {prediction['away_rating']}")
            print(f"   Win Prob: {prediction['home_win_prob']:.1%} / {prediction['draw_prob']:.1%} / {prediction['away_win_prob']:.1%}")
            
            # Build match data dict
            match_data = {
                'home_team': home_team,
                'away_team': away_team,
                'home_rating': prediction['home_rating'],
                'away_rating': prediction['away_rating'],
                'home_win_prob': prediction['home_win_prob'],
                'draw_prob': prediction['draw_prob'],
                'away_win_prob': prediction['away_win_prob'],
                'venue': fixture.get('venue', 'TBD'),
                'time': fixture.get('utcDate', 'TBD')
            }
            
            matches_data.append(match_data)
    
    # Generate HTML from template
    print("\n" + "=" * 60)
    print("📄 GENERATING WEBSITE")
    print("=" * 60)
    generate_html(matches_data)
    
    print("\n" + "=" * 60)
    print("✅ UPDATE COMPLETE!")
    print("=" * 60)
    print(f"🕐 Finished at {datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}")
