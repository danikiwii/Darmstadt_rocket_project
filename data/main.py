# This script calls all other scripts and unifies every JSON in one file.
import subprocess
import json
import os

# Step 1: Run proces_data.py to generate result.json
subprocess.run(["python", "data/process_data.py"], check=True)

# Step 2: Run api_weather_process.py to generate weather_data.json
subprocess.run(["python", "data/api_weather_process.py"], check=True)

# Step 3: Load both JSONs and combine them
with open("data/result_process_data.json", "r") as f:
    flight_results = json.load(f)
with open("data/weather_data.json", "r") as f:
    weather = json.load(f)

# Step 4: Combine into a single JSON
combined = {
    "flight_results": flight_results,
    "weather": weather
}

# Step 5: Save the combined JSON
with open("results.json", "w") as f:
    json.dump(combined, f, indent=2)

print("Combined results saved to results.json")

