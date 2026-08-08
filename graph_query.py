# pyrefly: ignore [missing-import]
from neo4j import GraphDatabase
from chatbot.config import NEO4J_URI, USERNAME, PASSWORD

# =====================================================
# Neo4j Configuration
# =====================================================

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(USERNAME, PASSWORD)
)



# =====================================================
# Function to Execute Query
# =====================================================

def execute_query(query):

    with driver.session() as session:

        result = session.run(query)

        records = list(result)

        if not records:
            print("\nNo records found.\n")
            return

        print()

        for record in records:

            print(record)

        print(f"\nTotal Records Displayed : {len(records)}")


# =====================================================
# Menu
# =====================================================

while True:

    print("\n" + "=" * 60)
    print("GRAPHMIND AI - KNOWLEDGE GRAPH QUERY")
    print("=" * 60)

    print("1. Show Mission Nodes")
    print("2. Mission -> Organization")
    print("3. Mission -> Person")
    print("4. Mission -> Location")
    print("5. Mission -> Date")
    print("6. Count Nodes")
    print("7. Count Relationships")
    print("8. Exit")

    choice = input("\nEnter Choice : ")

    if choice == "1":

        query = """
        MATCH (m:Mission)
        RETURN m.name AS Mission
        LIMIT 20
        """

        execute_query(query)

    elif choice == "2":

        query = """
        MATCH (m:Mission)-[:HAS_ORGANIZATION]->(o:Organization)
        RETURN
        m.name AS Mission,
        o.name AS Organization
        LIMIT 20
        """

        execute_query(query)

    elif choice == "3":

        query = """
        MATCH (m:Mission)-[:HAS_PERSON]->(p:Person)
        RETURN
        m.name AS Mission,
        p.name AS Person
        LIMIT 20
        """

        execute_query(query)

    elif choice == "4":

        query = """
        MATCH (m:Mission)-[:HAS_LOCATION]->(l:Location)
        RETURN
        m.name AS Mission,
        l.name AS Location
        LIMIT 20
        """

        execute_query(query)

    elif choice == "5":

        query = """
        MATCH (m:Mission)-[:HAS_DATE]->(d:Date)
        RETURN
        m.name AS Mission,
        d.name AS Date
        LIMIT 20
        """

        execute_query(query)

    elif choice == "6":

        query = """
        MATCH (n)
        RETURN count(n) AS Total_Nodes
        """

        execute_query(query)

    elif choice == "7":

        query = """
        MATCH ()-[r]->()
        RETURN count(r) AS Total_Relationships
        """

        execute_query(query)

    elif choice == "8":

        break

    else:

        print("\nInvalid Choice")

driver.close()

print("\nDisconnected from Neo4j.")