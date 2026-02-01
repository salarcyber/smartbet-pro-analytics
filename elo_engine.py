"""
Custom Elo Rating System for Soccer & Basketball
"""

import json
from datetime import datetime
from typing import Dict

class EloEngine:
    def __init__(self, sport: str = "soccer"):
        self.sport = sport
        self.ratings = self._load_ratings()
        
        if sport == "soccer":
            self.base_k = 32
            self.home_advantage = 100
            self.default_rating = 1500
        elif sport == "basketball":
            self.base_k = 20
            self.home_advantage = 70
            self.default_rating = 1500
    
    def _load_ratings(self) -> Dict:
        try:
            with open(f'data/{self.sport}_elo.json', 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_ratings(self):
        with open(f'data/{self.sport}_elo.json', 'w') as f:
            json.dump(self.ratings, f, indent=2)
    
    def get_rating(self, team: str) -> int:
        return self.ratings.get(team, {}).get('rating', self.default_rating)
    
    def get_form(self, team: str) -> float:
        form = self.ratings.get(team, {}).get('form', [1.5, 1.5, 1.5, 1.5, 1.5])
        weights = [1.5, 1.3, 1.1, 0.9, 0.7]
        weighted_form = sum(f * w for f, w in zip(form, weights)) / sum(weights)
        return weighted_form
    
    def expected_score(self, rating_a: int, rating_b: int, home_team: str = None, team_a: str = None) -> float:
        if home_team and team_a and team_a == home_team:
            rating_a += self.home_advantage
        elif home_team and team_a:
            rating_b += self.home_advantage
        
        expected = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
        return expected
    
    def predict_match(self, home_team: str, away_team: str) -> Dict:
        rating_home = self.get_rating(home_team)
        rating_away = self.get_rating(away_team)
        form_home = self.get_form(home_team)
        form_away = self.get_form(away_team)
        
        adjusted_home = rating_home + (form_home - 1.5) * 20
        adjusted_away = rating_away + (form_away - 1.5) * 20
        
        prob_home_win = self.expected_score(adjusted_home, adjusted_away, home_team, home_team)
        prob_away_win = self.expected_score(adjusted_away, adjusted_home, away_team, home_team)
        prob_draw = 1 - (prob_home_win + prob_away_win) if self.sport == "soccer" else 0
        
        if self.sport == "soccer":
            total = prob_home_win + prob_away_win + prob_draw
            prob_home_win /= total
            prob_away_win /= total
            prob_draw /= total
        
        return {
            'home_win_prob': prob_home_win,
            'away_win_prob': prob_away_win,
            'draw_prob': prob_draw,
            'home_rating': rating_home,
            'away_rating': rating_away,
            'home_form': form_home,
            'away_form': form_away
        }
