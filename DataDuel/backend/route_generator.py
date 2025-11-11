"""
Simple Route Generator for MVP
No LLM - uses form-based input and basic algorithms
"""
import json
from datetime import datetime

class SimpleRouteGenerator:
    """Generate simple routes based on distance preferences"""
    
    # Popular running routes database (hardcoded for MVP)
    POPULAR_ROUTES = [
        {
            "id": "route_1",
            "name": "Campus Loop",
            "distance_km": 5.0,
            "distance_miles": 3.1,
            "description": "Flat loop around campus with minimal traffic",
            "surface": "paved",
            "difficulty": "easy",
            "elevation_gain": 20,
            "estimated_time_min": 25
        },
        {
            "id": "route_2",
            "name": "Park Trail Run",
            "distance_km": 8.0,
            "distance_miles": 5.0,
            "description": "Scenic park trails with some hills",
            "surface": "mixed",
            "difficulty": "moderate",
            "elevation_gain": 85,
            "estimated_time_min": 42
        },
        {
            "id": "route_3",
            "name": "River Path",
            "distance_km": 10.2,
            "distance_miles": 6.3,
            "description": "Flat path along river, great for long runs",
            "surface": "paved",
            "difficulty": "moderate",
            "elevation_gain": 45,
            "estimated_time_min": 54
        },
        {
            "id": "route_4",
            "name": "Hill Challenge",
            "distance_km": 7.5,
            "distance_miles": 4.7,
            "description": "Challenging route with significant elevation",
            "surface": "paved",
            "difficulty": "hard",
            "elevation_gain": 180,
            "estimated_time_min": 45
        },
        {
            "id": "route_5",
            "name": "Downtown Circuit",
            "distance_km": 6.5,
            "distance_miles": 4.0,
            "description": "Urban route through city streets",
            "surface": "paved",
            "difficulty": "easy",
            "elevation_gain": 30,
            "estimated_time_min": 35
        }
    ]
    
    @classmethod
    def find_routes(cls, distance_km=None, difficulty=None, surface=None, max_results=3):
        """
        Find routes matching criteria
        
        Args:
            distance_km: Target distance in kilometers (will match within 20%)
            difficulty: 'easy', 'moderate', or 'hard'
            surface: 'paved', 'trail', or 'mixed'
            max_results: Maximum number of routes to return
            
        Returns:
            List of matching routes sorted by relevance
        """
        results = []
        
        for route in cls.POPULAR_ROUTES:
            score = 0
            
            # Distance matching (within 20% = good match)
            if distance_km:
                distance_diff = abs(route['distance_km'] - distance_km)
                distance_tolerance = distance_km * 0.2
                if distance_diff <= distance_tolerance:
                    score += 10 - (distance_diff / distance_tolerance * 5)
            
            # Difficulty matching
            if difficulty and route['difficulty'] == difficulty:
                score += 5
            
            # Surface matching
            if surface:
                if route['surface'] == surface:
                    score += 5
                elif route['surface'] == 'mixed':
                    score += 2
            
            results.append({
                **route,
                'match_score': score
            })
        
        # Sort by score
        results.sort(key=lambda x: x['match_score'], reverse=True)
        
        return results[:max_results]
    
    @classmethod
    def generate_custom_route(cls, distance_km, start_location=None):
        """
        Generate a simple out-and-back or loop route
        For MVP, this returns a template-based route
        
        Args:
            distance_km: Desired distance
            start_location: Starting point (optional for MVP)
            
        Returns:
            Generated route object
        """
        # Simple calculation for out-and-back
        one_way_km = distance_km / 2
        
        return {
            "id": f"custom_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "name": f"Custom {distance_km}km Route",
            "distance_km": distance_km,
            "distance_miles": round(distance_km * 0.621371, 1),
            "description": f"Out-and-back route ({one_way_km}km each way)",
            "surface": "paved",
            "difficulty": "moderate",
            "elevation_gain": int(distance_km * 10),
            "estimated_time_min": int(distance_km * 5.5),
            "custom": True
        }
    
    @classmethod
    def get_route_by_id(cls, route_id):
        """Get specific route by ID"""
        for route in cls.POPULAR_ROUTES:
            if route['id'] == route_id:
                return route
        return None
    
    @classmethod
    def get_all_routes(cls):
        """Get all available routes"""
        return cls.POPULAR_ROUTES

