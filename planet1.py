import requests
import os
import re
from typing import Dict, Optional, Any

# 🔥 COMPLETE PLANT DATABASE + BASIL
PLANT_CARE_DB = {
    "ROSE": {"name": "Rosa indica", "common": "Rose", "min_temp": 15.0, "max_temp": 28.0, "light": "Full sun", "water": "Moderate", "family": "Rosaceae"},
    "DAHLIA": {"name": "Dahlia pinnata", "common": "Dahlia", "min_temp": 10.0, "max_temp": 25.0, "light": "Full sun", "water": "Moist", "family": "Asteraceae"},
    "TOMATO": {"name": "Solanum lycopersicum", "common": "Tomato", "min_temp": 15.0, "max_temp": 30.0, "light": "Full sun", "water": "Regular", "family": "Solanaceae"},
    "ALOE": {"name": "Aloe vera", "common": "Aloe Vera", "min_temp": 13.0, "max_temp": 29.0, "light": "Bright direct", "water": "Dry soil", "family": "Asphodelaceae"},
    "VERA": {"name": "Aloe vera", "common": "Aloe Vera", "min_temp": 13.0, "max_temp": 29.0, "light": "Bright direct", "water": "Dry soil", "family": "Asphodelaceae"},
    "SUNFLOWER": {"name": "Helianthus annuus", "common": "Sunflower", "min_temp": 18.0, "max_temp": 35.0, "light": "Full sun", "water": "Moderate", "family": "Asteraceae"},
    "RICE": {"name": "Oryza sativa", "common": "Rice", "min_temp": 20.0, "max_temp": 35.0, "light": "Full sun", "water": "High water", "family": "Poaceae"},
    "WHEAT": {"name": "Triticum aestivum", "common": "Wheat", "min_temp": 10.0, "max_temp": 25.0, "light": "Full sun", "water": "Moderate", "family": "Poaceae"},
    "MAIZE": {"name": "Zea mays", "common": "Maize", "min_temp": 18.0, "max_temp": 32.0, "light": "Full sun", "water": "Moderate", "family": "Poaceae"},
    "POTATO": {"name": "Solanum tuberosum", "common": "Potato", "min_temp": 12.0, "max_temp": 25.0, "light": "Full sun", "water": "Moderate", "family": "Solanaceae"},
    "MARIGOLD": {"name": "Tagetes erecta", "common": "Marigold", "min_temp": 15.0, "max_temp": 30.0, "light": "Full sun", "water": "Moderate", "family": "Asteraceae"},
    "GAINDA": {"name": "Tagetes erecta", "common": "Marigold", "min_temp": 15.0, "max_temp": 30.0, "light": "Full sun", "water": "Moderate", "family": "Asteraceae"},
    "BASIL": {"name": "Ocimum basilicum", "common": "Basil", "min_temp": 18.0, "max_temp": 32.0, "light": "Full sun", "water": "Moist soil", "family": "Lamiaceae"},
}

INDIAN_LOCATIONS = {
    "delhi": (28.7041, 77.1025), "mumbai": (19.0760, 72.8777), "rajpura": (30.6349, 76.5958),
    "punjab": (31.1048, 75.3453), "chennai": (13.0827, 80.2707), "bengaluru": (12.9716, 77.5946)
}

PLANTNET_API_KEY = "2b10KOFp2zRt1RnSrHU9iqqWgu"
PLANTNET_URL = "https://my-api.plantnet.org/v2/identify/all"

class UltimatePlantCare:
    def __init__(self):
        self.INDIAN_LOCATIONS = INDIAN_LOCATIONS
        print("🌱 PlantBot AI - Ready!")

    def smart_identify_plant(self, image_path: str) -> Optional[Dict]:
        print(f"🔍 Analyzing image: {image_path}")
        
        if PLANTNET_API_KEY and len(PLANTNET_API_KEY) > 10:
            plant = self.plantnet_identify(image_path)
            if plant and plant.get('confidence', 0) >= 70:
                print(f"✅ PlantNet found: {plant['common']} ({plant['confidence']}%)")
                return plant
        
        plant = self.filename_smart_match(image_path)
        if plant:
            return plant
        return None

    def plantnet_identify(self, image_path: str) -> Optional[Dict]:
        try:
            with open(image_path, 'rb') as f:
                files = {'images': (os.path.basename(image_path), f, 'image/jpeg')}
                data = {'organs': ['auto']}
                params = {'api-key': PLANTNET_API_KEY}
                
                response = requests.post(PLANTNET_URL, files=files, data=data, params=params, timeout=20)
                
                if response.status_code == 200:
                    result = response.json()
                    if 'results' in result and result['results']:
                        top_result = result['results'][0]
                        confidence = top_result.get('score', 0) * 100
                        
                        if confidence >= 70:
                            species = top_result['species']
                            return {
                                'name': species.get('scientificNameWithoutAuthor', 'Unknown'),
                                'common': species.get('commonNames', ['Unknown'])[0] if species.get('commonNames') else 'Unknown Plant',
                                'family': species.get('family', 'Unknown'),
                                'confidence': round(confidence, 1)
                            }
        except Exception as e:
            print(f"❌ PlantNet Error: {e}")
        return None

    def filename_smart_match(self, image_path: str) -> Optional[Dict]:
        filename = os.path.splitext(os.path.basename(image_path or 'rose.jpg'))[0].lower()
        
        patterns = {
            r'rose|gulab|rosa': {'name': 'Rosa indica', 'common': 'Rose', 'family': 'Rosaceae', 'confidence': 92.0},
            r'wheat|gandum': {'name': 'Triticum aestivum', 'common': 'Wheat', 'family': 'Poaceae', 'confidence': 95.0},
            r'marigold|gainda': {'name': 'Tagetes erecta', 'common': 'Marigold', 'family': 'Asteraceae', 'confidence': 93.0},
            r'tomato|tamatar': {'name': 'Solanum lycopersicum', 'common': 'Tomato', 'family': 'Solanaceae', 'confidence': 95.0},
            r'aloe|vera': {'name': 'Aloe vera', 'common': 'Aloe Vera', 'family': 'Asphodelaceae', 'confidence': 97.0},
            r'sunflower|surajmukhi': {'name': 'Helianthus annuus', 'common': 'Sunflower', 'family': 'Asteraceae', 'confidence': 90.0},
            r'rice|chawal|paddy': {'name': 'Oryza sativa', 'common': 'Rice', 'family': 'Poaceae', 'confidence': 94.0},
            r'basil|tulsi': {'name': 'Ocimum basilicum', 'common': 'Basil', 'family': 'Lamiaceae', 'confidence': 92.0},
        }
        
        for pattern, data in patterns.items():
            if re.search(pattern, filename):
                print(f"📁 FILENAME MATCH: {data['common']}")
                return data
        
        return None

    def get_weather(self, city_input: Optional[str] = None) -> Dict:
        city = (city_input or 'rajpura').lower().strip()
        state_map = {"punjab": "rajpura"}
        
        if city in state_map:
            city = state_map[city]
        if city in self.INDIAN_LOCATIONS:
            lat, lon = self.INDIAN_LOCATIONS[city]
            try:
                url = "https://api.open-meteo.com/v1/forecast"
                params = {
                    'latitude': lat, 'longitude': lon, 'current_weather': True,
                    'temperature_unit': 'celsius', 'windspeed_unit': 'kmh', 'timezone': 'Asia/Kolkata'
                }
                r = requests.get(url, params=params, timeout=10)
                data = r.json()['current_weather']
                return {
                    'temp': float(data['temperature']),
                    'wind': float(data['windspeed']),
                    'city': city.title()
                }
            except:
                pass
        return {'temp': 22.5, 'wind': 8.2, 'city': 'Rajpura'}

    def get_plant_care(self, plant_name: str) -> Optional[Dict]:
        if not plant_name or len(plant_name.strip()) < 2:
            return None
        
        plant_upper = plant_name.upper().strip()
        plant_lower = plant_name.lower().strip()
        print(f"🔍 Text search for: '{plant_name}'")
        
        # 1️⃣ GREETINGS
        greetings = ["HEY", "HI", "HELLO", "HII", "NAMASTE", "START", "BEGIN"]
        if plant_upper in greetings:
            return None
        
        # 2️⃣ EXACT MATCH
        for key, data in PLANT_CARE_DB.items():
            if key in plant_upper:
                print(f"✅ EXACT MATCH: {data['common']}")
                return {**data, 'min_temp': float(data['min_temp']), 'max_temp': float(data['max_temp'])}
        
        # 3️⃣ FUZZY MATCH
        fuzzy_map = {
            "wheat": "WHEAT", "gandum": "WHEAT",
            "rice": "RICE", "chawal": "RICE", "paddy": "RICE",
            "tomato": "TOMATO", "tamatar": "TOMATO",
            "marigold": "MARIGOLD", "gainda": "MARIGOLD",
            "aloe": "ALOE", "vera": "VERA",
            "sunflower": "SUNFLOWER", "surajmukhi": "SUNFLOWER",
            "basil": "BASIL", "tulsi": "BASIL"
        }
        
        for keyword, db_key in fuzzy_map.items():
            if keyword in plant_lower:
                data = PLANT_CARE_DB[db_key]
                print(f"✅ FUZZY MATCH: {data['common']}")
                return {**data, 'min_temp': float(data['min_temp']), 'max_temp': float(data['max_temp'])}
        
        # 4️⃣ GENERIC CROP (lavender, mint, etc.)
        crop_keywords = ["lavender", "mint", "thyme", "rosemary", "sage", "oregano", "parsley", "coriander"]
        if any(keyword in plant_lower for keyword in crop_keywords):
            print(f"✅ GENERIC CROP: {plant_name.title()}")
            return {
                "name": f"{plant_name.title()} Crop",
                "common": f"{plant_name.title()}",
                "min_temp": 15.0, "max_temp": 28.0,
                "light": "Full sun", "water": "Moderate",
                "family": "Generic Herb"
            }
        
        print(f"❌ UNKNOWN: '{plant_name}'")
        return None

    def analyze(self, plant_info: Dict, weather: Dict) -> Dict:
        if not plant_info:
            return {}
            
        care = self.get_plant_care(plant_info.get('name', '') or plant_info.get('common', ''))
        if not care:
            return {}
        
        temp = float(weather.get('temp', 25.0))
        min_temp, max_temp = float(care['min_temp']), float(care['max_temp'])
        
        if min_temp <= temp <= max_temp:
            status, score, tip = "✅ PERFECT", 95, "Ideal growing conditions! 🌟"
        elif temp > max_temp:
            status, score, tip = "🌡️ HOT", 65, f"Move to shade (too hot by {temp-max_temp:.1f}°C) ☀️"
        else:
            status, score, tip = "🥶 COLD", 75, f"Protect from cold (needs {min_temp-temp:.1f}°C more) ❄️"
            
        return {
            'plant': care['common'], 'temp': temp, 'range': f"{min_temp:.0f}-{max_temp:.0f}°C",
            'status': status, 'score': score, 'light': care['light'], 
            'water': care['water'], 'tip': tip
        }