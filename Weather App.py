# Import customtkinter for the modern-looking UI widgets
import customtkinter as ctk
# Import requests to make HTTP calls to the weather APIs
import requests

# URL for the geocoding API (turns a city name into latitude/longitude)
geo = "https://geocoding-api.open-meteo.com/v1/search"
# URL for the weather forecast API (gives us the actual weather data)
url = "https://api.open-meteo.com/v1/forecast"

# This dictionary translates Open-Meteo's numeric "weather codes"
# into human-readable text. The API returns numbers like 3 or 61,
# and we use this dictionary to show "Overcast" or "Slight rain" instead.
WEATHER_CODES = {
    0: "Clear sky",                                            # totally clear
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",      # cloud cover levels
    45: "Fog", 48: "Depositing rime fog",                      # foggy conditions
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",  # drizzle levels
    56: "Light freezing drizzle", 57: "Dense freezing drizzle",         # freezing drizzle
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",           # rain levels
    66: "Light freezing rain", 67: "Heavy freezing rain",               # freezing rain
    71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",  # snow levels
    77: "Snow grains",                                         # tiny snow grains
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",  # showers
    85: "Slight snow showers", 86: "Heavy snow showers",       # snow showers
    95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",  # storms
}

# Set the app to dark mode (looks nicer for weather apps)
ctk.set_appearance_mode("dark")


# This function runs every time the user clicks "Search" (or presses Enter).
# It does everything: geocode the city, fetch the weather, and update the UI.
def search():
    # Grab whatever text the user typed into the entry box
    city = entry.get()
    try:
        # ---- STEP 1: Turn the city name into coordinates ----
        # Build the query parameters for the geocoding API
        geo_params = {"name": city}
        # Send the request and parse the JSON response
        geodata = requests.get(geo, params=geo_params, timeout=5).json()

        # The API returns a list of matching places. We take the first one.
        # [0] means "first result" - usually the most relevant match.
        latitude = geodata["results"][0]["latitude"]      # north/south position
        longitude = geodata["results"][0]["longitude"]    # east/west position
        # Get the clean city name from the API (falls back to what user typed)
        city_name = geodata["results"][0].get("name", city)
        # Get the country name (empty string if not provided)
        country = geodata["results"][0].get("country", "")

        # ---- STEP 2: Fetch the current weather for those coordinates ----
        # Build the query parameters for the weather API
        coords = {
            "latitude": latitude,     # which place to get weather for
            "longitude": longitude,   # which place to get weather for
            # "current" tells the API which current-weather fields we want back.
            # Multiple fields are comma-separated in one long string.
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,"
                       "precipitation,weather_code,wind_speed_10m,wind_direction_10m",
            # "auto" makes the API return times in the location's local timezone
            "timezone": "auto",
        }

        # Send the weather request and parse the JSON response
        data = requests.get(url, params=coords, timeout=5).json()
        # The "current" key holds all the current-weather values we asked for
        current_data = data["current"]

        # ---- STEP 3: Pull each value out of the response ----
        temp = current_data["temperature_2m"]              # actual temperature in °C
        wind = current_data["wind_speed_10m"]              # wind speed in km/h
        humidity = current_data["relative_humidity_2m"]    # humidity percentage
        feels_like = current_data["apparent_temperature"]  # "feels like" temperature in °C
        precipitation = current_data["precipitation"]      # rain/snow amount in mm
        weather_code = current_data["weather_code"]        # numeric code (0-99)
        wind_dir = current_data["wind_direction_10m"]      # wind direction in degrees
        local_time = current_data["time"]                  # local time string

        # Translate the numeric weather code into readable text using our dictionary.
        # .get() returns "Unknown" if the code isn't in the dictionary.
        condition = WEATHER_CODES.get(weather_code, "Unknown")

        # ---- STEP 4: Update the UI with the new values ----
        # Update each label's text with the fresh weather data
        city_label.configure(text="Enter a City, Country or Town.")
        location_label.configure(text=f"{city_name}, {country}")        # "London, United Kingdom"
        condition_label.configure(text=condition)                       # "Partly cloudy"
        temperature_value.configure(text=f"{temp}°C")                   # "15°C"
        feels_like_value.configure(text=f"{feels_like}°C")              # "13°C"
        humidity_value.configure(text=f"{humidity}%")                   # "72%"
        wind_value.configure(text=f"{wind} km/h")                       # "12 km/h"
        wind_dir_value.configure(text=f"{wind_dir}°")                   # "180°"
        precipitation_value.configure(text=f"{precipitation} mm")       # "0.0 mm"
        time_value.configure(text=f"{local_time}")                      # "2024-01-15T14:30"
    except (KeyError, IndexError):
        # KeyError happens when a key is missing (e.g. API returned an error)
        # IndexError happens when "results" is empty (city not found)
        # Either way, show a friendly error to the user.
        city_label.configure(
            text="City not found. Please enter a valid city or full city name."
        )
        city_label.configure(text="Enter a City, Country or Town.")
        location_label.configure(text="Search a valid city, town or country to begin", font=("Arial", 24, "bold")
        )
      
        condition_label.configure(text="N/A")                       
        temperature_value.configure(text="N/A")                
        feels_like_value.configure(text="N/A")           
        humidity_value.configure(text="N/A")                   
        wind_value.configure(text="N/A")                       
        wind_dir_value.configure(text="N/A")                   
        precipitation_value.configure(text="N/A")       
        time_value.configure(text="N/A")                      
        
        # Show the error label again

# ---------------- BUILD THE WINDOW ----------------

# Create the main application window
root = ctk.CTk()
# Set the window title bar text
root.title("Weather App")

# Get the size of the user's screen (in pixels)
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Estimate the taskbar height so the window doesn't cover it
task_bar_height = 50
# The app's height = full screen height minus the taskbar
window_height = screen_height - task_bar_height

# Set the window size and position it at the top-left corner (0,0)
root.geometry(f"{screen_width}x{window_height}+0+0")

# Configure the main window's grid so it stretches properly:
# Row 0 (title) - weight 0 = fixed size, doesn't stretch
root.grid_rowconfigure(0, weight=0)
# Row 1 (search bar) - weight 0 = fixed size, doesn't stretch
root.grid_rowconfigure(1, weight=0)
# Row 2 (cards area) - weight 1 = takes ALL remaining space (stretches)
root.grid_rowconfigure(2, weight=1)
# Column 0 - weight 1 = stretches to fill the width
root.grid_columnconfigure(0, weight=1)

# ---------------- TITLE ROW ----------------
# A big bold title at the top of the window
title_label = ctk.CTkLabel(root, text="Weather App", font=("Arial", 60, "bold"))
# Place it in row 0, column 0, with some vertical padding, aligned to the top (north)
title_label.grid(row=0, column=0, pady=(20, 10), sticky="n")

# ---------------- SEARCH ROW ----------------
# A frame (invisible container) to group the search controls together
search_frame = ctk.CTkFrame(root, fg_color="transparent")
# Place the frame in row 1, centered at the top
search_frame.grid(row=1, column=0, pady=10, sticky="n")

# A label telling the user what to do
city_label = ctk.CTkLabel(
    search_frame, text="Enter a City, Country or Town.", font=("Arial", 16)
)
# Span both columns above the entry + button
city_label.grid(row=0, column=0, columnspan=2, pady=(0, 5))

# The text input box where the user types a city name
entry = ctk.CTkEntry(search_frame, width=300, font=("Arial", 16))
# Place the entry in the left column
entry.grid(row=1, column=0, padx=(0, 10))

# The button that triggers the search when clicked
button = ctk.CTkButton(
    search_frame, text="Search", command=search,     # runs search() when clicked
    font=("Arial", 16), width=140, height=40,        # size and font
    fg_color="darkgrey", hover_color="lightgrey",    # grey colors
    text_color="black"                                # black text on grey button
)
# Place the button in the right column next to the entry
button.grid(row=1, column=1)

# ---------------- CARDS AREA ----------------
# A big frame that holds all the weather "cards" (one per data point)
cards_frame = ctk.CTkFrame(root, fg_color="transparent")
# Place it in row 2 (the stretchy row) and let it expand in all directions
cards_frame.grid(row=2, column=0, sticky="nsew", padx=40, pady=(0, 40))

# Configure the cards grid to stretch evenly:
# 3 columns, each gets equal width (weight=1, uniform makes them equal)
for c in range(3):
    cards_frame.grid_columnconfigure(c, weight=1, uniform="card")
# 3 rows, each gets equal height
for r in range(3):
    cards_frame.grid_rowconfigure(r, weight=1, uniform="row")


# Helper function to build one "card" (a titled box showing one value).
# Returns the card frame AND the value label so we can update it later.
def make_card(parent, title, emoji):
    """Create a card frame with a title label and a value label."""
    # The card itself is a rounded frame
    card = ctk.CTkFrame(parent, corner_radius=95)
    # The header (title) of the card, e.g. "🌡️ Temperature"
    header = ctk.CTkLabel(
        card, text=f"{emoji} {title}", font=("Arial", 16, "bold")
    )
    # Pack the header near the top with some spacing
    header.pack(pady=(15, 5))
    # The big value label showing the number, e.g. "15°C" (starts as a dash)
    value = ctk.CTkLabel(card, text="—", font=("Arial", 28))
    # Pack the value below the header, expanding to fill the remaining card space
    value.pack(pady=(0, 15), expand=True)
    # Return both so the caller can update the value later
    return card, value


# ---------- Location banner (spans all 3 columns) ----------
# A wide card at the top of the cards area showing the searched city and condition
location_card = ctk.CTkFrame(cards_frame, corner_radius=15)
# Place it in row 0, spanning all 3 columns, stretching in all directions
location_card.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)
# The big city/country label inside the banner
location_label = ctk.CTkLabel(
    location_card, text="Search a city to begin", font=("Arial", 24, "bold")
)
location_label.pack(pady=10)
# The smaller weather-condition label (e.g. "Partly cloudy") inside the banner
condition_label = ctk.CTkLabel(location_card, text="", font=("Arial", 18))
condition_label.pack(pady=(0, 10))

# ---------- Row 1: Temperature, Feels like, Humidity ----------
# Temperature card (left column)
temp_card, temperature_value = make_card(cards_frame, "Temperature", "🌡️")
temp_card.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

# Feels-like card (middle column)
feels_card, feels_like_value = make_card(cards_frame, "Feels like", "🤔")
feels_card.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

# Humidity card (right column)
humidity_card, humidity_value = make_card(cards_frame, "Humidity", "💧")
humidity_card.grid(row=1, column=2, sticky="nsew", padx=10, pady=10)

# ---------- Row 2: Wind speed, Wind direction, Precipitation ----------
# Wind speed card (left column)
wind_card, wind_value = make_card(cards_frame, "Wind speed", "💨")
wind_card.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

# Wind direction card (middle column)
wind_dir_card, wind_dir_value = make_card(cards_frame, "Wind direction", "🧭")
wind_dir_card.grid(row=2, column=1, sticky="nsew", padx=10, pady=10)

# Precipitation card (right column)
precip_card, precipitation_value = make_card(cards_frame, "Precipitation", "🌧️")
precip_card.grid(row=2, column=2, sticky="nsew", padx=10, pady=10)

# ---------- Row 3: Local time (spans all 3 columns) ----------
# A wide card showing the local time at the searched location
time_card, time_value = make_card(cards_frame, "Local time", "🕒")
# Place it in row 3, spanning all 3 columns
time_card.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

# BONUS: Let the user press Enter instead of clicking "Search"
entry.bind("<Return>", lambda e: search())

# Start the app's main event loop (this is what keeps the window open)
root.mainloop()
