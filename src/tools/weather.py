"""Weather lookup tool."""

from langchain_core.tools import tool


@tool
def get_weather(location: str) -> str:
    """Get the current weather for a location.

    Args:
        location: The city name
    """
    # Mock weather data
    weather_data = {
        "seoul": "Sunny, 15°C",
        "tokyo": "Cloudy, 18°C",
        "new york": "Rainy, 12°C",
        "london": "Foggy, 10°C",
        "paris": "Partly cloudy, 14°C",
    }

    location_lower = location.lower()
    return weather_data.get(
        location_lower,
        f"Weather data not available for {location}"
    )
