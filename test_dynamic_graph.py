from chatbot.llm_cypher_generator import generate_cypher
from chatbot.cypher_executor import execute_cypher
from chatbot.dynamic_response_generator import summarize

print("=" * 70)
print("GRAPHMIND AI - COMPLETE GRAPHRAG")
print("=" * 70)

while True:

    question = input("\nAsk : ")

    if question.lower() == "exit":
        break

    cypher = generate_cypher(question)

    print("\nGenerated Cypher:\n")
    print(cypher)

    graph_data = execute_cypher(cypher)

    print("\nGenerating Answer...\n")

    answer = summarize(question, graph_data)

    print("=" * 70)
    print(answer)
    print("=" * 70)