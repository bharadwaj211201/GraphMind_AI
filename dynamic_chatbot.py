from chatbot.cypher_generator import generate_cypher
from dynamic_graph_search import run_cypher
from chatbot.response_generator import generate_response


print("=" * 70)
print("GRAPHMIND AI (Dynamic Cypher)")
print("=" * 70)

while True:

    question = input("\nAsk : ")

    if question.lower() == "exit":
        break

    cypher = generate_cypher(question)

    print("\nGenerated Cypher:\n")
    print(cypher)

    try:
        graph_data = run_cypher(cypher)

        answer = generate_response(question, graph_data)

        print("\n" + "=" * 70)
        print(answer)
        print("=" * 70)

    except Exception as e:
        print("\nCypher Error:")
        print(e)