from dataclasses import dataclass
from coordinates import Coordinates

@dataclass
class WeatherForecast:
    """Class for storing weather and generating current status"""
    coords: Coordinates
    temp: int
    code_int: int

    @property
    def weather_code_emoji(self):
        match self.code_int:
            case 0:
                return "☀️"
            case 1|2:
                return "⛅️"
            case 3:
                return "☁️"
            case 45|48:
                return "🌁"
            case 51|53|55|56|57|61|63|65|66|67|80|81|82:
                return "🌧"
            case 71|73|75|77|85|86:
                return "🌨"
            case 95|96|99:
                return "⛈"
        return ""

    def generate_report(self) -> str:
        return f"The current weather in {self.coords.name}, {self.coords.country} is {self.temp}°C {self.weather_code_emoji}"
