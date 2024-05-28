import requests

class SolarForecastService:
    
    @staticmethod
    def get_solar_forecast(lat, lon):
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=direct_radiation"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            forecast = []
            for i, hour in enumerate(data['hourly']['time']):
                forecast.append({
                    "dateAndTime": hour,
                    "solarRadiation": abs(data['hourly']['direct_radiation'][i])  # Strahlung in W/m²
                })
            return forecast
        else:
            print(f"Error fetching data: {response.status_code, response}")
            return []
        
    
    @staticmethod
    def calculate_solar_power(solar_radiation, einstellungen):
        return solar_radiation * einstellungen["surface"] / 1000 * 0.65