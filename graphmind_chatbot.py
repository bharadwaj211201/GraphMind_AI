from mission_parser import get_mission
from intent_classifier import get_intent
from graph_search import search_graph
from response_generator import generate_response

print("=" * 70)
print("GRAPHMIND AI")
print("Type exit to quit")
print("=" * 70)

while True:

    question = input("\nAsk : ")

    if question.lower() == "exit":
        break

    mission = get_mission(question)

    intent = get_intent(question)

    graph_data = search_graph(mission, intent)

    if not graph_data:
        print("\nNo information found.\n")
        continue

    answer = generate_response(question, graph_data)

    print("\n" + "=" * 70)
    print(answer)
    print("=" * 70)