#DANI'S CODE:
import os
import json
import requests
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Anthropic client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

WARDROBE_FILE = "wardrobe.json"
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_current_city():
    """
    Detect the user's city using their IP address.
    """

    try:
        response = requests.get("http://ip-api.com/json", timeout=5)

        data = response.json()

        if data["status"] == "success":
            return data["city"]

        return "Tel Aviv"

    except Exception:
        return "Tel Aviv"

def get_weather(city):

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    )

    response = requests.get(url)

    print("Status Code:", response.status_code)
    print(response.text)

    data = response.json()

    if response.status_code != 200:
        return "Weather unavailable"

    return {
        "temperature": data["main"]["temp"],
        "condition": data["weather"][0]["main"]
    }

def save_item(item):
    try:
        with open(WARDROBE_FILE, "r") as file:
            wardrobe = json.load(file)
    except FileNotFoundError:
        wardrobe = []

    wardrobe.append(item)

    with open(WARDROBE_FILE, "w") as file:
        json.dump(wardrobe, file, indent=4)

    print("Item saved to wardrobe 👑")


def load_wardrobe():
    try:
        with open(WARDROBE_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def show_wardrobe():
    wardrobe = load_wardrobe()

    if not wardrobe:
        print("Your wardrobe is empty.")
        return

    print("\nYour Wardrobe:\n")

    for i, item in enumerate(wardrobe, start=1):
        print(f"{i}. {item['color']} {item['type']} ({item['category']})")


def run_chat():
    print("Welcome to Caissy 👗")
    city = get_current_city()
    print("Detected city:", city)
    weather = get_weather(city)
    print("Weather:", weather)
    print("Type 'exit' to quit.\n")

    system_message = """
You are Caissy, a Digital Wardrobe Agent.

Your job is to:
- Manage the user's wardrobe.
- Recommend outfits based on the wardrobe, weather, and occasion.
- Never recommend clothing that is not in the wardrobe unless marked as a suggestion. 
- ask about the occasion and the user's preferences before making recommendations.

Always respond in this format:

[Summary]:
One sentence repeating what the user asked.

[Response]:
Provide wardrobe updates and outfit recommendations.

[Next Step]:
Suggest one clear next action.
"""
#after conecting 2 agents change the system message.
    history = []

    while True:
        user_input = input(">> ")

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        weather = get_weather(city)
        wardrobe = load_wardrobe()

        history.append({
            "role": "user",
            "content": f"""
User request:
{user_input}

Current weather:
{weather}

Current wardrobe:
{json.dumps(wardrobe, indent=2)}
"""
        })

        try:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1000,
                temperature=0.7,
                system=system_message,
                messages=history
            )

            reply = response.content[0].text

            print("\nCaissy:")
            print(reply)
            print()

            history.append({
                "role": "assistant",
                "content": reply
            })

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    run_chat()