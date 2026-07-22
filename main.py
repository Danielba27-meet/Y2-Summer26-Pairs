from app1 import run_chat as Yasmines_agent
from app2 import run_chat as Danis_agent


active_agent = "shopping"

print("""
Choose an agent:
1. Shopping Agent
2. Wardrobe Agent
""")

choice = input("> ")

if choice == "1":
    active_agent = "shopping"
else:
    active_agent = "wardrobe"


print("\nType 'switch' anytime to change agents.")
print("Type 'exit' to quit.\n")


while True:

    if active_agent == "shopping":

        result = Yasmines_agent()

    else:

        result = Danis_agent()


    if result == "exit":
        print("Goodbye!")
        break


    if result == "switch":

        if active_agent == "shopping":
            active_agent = "wardrobe"
            print("\nSwitched to Wardrobe Agent 👗\n")

        else:
            active_agent = "shopping"
            print("\nSwitched to Shopping Agent 🛍\n")