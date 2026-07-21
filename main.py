#how to import python file
from app1 import shopping_agent
from app2 import run_chat

choice = input("""
Choose an agent:
1. Shopping Agent
2. Wardrobe Agent

> """)

if choice == "1":
    shopping_agent()

elif choice == "2":
    run_chat()

else:
    print("Invalid choice.")