import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from streamlit_agraph import agraph, Node, Edge, Config

from app.dashboard import get_dashboard_data
from chatbot.cypher_generator import generate_cypher
from chatbot.cypher_executor import execute_cypher
from chatbot.dynamic_response_generator import summarize


st.set_page_config(
    page_title="GraphMind AI",
    page_icon="🛰️",
    layout="wide"
)


NODE_COLORS = {
    "Mission": "#FF6B6B",
    "Organization": "#4ECDC4",
    "Person": "#FFD93D",
    "Location": "#6BCB77",
    "Date": "#A29BFE",
    "Default": "#A0A0A0"
}


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


def build_graph(graph_data):
    nodes = {}
    edges = []

    for row in graph_data:
        if not isinstance(row, dict):
            continue

        row_nodes = []
        rel_label = "RELATED_TO"

        # Separate nodes and relationship types from the executor's dictionary output
        for key, val in row.items():
            if isinstance(val, dict):
                if "properties" in val:
                    row_nodes.append((key, val))
                elif "relationship" in val:
                    rel_label = val["relationship"]

        # Register nodes in PyVis format
        created_node_ids = []
        for key, node_info in row_nodes:
            node_type = node_info.get("type", "Default")
            props = node_info.get("properties", {})
            
            # Extract printable entity name
            full_name = str(props.get("name", props.get("title", props.get("id", ""))))
            if not full_name or full_name == "{}":
                continue

            # Limit label text length for visual clarity
            display_label = full_name if len(full_name) <= 22 else full_name[:19] + "..."
            node_id = f"{node_type}:{full_name}"
            created_node_ids.append(node_id)

            if node_id not in nodes:
                nodes[node_id] = Node(
                    id=node_id,
                    label=display_label,
                    title=full_name,
                    size=28 if node_type == "Mission" else 20,
                    color=NODE_COLORS.get(node_type, NODE_COLORS["Default"]),
                    font={"color": "#FFFFFF", "size": 13}
                )

        # Connect pairs of nodes returned in the single record
        if len(created_node_ids) >= 2:
            edges.append(
                Edge(
                    source=created_node_ids[0],
                    target=created_node_ids[1],
                    label=rel_label,
                    color="#888888"
                )
            )

    return list(nodes.values()), edges


def render_graph(graph_data):
    if not graph_data:
        st.info("No graph data to display for this query.")
        return

    nodes, edges = build_graph(graph_data)

    if not nodes:
        st.info("No visual graph data found in the query result.")
        return

    config = Config(
        width=800,
        height=500,
        directed=True,
        physics=True,
        hierarchical=False,
        nodeHighlightBehavior=True,
        highlightColor="#F7A7A6",
        collapsible=False,
        node={"labelProperty": "label"},
        link={"labelProperty": "label", "renderItalic": True}
    )

    agraph(nodes=nodes, edges=edges, config=config)


def render_dashboard_tab():
    data = get_dashboard_data()

    st.subheader("Knowledge Graph Overview")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Missions", data["missions"])
    col2.metric("Organizations", data["organizations"])
    col3.metric("People", data["people"])
    col4.metric("Locations", data["locations"])
    col5.metric("Dates", data["dates"])

    st.markdown("---")

    left, right = st.columns(2)

    with left:
        st.markdown("### Missions")
        mission_df = pd.DataFrame(data["mission_list"])
        st.dataframe(mission_df, hide_index=True)

    with right:
        st.markdown("### Organizations")
        org_df = pd.DataFrame(data["organization_list"])
        st.dataframe(org_df, hide_index=True)


def render_chat_tab():
    st.subheader("Ask GraphMind AI")

    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(chat["question"])

        with st.chat_message("assistant"):
            st.write(chat["answer"])

            with st.expander("Generated Cypher"):
                st.code(chat["cypher"], language="cypher")

            with st.expander("Knowledge Graph", expanded=True):
                render_graph(chat["graph_data"])

            with st.expander("Raw Neo4j Result"):
                st.json(chat["graph_data"])

    question = st.chat_input("Ask about an ISRO mission...")

    if question:
        with st.chat_message("user"):
            st.write(question)

        with st.spinner("Thinking..."):
            cypher = generate_cypher(question)
            graph_data = execute_cypher(cypher)
            answer = summarize(question, graph_data)

        with st.chat_message("assistant"):
            st.write(answer)

            with st.expander("Generated Cypher"):
                st.code(cypher, language="cypher")

            with st.expander("Knowledge Graph", expanded=True):
                render_graph(graph_data)

            with st.expander("Raw Neo4j Result"):
                st.json(graph_data)

        st.session_state.chat_history.append({
            "question": question,
            "cypher": cypher,
            "graph_data": graph_data,
            "answer": answer,
            "timestamp": str(datetime.now())
        })


def render_sidebar():
    data = get_dashboard_data()

    st.sidebar.title("🛰️ GraphMind AI")
    st.sidebar.caption("ISRO Knowledge Graph Assistant")

    st.sidebar.markdown("---")

    st.sidebar.markdown("### Quick Stats")
    st.sidebar.write(f"Missions: {data['missions']}")
    st.sidebar.write(f"Organizations: {data['organizations']}")
    st.sidebar.write(f"People: {data['people']}")

    st.sidebar.markdown("---")

    if st.session_state.chat_history:
        history_json = json.dumps(st.session_state.chat_history, indent=2, default=str)

        st.sidebar.download_button(
            label="Download Chat History",
            data=history_json,
            file_name="graphmind_chat_history.json",
            mime="application/json"
        )

    if st.sidebar.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.caption("CDAC BDA Major Project")
    st.sidebar.caption("Team: Shashank, Bharadwaj")


render_sidebar()

st.title("GraphMind AI")
st.caption("Graph-Based Conversational Assistant for ISRO Missions")

tab1, tab2 = st.tabs(["💬 Chat Assistant", "📊 Dashboard"])

with tab1:
    render_chat_tab()

with tab2:
    render_dashboard_tab()