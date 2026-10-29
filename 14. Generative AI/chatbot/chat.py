from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

load_dotenv()

model = ChatGroq(model="openai/gpt-oss-120b")

print("Press 1 for funny mode")
print("Press 2 for sad mode")
print("Press 3 for angry mode")
print("Press 4 for sarcastic mode")

choice = int(input("Choose your chat mode: "))

if choice == 1:
    mode = "You are a funny AI agent who responds in a funny way in every interaction"
elif choice == 2:
    mode = "You are a sad AI agent who responds logicless depressing words in every interaction like you have lost everything"
elif choice == 3:
    mode = "You are a angry AI agent who responds aggressively and impatiently"
elif choice == 4:
    mode = "You are a sarcastic AI agent who taunts in every chat"
else:
    print("Invalid mode. Please choose 1, 2, 3, or 4.")
    exit()

messages = [
    SystemMessage(content=mode)
]

print("-------------------Type 0 to exit the application---------------------------")
print("--------------------------------AuraBot-------------------------------------")
while True:
    prompt = input("You: ")
    messages.append(HumanMessage(content=prompt))
    if prompt == "0":
        break 
    response = model.invoke(messages)
    messages.append(AIMessage(content=response.content))
    print(response.content)

