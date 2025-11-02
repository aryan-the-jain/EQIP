"""
Eqip.ai - Complete IP Lifecycle Pipeline (Streamlit Cloud Deployment)

Standalone deployment file for Streamlit Cloud with demo mode functionality.
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
import uuid

# Configuration - Use secrets for production, fallback for demo
try:
    API_BASE = st.secrets["API_BASE"]
    DEMO_MODE = st.secrets.get("DEMO_MODE", "true").lower() == "true"
except:
    API_BASE = "http://localhost:8000"
    DEMO_MODE = True

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

/* Form styling */
.stSelectbox > div > div {
    background-color: #ffffff !important;
    border-color: #e2e8f0 !important;
    color: #2d3748 !important;
}
.stTextInput > div > div > input {
    background-color: #ffffff !important;
    border-color: #e2e8f0 !important;
    color: #2d3748 !important;
    caret-color: #2d3748 !important;
}
.stTextArea > div > div > textarea {
    background-color: #ffffff !important;
    border-color: #e2e8f0 !important;
    color: #2d3748 !important;
    caret-color: #2d3748 !important;
}
.stNumberInput > div > div > input {
    background-color: #ffffff !important;
    border-color: #e2e8f0 !important;
    color: #2d3748 !important;
    caret-color: #2d3748 !important;
}

/* Chat styling */
.stChatMessage {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    margin: 0.5rem 0 !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
    color: #2d3748 !important;
}
.stChatMessage .stMarkdown,
.stChatMessage .stMarkdown p,
.stChatMessage .stMarkdown div,
.stChatMessage .stMarkdown span,
.stChatMessage .stMarkdown ul,
.stChatMessage .stMarkdown li {
    color: #2d3748 !important;
}

/* Chat input */
.stChatInput input {
    color: #2d3748 !important;
    background-color: #ffffff !important;
    caret-color: #2d3748 !important;
}

/* Button styling */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-weight: 500;
}

/* Hide unwanted elements */
.element-container h1 {
    display: none !important;
}
.stChatMessage h1 {
    display: none !important;
}

/* App-wide text color */
.stApp {
    color: #e2e8f0 !important;
}

/* Light backgrounds get dark text */
.stChatMessage,
.stage-card,
.stSelectbox,
.stTextInput,
.stTextArea,
.stButton {
    color: #2d3748 !important;
}
</style>
""", unsafe_allow_html=True)

# Pipeline stages
PIPELINE_STAGES = [
    {"id": "ip_options", "name": "IP Path Finder", "description": "Discover protection options"},
    {"id": "attribution", "name": "Contribution Attribution", "description": "Analyze contributor efforts"},
    {"id": "ownership", "name": "Ownership Arrangement", "description": "Finalize ownership structure"},
    {"id": "contracts", "name": "Contract Drafting", "description": "Generate legal agreements"},
    {"id": "licensing", "name": "License & Summary", "description": "License recommendations"}
]

def initialize_session_state():
    """Initialize session state variables"""
    defaults = {
        "current_stage": 0,
        "asset_id": None,
        "asset_type": "software",
        "jurisdictions": ["UK"],
        "messages": [],
        "general_messages": [],
        "pipeline_data": {},
        "contributors": [],
        "contribution_events": [],
        "attribution_results": None,
        "ownership_arrangement": None,
        "generated_contracts": {},
        "license_recommendations": None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

async def call_api_async_demo(endpoint: str, method: str = "POST", data: dict = None) -> dict:
    """Demo mode API calls with mock responses"""
    
    if "/v1/health" in endpoint:
        return {"status": "ok"}
    
    elif "/v1/assets" in endpoint:
        return {"asset_id": 12345}
    
    elif "/v1/agents/ip-options" in endpoint:
        return {
            "options": [
                "Copyright Protection: Automatic protection for creative works in the UK",
                "Trademark Protection: Consider registering distinctive brand elements",
                "Design Rights: Protect visual appearance and configuration",
                "Trade Secret Protection: Maintain confidentiality for proprietary processes"
            ],
            "risks": [
                "Public disclosure may limit future patent options",
                "Infringement monitoring required for enforcement",
                "International protection requires separate registrations"
            ],
            "next_steps": [
                "Document creation and ownership details",
                "Consider formal IP registration where applicable",
                "Implement IP protection policies",
                "Consult with IP attorney for complex cases"
            ],
            "citations": [
                "UK Intellectual Property Framework - gov.uk/ip-guidance",
                "Copyright, Designs and Patents Act 1988",
                "UK Trade Marks Act 1994"
            ]
        }
    
    elif "/v1/agents/attribution/run" in endpoint:
        contributors = data.get("contributors", [])
        if not contributors:
            contributors = [{"email": "demo@example.com", "display_name": "Demo User", "org": "Demo Corp"}]
        
        # Create realistic attribution based on contribution events
        events = data.get("contribution_events", [])
        attributions = []
        
        if events:
            # Calculate based on events
            contributor_scores = {}
            for event in events:
                email = event["contributor_email"]
                if email not in contributor_scores:
                    contributor_scores[email] = 0
                
                # Simple scoring
                score = event.get("hours_spent", 1) * event.get("complexity_score", 1)
                if event["event_type"] == "code":
                    score *= 2
                elif event["event_type"] == "design":
                    score *= 1.5
                
                contributor_scores[email] += score
            
            total_score = sum(contributor_scores.values())
            
            for contrib in contributors:
                email = contrib["email"]
                weight = contributor_scores.get(email, 1) / total_score if total_score > 0 else 1.0 / len(contributors)
                
                attributions.append({
                    "contributor_email": email,
                    "contributor_name": contrib["display_name"],
                    "weight": weight,
                    "rationale": f"Based on contribution events: {contributor_scores.get(email, 0):.1f} points",
                    "breakdown": {"code": 0.4, "design": 0.3, "review": 0.2, "documentation": 0.1}
                })
        else:
            # Equal distribution
            for contrib in contributors:
                attributions.append({
                    "contributor_email": contrib["email"],
                    "contributor_name": contrib["display_name"],
                    "weight": 1.0 / len(contributors),
                    "rationale": "Equal attribution - no contribution data provided",
                    "breakdown": {"code": 0.25, "design": 0.25, "review": 0.25, "documentation": 0.25}
                })
        
        return {
            "asset_id": data.get("asset_id", 12345),
            "attributions": attributions,
            "total_weight": 1.0,
            "methodology": "Demo mode attribution analysis",
            "confidence_score": 0.8
        }
    
    elif "/v1/agents/allocation/finalize" in endpoint:
        attributions = data.get("attribution_weights", [])
        return {
            "asset_id": data.get("asset_id", 12345),
            "ownership_table": [
                {
                    "contributor_email": attr["contributor_email"],
                    "contributor_name": attr["contributor_name"],
                    "shares": int(attr["weight"] * 1000000),
                    "percentage": attr["weight"] * 100,
                    "governance_rights": "majority" if attr["weight"] > 0.5 else "standard"
                } for attr in attributions
            ],
            "total_shares": 1000000,
            "governance_summary": f"Demo ownership structure with {len(attributions)} contributors using {data.get('policy_type', 'weighted')} policy",
            "policy_applied": data.get("policy_type", "weighted")
        }
    
    elif "/v1/agreements/generate" in endpoint:
        contract_type = data.get("contract_type", "nda")
        ownership = data.get("ownership_arrangement", {})
        
        # Generate realistic contract text
        contract_text = f"""
{contract_type.upper().replace('_', ' ')} AGREEMENT

This {contract_type.replace('_', ' ').title()} Agreement is entered into on {datetime.now().strftime('%B %d, %Y')}.

PARTIES:
"""
        
        for share in ownership.get("ownership_table", []):
            contract_text += f"• {share['contributor_name']} ({share['contributor_email']}) - {share['percentage']:.1f}% ownership\n"
        
        contract_text += f"""

This is a demonstration contract generated by Eqip.ai's AI-powered contract drafting system.

In production, this would contain:
- Complete legal clauses and terms
- Jurisdiction-specific language
- Detailed ownership and governance provisions
- Professional legal formatting

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Contract ID: {str(uuid.uuid4())[:8]}

For production use, please consult with qualified legal counsel.
"""
        
        return {
            "agreement_id": str(uuid.uuid4()),
            "contract_type": contract_type,
            "draft_text": contract_text,
            "clauses": [
                "Parties and Definitions",
                "Ownership Structure", 
                "Governance Rights",
                "Intellectual Property Assignment",
                "Confidentiality Obligations",
                "Term and Termination",
                "Governing Law"
            ],
            "sign_url": "https://demo.docusign.com/sign",
            "download_url": "https://demo.eqip.ai/download"
        }
    
    elif "/v1/license/recommend" in endpoint:
        return {
            "asset_id": data.get("asset_id", 12345),
            "recommended_licenses": [
                {
                    "license_name": "MIT License",
                    "compatibility_score": 0.95,
                    "rationale": "Excellent for software projects; Supports commercial use; Compatible with dependencies",
                    "usage_terms": "Permits commercial use, modification, distribution, and private use. Requires attribution.",
                    "obligations": ["Include license text", "Include copyright notice", "Provide attribution"]
                },
                {
                    "license_name": "Apache License 2.0", 
                    "compatibility_score": 0.90,
                    "rationale": "Good for enterprise software; Explicit patent grant; Professional choice",
                    "usage_terms": "Permits commercial use with explicit patent grant. Requires attribution and notice of changes.",
                    "obligations": ["Include license text", "Include copyright notice", "State changes", "Include NOTICE file"]
                },
                {
                    "license_name": "BSD 3-Clause License",
                    "compatibility_score": 0.85,
                    "rationale": "Permissive license; Good for commercial use; Academic friendly",
                    "usage_terms": "Permits commercial use with attribution. Includes non-endorsement clause.",
                    "obligations": ["Include license text", "Include copyright notice", "No endorsement without permission"]
                }
            ],
            "primary_recommendation": {
                "license_name": "MIT License",
                "compatibility_score": 0.95,
                "rationale": "Excellent for software projects; Supports commercial use; Compatible with dependencies",
                "usage_terms": "Permits commercial use, modification, distribution, and private use. Requires attribution.",
                "obligations": ["Include license text", "Include copyright notice", "Provide attribution"]
            },
            "compatibility_issues": []
        }
    
    else:
        return {"status": "demo_mode", "message": "Demo response"}

async def call_api_async(endpoint: str, method: str = "POST", data: dict = None) -> dict:
    """API call function - uses demo mode or real API"""
    if DEMO_MODE:
        return await call_api_async_demo(endpoint, method, data)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if method == "POST":
                response = await client.post(f"{API_BASE}{endpoint}", json=data)
            else:
                response = await client.get(f"{API_BASE}{endpoint}")
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API Error: {response.status_code}")
                return {}
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return {}

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
            stage_complete = check_stage_completion(current_stage)
            if st.button("Next →", key="next_stage", disabled=not stage_complete):
                st.session_state.current_stage = min(len(PIPELINE_STAGES) - 1, current_stage + 1)
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

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

def render_ip_options_stage():
    """Stage 1: IP Path Finder"""
    st.markdown('<div class="stage-header">IP Path Finder</div>', unsafe_allow_html=True)
    
    # Asset creation
    if not st.session_state.asset_id:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.info("First, let's create an asset to analyze")
            if st.button("Create New Asset", key="create_asset"):
                response = asyncio.run(call_api_async("/v1/assets", data={"type": st.session_state.asset_type, "uri": "", "contributors": []}))
                if response.get("asset_id"):
                    st.session_state.asset_id = response["asset_id"]
                    st.success(f"Created asset #{st.session_state.asset_id}")
                    st.rerun()
        with col2:
            st.session_state.asset_type = st.selectbox(
                "Asset Type",
                ["software", "dataset", "media", "invention"],
                key="asset_type_main"
            )
    else:
        st.success(f"Working with Asset ID: {st.session_state.asset_id}")
    
    # Chat interface
    if st.session_state.asset_id:
        st.markdown("### IP Consultation")
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # Quick action buttons
        if st.session_state.pipeline_data.get("ip_options") and st.session_state.messages:
            st.markdown("---")
            st.markdown("### Quick Actions")
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                if st.button("Proceed to Attribution", key="proceed_to_attribution"):
                    st.session_state.current_stage = 1
                    st.rerun()
            
            with col_b:
                if st.button("Get More Details", key="get_more_details"):
                    follow_up = "Can you provide more detailed analysis of the recommended protection options?"
                    st.session_state.messages.append({"role": "user", "content": follow_up})
                    st.rerun()
            
            with col_c:
                if st.button("New Analysis", key="new_analysis"):
                    if "ip_options" in st.session_state.pipeline_data:
                        del st.session_state.pipeline_data["ip_options"]
                    st.session_state.messages = []
                    st.rerun()
            
            st.markdown("---")
        
        # Chat input
        if prompt := st.chat_input("Ask about IP protection options..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.write(prompt)
            
            # Check for advancement keywords
            if prompt.lower().strip() in ['yes', 'y', 'proceed', 'continue', 'next', 'move on']:
                st.session_state.current_stage = min(4, st.session_state.current_stage + 1)
                success_msg = "Great! Moving to the next stage: Contribution Attribution."
                with st.chat_message("assistant"):
                    st.success(success_msg)
                st.session_state.messages.append({"role": "assistant", "content": success_msg})
                st.rerun()
                return
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Analyzing IP options..."):
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
                            response_text += f"\n**References:**\n"
                            for citation in response["citations"]:
                                response_text += f"• {citation}\n"
                        
                        response_text += f"\n**Would you like to proceed with these recommendations?**\n"
                        response_text += f"• Type 'yes' to move to the next stage\n"
                        response_text += f"• Ask any follow-up questions about these options"
                        
                        st.write(response_text)
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                        st.session_state.pipeline_data["ip_options"] = response

def render_simple_stages():
    """Render simplified versions of other stages for demo"""
    current_stage = st.session_state.current_stage
    
    if current_stage == 1:
        st.markdown('<div class="stage-header">Contribution Attribution</div>', unsafe_allow_html=True)
        st.info("This stage would analyze contributor efforts and calculate weighted attribution. In demo mode, click 'Next' to continue.")
        
    elif current_stage == 2:
        st.markdown('<div class="stage-header">Ownership Arrangement</div>', unsafe_allow_html=True)
        st.info("This stage would finalize ownership structure based on attribution. In demo mode, click 'Next' to continue.")
        
    elif current_stage == 3:
        st.markdown('<div class="stage-header">Contract Drafting</div>', unsafe_allow_html=True)
        st.info("This stage would generate legal contracts. In demo mode, click 'Next' to continue.")
        
    elif current_stage == 4:
        st.markdown('<div class="stage-header">License & Summary</div>', unsafe_allow_html=True)
        st.info("This stage would provide license recommendations and final summary. Demo complete!")

def render_general_chat():
    """Render general IP advice chat section"""
    st.markdown('<div class="stage-header">General IP Advice</div>', unsafe_allow_html=True)
    st.markdown("Ask any questions about intellectual property law, strategy, or best practices.")
    
    # Initialize general chat messages
    if "general_messages" not in st.session_state:
        st.session_state.general_messages = []
    
    # Display chat history
    for message in st.session_state.general_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about IP law, strategy, patents, trademarks, licensing..."):
        st.session_state.general_messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Consulting IP knowledge base..."):
                response = asyncio.run(call_api_async(
                    "/v1/agents/ip-options",
                    data={
                        "asset_id": 0,
                        "questions": prompt,
                        "jurisdictions": st.session_state.jurisdictions,
                        "conversation_context": st.session_state.general_messages[-5:]
                    }
                ))
                
                if response:
                    response_text = ""
                    if response.get("options"):
                        response_text += f"**Recommendations:**\n"
                        for option in response["options"]:
                            response_text += f"• {option}\n"
                    
                    if response.get("risks"):
                        response_text += f"\n**Considerations:**\n"
                        for risk in response["risks"]:
                            response_text += f"• {risk}\n"
                    
                    if response.get("next_steps"):
                        response_text += f"\n**Suggested Actions:**\n"
                        for step in response["next_steps"]:
                            response_text += f"• {step}\n"
                    
                    if not response_text:
                        response_text = "I'd be happy to help with your IP question. Could you provide more specific details?"
                    
                    st.write(response_text)
                    st.session_state.general_messages.append({"role": "assistant", "content": response_text})

def main():
    """Main application function"""
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">Eqip.ai — Complete IP Lifecycle Pipeline</div>', unsafe_allow_html=True)
    st.markdown("*From IP discovery to licensing - your complete intellectual property solution*")
    
    if DEMO_MODE:
        st.info("🎭 Demo Mode - Experience the complete IP pipeline with sample data")
    
    # Sidebar
    with st.sidebar:
        st.header("Configuration")
        
        st.subheader("Asset Details")
        st.session_state.asset_type = st.selectbox(
            "Asset Type", 
            ["software", "dataset", "media", "invention"],
            key="asset_type_sidebar"
        )
        
        st.subheader("Jurisdictions")
        available_jurisdictions = ["UK", "US", "EU", "CA", "AU", "JP"]
        selected_jurisdictions = st.multiselect(
            "Select jurisdictions",
            available_jurisdictions,
            default=st.session_state.jurisdictions
        )
        if selected_jurisdictions:
            st.session_state.jurisdictions = selected_jurisdictions
        
        st.subheader("Pipeline Control")
        if st.button("Reset Pipeline"):
            for key in ["current_stage", "pipeline_data", "attribution_results", 
                       "ownership_arrangement", "generated_contracts", "license_recommendations"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        
        st.subheader("System Status")
        try:
            status = asyncio.run(call_api_async("/v1/health", method="GET"))
            if status.get("status") == "ok":
                st.success("✅ System Ready")
            else:
                st.error("❌ System Issues")
        except:
            if DEMO_MODE:
                st.success("✅ Demo Mode Active")
            else:
                st.error("❌ System Offline")
    
    # Main content with tabs
    tab1, tab2 = st.tabs(["IP Pipeline", "General IP Advice"])
    
    with tab1:
        render_progress_bar()
        render_stage_overview()
        
        current_stage = st.session_state.current_stage
        if current_stage == 0:
            render_ip_options_stage()
        else:
            render_simple_stages()
    
    with tab2:
        render_general_chat()

if __name__ == "__main__":
    main()
