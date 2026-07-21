def shopping_agent():
    import os
    import base64
    from serpapi import GoogleSearch
    from anthropic import Anthropic
    from dotenv import load_dotenv
    from app2 import load_wardrobe
    load_dotenv()

    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


    # -----------------------------
    # 1. Search products online
    # -----------------------------

    def search_products(query):

        params = {
            "engine": "google_shopping",
            "q": query,
            "api_key": os.getenv("SERPAPI_API_KEY"),
            "gl": "il",
            "hl": "en",
            "currency": "ILS"
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        products = results.get("shopping_results", [])

        return products[:5]



    # -----------------------------
    # 2. Analyze clothing image
    # -----------------------------

    def analyze_image(image_path):

        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(
                image_file.read()
            ).decode("utf-8")


        response = client.messages.create(

            model="claude-3-5-sonnet-20241022",

            max_tokens=300,

            messages=[

                {
                    "role": "user",
                    "content":[

                        {
                            "type":"text",
                            "text":
                            """
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


        return response.content[0].text



    # -----------------------------
    # 3. Main Agent
    # -----------------------------

    def run_chat():

        print("StyleFinder 👗")
        print("Type 'exit' to quit")
        print("Type 'image' to search using a clothing photo")
        wardrobe = load_wardrobe()
        print(f"Your wardrobe contains {len(wardrobe)} items 👕")


        while True:

            user_input = input("\n>> ")


            if user_input.lower() == "exit":
                break



            # IMAGE SEARCH

            if user_input.lower() == "image":

                image_path = input(
                    "Enter image path: "
                )


                description = analyze_image(image_path)

                print(description)



                products = search_products(
                    description + " affordable"
                )



            # TEXT SEARCH

            else:

                products = search_products(user_input)



            # Show results


            if not products:

                print(
                    "\nNo matching products found."
                )

                continue



            print("\nSimilar products found:\n")


            for product in products:
                
                print("--------------------")

                print(
                    "Name:",
                    product.get("title")
                )

                print(
                    "Price:",
                    product.get("price")
                )

                print(
                    "Store:",
                    product.get("source")
                )

                print(
                    "Link:",
                    product.get("product_link")
                )


            print("Done ✅")

    run_chat()