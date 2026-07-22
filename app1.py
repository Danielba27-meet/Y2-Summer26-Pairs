def shopping_agent():

    import os
    import base64
    import requests

    from serpapi import GoogleSearch
    from anthropic import Anthropic
    from dotenv import load_dotenv

    from app2 import load_wardrobe

    load_dotenv()

    client = Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )

    # -----------------------------------
    # Search Products
    # -----------------------------------

    def search_products(query):

        params = {
            "engine": "google_shopping",
            "q": query,
            "api_key": os.getenv("SERPAPI_API_KEY"),
            "gl": "il",
            "hl": "en",
            "currency": "ILS",
            "num": 10
        }

        try:

            search = GoogleSearch(params)

            results = search.get_dict()

            shopping_results = results.get(
                "shopping_results",
                []
            )

            products = []

            for item in shopping_results[:5]:

                link = (
                    item.get("product_link")
                    or item.get("offer_link")
                    or item.get("merchant_link")
                    or item.get("link")
                    or item.get("redirect_link")
                    or "No link available"
                )

                products.append({

                    "title": item.get(
                        "title",
                        "Unknown Product"
                    ),

                    "price": item.get(
                        "price",
                        "Unknown"
                    ),

                    "store": item.get(
                        "source",
                        "Unknown Store"
                    ),

                    "link": link

                })

            return products

        except Exception as e:

            print("\nSearch Error:", e)

            return []


    # -----------------------------------
    # Analyze Clothing Image
    # -----------------------------------

    def analyze_image(image_bytes):

        image_data = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        response = client.messages.create(

            model="claude-sonnet-4-5",

            max_tokens=300,

            messages=[

                {

                    "role": "user",

                    "content": [

                        {

                            "type": "text",

                            "text": """
You are a fashion shopping assistant.

Look at this image.

Return ONLY a Google Shopping search query.

Examples:

black nike hoodie

white adidas sneakers

beige oversized knitted sweater

red floral maxi dress

Do not explain.

Only return the search keywords.
"""

                        },

                        {

                            "type": "image",

                            "source": {

                                "type": "base64",

                                "media_type": "image/jpeg",

                                "data": image_data

                            }

                        }

                    ]

                }

            ]

        )

        return response.content[0].text.strip()
        # -----------------------------------
    # Download Image
    # -----------------------------------

    def download_image(image_url):

        try:

            response = requests.get(
                image_url,
                timeout=15
            )

            response.raise_for_status()

            return response.content

        except requests.exceptions.RequestException as e:

            print("Couldn't download image.")
            print(e)

            return None


    # -----------------------------------
    # Display Products
    # -----------------------------------

    def show_products(products):

        if not products:

            print(" Sorry, I couldn't find any matching products.")

            return

        print(" are the best matches I found:")

        for i, product in enumerate(products, start=1):

            print("=" * 60)

            print(f"{i}. {product['title']}")
            print(f" Price : {product['price']}")
            print(f" Store : {product['store']}")
            print(f" Link  : {product['link']}")

        print("\nHappy shopping! ")


    # -----------------------------------
    # Main Chat
    # -----------------------------------

    def run_chat():

        wardrobe = load_wardrobe()

        print("\n====================================")
        print("Welcome to StyleFinder!")
        print("====================================")

        print("\nYour wardrobe contains {len(wardrobe)} items ")

        print("\nYou can:")

        print("- Describe what you're looking for")
        print("- Type image to search using an image URL")
        print("- Type exit to quit")

        while True:

            user_input = input("You: ").strip()

            if not user_input:

                continue

            if user_input.lower() == "exit":

                print("\nSee you next time ")

                break

            if user_input.lower() == "image":

                image_url = input(
                    "\nPaste the image URL:\n> "
                ).strip()

                image_bytes = download_image(
                    image_url
                )

                if image_bytes is None:

                    continue

                print("\n Analyzing image...")
                try:

                    search_query = analyze_image(
                        image_bytes
                    )

                    print("\nDetected item:")
                    print(search_query)

                    print("\nSearching for similar products...")

                    products = search_products(
                        search_query
                    )

                    show_products(
                        products
                    )

                except Exception as e:

                    print("\nImage analysis failed.")

                    print(e)

                continue

            print("\nSearching...")

            products = search_products(
                user_input
            )

            show_products(
                products
            )
    run_chat()