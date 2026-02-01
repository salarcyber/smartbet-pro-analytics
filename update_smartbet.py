"""
SmartBet Pro Analytics - Main Update Script
Fetches data, runs models, generates HTML
"""

import os
import json
import requests
from datetime import datetime
import pytz
import re

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
        params = {
            'status': 'SCHEDULED',
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

# Generate updated HTML
def generate_html():
    """Generate the updated index.html file"""
    
    try:
        # Check if index.html exists
        if not os.path.exists('index.html'):
            print("⚠️  index.html not found - creating placeholder")
            with open('index.html', 'w') as f:
                f.write('<html><body><h1>SmartBet Pro - Updating...</h1></body></html>')
        
        with open('index.html', 'r') as f:
            html = f.read()
        
        # Update timestamp
        current_time = datetime.now(pytz.UTC)
        date_str = current_time.strftime('%A, %B %d, %Y')
        time_str = current_time.strftime('%I:%M %p UTC')
        
        # Replace any date pattern like "Saturday, January 31, 2026"
        date_pattern = r'[A-Z][a-z]+day,\s+[A-Z][a-z]+\s+\d{1,2},\s+\d{4}'
        if re.search(date_pattern, html):
            html = re.sub(date_pattern, date_str, html)
            print(f"✅ Updated date to: {date_str}")
        else:
            print("⚠️  Date pattern not found in HTML")
        
        # Add a comment with last update time
        update_comment = f'\n<!-- Last updated: {current_time.strftime("%Y-%m-%d %H:%M:%S UTC")} -->\n'
        if '</body>' in html:
            html = html.replace('</body>', f'{update_comment}</body>')
        
        with open('index.html', 'w') as f:
            f.write(html)
        
        print(f"✅ Updated HTML successfully")
        print(f"   Date: {date_str}")
        print(f"   Time: {time_str}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating HTML: {e}")
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
    
    # Generate predictions for each match
    if fixtures:
        print("\n" + "=" * 60)
        print("🧮 GENERATING PREDICTIONS")
        print("=" * 60)
        
        for fixture in fixtures:  # Process all fixtures
            home_team = fixture['homeTeam']['name']
            away_team = fixture['awayTeam']['name']
            
            print(f"\n🎯 Analyzing: {home_team} vs {away_team}")
            
            # Get Elo prediction
            prediction = soccer_elo.predict_match(home_team, away_team)
            
            print(f"   Home Elo: {prediction['home_rating']}")
            print(f"   Away Elo: {prediction['away_rating']}")
            print(f"   Win Prob: {prediction['home_win_prob']:.1%} / {prediction['draw_prob']:.1%} / {prediction['away_win_prob']:.1%}")
    
    # Update HTML
    print("\n" + "=" * 60)
    print("📄 UPDATING WEBSITE")
    print("=" * 60)
    generate_html()
    
    print("\n" + "=" * 60)
    print("✅ UPDATE COMPLETE!")
    print("=" * 60)
    print(f"🕐 Finished at {datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}")
