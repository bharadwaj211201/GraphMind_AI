from chatbot.cypher_generator import generate_cypher
from chatbot.cypher_executor import execute_cypher
from chatbot.dynamic_response_generator import summarize

print("=" * 70)
print("GRAPHMIND AI")
print("=" * 70)

while True:

    question = input("\nAsk : ")

    if question.lower() == "exit":
        break

    cypher = generate_cypher(question)

    print("\nGenerated Cypher\n")
    print(cypher)

    try:

        graph_data = execute_cypher(cypher)

    except Exception as e:

        print("\nCypher Error\n")
        print(e)
        continue

    answer = summarize(question, graph_data)

    print("\n" + "=" * 70)
    print(answer)
    print("=" * 70)