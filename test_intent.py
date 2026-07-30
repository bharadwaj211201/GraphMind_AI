from chatbot.intent_classifier import get_intent

print("=" * 60)
print("GRAPHMIND AI - INTENT TEST")
print("=" * 60)

while True:

    question = input("\nQuestion : ")

    if question.lower() == "exit":
        break

    intent = get_intent(question)

    print("\nIntent :", intent)