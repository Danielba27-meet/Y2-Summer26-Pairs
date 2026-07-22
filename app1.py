# YASMINE'S SHOPPING AGENT

import os
import base64
import requests

from serpapi import GoogleSearch
from anthropic import Anthropic
from dotenv import load_dotenv

from app2 import (
    save_product_to_wardrobe,
    load_wardrobe
)


# -----------------------------------
# Setup
# -----------------------------------

load_dotenv()


client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)


SERPAPI_API_KEY = os.getenv(
    "SERPAPI_API_KEY"
)




# -----------------------------------
# Search Products
# -----------------------------------

def search_products(query):


    print(
        "\n🔎 Searching:",
        query
    )


    params = {

        "engine": "google_shopping",

        "q": query,

        "api_key": SERPAPI_API_KEY,

        "gl": "il",

        "hl": "en",

        "currency": "ILS",

        "num": 10
    }



    try:


        search = GoogleSearch(
            params
        )


        results = search.get_dict()



        if "error" in results:

            print(
                "❌ SerpAPI Error:"
            )

            print(
                results["error"]
            )

            return []



        shopping_results = results.get(
            "shopping_results",
            []
        )



        products = []



        for item in shopping_results[:5]:


            products.append({

                "title":
                    item.get(
                        "title",
                        "Unknown"
                    ),

                "price":
                    item.get(
                        "price",
                        "Unknown"
                    ),

                "store":
                    item.get(
                        "source",
                        "Unknown"
                    ),

                "link":
                    item.get(
                        "product_link",
                        "No link"
                    )

            })



        return products



    except Exception as e:


        print(
            "Search error:",
            e
        )


        return []







# -----------------------------------
# Download Image
# -----------------------------------

def download_image(url):


    try:


        response = requests.get(
            url,
            timeout=15
        )


        print(
            "Image status:",
            response.status_code
        )

        print(
            "Image type:",
            response.headers.get(
                "Content-Type"
            )
        )



        response.raise_for_status()



        return response.content



    except Exception as e:


        print(
            "Image error:",
            e
        )


        return None






# -----------------------------------
# Claude Vision
# -----------------------------------

def analyze_image(image_bytes):


    image_data = base64.b64encode(
        image_bytes
    ).decode(
        "utf-8"
    )



    response = client.messages.create(

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
Your name is Blair. are a fashion shopping assistant.
you are an expert in fashion and shopping. You know everything about fashion trends, styles, and brands. You are very helpful and provide detailed information about clothing items, including their features, materials, and styling tips. 
you know everything about the show "gossip girl".
you finish every conversation with "XOXO ICONE girlll" and with a fashion tip.

Look at this clothing image.

Return ONLY a Google Shopping search query.

Example:

pink jeans women

black hoodie

white sneakers
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



    query = response.content[0].text.strip()


    print(
        "🤖 Claude:",
        query
    )


    return query







# -----------------------------------
# Display Products
# -----------------------------------

def show_products(products):


    if not products:

        print(
            "No products found."
        )

        return



    print(
        "\n🛍 Products:"
    )



    for i,product in enumerate(
        products,
        1
    ):

        print(
            "="*50
        )


        print(
            f"{i}. {product['title']}"
        )


        print(
            "Price:",
            product["price"]
        )


        print(
            "Store:",
            product["store"]
        )


        print(
            "Link:",
            product["link"]
        )







# -----------------------------------
# Shopping Agent
# -----------------------------------

def run_chat():


    print(
"""
================================
Welcome to StyleFinder 🛍
================================

Commands:

image  - search from image
switch - change agent
exit   - quit

"""
    )


    last_products = []

    selected_product = None




    while True:


        user_input = input(
            "\nYou: "
        ).strip()



        # EXIT

        if user_input.lower()=="exit":

            return "exit"



        # SWITCH

        if user_input.lower()=="switch":

            return "switch"





        # -----------------------------------
        # Buying detection
        # -----------------------------------

        buy_phrases = [

            "i bought it",

            "i bought this",

            "i purchased it",

            "save it",

            "save this",

            "add it",

            "add this",

            "put it in my wardrobe",

            "keep it"

        ]



        if any(
            phrase in user_input.lower()
            for phrase in buy_phrases
        ):


            if selected_product is None:


                print(
                    "Please select a product first."
                )


                continue




            print(
                "\nAdding to wardrobe..."
            )



            item = save_product_to_wardrobe(

                selected_product["title"]

            )



            print(
                "✅ Added:"
            )


            print(item)



            continue







        # -----------------------------------
        # Image Search
        # -----------------------------------

        if user_input.lower()=="image":


            image_url = input(
                "\nPaste image URL:\n> "
            )



            image = download_image(
                image_url
            )



            if image:


                query = analyze_image(
                    image
                )


                last_products = search_products(
                    query
                )


                show_products(
                    last_products
                )



            continue






        # -----------------------------------
        # Normal Search
        # -----------------------------------


        last_products = search_products(
            user_input
        )


        show_products(
            last_products
        )



        if last_products:


            choice = input(
                "\nWhich item interests you? (number or Enter): "
            )



            if choice.isdigit():


                selected_product = last_products[
                    int(choice)-1
                ]


                print(
                    "\nSelected:"
                )


                print(
                    selected_product["title"]
                )



                print(
"""
You can continue asking questions.

When you buy it say:
"I bought it"
"""
                )