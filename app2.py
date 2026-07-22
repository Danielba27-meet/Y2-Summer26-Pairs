#DANI'S CODE:
import os
import json
import base64
import requests
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Anthropic client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

WARDROBE_FILE = "wardrobe.json"
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather(city):

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    )

    response = requests.get(url)

    data = response.json()

    if response.status_code != 200:
        print("Weather Error:", data)
        return None

    return {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "condition": data["weather"][0]["main"],
        "description": data["weather"][0]["description"]
    }

def analyze_image(image_url):

    response = requests.get(image_url)

    if response.status_code != 200:
        return "Failed to download image."

    image_data = base64.b64encode(response.content).decode("utf-8")

    content_type = response.headers.get("Content-Type", "image/jpeg")

    response = client.messages.create(

        model="claude-3-5-sonnet-20241022",

        max_tokens=300,

        messages=[

            {
                "role": "user",
                "content": [

                    {
                        "type": "text",
                        "text": """
Analyze this clothing image.

Describe:
- clothing type
- color
- style
- material if possible
- occasion

Give only a short shopping description.
"""
                    },

                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": content_type,
                            "data": image_data
                        }
                    }

                ]
            }

        ]

    )

    return response.content[0].text

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


    print("getting weather")
    weather = get_weather("modiin")  # Replace with your city or use lat/lon for more accuracy

    print("Weather:", weather)
    print("Type 'exit' to quit.\n")

    system_message = """
You are Caissy, a Digital Wardrobe Agent.
You receive the user's current weather inside every user message under the heading "Current weather".

Your job is to:
- Manage the user's wardrobe.
- Recommend outfits based on the wardrobe, weather, and occasion.
- Never recommend clothing that is not in the wardrobe unless marked as a suggestion. 
- ask about the occasion and the user's preferences before making recommendations.

IMPORTANT:
- The weather information is already provided to you.
- Never say you don't have access to real-time weather.
- Always use the "Current weather" data when answering.
- If the weather says temperature, condition, humidity, etc., use those values in your recommendations.
- Only say weather is unavailable if "Current weather" is None.

Always respond in this format:
1.One sentence repeating what the user asked. (the summary)
2.Provide wardrobe updates and outfit recommendations.(the response)
3.Suggest one clear next action. (the next step)
"""
#after conecting 2 agents change the system message.
    history = []

    while True:
        user_input = input(">> ")

        image_url = input("Image URL (press Enter to skip): ")

        if image_url:
            description = analyze_image(image_url)
            print(description)

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        weather = get_weather("Jerusalem")  # Replace with your city or use lat/lon for more accuracy
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