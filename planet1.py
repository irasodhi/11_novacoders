import requests
import os
import re
from typing import Dict, Optional

# ---------------- PLANT DATABASE ----------------
PLANT_CARE_DB = {
    "ROSE": {"name": "Rosa indica", "common": "Rose", "min_temp": 15, "max_temp": 28, "light": "Full sun", "water": "Moderate", "family": "Rosaceae"},
    "TOMATO": {"name": "Solanum lycopersicum", "common": "Tomato", "min_temp": 15, "max_temp": 30, "light": "Full sun", "water": "Regular", "family": "Solanaceae"},
    "ALOE": {"name": "Aloe vera", "common": "Aloe Vera", "min_temp": 13, "max_temp": 29, "light": "Bright direct", "water": "Dry soil", "family": "Asphodelaceae"},
    "SUNFLOWER": {"name": "Helianthus annuus", "common": "Sunflower", "min_temp": 18, "max_temp": 35, "light": "Full sun", "water": "Moderate", "family": "Asteraceae"},
    "RICE": {"name": "Oryza sativa", "common": "Rice", "min_temp": 20, "max_temp": 35, "light": "Full sun", "water": "High water", "family": "Poaceae"},
    "WHEAT": {"name": "Triticum aestivum", "common": "Wheat", "min_temp": 10, "max_temp": 25, "light": "Full sun", "water": "Moderate", "family": "Poaceae"},
    "MARIGOLD": {"name": "Tagetes erecta", "common": "Marigold", "min_temp": 15, "max_temp": 30, "light": "Full sun", "water": "Moderate", "family": "Asteraceae"},
    "BASIL": {"name": "Ocimum basilicum", "common": "Basil", "min_temp": 18, "max_temp": 32, "light": "Full sun", "water": "Moist soil", "family": "Lamiaceae"},
    "LOTUS": {
    "name": "Nelumbo nucifera",
    "common": "Lotus",
    "min_temp": 20,
    "max_temp": 35,
    "light": "Full sun",
    "water": "Aquatic",
    "family": "Nelumbonaceae"
},

}

# ---------------- LOCATIONS ----------------
INDIAN_LOCATIONS = {
    "delhi": (28.7041, 77.1025),
    "mumbai": (19.0760, 72.8777),
    "rajpura": (30.6349, 76.5958),
    "punjab": (31.1048, 75.3453),
    "chennai": (13.0827, 80.2707),
    "bengaluru": (12.9716, 77.5946)
}

# ---------------- PLANTNET CONFIG ----------------
PLANTNET_API_KEY = "2b10KOFp2zRt1RnSrHU9iqqWgu"
PLANTNET_URL = "https://my-api.plantnet.org/v2/identify/all"

# =================================================
class UltimatePlantCare:
    def __init__(self):
        print("🌱 PlantBot AI - Ready!")

    # ---------------- IMAGE IDENTIFICATION ----------------
    def smart_identify_plant(self, image_path: str) -> Optional[Dict]:
        print(f"🔍 Analyzing image: {image_path}")

        plant = self.plantnet_identify(image_path)
        if plant and plant["confidence"] >= 20:
            print(f"✅ PlantNet detected: {plant['common']} ({plant['confidence']}%)")
            return plant

        print("⚠️ PlantNet failed — trying filename match")
        return self.filename_match(image_path)

    def plantnet_identify(self, image_path: str) -> Optional[Dict]:
        try:
            with open(image_path, "rb") as f:
                files = {"images": f}
                data = {"organs": "auto"}
                params = {"api-key": PLANTNET_API_KEY}

                response = requests.post(
                    PLANTNET_URL,
                    files=files,
                    data=data,
                    params=params,
                    timeout=20
                )

            print("🌐 PlantNet Status:", response.status_code)
            print("🧠 Raw PlantNet result:", result["results"][:1])

            if response.status_code != 200:
                return None

            result = response.json()

            if not result.get("results"):
                return None

            top = result["results"][0]
            confidence = round(top["score"] * 100, 1)
            species = top["species"]

            return {
                "name": species.get("scientificNameWithoutAuthor", "Unknown"),
                "common": species.get("commonNames", ["Unknown"])[0],
                "family": species.get("family", {}).get("scientificName", "Unknown"),
                "confidence": confidence
            }

        except Exception as e:
            print("❌ PlantNet Error:", e)
            return None

    # ---------------- FILENAME FALLBACK ----------------
    def filename_match(self, image_path: str) -> Optional[Dict]:
        filename = os.path.basename(image_path).lower()

        patterns = {
            r"rose|gulab": "ROSE",
            r"tomato|tamatar": "TOMATO",
            r"aloe|vera": "ALOE",
            r"sunflower|suraj": "SUNFLOWER",
            r"rice|chawal|paddy": "RICE",
            r"wheat|gandum": "WHEAT",
            r"marigold|gainda": "MARIGOLD",
            r"basil|tulsi": "BASIL",
            r"lotus|kamal": "LOTUS",
        }

        for pattern, key in patterns.items():
            if re.search(pattern, filename):
                plant = PLANT_CARE_DB[key]
                print(f"📁 Filename match: {plant['common']}")
                return {**plant, "confidence": 90}

        return None

    # ---------------- WEATHER ----------------
    def get_weather(self, city="rajpura") -> Dict:
        city = city.lower()
        if city in INDIAN_LOCATIONS:
            lat, lon = INDIAN_LOCATIONS[city]
            try:
                r = requests.get(
                    "https://api.open-meteo.com/v1/forecast",
                    params={
                        "latitude": lat,
                        "longitude": lon,
                        "current_weather": True,
                        "timezone": "Asia/Kolkata"
                    },
                    timeout=10
                )
                w = r.json()["current_weather"]
                return {"temp": w["temperature"], "city": city.title()}
            except:
                pass
        return {"temp": 25, "city": "Rajpura"}

    # ---------------- TEXT SEARCH ----------------
    def get_plant_care(self, text: str) -> Optional[Dict]:
        if not text:
            return None

        text = text.lower()
        for key, data in PLANT_CARE_DB.items():
            if key.lower() in text or data["common"].lower() in text:
                print(f"🔍 Text match: {data['common']}")
                return data
        return None

    # ---------------- ANALYSIS ----------------
    def analyze(self, plant: Dict, weather: Dict) -> Dict:
        temp = weather["temp"]
        min_t, max_t = plant["min_temp"], plant["max_temp"]

        if min_t <= temp <= max_t:
            status, tip = "✅ PERFECT", "Ideal growing conditions 🌱"
        elif temp > max_t:
            status, tip = "🌡️ TOO HOT", "Move plant to shade ☀️"
        else:
            status, tip = "🥶 TOO COLD", "Protect from cold ❄️"

        return {
            "plant": plant["common"],
            "temp": temp,
            "range": f"{min_t}-{max_t}°C",
            "status": status,
            "light": plant["light"],
            "water": plant["water"],
            "tip": tip
        }
