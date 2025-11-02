"""
Enhanced Streamlit App for Eqip.ai - Complete IP Lifecycle Pipeline

Implements the full end-to-end flow:
User Input → IP Options → Contribution Attribution → Ownership Arrangement → Contract Drafting → License/Revenue Summary
"""

import os
import json
import time
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import streamlit as st
import httpx
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from io import BytesIO
import base64

# Configuration
API_BASE = os.getenv("API_BASE", "http://localhost:8000")
MAX_CONVERSATION_HISTORY = 5

# Page configuration
st.set_page_config(
    page_title="Eqip.ai - Complete IP Pipeline", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Professional & Classy Theme
st.markdown("""
<style>
/* Main styling */
.main-header {
    font-size: 3rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    margin-bottom: 2rem;
    font-weight: 700;
    letter-spacing: -1px;
    text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.stage-header {
    font-size: 1.4rem;
    color: #e2e8f0 !important;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 0.5rem;
    margin: 1.5rem 0 1rem 0;
    font-weight: 500;
}
.progress-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    color: white;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.stage-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 0.5rem 0;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: all 0.2s ease;
}
.stage-card:hover {
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transform: translateY(-1px);
}
.completed-stage {
    background: #f0fff4;
    border-color: #68d391;
    box-shadow: 0 2px 4px rgba(104, 211, 145, 0.2);
}
.active-stage {
    background: #fffaf0;
    border-color: #ed8936;
    box-shadow: 0 2px 4px rgba(237, 137, 54, 0.2);
}
.metric-card {
    background: #ffffff;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    margin: 0.5rem 0;
    border: 1px solid #e2e8f0;
}

/* Professional color scheme */
.stSelectbox > div > div {
    background-color: #f7fafc;
    border-color: #e2e8f0;
}
.stTextInput > div > div > input {
    background-color: #f7fafc;
    border-color: #e2e8f0;
}
.stTextArea > div > div > textarea {
    background-color: #f7fafc;
    border-color: #e2e8f0;
}

/* Remove large numbers and improve formatting */
.element-container h1 {
    display: none !important;
}
.stMarkdown h1 {
    font-size: 1.5rem !important;
    color: #2d3748 !important;
    margin: 0.5rem 0 !important;
}

/* Hide all unwanted large numbers */
.stMarkdown h1:first-child {
    display: none !important;
}

h1:contains("1") {
    display: none !important;
}

/* Force hide any standalone numbers */
.stMarkdown > h1:only-child {
    display: none !important;
}

/* Chat message content - dark text on white background */
.stChatMessage,
.stChatMessage .stMarkdown,
.stChatMessage .stMarkdown p,
.stChatMessage .stMarkdown div,
.stChatMessage .stMarkdown span,
.stChatMessage .stMarkdown ul,
.stChatMessage .stMarkdown li {
    color: #2d3748 !important;
    background-color: #ffffff !important;
}

/* All text inputs - dark text on white background */
input, textarea, .stTextInput input, .stTextArea textarea {
    color: #2d3748 !important;
    background-color: #ffffff !important;
}

/* Status messages - inherit from container */
.stSuccess .stMarkdown, .stInfo .stMarkdown, .stWarning .stMarkdown, .stError .stMarkdown {
    color: #2d3748 !important;
}

/* Main content areas - light text on dark background */
.main .stMarkdown {
    color: #e2e8f0 !important;
}

/* Headers and titles - light text */
.stage-header, .main-header {
    color: #e2e8f0 !important;
}

/* Professional button styling */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-weight: 500;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
}

/* Chat interface styling */
.stChatMessage {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    margin: 0.5rem 0 !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
    color: #2d3748 !important;
}

.stChatMessage .stMarkdown {
    color: #2d3748 !important;
}

.stChatMessage .stMarkdown p {
    color: #2d3748 !important;
}

.stChatMessage .stMarkdown h1,
.stChatMessage .stMarkdown h2,
.stChatMessage .stMarkdown h3,
.stChatMessage .stMarkdown h4 {
    color: #1a365d !important;
}

.stChatMessage .stMarkdown ul,
.stChatMessage .stMarkdown li {
    color: #2d3748 !important;
}

/* Chat input styling */
.stChatInput {
    background: #f7fafc !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
}

.stChatInput > div > div > div > div > input {
    color: #2d3748 !important;
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
}

.stChatInput input {
    color: #2d3748 !important;
    background-color: #ffffff !important;
}

.stChatInput textarea {
    color: #2d3748 !important;
    background-color: #ffffff !important;
}

/* Chat input placeholder */
.stChatInput input::placeholder {
    color: #a0aec0 !important;
}

/* Spinner and loading text */
.stSpinner > div {
    color: #2d3748 !important;
}

.stAlert {
    color: #2d3748 !important;
}

/* Make chat full width */
.main .block-container {
    max-width: none !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* Professional sidebar */
.css-1d391kg {
    background-color: #f7fafc;
}

/* Hide unwanted elements */
.stDeployButton {
    display: none;
}

/* Aggressively hide large standalone numbers */
.stMarkdown h1:contains("1"),
.stMarkdown h1:contains("2"),
.stMarkdown h1:contains("3") {
    display: none !important;
}

/* Hide numbered list headers that appear as large text */
.stChatMessage h1:first-of-type {
    display: none !important;
}

/* Override any large text in chat */
.stChatMessage h1 {
    display: none !important;
}

/* Ensure all chat text is properly styled */
.stChatMessage .stMarkdown > * {
    color: #2d3748 !important;
    font-size: 1rem !important;
}

/* Fix chat input specifically */
[data-testid="stChatInput"] input {
    color: #2d3748 !important;
    background-color: #ffffff !important;
}

[data-testid="stChatInput"] textarea {
    color: #2d3748 !important;
    background-color: #ffffff !important;
}

/* Selective text color based on background */
.stApp {
    color: #e2e8f0 !important;
}

/* Light backgrounds get dark text */
.stChatMessage,
.stage-card,
.metric-card,
.stSelectbox,
.stTextInput,
.stTextArea,
.stButton {
    color: #2d3748 !important;
}

/* Ensure sidebar has appropriate text color */
.css-1d391kg {
    color: #2d3748 !important;
}
</style>
""", unsafe_allow_html=True)

# Pipeline stages with formal icons
PIPELINE_STAGES = [
    {"id": "ip_options", "name": "IP Path Finder", "description": "Discover protection options", "icon": "🔍"},
    {"id": "attribution", "name": "Contribution Attribution", "description": "Analyze contributor efforts", "icon": "⚖️"},
    {"id": "ownership", "name": "Ownership Arrangement", "description": "Finalize ownership structure", "icon": "🏛️"},
    {"id": "contracts", "name": "Contract Drafting", "description": "Generate legal agreements", "icon": "📄"},
    {"id": "licensing", "name": "License & Summary", "description": "License recommendations", "icon": "⚖️"}
]

def initialize_session_state():
    """Initialize session state variables"""
    defaults = {
        "current_stage": 0,
        "asset_id": None,
        "asset_type": "software",
        "jurisdictions": ["UK"],
        "messages": [],
        "pipeline_data": {},
        "contributors": [],
        "contribution_events": [],
        "team_votes": [],
        "attribution_results": None,
        "ownership_arrangement": None,
        "generated_contracts": {},
        "license_recommendations": None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def render_progress_bar():
    """Render pipeline progress indicator"""
    current_stage = st.session_state.current_stage
    progress = (current_stage + 1) / len(PIPELINE_STAGES)
    
    st.markdown('<div class="progress-container">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.progress(progress)
        st.write(f"**Stage {current_stage + 1} of {len(PIPELINE_STAGES)}: {PIPELINE_STAGES[current_stage]['name']}**")
        st.write(PIPELINE_STAGES[current_stage]['description'])
    
    with col2:
        if current_stage > 0:
            if st.button("← Previous", key="prev_stage"):
                st.session_state.current_stage = max(0, current_stage - 1)
                st.rerun()
        
        if current_stage < len(PIPELINE_STAGES) - 1:
            # Check if current stage is complete
            stage_complete = check_stage_completion(current_stage)
            if st.button("Next →", key="next_stage", disabled=not stage_complete):
                st.session_state.current_stage = min(len(PIPELINE_STAGES) - 1, current_stage + 1)
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def check_stage_completion(stage_index: int) -> bool:
    """Check if a pipeline stage is complete"""
    if stage_index == 0:  # IP Options
        return len(st.session_state.messages) > 0
    elif stage_index == 1:  # Attribution
        return st.session_state.attribution_results is not None
    elif stage_index == 2:  # Ownership
        return st.session_state.ownership_arrangement is not None
    elif stage_index == 3:  # Contracts
        return len(st.session_state.generated_contracts) > 0
    elif stage_index == 4:  # Licensing
        return st.session_state.license_recommendations is not None
    return False

def render_stage_overview():
    """Render overview of all pipeline stages"""
    st.markdown("### Pipeline Overview")
    
    cols = st.columns(len(PIPELINE_STAGES))
    for i, (col, stage) in enumerate(zip(cols, PIPELINE_STAGES)):
        with col:
            is_completed = check_stage_completion(i)
            is_current = i == st.session_state.current_stage
            
            if is_completed:
                status_indicator = "●"
                status_color = "#68d391"
                card_class = "completed-stage"
            elif is_current:
                status_indicator = "●"
                status_color = "#ed8936"
                card_class = "active-stage"
            else:
                status_indicator = "○"
                status_color = "#a0aec0"
                card_class = ""
            
            st.markdown(f"""
            <div class="stage-card {card_class}">
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; color: {status_color}; margin-bottom: 0.5rem;">{status_indicator}</div>
                    <div style="font-weight: 600; margin: 0.5rem 0; color: #2d3748; font-size: 0.9rem;">{stage['name']}</div>
                    <div style="font-size: 0.75rem; color: #718096; line-height: 1.3;">{stage['description']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

async def call_api_async(endpoint: str, method: str = "POST", data: dict = None) -> dict:
    """Async API call helper"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        if method == "POST":
            response = await client.post(f"{API_BASE}{endpoint}", json=data)
        else:
            response = await client.get(f"{API_BASE}{endpoint}")
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return {}

def render_ip_options_stage():
    """Stage 1: IP Path Finder"""
    st.markdown('<div class="stage-header">IP Path Finder</div>', unsafe_allow_html=True)
    
    # Asset creation/selection - Full width
    if not st.session_state.asset_id:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.info("First, let's create an asset to analyze")
            if st.button("Create New Asset", key="create_asset"):
                try:
                    response = asyncio.run(call_api_async(
                        "/v1/assets",
                        data={
                            "type": st.session_state.asset_type,
                            "uri": "",
                            "contributors": []
                        }
                    ))
                    if response.get("asset_id"):
                        st.session_state.asset_id = response["asset_id"]
                        st.success(f"Created asset #{st.session_state.asset_id}")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error creating asset: {str(e)}")
        with col2:
            st.session_state.asset_type = st.selectbox(
                "Asset Type",
                ["software", "dataset", "media", "invention"],
                index=["software", "dataset", "media", "invention"].index(st.session_state.asset_type),
                key="asset_type_main"
            )
    else:
        st.success(f"Working with Asset ID: {st.session_state.asset_id}")
    
    # Chat interface for IP consultation - Full width
    if st.session_state.asset_id:
        st.markdown("### IP Consultation")
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask about IP protection options..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.write(prompt)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Analyzing IP options..."):
                    try:
                        response = asyncio.run(call_api_async(
                            "/v1/agents/ip-options",
                            data={
                                "asset_id": st.session_state.asset_id,
                                "questions": prompt,
                                "jurisdictions": st.session_state.jurisdictions,
                                "conversation_context": st.session_state.messages[-5:]
                            }
                        ))
                        
                        if response:
                            # Format response professionally without emojis
                            response_text = f"**Protection Options:**\n"
                            for option in response.get("options", []):
                                response_text += f"• {option}\n"
                            
                            response_text += f"\n**Risks to Consider:**\n"
                            for risk in response.get("risks", []):
                                response_text += f"• {risk}\n"
                            
                            response_text += f"\n**Next Steps:**\n"
                            for step in response.get("next_steps", []):
                                response_text += f"• {step}\n"
                            
                            if response.get("citations"):
                                response_text += f"\n**Citations:**\n"
                                for citation in response["citations"]:
                                    response_text += f"• {citation}\n"
                            
                            st.write(response_text)
                            st.session_state.messages.append({"role": "assistant", "content": response_text})
                            st.session_state.pipeline_data["ip_options"] = response
                        
                    except Exception as e:
                        error_msg = f"Sorry, I encountered an error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})

def render_attribution_stage():
    """Stage 2: Contribution Attribution"""
    st.markdown('<div class="stage-header">Contribution Attribution</div>', unsafe_allow_html=True)
    
    # Contributors management
    st.markdown("### Contributors")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Add contributor form
        with st.expander("Add Contributor", expanded=len(st.session_state.contributors) == 0):
            with st.form("add_contributor"):
                email = st.text_input("Email")
                name = st.text_input("Display Name")
                org = st.text_input("Organization (optional)")
                
                if st.form_submit_button("Add Contributor"):
                    if email and name:
                        contributor = {"email": email, "display_name": name, "org": org or None}
                        if contributor not in st.session_state.contributors:
                            st.session_state.contributors.append(contributor)
                            st.success(f"Added {name}")
                            st.rerun()
                    else:
                        st.error("Email and name are required")
    
    with col2:
        # Display current contributors
        if st.session_state.contributors:
            st.markdown("**Current Contributors:**")
            for i, contrib in enumerate(st.session_state.contributors):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"• {contrib['display_name']} ({contrib['email']})")
                with col_b:
                    if st.button("Remove", key=f"remove_contrib_{i}"):
                        st.session_state.contributors.pop(i)
                        st.rerun()
    
    # Contribution events
    if st.session_state.contributors:
        st.markdown("### Contribution Events")
        
        # Add contribution event
        with st.expander("Add Contribution Event"):
            with st.form("add_contribution"):
                contributor_email = st.selectbox(
                    "Contributor",
                    [c["email"] for c in st.session_state.contributors],
                    key="contributor_select"
                )
                event_type = st.selectbox(
                    "Contribution Type",
                    ["code", "design", "review", "documentation", "testing"],
                    key="event_type_select"
                )
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    lines_of_code = st.number_input("Lines of Code", min_value=0, value=0)
                with col_b:
                    hours_spent = st.number_input("Hours Spent", min_value=0.0, value=0.0, step=0.5)
                with col_c:
                    complexity = st.selectbox("Complexity", [1.0, 1.5, 2.0, 2.5, 3.0], index=0, key="complexity_select")
                
                description = st.text_area("Description (optional)")
                
                if st.form_submit_button("Add Event"):
                    event = {
                        "contributor_email": contributor_email,
                        "event_type": event_type,
                        "lines_of_code": lines_of_code,
                        "hours_spent": hours_spent,
                        "complexity_score": complexity,
                        "description": description,
                        "timestamp": datetime.now().isoformat()
                    }
                    st.session_state.contribution_events.append(event)
                    st.success("Added contribution event")
                    st.rerun()
        
        # Display events
        if st.session_state.contribution_events:
            st.markdown("**Contribution Events:**")
            events_df = pd.DataFrame(st.session_state.contribution_events)
            st.dataframe(events_df)
        
        # Run attribution analysis
        if st.button("Analyze Contributions", key="run_attribution"):
            if st.session_state.contributors:
                with st.spinner("Analyzing contributions..."):
                    try:
                        response = asyncio.run(call_api_async(
                            "/v1/agents/attribution/run",
                            data={
                                "asset_id": st.session_state.asset_id,
                                "contributors": st.session_state.contributors,
                                "contribution_events": st.session_state.contribution_events,
                                "team_votes": st.session_state.team_votes,
                                "mode": "hybrid"
                            }
                        ))
                        
                        if response:
                            st.session_state.attribution_results = response
                            st.success("Attribution analysis complete!")
                            st.rerun()
                    
                    except Exception as e:
                        st.error(f"Error in attribution analysis: {str(e)}")
        
        # Display attribution results
        if st.session_state.attribution_results:
            st.markdown("### Attribution Results")
            
            results = st.session_state.attribution_results
            
            # Create visualization
            attributions = results["attributions"]
            names = [attr["contributor_name"] for attr in attributions]
            weights = [attr["weight"] for attr in attributions]
            
            # Pie chart
            fig = px.pie(
                values=weights,
                names=names,
                title="Contribution Attribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Attribution table
            st.markdown("**Detailed Attribution:**")
            for attr in attributions:
                with st.expander(f"{attr['contributor_name']} - {attr['weight']:.1%}"):
                    st.write(f"**Rationale:** {attr['rationale']}")
                    if attr.get("breakdown"):
                        st.write("**Breakdown by type:**")
                        for contrib_type, score in attr["breakdown"].items():
                            if score > 0:
                                st.write(f"• {contrib_type}: {score:.2f}")
            
            # Methodology info
            st.info(f"**Methodology:** {results['methodology']} (Confidence: {results['confidence_score']:.1%})")

def render_ownership_stage():
    """Stage 3: Ownership Arrangement"""
    st.markdown('<div class="stage-header">Ownership Arrangement</div>', unsafe_allow_html=True)
    
    if not st.session_state.attribution_results:
        st.warning("Please complete the Contribution Attribution stage first.")
        return
    
    # Policy selection
    st.markdown("### 📋 Ownership Policy")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        policy_type = st.selectbox(
            "Select Ownership Policy",
            ["equal", "weighted", "funding_based", "time_vested"],
            format_func=lambda x: {
                "equal": "Equal Split - All contributors get equal shares",
                "weighted": "Weighted by Contribution - Shares based on attribution",
                "funding_based": "Funding-Based - Considers financial investment",
                "time_vested": "Time-Vested - Shares vest over time"
            }[x],
            key="policy_type_select"
        )
    
    with col2:
        total_shares = st.number_input("Total Shares", min_value=1000, value=1000000, step=1000)
    
    # Policy-specific parameters
    policy_params = {"total_shares": total_shares}
    
    if policy_type == "funding_based":
        st.markdown("**Funding Information:**")
        funding_data = {}
        for contrib in st.session_state.contributors:
            funding_amount = st.number_input(
                f"Funding from {contrib['display_name']} ($)",
                min_value=0.0,
                value=0.0,
                key=f"funding_{contrib['email']}"
            )
            if funding_amount > 0:
                funding_data[contrib["email"]] = funding_amount
        
        policy_params["funding"] = funding_data
        policy_params["sweat_equity_weight"] = st.slider(
            "Sweat Equity Weight", 0.0, 1.0, 0.3, 0.1,
            help="Proportion of ownership based on contributions vs funding"
        )
    
    elif policy_type == "time_vested":
        st.markdown("**Vesting Parameters:**")
        policy_params["vesting_period_months"] = st.number_input(
            "Vesting Period (months)", min_value=12, value=48, step=6
        )
        policy_params["cliff_months"] = st.number_input(
            "Cliff Period (months)", min_value=0, value=12, step=3
        )
        
        # Time data for each contributor
        time_data = {}
        for contrib in st.session_state.contributors:
            months = st.number_input(
                f"Months contributed - {contrib['display_name']}",
                min_value=0, value=12, step=1,
                key=f"time_{contrib['email']}"
            )
            time_data[contrib["email"]] = months
        policy_params["time_data"] = time_data
    
    # Generate ownership arrangement
    if st.button("Finalize Ownership Arrangement", key="finalize_ownership"):
        with st.spinner("Calculating ownership arrangement..."):
            try:
                response = asyncio.run(call_api_async(
                    "/v1/agents/allocation/finalize",
                    data={
                        "asset_id": st.session_state.asset_id,
                        "attribution_weights": st.session_state.attribution_results["attributions"],
                        "policy_type": policy_type,
                        "policy_params": policy_params
                    }
                ))
                
                if response:
                    st.session_state.ownership_arrangement = response
                    st.success("Ownership arrangement finalized!")
                    st.rerun()
            
            except Exception as e:
                st.error(f"Error finalizing ownership: {str(e)}")
    
    # Display ownership arrangement
    if st.session_state.ownership_arrangement:
        st.markdown("### 📊 Ownership Structure")
        
        arrangement = st.session_state.ownership_arrangement
        
        # Ownership table
        ownership_data = []
        for share in arrangement["ownership_table"]:
            ownership_data.append({
                "Contributor": share["contributor_name"],
                "Email": share["contributor_email"],
                "Shares": f"{share['shares']:,}",
                "Percentage": f"{share['percentage']:.2f}%",
                "Governance": share["governance_rights"]
            })
        
        df = pd.DataFrame(ownership_data)
        st.dataframe(df, use_container_width=True)
        
        # Visualization
        names = [share["contributor_name"] for share in arrangement["ownership_table"]]
        percentages = [share["percentage"] for share in arrangement["ownership_table"]]
        
        fig = go.Figure(data=[go.Bar(x=names, y=percentages)])
        fig.update_layout(
            title="Ownership Distribution",
            xaxis_title="Contributors",
            yaxis_title="Ownership Percentage",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Governance summary
        st.info(f"**Governance:** {arrangement['governance_summary']}")
        st.success(f"**Policy Applied:** {arrangement['policy_applied']}")

def render_contracts_stage():
    """Stage 4: Contract Drafting"""
    st.markdown('<div class="stage-header">Contract Drafting</div>', unsafe_allow_html=True)
    
    if not st.session_state.ownership_arrangement:
        st.warning("Please complete the Ownership Arrangement stage first.")
        return
    
    # Contract type selection
    st.markdown("### 📋 Contract Generation")
    
    contract_types = {
        "nda": "Non-Disclosure Agreement",
        "ip_assignment": "IP Assignment Agreement",
        "jda": "Joint Development Agreement",
        "revenue_share": "Revenue Sharing Addendum"
    }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_contract = st.selectbox(
            "Select Contract Type",
            list(contract_types.keys()),
            format_func=lambda x: contract_types[x],
            key="contract_type_select"
        )
    
    with col2:
        jurisdiction = st.selectbox(
            "Jurisdiction",
            ["US", "UK", "EU", "CA", "AU"],
            index=0,
            key="jurisdiction_select"
        )
    
    # Additional clauses
    additional_clauses_text = st.text_area(
        "Additional Clauses (optional)",
        placeholder="Enter any additional clauses or requirements..."
    )
    additional_clauses = additional_clauses_text.split('\n') if additional_clauses_text.strip() else []
    
    # Generate contract
    if st.button(f"Generate {contract_types[selected_contract]}", key="generate_contract"):
        with st.spinner("Generating contract..."):
            try:
                response = asyncio.run(call_api_async(
                    "/v1/agreements/generate",
                    data={
                        "asset_id": st.session_state.asset_id,
                        "contract_type": selected_contract,
                        "ownership_arrangement": st.session_state.ownership_arrangement,
                        "additional_clauses": additional_clauses,
                        "jurisdiction": jurisdiction
                    }
                ))
                
                if response:
                    st.session_state.generated_contracts[selected_contract] = response
                    st.success(f"{contract_types[selected_contract]} generated successfully!")
                    st.rerun()
            
            except Exception as e:
                st.error(f"Error generating contract: {str(e)}")
    
    # Display generated contracts
    if st.session_state.generated_contracts:
        st.markdown("### 📑 Generated Contracts")
        
        for contract_type, contract_data in st.session_state.generated_contracts.items():
            with st.expander(f"{contract_types.get(contract_type, contract_type)} - {contract_data['agreement_id'][:8]}..."):
                
                # Contract metadata
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"**Agreement ID:** {contract_data['agreement_id']}")
                    st.write(f"**Type:** {contract_data['contract_type']}")
                with col_b:
                    # Download button for contract
                    st.download_button(
                        "📥 Download Contract",
                        data=contract_data["draft_text"],
                        file_name=f"{contract_data['contract_type']}_agreement_{contract_data['agreement_id'][:8]}.txt",
                        mime="text/plain",
                        key=f"download_{contract_type}"
                    )
                    
                    # Sign URL (placeholder - would integrate with DocuSign/HelloSign in production)
                    if st.button("📝 Sign Contract", key=f"sign_{contract_type}"):
                        st.info("🔗 In production, this would redirect to DocuSign or HelloSign for electronic signature.")
                
                # Contract text (editable)
                edited_text = st.text_area(
                    "Contract Text (Editable)",
                    value=contract_data["draft_text"],
                    height=400,
                    key=f"contract_text_{contract_type}"
                )
                
                # Update contract if edited
                if edited_text != contract_data["draft_text"]:
                    if st.button(f"💾 Save Changes", key=f"save_{contract_type}"):
                        st.session_state.generated_contracts[contract_type]["draft_text"] = edited_text
                        st.success("Contract updated!")
                
                # Clauses
                st.write("**Included Clauses:**")
                for clause in contract_data["clauses"]:
                    st.write(f"• {clause}")

def render_licensing_stage():
    """Stage 5: License & Summary"""
    st.markdown('<div class="stage-header">License & Summary</div>', unsafe_allow_html=True)
    
    if not st.session_state.ownership_arrangement:
        st.warning("Please complete the Ownership Arrangement stage first.")
        return
    
    # License recommendation parameters
    st.markdown("### 🎯 License Recommendation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        intended_use = st.selectbox(
            "Intended Use",
            ["commercial", "open_source", "research"],
            format_func=lambda x: x.replace("_", " ").title(),
            key="intended_use_select"
        )
    
    with col2:
        asset_type = st.selectbox(
            "Asset Type",
            ["software", "dataset", "media", "documentation"],
            index=0,
            key="license_asset_type_select"
        )
    
    # Dependencies
    dependencies_text = st.text_area(
        "Dependencies (one per line)",
        placeholder="MIT\nApache-2.0\nGPL-3.0"
    )
    dependencies = [dep.strip() for dep in dependencies_text.split('\n') if dep.strip()]
    
    # Generate license recommendations
    if st.button("Get License Recommendations", key="get_licenses"):
        with st.spinner("Analyzing license options..."):
            try:
                response = asyncio.run(call_api_async(
                    "/v1/license/recommend",
                    data={
                        "asset_id": st.session_state.asset_id,
                        "asset_type": asset_type,
                        "ownership_arrangement": st.session_state.ownership_arrangement,
                        "intended_use": intended_use,
                        "dependencies": dependencies
                    }
                ))
                
                if response:
                    st.session_state.license_recommendations = response
                    st.success("License recommendations generated!")
                    st.rerun()
            
            except Exception as e:
                st.error(f"Error getting license recommendations: {str(e)}")
    
    # Display license recommendations
    if st.session_state.license_recommendations:
        st.markdown("### 📋 License Recommendations")
        
        recs = st.session_state.license_recommendations
        
        # Primary recommendation
        if recs.get("primary_recommendation"):
            primary = recs["primary_recommendation"]
            st.markdown("#### 🏆 Primary Recommendation")
            
            col_a, col_b = st.columns([2, 1])
            with col_a:
                st.markdown(f"**{primary['license_name']}**")
                st.write(primary["rationale"])
                st.write(f"**Usage Terms:** {primary['usage_terms']}")
            with col_b:
                st.metric("Compatibility Score", f"{primary['compatibility_score']:.1%}")
        
        # All recommendations
        st.markdown("#### 📊 All Recommendations")
        
        rec_data = []
        for rec in recs["recommended_licenses"]:
            rec_data.append({
                "License": rec["license_name"],
                "Score": f"{rec['compatibility_score']:.1%}",
                "Rationale": rec["rationale"][:100] + "..." if len(rec["rationale"]) > 100 else rec["rationale"]
            })
        
        df = pd.DataFrame(rec_data)
        st.dataframe(df, use_container_width=True)
        
        # Detailed view
        for rec in recs["recommended_licenses"][:3]:  # Show top 3
            with st.expander(f"{rec['license_name']} - {rec['compatibility_score']:.1%}"):
                st.write(f"**Rationale:** {rec['rationale']}")
                st.write(f"**Usage Terms:** {rec['usage_terms']}")
                st.write("**Obligations:**")
                for obligation in rec["obligations"]:
                    st.write(f"• {obligation}")
        
        # Compatibility issues
        if recs.get("compatibility_issues"):
            st.markdown("#### ⚠️ Compatibility Issues")
            for issue in recs["compatibility_issues"]:
                st.warning(issue)
        
        # Final summary
        render_final_summary()

def generate_text_report() -> str:
    """Generate a comprehensive text report of the IP pipeline"""
    
    report_lines = []
    report_lines.append("=" * 60)
    report_lines.append("EQIP.AI INTELLECTUAL PROPERTY REPORT")
    report_lines.append("=" * 60)
    report_lines.append("")
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Asset ID: {st.session_state.asset_id}")
    report_lines.append("")
    
    # Contributors section
    if st.session_state.contributors:
        report_lines.append("CONTRIBUTORS")
        report_lines.append("-" * 20)
        for i, contrib in enumerate(st.session_state.contributors, 1):
            report_lines.append(f"{i}. {contrib['display_name']} ({contrib['email']})")
            if contrib.get('org'):
                report_lines.append(f"   Organization: {contrib['org']}")
        report_lines.append("")
    
    # Attribution results
    if st.session_state.attribution_results:
        results = st.session_state.attribution_results
        report_lines.append("CONTRIBUTION ATTRIBUTION")
        report_lines.append("-" * 25)
        report_lines.append(f"Methodology: {results['methodology']}")
        report_lines.append(f"Confidence Score: {results['confidence_score']:.1%}")
        report_lines.append("")
        
        for attr in results['attributions']:
            report_lines.append(f"• {attr['contributor_name']}: {attr['weight']:.1%}")
            report_lines.append(f"  Rationale: {attr['rationale']}")
        report_lines.append("")
    
    # Ownership arrangement
    if st.session_state.ownership_arrangement:
        arrangement = st.session_state.ownership_arrangement
        report_lines.append("OWNERSHIP STRUCTURE")
        report_lines.append("-" * 20)
        report_lines.append(f"Policy Applied: {arrangement['policy_applied']}")
        report_lines.append(f"Total Shares: {arrangement['total_shares']:,}")
        report_lines.append("")
        
        for share in arrangement['ownership_table']:
            report_lines.append(f"• {share['contributor_name']}: {share['percentage']:.2f}% ({share['shares']:,} shares)")
            report_lines.append(f"  Governance Rights: {share['governance_rights']}")
        
        report_lines.append("")
        report_lines.append(f"Governance Summary: {arrangement['governance_summary']}")
        report_lines.append("")
    
    # Generated contracts
    if st.session_state.generated_contracts:
        report_lines.append("GENERATED CONTRACTS")
        report_lines.append("-" * 20)
        for contract_type, contract_data in st.session_state.generated_contracts.items():
            report_lines.append(f"• {contract_type.upper()}: {contract_data['agreement_id']}")
            report_lines.append(f"  Clauses: {len(contract_data['clauses'])}")
        report_lines.append("")
    
    # License recommendations
    if st.session_state.license_recommendations:
        recs = st.session_state.license_recommendations
        report_lines.append("LICENSE RECOMMENDATIONS")
        report_lines.append("-" * 25)
        
        if recs.get('primary_recommendation'):
            primary = recs['primary_recommendation']
            report_lines.append(f"Primary Recommendation: {primary['license_name']}")
            report_lines.append(f"Compatibility Score: {primary['compatibility_score']:.1%}")
            report_lines.append(f"Rationale: {primary['rationale']}")
            report_lines.append("")
        
        report_lines.append("All Recommendations:")
        for i, rec in enumerate(recs['recommended_licenses'][:5], 1):
            report_lines.append(f"{i}. {rec['license_name']} ({rec['compatibility_score']:.1%})")
        report_lines.append("")
    
    report_lines.append("=" * 60)
    report_lines.append("End of Report")
    report_lines.append("=" * 60)
    
    return "\n".join(report_lines)


def render_final_summary():
    """Render final pipeline summary"""
    st.markdown("### Complete IP Report Summary")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Asset ID", st.session_state.asset_id or "N/A")
    
    with col2:
        contributors_count = len(st.session_state.contributors)
        st.metric("Contributors", contributors_count)
    
    with col3:
        contracts_count = len(st.session_state.generated_contracts)
        st.metric("Contracts Generated", contracts_count)
    
    with col4:
        if st.session_state.license_recommendations:
            license_count = len(st.session_state.license_recommendations["recommended_licenses"])
            st.metric("License Options", license_count)
        else:
            st.metric("License Options", "N/A")
    
    # Export options
    st.markdown("### Export Options")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        # Generate comprehensive text report
        if st.session_state.attribution_results and st.session_state.ownership_arrangement:
            report_content = generate_text_report()
            st.download_button(
                "📄 Download Text Report",
                data=report_content,
                file_name=f"eqip_ip_report_{st.session_state.asset_id}_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                key="download_report"
            )
        else:
            st.info("Complete the pipeline to generate a full report")
    
    with col_b:
        # Export all pipeline data as JSON
        export_data = {
            "asset_id": st.session_state.asset_id,
            "contributors": st.session_state.contributors,
            "attribution_results": st.session_state.attribution_results,
            "ownership_arrangement": st.session_state.ownership_arrangement,
            "generated_contracts": {k: {
                "agreement_id": v["agreement_id"],
                "contract_type": v["contract_type"],
                "clauses": v["clauses"]
            } for k, v in st.session_state.generated_contracts.items()},
            "license_recommendations": st.session_state.license_recommendations,
            "export_timestamp": datetime.now().isoformat()
        }
        
        json_str = json.dumps(export_data, indent=2, default=str)
        st.download_button(
            "📊 Download JSON Data",
            json_str,
            file_name=f"eqip_data_{st.session_state.asset_id}_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            key="download_json"
        )

def main():
    """Main application function"""
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">Eqip.ai — Complete IP Lifecycle Pipeline</div>', unsafe_allow_html=True)
    st.markdown("*From IP discovery to licensing - your complete intellectual property solution*")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Asset configuration
        st.subheader("Asset Details")
        st.session_state.asset_type = st.selectbox(
            "Asset Type", 
            ["software", "dataset", "media", "invention"],
            index=["software", "dataset", "media", "invention"].index(st.session_state.asset_type),
            key="asset_type_sidebar"
        )
        
        # Jurisdiction selection
        st.subheader("Jurisdictions")
        available_jurisdictions = ["UK", "US", "EU", "CA", "AU", "JP"]
        selected_jurisdictions = st.multiselect(
            "Select jurisdictions",
            available_jurisdictions,
            default=st.session_state.jurisdictions
        )
        if selected_jurisdictions:
            st.session_state.jurisdictions = selected_jurisdictions
        
        # Pipeline reset
        st.subheader("Pipeline Control")
        if st.button("Reset Pipeline"):
            for key in ["current_stage", "pipeline_data", "attribution_results", 
                       "ownership_arrangement", "generated_contracts", "license_recommendations"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        
        # System status
        st.subheader("System Status")
        try:
            status = asyncio.run(call_api_async("/v1/health", method="GET"))
            if status.get("status") == "ok":
                st.success("✅ API Connected")
            else:
                st.error("❌ API Issues")
        except:
            st.error("❌ API Offline")
    
    # Main content
    render_progress_bar()
    render_stage_overview()
    
    # Render current stage
    current_stage = st.session_state.current_stage
    
    if current_stage == 0:
        render_ip_options_stage()
    elif current_stage == 1:
        render_attribution_stage()
    elif current_stage == 2:
        render_ownership_stage()
    elif current_stage == 3:
        render_contracts_stage()
    elif current_stage == 4:
        render_licensing_stage()

if __name__ == "__main__":
    main()
