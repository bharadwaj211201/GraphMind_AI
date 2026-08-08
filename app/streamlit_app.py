import sys
from pathlib import Path

# Add project root directory to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import json
from datetime import datetime
import pandas as pd
import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

from app.dashboard import get_dashboard_data
from chatbot.cypher_generator import generate_cypher
from chatbot.cypher_executor import execute_cypher
from chatbot.dynamic_response_generator import summarize

# ==========================================================
# Page Configuration (Forced Pure Light Theme)
# ==========================================================

st.set_page_config(
    page_title="GraphMind AI — ISRO Knowledge Graph",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# Pure White & Vibrant Color CSS System
# ==========================================================

PURE_LIGHT_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    /* Force Pure White Backgrounds Across All Containers */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    [data-testid="stHeader"] {
        background-color: #FFFFFF !important;
    }

    /* Sidebar Light Theme */
    section[data-testid="stSidebar"] {
        background-color: #F8FAFC !important;
        border-right: 1px solid #E2E8F0 !important;
    }

    /* Block Container Padding */
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2.5rem;
        max-width: 1400px;
    }

    /* Light Header Banner */
    .header-banner-white {
        background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 50%, #F0F9FF 100%);
        border: 1px solid #BAE6FD;
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        box-shadow: 0 4px 16px rgba(2, 132, 199, 0.06);
    }
    .header-title-white {
        color: #0369A1;
        font-size: 2.3rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .header-subtitle-white {
        color: #0284C7;
        font-size: 1.05rem;
        margin-top: 6px;
        font-weight: 500;
    }

    /* Metric Cards */
    div[data-testid="stMetric"] {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 14px !important;
        padding: 16px 20px !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.03) !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #64748B !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        text-transform: uppercase;
    }
    div[data-testid="stMetricValue"] {
        color: #0F172A !important;
        font-weight: 800 !important;
        font-size: 1.8rem !important;
    }

    /* Status Badges */
    .status-badge-white {
        display: inline-block;
        padding: 5px 14px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .badge-online-white {
        background: #DCFCE7;
        color: #15803D;
        border: 1px solid #86EFAC;
    }
    .badge-info-white {
        background: #E0F2FE;
        color: #0369A1;
        border: 1px solid #7DD3FC;
    }

    /* Graph Legend */
    .legend-box-white {
        display: flex;
        flex-wrap: wrap;
        gap: 14px;
        padding: 12px 18px;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
    }
    .legend-item-white {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #334155;
    }
    .legend-dot {
        width: 14px;
        height: 14px;
        border-radius: 50%;
    }

    /* Node Details Container */
    .details-card-white {
        background: #F8FAFC;
        border: 1px solid #CBD5E1;
        border-radius: 14px;
        padding: 20px 24px;
        margin-top: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    .details-card-header {
        color: #0284C7;
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 12px;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
"""

st.markdown(PURE_LIGHT_CSS, unsafe_allow_html=True)

# ==========================================================
# Distinct Node Colors
# ==========================================================

NODE_COLORS = {
    "Mission": "#EF4444",         # Crimson Red
    "Organization": "#0EA5E9",    # Sky Blue
    "Centre": "#6366F1",          # Indigo Blue
    "Person": "#F59E0B",          # Amber Gold
    "Scientist": "#F59E0B",       # Amber Gold
    "Location": "#10B981",        # Emerald Green
    "Spaceport": "#10B981",       # Emerald Green
    "Date": "#8B5CF6",            # Purple
    "LaunchVehicle": "#06B6D4",   # Cyan
    "Payload": "#EC4899",         # Rose Pink
    "CelestialBody": "#F97316",   # Orange
    "Default": "#64748B"          # Slate Grey
}

# ==========================================================
# State Management
# ==========================================================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

# ==========================================================
# ==========================================================
# Graph Builder (Clean Spacing, No Overlap & Target Highlighting)
# ==========================================================

def extract_query_target(question: str) -> str:
    if not question:
        return ""
    q_low = question.lower()
    targets = [
        "chandrayaan-3", "chandrayaan 3", "chandrayaan-2", "chandrayaan-1", "chandrayaan-4",
        "aditya-l1", "aditya l1", "gaganyaan", "mangalyaan", "astrosat", "xposat",
        "abdul kalam", "kalam", "sarabhai", "dhawan", "somanath", "sivan", "isro"
    ]
    for t in targets:
        if t in q_low:
            return t
    return ""


def build_graph(graph_data, query_target=""):
    nodes = {}
    edges = []
    seen_edge_keys = set()
    node_metadata = {}

    if not graph_data or not isinstance(graph_data, list):
        return [], [], {}

    target_clean = query_target.lower().replace("-", " ") if query_target else ""

    for row in graph_data:
        if not isinstance(row, dict):
            continue

        row_nodes = []
        rel_label = ""

        for key, val in row.items():
            if isinstance(val, dict):
                if "properties" in val:
                    row_nodes.append((key, val))
                elif "relationship" in val:
                    rel_label = val.get("relationship", "")

        created_node_ids = []
        for key, node_info in row_nodes:
            node_type = node_info.get("type", "Default")
            props = node_info.get("properties", {})

            full_name = str(props.get("name", props.get("title", props.get("id", "")))).strip()
            if not full_name or full_name == "{}":
                continue

            # Check if this node is the main query target keyword
            name_clean = full_name.lower().replace("-", " ")
            is_highlight_target = False
            if target_clean and (target_clean in name_clean or name_clean in target_clean):
                is_highlight_target = True

            display_label = full_name if len(full_name) <= 22 else full_name[:19] + "..."
            node_id = f"{node_type}:{full_name}"
            created_node_ids.append((node_id, full_name, node_type, props))

            if node_id not in nodes:
                if is_highlight_target:
                    color = "#FFD700"  # Vibrant Highlight Gold
                    size = 55         # Prominent size
                    font_cfg = {
                        "color": "#0F172A",
                        "size": 15,
                        "face": "Plus Jakarta Sans",
                        "strokeWidth": 4,
                        "strokeColor": "#FFD700"
                    }
                    lbl_text = f"⭐ {display_label}"
                else:
                    color = NODE_COLORS.get(node_type, NODE_COLORS["Default"])
                    size = 32 if node_type == "Mission" else (26 if node_type in ("Organization", "LaunchVehicle", "Centre", "Scientist", "Person") else 22)
                    font_cfg = {
                        "color": "#0F172A",
                        "size": 12,
                        "face": "Plus Jakarta Sans",
                        "strokeWidth": 3,
                        "strokeColor": "#FFFFFF"
                    }
                    lbl_text = display_label

                nodes[node_id] = Node(
                    id=node_id,
                    label=lbl_text,
                    title=f"Name: {full_name}\nType: {node_type}" + ("\n⭐ [MAIN QUERY TARGET]" if is_highlight_target else ""),
                    size=size,
                    color=color,
                    font=font_cfg
                )

                node_metadata[node_id] = {
                    "name": full_name,
                    "type": node_type,
                    "properties": props,
                    "connections": []
                }

        # Deduplicate edges & prevent overlap
        if len(created_node_ids) >= 2:
            src_id = created_node_ids[0][0]
            tgt_id = created_node_ids[1][0]
            edge_key = (src_id, tgt_id, rel_label)

            if src_id in node_metadata and tgt_id in node_metadata:
                node_metadata[src_id]["connections"].append((rel_label, node_metadata[tgt_id]["name"], node_metadata[tgt_id]["type"]))
                node_metadata[tgt_id]["connections"].append((rel_label, node_metadata[src_id]["name"], node_metadata[src_id]["type"]))

            if edge_key not in seen_edge_keys and src_id != tgt_id:
                seen_edge_keys.add(edge_key)
                edges.append(
                    Edge(
                        source=src_id,
                        target=tgt_id,
                        label=rel_label if len(rel_label) < 15 else rel_label[:12] + "..",
                        color="#94A3B8",
                        font={"color": "#64748B", "size": 9, "strokeWidth": 2, "strokeColor": "#FFFFFF"}
                    )
                )

    return list(nodes.values()), edges, node_metadata


def render_graph(graph_data, query="", key_suffix=""):
    if not graph_data:
        st.info("No knowledge graph records returned for this query.")
        return

    query_target = extract_query_target(query)
    nodes, edges, node_metadata = build_graph(graph_data, query_target=query_target)

    # Prevent graph canvas overcrowding by capping max nodes to 12
    if len(nodes) > 12:
        target_nodes = [n for n in nodes if "⭐" in str(n.label)]
        other_nodes = [n for n in nodes if "⭐" not in str(n.label)]
        allowed_nodes = target_nodes + other_nodes[:(12 - len(target_nodes))]
        allowed_ids = {n.id for n in allowed_nodes}
        nodes = allowed_nodes
        edges = [e for e in edges if e.source in allowed_ids and e.target in allowed_ids]

    if not nodes:
        st.info("No structural nodes found to render visually.")
        return


    # Legend Header
    st.markdown(
        """
        <div class="legend-box-white">
            <div class="legend-item-white"><div class="legend-dot" style="background:#FFD700;"></div> ⭐ Main Target</div>
            <div class="legend-item-white"><div class="legend-dot" style="background:#EF4444;"></div> Mission</div>
            <div class="legend-item-white"><div class="legend-dot" style="background:#0EA5E9;"></div> Organization</div>
            <div class="legend-item-white"><div class="legend-dot" style="background:#6366F1;"></div> ISRO Centre</div>
            <div class="legend-item-white"><div class="legend-dot" style="background:#F59E0B;"></div> Scientist</div>
            <div class="legend-item-white"><div class="legend-dot" style="background:#10B981;"></div> Spaceport</div>
            <div class="legend-item-white"><div class="legend-dot" style="background:#06B6D4;"></div> Launch Vehicle</div>
            <div class="legend-item-white"><div class="legend-dot" style="background:#EC4899;"></div> Payload</div>
            <div class="legend-item-white"><div class="legend-dot" style="background:#F97316;"></div> Celestial Body</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Wide Spacing Physics Engine Configuration (Zero Label Overlap)
    config = Config(
        width=920,
        height=540,
        directed=True,
        physics=True,
        hierarchical=False,
        nodeHighlightBehavior=True,
        highlightColor="#2563EB",
        collapsible=False,
        node={"labelProperty": "label"},
        link={"labelProperty": "label", "renderItalic": False},
        barnesHut={
            "gravitationalConstant": -22000,
            "centralGravity": 0.05,
            "springLength": 280,
            "springConstant": 0.008,
            "damping": 0.09,
            "avoidOverlap": 1.0
        }
    )

    # agraph canvas execution
    clicked_node_id = agraph(nodes=nodes, edges=edges, config=config)

    # Interactive Node Selector Dropdown & Inspector
    node_choices = ["-- Click a node in the graph or select from list below --"] + [
        f"{info['name']} ({info['type']})" for info in node_metadata.values()
    ]
    
    selected_option = st.selectbox(
        "🔍 Inspect Key-Value Details for Graph Node:",
        node_choices,
        key=f"select_{key_suffix}"
    )

    target_info = None
    if clicked_node_id and clicked_node_id in node_metadata:
        target_info = node_metadata[clicked_node_id]
    elif selected_option and selected_option != node_choices[0]:
        sel_name = selected_option.rsplit(" (", 1)[0]
        for n_info in node_metadata.values():
            if n_info["name"] == sel_name:
                target_info = n_info
                break

    # Display Node Key-Value Details Panel
    if target_info:
        st.markdown(
            f"""
            <div class="details-card-white">
                <div class="details-card-header">📌 Selected Node Key-Value Details</div>
                <table style="width:100%; border-collapse: collapse; font-size:0.92rem;">
                    <tr style="border-bottom: 1px solid #E2E8F0;">
                        <td style="padding:8px 0; font-weight:700; color:#0F172A; width:30%;">Node Name:</td>
                        <td style="padding:8px 0; color:#0284C7; font-weight:700;">{target_info['name']}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #E2E8F0;">
                        <td style="padding:8px 0; font-weight:700; color:#0F172A;">Entity Category / Type:</td>
                        <td style="padding:8px 0; color:#334155;">{target_info['type']}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #E2E8F0;">
                        <td style="padding:8px 0; font-weight:700; color:#0F172A;">Connected Relationships:</td>
                        <td style="padding:8px 0; color:#334155;">{len(target_info['connections'])} Linked Entities</td>
                    </tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True
        )

        if target_info["connections"]:
            st.markdown("##### 🔗 Connected Relationships & Nodes")
            conn_df = pd.DataFrame([
                {"Relationship": rel, "Connected Entity": target_name, "Entity Type": target_type}
                for rel, target_name, target_type in target_info["connections"]
            ])
            st.dataframe(conn_df, use_container_width=True, hide_index=True)

# ==========================================================
# Tab 1: Chat Assistant
# ==========================================================

def render_chat_tab():
    st.markdown("### 💬 Ask GraphMind AI")
    st.caption("Ask questions in natural language. GraphMind AI generates Cypher queries, retrieves graph triples, and synthesizes answers using Ollama.")

    # Sample Quick Prompts
    st.markdown("##### 💡 Suggested Questions")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🚀 Chandrayaan-3 Details", use_container_width=True):
            st.session_state.pending_question = "Tell me about Chandrayaan-3 mission, launch date, payloads, and organizations."
    with col2:
        if st.button("☀️ Aditya-L1 Solar Mission", use_container_width=True):
            st.session_state.pending_question = "Tell me about Aditya-L1 solar mission and its payloads."
    with col3:
        if st.button("👨‍🔬 APJ Abdul Kalam & ISRO", use_container_width=True):
            st.session_state.pending_question = "Who is APJ Abdul Kalam and what was his role in ISRO?"
    with col4:
        if st.button("📋 List All Missions", use_container_width=True):
            st.session_state.pending_question = "List all ISRO missions available in the knowledge graph."

    st.markdown("---")

    # Render Chat History
    for idx, chat in enumerate(st.session_state.chat_history):
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(f"**{chat['question']}**")

        with st.chat_message("assistant", avatar="🛰️"):
            st.markdown(chat["answer"])

            with st.expander("🔍 View Generated Cypher Query", expanded=False):
                st.code(chat["cypher"], language="cypher")

            with st.expander("🕸️ Interactive Knowledge Graph", expanded=True):
                render_graph(chat["graph_data"], query=chat["question"], key_suffix=f"hist_{idx}")

            with st.expander("📦 Raw Neo4j Graph Data", expanded=False):
                st.json(chat["graph_data"])

    # Handle User Input
    question_input = st.chat_input("Ask about an ISRO mission, satellite, payload, or scientist...")
    
    question = question_input or st.session_state.pending_question
    if question:
        st.session_state.pending_question = None

        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(f"**{question}**")

        with st.chat_message("assistant", avatar="🛰️"):
            with st.spinner("Analyzing Knowledge Graph & generating response..."):
                cypher = generate_cypher(question)
                graph_data = execute_cypher(cypher)
                answer = summarize(question, graph_data)

            st.markdown(answer)

            with st.expander("🔍 View Generated Cypher Query", expanded=False):
                st.code(cypher, language="cypher")

            with st.expander("🕸️ Interactive Knowledge Graph", expanded=True):
                render_graph(graph_data, query=question, key_suffix="live_new")

            with st.expander("📦 Raw Neo4j Graph Data", expanded=False):
                st.json(graph_data)

        st.session_state.chat_history.append({
            "question": question,
            "cypher": cypher,
            "graph_data": graph_data,
            "answer": answer,
            "timestamp": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        })


# ==========================================================
# Tab 2: Dashboard Analytics
# ==========================================================

def render_dashboard_tab():
    st.markdown("### 📊 Knowledge Graph Metrics & Entities")
    st.caption("Real-time node counts and entity breakdowns loaded directly from Neo4j / In-Memory Graph Engine.")

    try:
        data = get_dashboard_data()
    except Exception as e:
        st.error(f"Could not load dashboard data.\n\n`{e}`")
        return

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Missions & Satellites", data["missions"])
    m2.metric("Organizations", data["organizations"])
    m3.metric("People / Scientists", data["people"])
    m4.metric("Locations / Spaceports", data["locations"])
    m5.metric("Dates & Milestones", data["dates"])

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### 🚀 Space Missions Sample")
        if data["mission_list"]:
            mission_df = pd.DataFrame(data["mission_list"])
            st.dataframe(mission_df, use_container_width=True, hide_index=True)
        else:
            st.info("No mission records found.")

    with col_right:
        st.markdown("#### 🏢 Space Organizations & Centres")
        if data["organization_list"]:
            org_df = pd.DataFrame(data["organization_list"])
            st.dataframe(org_df, use_container_width=True, hide_index=True)
        else:
            st.info("No organization records found.")

# ==========================================================
# Sidebar Interface
# ==========================================================

def render_sidebar():
    st.sidebar.markdown(
        """
        <div style="text-align: center; padding: 12px 0;">
            <h2 style="margin:0; font-size: 1.7rem; color: #0369A1; font-weight:800;">🛰️ GraphMind AI</h2>
            <p style="margin:4px 0 0 0; color: #0284C7; font-size: 0.85rem; font-weight:600;">ISRO Knowledge Graph Assistant</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.sidebar.markdown("---")

    # Connection Status Badge
    st.sidebar.markdown("### 📡 Database Status")
    try:
        stats = get_dashboard_data()
        if stats.get("is_neo4j"):
            st.sidebar.markdown('<span class="status-badge-white badge-online-white">● Neo4j Live</span>', unsafe_allow_html=True)
            st.sidebar.caption(f"Connected to Neo4j Database<br>Total nodes: <b>{stats['missions'] + stats['organizations'] + stats['people'] + stats['locations'] + stats['dates']}</b>", unsafe_allow_html=True)
        else:
            st.sidebar.markdown('<span class="status-badge-white badge-info-white">● In-Memory Graph Ready</span>', unsafe_allow_html=True)
            st.sidebar.caption(f"Using local knowledge base graph<br>Loaded entities: <b>{stats['missions'] + stats['organizations'] + stats['people']}</b>", unsafe_allow_html=True)
    except Exception:
        st.sidebar.markdown('<span class="status-badge-white badge-info-white">● In-Memory Fallback</span>', unsafe_allow_html=True)

    st.sidebar.markdown("---")

    # Quick Actions
    st.sidebar.markdown("### ⚙️ Quick Actions")
    if st.session_state.chat_history:
        history_json = json.dumps(st.session_state.chat_history, indent=2, default=str)
        st.sidebar.download_button(
            label="📥 Export Chat History",
            data=history_json,
            file_name="graphmind_chat_history.json",
            mime="application/json",
            use_container_width=True
        )

    if st.sidebar.button("🗑️ Clear Chat Session", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style="font-size: 0.82rem; color: #334155; text-align: center; background: #FFFFFF; border:1px solid #CBD5E1; padding: 12px; border-radius: 10px;">
            <p style="margin:0 0 6px 0; font-weight:700; color:#0F172A;">CDAC BDA Major Project</p>
            <p style="margin:2px 0;"><b>Team:</b> Shashank, Bharadwaj, Shivam, Prabhas</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================================================
# Main Execution Layout
# ==========================================================

render_sidebar()

# Top Banner Header (Pure White Theme)
st.markdown(
    """
    <div class="header-banner-white">
        <h1 class="header-title-white">GraphMind AI</h1>
        <p class="header-subtitle-white">Graph-Based Retrieval-Augmented Generation (GraphRAG) for ISRO Space Missions</p>
    </div>
    """,
    unsafe_allow_html=True
)

tab1, tab2 = st.tabs(["💬 Chat Assistant", "📊 Analytics Dashboard"])

with tab1:
    render_chat_tab()

with tab2:
    render_dashboard_tab()