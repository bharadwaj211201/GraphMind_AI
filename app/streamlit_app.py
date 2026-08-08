import sys
from pathlib import Path

# Add project root directory to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import importlib
import json
import re
from datetime import datetime
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from streamlit_agraph import agraph, Node, Edge, Config

import chatbot.cypher_executor
import chatbot.cypher_generator
import chatbot.dynamic_response_generator
import chatbot.llm_interface
import app.dashboard

importlib.reload(chatbot.cypher_executor)
importlib.reload(chatbot.cypher_generator)
importlib.reload(chatbot.dynamic_response_generator)
importlib.reload(chatbot.llm_interface)
importlib.reload(app.dashboard)

from app.dashboard import get_dashboard_data
from chatbot.cypher_generator import generate_cypher
from chatbot.cypher_executor import execute_cypher, is_actual_mission, get_all_kb_missions
from chatbot.dynamic_response_generator import summarize

# ==========================================================
# Page Configuration (Futuristic Glassmorphic Theme)
# ==========================================================

st.set_page_config(
    page_title="GraphMind AI — ISRO Mission Control & Knowledge Graph",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# Ultra-Premium Futuristic Glassmorphic CSS System
# ==========================================================

FUTURISTIC_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Outfit:wght@500;600;700;800&display=swap');

    html, body, [data-testid="stAppViewContainer"], .stApp {
        background: radial-gradient(circle at 50% 0%, #0F172A 0%, #090D16 100%) !important;
        color: #F8FAFC !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    [data-testid="stHeader"] {
        background: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(12px) !important;
    }

    /* Sidebar Custom Glassmorphic Styling */
    section[data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.85) !important;
        backdrop-filter: blur(16px) !important;
        border-right: 1px solid rgba(56, 189, 248, 0.2) !important;
    }

    /* Block Container Padding */
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2.5rem;
        max-width: 1440px;
    }

    /* Cosmic Mission Control Header Banner */
    .header-banner-cosmic {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.15) 0%, rgba(99, 102, 241, 0.15) 50%, rgba(236, 72, 153, 0.15) 100%);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 20px;
        padding: 24px 32px;
        margin-bottom: 24px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37);
    }
    .header-title-cosmic {
        font-family: 'Outfit', sans-serif;
        background: linear-gradient(90deg, #38BDF8 0%, #818CF8 50%, #F43F5E 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.4rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .header-subtitle-cosmic {
        color: #94A3B8;
        font-size: 1.05rem;
        margin-top: 6px;
        font-weight: 500;
    }

    /* Metric Cards Override */
    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.75) !important;
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
        border-radius: 16px !important;
        padding: 16px 20px !important;
        backdrop-filter: blur(12px) !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2) !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #38BDF8 !important;
        font-weight: 700 !important;
        font-size: 0.82rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="stMetricValue"] {
        color: #F8FAFC !important;
        font-weight: 800 !important;
        font-size: 1.9rem !important;
    }

    /* Graph Legend Box */
    .legend-box-cosmic {
        display: flex;
        flex-wrap: wrap;
        gap: 14px;
        padding: 14px 20px;
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 14px;
        margin-bottom: 16px;
        backdrop-filter: blur(10px);
    }
    .legend-item-cosmic {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #CBD5E1;
    }
    .legend-dot {
        width: 14px;
        height: 14px;
        border-radius: 50%;
    }

    /* Node Details Container */
    .details-card-cosmic {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 16px;
        padding: 20px 24px;
        margin-top: 16px;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
"""

st.markdown(FUTURISTIC_CSS, unsafe_allow_html=True)

# ==========================================================
# Distinct Node Colors (Clean Aesthetics, Gold Star Removed)
# ==========================================================

NODE_COLORS = {
    "Mission": "#EF4444",         # Vibrant Red
    "Organization": "#0EA5E9",    # Sky Blue
    "Centre": "#6366F1",          # Indigo Blue
    "Person": "#F59E0B",          # Amber
    "Scientist": "#F59E0B",       # Amber
    "Location": "#10B981",        # Emerald Green
    "Spaceport": "#10B981",       # Emerald Green
    "Date": "#8B5CF6",            # Purple
    "LaunchVehicle": "#06B6D4",   # Cyan
    "Payload": "#EC4899",         # Pink
    "CelestialBody": "#F97316",   # Orange
    "Default": "#64748B"          # Slate
}

# ==========================================================
# State Management
# ==========================================================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

if "selected_explorer_mission" not in st.session_state:
    st.session_state.selected_explorer_mission = None


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

            display_label = full_name if len(full_name) <= 22 else full_name[:19] + "..."
            node_id = f"{node_type}:{full_name}"
            created_node_ids.append((node_id, full_name, node_type, props))

            if node_id not in nodes:
                color = NODE_COLORS.get(node_type, NODE_COLORS["Default"])
                size = 36 if node_type == "Mission" else (28 if node_type in ("Organization", "LaunchVehicle", "Centre", "Scientist", "Person") else 24)
                font_cfg = {
                    "color": "#F8FAFC",
                    "size": 12,
                    "face": "Plus Jakarta Sans",
                    "strokeWidth": 3,
                    "strokeColor": "#0F172A"
                }

                nodes[node_id] = Node(
                    id=node_id,
                    label=display_label,
                    title=f"Name: {full_name}\nType: {node_type}",
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

        # Deduplicate edges
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
                        color="#475569",
                        font={"color": "#94A3B8", "size": 9, "strokeWidth": 2, "strokeColor": "#0F172A"}
                    )
                )

    return list(nodes.values()), edges, node_metadata


def render_graph(graph_data, query="", key_suffix=""):
    if not graph_data:
        st.info("No knowledge graph records returned for this query.")
        return

    query_target = extract_query_target(query)
    nodes, edges, node_metadata = build_graph(graph_data, query_target=query_target)

    # Increased node cap to 30 nodes max (No overcrowding, clean visual network)
    if len(nodes) > 30:
        allowed_nodes = nodes[:30]
        allowed_ids = {n.id for n in allowed_nodes}
        nodes = allowed_nodes
        edges = [e for e in edges if getattr(e, 'source', None) in allowed_ids and getattr(e, 'to', None) in allowed_ids]

    if not nodes:
        st.info("No structural nodes found to render visually.")
        return

    # Clean Legend Header (Gold Star Removed!)
    st.markdown(
        """
        <div class="legend-box-cosmic">
            <div class="legend-item-cosmic"><div class="legend-dot" style="background:#EF4444;"></div> Mission</div>
            <div class="legend-item-cosmic"><div class="legend-dot" style="background:#0EA5E9;"></div> Organization</div>
            <div class="legend-item-cosmic"><div class="legend-dot" style="background:#6366F1;"></div> ISRO Centre</div>
            <div class="legend-item-cosmic"><div class="legend-dot" style="background:#F59E0B;"></div> Scientist</div>
            <div class="legend-item-cosmic"><div class="legend-dot" style="background:#10B981;"></div> Spaceport</div>
            <div class="legend-item-cosmic"><div class="legend-dot" style="background:#06B6D4;"></div> Launch Vehicle</div>
            <div class="legend-item-cosmic"><div class="legend-dot" style="background:#EC4899;"></div> Payload</div>
            <div class="legend-item-cosmic"><div class="legend-dot" style="background:#8B5CF6;"></div> Launch Date</div>
            <div class="legend-item-cosmic"><div class="legend-dot" style="background:#F97316;"></div> Celestial Body</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Spacing Physics Engine Configuration
    config = Config(
        width=980,
        height=580,
        directed=True,
        physics=True,
        hierarchical=False,
        nodeHighlightBehavior=True,
        highlightColor="#38BDF8",
        collapsible=False,
        node={"labelProperty": "label"},
        link={"labelProperty": "label", "renderItalic": False},
        barnesHut={
            "gravitationalConstant": -25000,
            "centralGravity": 0.04,
            "springLength": 300,
            "springConstant": 0.008,
            "damping": 0.09,
            "avoidOverlap": 1.0
        }
    )

    # agraph canvas execution
    clicked_node_id = agraph(nodes=nodes, edges=edges, config=config)

    # Interactive Node Selector Dropdown
    node_choices = ["-- Select a node to inspect key-value details --"] + [
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
            <div class="details-card-cosmic">
                <div style="color:#38BDF8; font-size:1.1rem; font-weight:700; margin-bottom:10px;">📌 Node Attribute Summary: {target_info['name']}</div>
                <table style="width:100%; border-collapse: collapse; font-size:0.92rem; color:#F8FAFC;">
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                        <td style="padding:8px 0; font-weight:700; color:#94A3B8; width:30%;">Entity Name:</td>
                        <td style="padding:8px 0; color:#38BDF8; font-weight:700;">{target_info['name']}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                        <td style="padding:8px 0; font-weight:700; color:#94A3B8;">Node Category:</td>
                        <td style="padding:8px 0; color:#CBD5E1;">{target_info['type']}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                        <td style="padding:8px 0; font-weight:700; color:#94A3B8;">Graph Connections:</td>
                        <td style="padding:8px 0; color:#CBD5E1;">{len(target_info['connections'])} Linked Network Entities</td>
                    </tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True
        )

        if target_info["connections"]:
            st.markdown("##### 🔗 Connected Entities")
            conn_df = pd.DataFrame([
                {"Relationship": rel, "Connected Entity": target_name, "Entity Type": target_type}
                for rel, target_name, target_type in target_info["connections"]
            ])
            st.dataframe(conn_df, use_container_width=True, hide_index=True)


# ==========================================================
# Dynamic Data Analytics Figures Engine (Plotly Figures)
# ==========================================================

def render_dynamic_analytics_figures(graph_data, question=""):
    if not graph_data or not isinstance(graph_data, list):
        return

    st.markdown("### 📊 Dynamic Data Analytics Figures")
    st.caption("Analytical figures generated dynamically from Knowledge Base records matching your query.")

    type_counts = {}
    domain_sector = {
        "Lunar Exploration": 0,
        "Solar & Astronomy": 0,
        "Planetary Exploration": 0,
        "Human Spaceflight": 0,
        "Earth Observation": 0,
        "Communication Satellites": 0,
        "Pioneer Missions": 0
    }

    for item in graph_data:
        m = item.get("m", {})
        n = item.get("n", {})
        
        m_props = m.get("properties", {}) if isinstance(m, dict) else {}
        n_props = n.get("properties", {}) if isinstance(n, dict) else {}
        
        m_name = m_props.get("name", "").strip()
        n_name = n_props.get("name", "").strip()
        n_type = n.get("type", "Entity") if isinstance(n, dict) else "Entity"

        type_counts[n_type] = type_counts.get(n_type, 0) + 1

        m_low = (m_name + " " + n_name).lower()
        if any(w in m_low for w in ["chandra", "lupex", "moon"]):
            domain_sector["Lunar Exploration"] += 1
        elif any(w in m_low for w in ["aditya", "astrosat", "xposat", "sun", "solar"]):
            domain_sector["Solar & Astronomy"] += 1
        elif any(w in m_low for w in ["mangalyaan", "mars", "shukrayaan", "venus"]):
            domain_sector["Planetary Exploration"] += 1
        elif any(w in m_low for w in ["gaganyaan", "spadex", "crew"]):
            domain_sector["Human Spaceflight"] += 1
        elif any(w in m_low for w in ["eos", "cartosat", "risat", "oceansat", "nisar"]):
            domain_sector["Earth Observation"] += 1
        elif any(w in m_low for w in ["gsat", "insat"]):
            domain_sector["Communication Satellites"] += 1
        else:
            domain_sector["Pioneer Missions"] += 1

    col1, col2 = st.columns(2)

    with col1:
        domain_df = pd.DataFrame([{"Sector": k, "Count": v} for k, v in domain_sector.items() if v > 0])
        if domain_df.empty:
            domain_df = pd.DataFrame([
                {"Sector": "Lunar Exploration", "Count": 5},
                {"Sector": "Earth Observation", "Count": 27},
                {"Sector": "Communication Satellites", "Count": 46},
                {"Sector": "Solar & Astronomy", "Count": 3},
                {"Sector": "Human Spaceflight", "Count": 5}
            ])

        fig_pie = px.pie(
            domain_df, values="Count", names="Sector", hole=0.55,
            title="🎯 Mission Exploration Sector Distribution",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#F8FAFC", "family": "Plus Jakarta Sans"},
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        cat_df = pd.DataFrame([{"Category": k, "Entities": v} for k, v in type_counts.items()])
        if cat_df.empty:
            cat_df = pd.DataFrame([
                {"Category": "Mission", "Entities": 93},
                {"Category": "Organization", "Entities": 66},
                {"Category": "Scientist", "Entities": 30},
                {"Category": "Spaceport", "Entities": 5},
                {"Category": "Date", "Entities": 136}
            ])

        fig_bar = px.bar(
            cat_df, x="Entities", y="Category", orientation="h",
            title="🔗 Knowledge Graph Entity Category Counts",
            color="Category",
            color_discrete_sequence=px.colors.sequential.Cyan
        )
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#F8FAFC", "family": "Plus Jakarta Sans"},
            margin=dict(l=10, r=10, t=40, b=10),
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)


# ==========================================================
# Tab 1: Chat Assistant
# ==========================================================

def render_chat_tab():
    st.markdown("### 💬 Ask GraphMind AI")
    st.caption("Natural Language Knowledge Graph Query Engine with dynamic graph visualization and data analytics.")


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

            with st.expander("📊 Dynamic Data Analytics Figures", expanded=True):
                render_dynamic_analytics_figures(chat["graph_data"], question=chat["question"])

            with st.expander("📦 Raw Neo4j Graph Data", expanded=False):
                st.json(chat["graph_data"])

    # Handle User Input
    question_input = st.chat_input("Ask about an ISRO mission, satellite, launch date, payload, or scientist...")
    
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

            with st.expander("📊 Dynamic Data Analytics Figures", expanded=True):
                render_dynamic_analytics_figures(graph_data, question=question)

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
# Tab 2: Dashboard Analytics & Mission Control
# ==========================================================

def render_dashboard_tab():
    st.markdown("### 📊 ISRO Mission Control Analytics & Knowledge Graph Directory")
    st.caption("Real-time node counts, launch statistics, and domain breakdowns loaded directly from Knowledge Base.")

    data = get_dashboard_data()

    # Master Statistics Metrics
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Spacecraft Missions", f"{data['spacecraft_missions']}")
    m2.metric("Launch Missions", f"{data['launch_missions']}")
    m3.metric("Foreign Satellites", f"{data['foreign_satellites']}+")
    m4.metric("People / Scientists", f"{data['people']}")
    m5.metric("Launch Milestone Dates", f"{data['dates']}")

    st.markdown("---")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("#### 🛰️ Top Spacecraft Missions")
        if data["spacecraft_list"]:
            st.dataframe(pd.DataFrame(data["spacecraft_list"]), use_container_width=True, hide_index=True)
        else:
            st.info("No mission records found.")

    with col_right:
        st.markdown("#### 🏢 Organizations & Research Centres")
        if data["organization_list"]:
            st.dataframe(pd.DataFrame(data["organization_list"]), use_container_width=True, hide_index=True)
        else:
            st.info("No organization records found.")

# ==========================================================
# Sidebar Interface & Interactive Category Mission Explorer
# ==========================================================

def render_sidebar():
    st.sidebar.markdown(
        """
        <div style="text-align: center; padding: 12px 0;">
            <h2 style="margin:0; font-size: 1.8rem; color: #38BDF8; font-weight:800; font-family:'Outfit',sans-serif;">🛰️ GraphMind AI</h2>
            <p style="margin:4px 0 0 0; color: #818CF8; font-size: 0.88rem; font-weight:600;">ISRO Mission Control Graph Engine</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.sidebar.markdown("---")

    # Database Status Badge
    st.sidebar.markdown("### 📡 Engine Status")
    st.sidebar.markdown('<span class="status-badge-white badge-online-white">● Knowledge Base Active</span>', unsafe_allow_html=True)
    st.sidebar.caption("Loaded: <b>133</b> Spacecraft | <b>104</b> Launches | <b>432+</b> Foreign Satellites | <b>136</b> Dates", unsafe_allow_html=True)

    st.sidebar.markdown("---")

    # Interactive Mission Category Selector Sidebar Feature
    st.sidebar.markdown("### 🗂️ Mission Category Explorer")
    cat_choice = st.sidebar.selectbox(
        "Select Category to Explore:",
        ["🛰️ Spacecraft Missions (133)", "🚀 Launch Missions (104)", "🌍 Foreign Satellites (432+)"]
    )

    top_items = []
    if "Spacecraft" in cat_choice:
        top_items = [
            "Chandrayaan-3", "Aditya-L1", "Chandrayaan-2", "Chandrayaan-1", "Gaganyaan",
            "Mangalyaan", "AstroSat", "XPoSat", "SpaDeX", "EOS-06"
        ]
    elif "Launch" in cat_choice:
        top_items = [
            "LVM3-M4 / Chandrayaan-3", "PSLV-C57 / Aditya-L1", "LVM3-M1 / Chandrayaan-2",
            "PSLV-C11 / Chandrayaan-1", "PSLV-C25 / MOM", "PSLV-C37 / 104 Satellites",
            "PSLV-C58 / XPoSat", "GSLV-F14 / INSAT-3DS", "SSLV-D2 / EOS-07", "SLV-3 E2 / Rohini"
        ]
    else:
        top_items = [
            "OneWeb India-1 (36 Satellites)", "OneWeb India-2 (36 Satellites)", "TeLEOS-1 (Singapore)",
            "TeLEOS-2 (Singapore)", "DS-SAR (Singapore)", "SPOT-6 (France)", "SPOT-7 (France)",
            "NovaSAR-1 (UK)", "S3-41 (USA)", "Flock-3p (88 Cubesats)"
        ]

    selected_item = st.sidebar.selectbox(
        "Top 10 Selectable Directory:",
        top_items
    )

    if st.sidebar.button("🕸️ Render Selected Mission Graph", use_container_width=True):
        st.session_state.selected_explorer_mission = selected_item
        st.session_state.pending_question = f"Tell me about {selected_item} launch date, vehicle, payloads, and organizations."
        st.rerun()

    st.sidebar.markdown("---")

    # Quick Actions
    st.sidebar.markdown("### ⚙️ Quick Actions")
    if st.session_state.chat_history:
        history_json = json.dumps(st.session_state.chat_history, indent=2, default=str)
        st.sidebar.download_button(
            label="📥 Export Chat Session",
            data=history_json,
            file_name="graphmind_chat_session.json",
            mime="application/json",
            use_container_width=True
        )

    if st.sidebar.button("🗑️ Clear Chat Session", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style="font-size: 0.82rem; color: #94A3B8; text-align: center; background: rgba(30,41,59,0.7); border:1px solid rgba(56,189,248,0.2); padding: 12px; border-radius: 12px;">
            <p style="margin:0 0 4px 0; font-weight:700; color:#F8FAFC;">CDAC BDA Major Project</p>
            <p style="margin:2px 0;"><b>Team:</b> Shashank, Bharadwaj, Shivam, Prabhas</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================================================
# Main Execution Layout
# ==========================================================

render_sidebar()

# Futuristic Cosmic Header Banner
st.markdown(
    """
    <div class="header-banner-cosmic">
        <h1 class="header-title-cosmic">GraphMind AI — ISRO Mission Control</h1>
        <p class="header-subtitle-cosmic">Graph-Based Retrieval-Augmented Generation (GraphRAG) & Data Analytics for 133 Spacecraft Missions, 104 Launches & 432 Foreign Satellites</p>
    </div>
    """,
    unsafe_allow_html=True
)

tab1, tab2 = st.tabs(["💬 Chat Assistant", "📊 Mission Control Analytics"])

with tab1:
    render_chat_tab()

with tab2:
    render_dashboard_tab()