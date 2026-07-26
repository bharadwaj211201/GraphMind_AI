from chatbot.llm_cypher_generator import generate_cypher

print("=" * 60)
print("GRAPHMIND AI - LLM CYPHER GENERATOR")
print("=" * 60)

while True:

    question = input("\nAsk : ")

    if question.lower() == "exit":
        break

    cypher = generate_cypher(question)

    print("\nGenerated Cypher:\n")
    print(cypher)