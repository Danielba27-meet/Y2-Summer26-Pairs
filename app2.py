# DANI'S WARDROBE AGENT

import os
import json
import base64
import requests

from anthropic import Anthropic
from dotenv import load_dotenv


load_dotenv()


client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)


WARDROBE_FILE = "wardrobe.json"

OPENWEATHER_API_KEY = os.getenv(
    "OPENWEATHER_API_KEY"
)



# -----------------------------------
# Weather
# -----------------------------------

def get_weather(city):

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    )


    response = requests.get(url)

    data = response.json()


    if response.status_code != 200:
        return None


    return {

        "city": data["name"],

        "temperature": data["main"]["temp"],

        "condition": data["weather"][0]["main"],

        "description": data["weather"][0]["description"]

    }





# -----------------------------------
# Wardrobe Storage
# -----------------------------------

def save_item(item):


    try:

        with open(
            WARDROBE_FILE,
            "r"
        ) as file:

            wardrobe = json.load(file)


    except:

        wardrobe = []



    wardrobe.append(item)



    with open(
        WARDROBE_FILE,
        "w"
    ) as file:

        json.dump(
            wardrobe,
            file,
            indent=4
        )


    print(
        "✅ Item saved to wardrobe"
    )





def load_wardrobe():

    try:

        with open(
            WARDROBE_FILE,
            "r"
        ) as file:

            return json.load(file)


    except:

        return []






def show_wardrobe():


    wardrobe = load_wardrobe()


    if not wardrobe:

        print(
            "Your wardrobe is empty."
        )

        return



    print(
        "\nYour wardrobe:"
    )


    for i,item in enumerate(
        wardrobe,
        1
    ):

        print(
            f"{i}. {item['color']} {item['type']} ({item['category']})"
        )







# -----------------------------------
# Communication From Shopping Agent
# -----------------------------------

def save_product_to_wardrobe(product_name):


    prompt = f"""

Convert this shopping product into wardrobe JSON.

Product:
{product_name}


Return ONLY:

{{
"type":"",
"color":"",
"category":""
}}


Categories:

tops
bottoms
dresses
shoes
outerwear
accessories

"""



    response = client.messages.create(

        model="claude-haiku-4-5-20251001",

        max_tokens=200,

        messages=[

            {

                "role":"user",

                "content":prompt

            }

        ]

    )


    text = response.content[0].text.strip()



    # remove markdown formatting

    text = text.replace(
        "```json",
        ""
    )

    text = text.replace(
        "```",
        ""
    )

    text = text.strip()



    item = json.loads(
        text
    )



    save_item(item)


    return item







# -----------------------------------
# Image Analysis
# -----------------------------------

def analyze_image(image_url):


    response = requests.get(
        image_url
    )


    if response.status_code != 200:

        return None



    image_data = base64.b64encode(
        response.content
    ).decode(
        "utf-8"
    )



    result = client.messages.create(

        model="claude-3-5-sonnet-20241022",

        max_tokens=300,


        messages=[

            {

                "role":"user",

                "content":[


                    {

                        "type":"text",

                        "text":
"""
Analyze this clothing image.

Describe the clothing,
color,
style,
and occasion.
"""

                    },


                    {

                        "type":"image",

                        "source":{

                            "type":"base64",

                            "media_type":"image/jpeg",

                            "data":image_data

                        }

                    }

                ]

            }

        ]

    )


    return result.content[0].text







# -----------------------------------
# Wardrobe Agent Chat
# -----------------------------------

def run_chat():


    print(
"""
==============================
Welcome to Serena 👗
==============================

Commands:
switch - change agent
exit - quit

"""
    )



    history = []



    system_message = """

You are serena, a Digital Wardrobe Agent.

Help the user manage their wardrobe.

Recommend outfits using saved clothes.
you are an serena from the show "gossip girl" and you are a fashion expert.
you know everyting about the show, your king and love using emojis. every conversation you finish with "XOXO ICONE girlll" and with a fasion tip.

"""



    while True:


        user_input = input(
            "\nYou: "
        )


        if user_input.lower()=="exit":

            return "exit"



        if user_input.lower()=="switch":

            return "switch"




        wardrobe = load_wardrobe()

        weather = get_weather(
            "Jerusalem"
        )


        history.append({

            "role":"user",

            "content":f"""

User:
{user_input}


Weather:
{weather}


Wardrobe:
{json.dumps(wardrobe,indent=2)}

"""

        })



        response = client.messages.create(

            model="claude-haiku-4-5-20251001",

            max_tokens=1000,

            system=system_message,

            messages=history

        )


        reply = response.content[0].text



        print(
            "\nCaissy:"
        )

        print(reply)



        history.append({

            "role":"assistant",

            "content":reply

        })