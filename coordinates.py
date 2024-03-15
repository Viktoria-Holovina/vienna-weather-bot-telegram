from dataclasses import dataclass

@dataclass
class Coordinates:
    """Class for storing city coordinates and location"""
    name: str
    country: str
    lat: float
    long: float
