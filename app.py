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

/* Expander and dialog styling */
.streamlit-expanderHeader {
    background-color: #f7fafc !important;
    color: #2d3748 !important;
}

.streamlit-expanderContent {
    background-color: #ffffff !important;
    color: #2d3748 !important;
    border: 1px solid #e2e8f0 !important;
}

.streamlit-expanderContent .stMarkdown,
.streamlit-expanderContent .stMarkdown p,
.streamlit-expanderContent .stText,
.streamlit-expanderContent .stTextArea,
.streamlit-expanderContent .stTextInput {
    color: #2d3748 !important;
}

/* Text area in expanders - force dark text */
.streamlit-expanderContent textarea {
    color: #2d3748 !important;
    background-color: #ffffff !important;
    caret-color: #2d3748 !important;
}

/* All form elements in expanders */
.streamlit-expanderContent input,
.streamlit-expanderContent textarea,
.streamlit-expanderContent select {
    color: #2d3748 !important;
    background-color: #ffffff !important;
    caret-color: #2d3748 !important;
}

/* Form labels in expanders */
.streamlit-expanderContent label {
    color: #2d3748 !important;
}

/* Placeholder text in expanders - darker gray */
.streamlit-expanderContent textarea::placeholder,
.streamlit-expanderContent input::placeholder {
    color: #4a5568 !important;
    font-weight: 400 !important;
}

/* Global placeholder text - darker */
textarea::placeholder,
input::placeholder {
    color: #4a5568 !important;
}

/* Radio button styling */
.stRadio > div {
    background-color: #f7fafc;
    padding: 1rem;
    border-radius: 8px;
    border: 2px solid #667eea;
}

.stRadio > div > label {
    font-weight: 600 !important;
    font-size: 1.1rem !important;
    color: #2d3748 !important;
}

/* Radio button options text - make black with multiple selectors */
.stRadio > div > div > label,
.stRadio > div > div > label > div,
.stRadio > div > div > label span,
.stRadio > div > div > label p,
.stRadio label,
.stRadio label div,
.stRadio label span {
    color: #000000 !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
}

/* Force black text on radio options */
[data-testid="stRadio"] label,
[data-testid="stRadio"] label div,
[data-testid="stRadio"] label span {
    color: #000000 !important;
    font-weight: 600 !important;
}

/* Radio button container text */
.stRadio div[role="radiogroup"] label {
    color: #000000 !important;
    font-weight: 600 !important;
}

/* Radio button input styling */
.stRadio > div > div > div > input {
    accent-color: #667eea !important;
}

/* Radio button container */
.stRadio > div > div {
    padding: 0.5rem;
    margin: 0.3rem 0;
    border-radius: 6px;
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
}

.stRadio > div > div:hover {
    background-color: #f7fafc;
    border-color: #667eea;
}

/* Small screen responsive buttons */
@media (max-width: 768px) {
    .small-button {
        font-size: 0.8rem !important;
        padding: 0.3rem 0.6rem !important;
        white-space: nowrap !important;
    }
}

/* Global radio button text override */
.stRadio * {
    color: #000000 !important;
}

/* Ensure radio button text is always black */
.stRadio [role="radiogroup"] * {
    color: #000000 !important;
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
    
    # Stage description
    st.markdown("""
    **What is IP Path Finder?**
    
    This is your AI-powered intellectual property consultant. Ask questions about protecting your creative work,
    software, inventions, or business assets. Our RAG (Retrieval-Augmented Generation) system provides expert
    advice based on UK and international IP law.
    
    **What you can ask:**
    - "How should I protect my software algorithm?"
    - "Do I need a patent or is copyright enough?"
    - "What are the risks of open-source licensing?"
    - "Should I file a trademark for my brand?"
    
    **Get personalized recommendations** with citations from legal frameworks and best practices.
    """)
    
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

def render_attribution_stage():
    """Stage 2: Contribution Attribution"""
    st.markdown('<div class="stage-header">Contribution Attribution</div>', unsafe_allow_html=True)
    
    # Stage description
    st.markdown("""
    **What is Contribution Attribution?**
    
    This stage analyzes each team member's contributions to determine fair ownership percentages. 
    Choose between two approaches based on your preference and available information.
    """)
    
    # Method selection - Make it more prominent
    st.markdown("---")
    st.markdown("## 🎯 Choose Attribution Method")
    
    attribution_method = st.radio(
        "Select your preferred approach:",
        ["Quantitative Analysis", "Qualitative Description"],
        format_func=lambda x: {
            "Quantitative Analysis": "📊 Quantitative Analysis - Log specific events (hours, lines of code, complexity)",
            "Qualitative Description": "📝 Qualitative Description - Describe contributions in text, AI analyzes and scores"
        }[x],
        key="attribution_method",
        horizontal=True
    )
    st.markdown("---")
    
    if attribution_method == "Quantitative Analysis":
        st.markdown("""
        **Quantitative Method:**
        1. Add contributors and log specific contribution events
        2. Include details like hours spent, lines of code, complexity scores
        3. AI calculates weighted attribution based on measurable data
        4. View precise breakdowns and interactive visualizations
        """)
        render_quantitative_attribution()
        
    else:  # Qualitative Description
        st.markdown("""
        **Qualitative Method:**
        1. Add contributors and describe what each person contributed
        2. AI analyzes the descriptions using common IP attribution methodologies
        3. Review and adjust the AI's suggested attribution percentages
        4. Confirm the final attribution to proceed
        """)
        render_qualitative_attribution()

def render_quantitative_attribution():
    """Render the quantitative contribution attribution interface"""
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
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    st.write(f"• {contrib['display_name']} ({contrib['email']})")
                with col_b:
                    # Use compact symbol for better responsive design
                    if st.button("✕", key=f"remove_contrib_{i}", help=f"Remove {contrib['display_name']}"):
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
                    response = asyncio.run(call_api_async(
                        "/v1/agents/attribution/run",
                        data={
                            "asset_id": st.session_state.asset_id,
                            "contributors": st.session_state.contributors,
                            "contribution_events": st.session_state.contribution_events,
                            "team_votes": [],
                            "mode": "hybrid"
                        }
                    ))
                    
                    if response:
                        st.session_state.attribution_results = response
                        st.success("Attribution analysis complete!")
                        st.rerun()
        
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

def render_qualitative_attribution():
    """Render the qualitative contribution attribution interface"""
    # Contributors management
    st.markdown("### Contributors")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Add contributor form
        with st.expander("Add Contributor", expanded=len(st.session_state.contributors) == 0):
            with st.form("add_contributor_qual"):
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
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    st.write(f"• {contrib['display_name']} ({contrib['email']})")
                with col_b:
                    # Use HTML for better responsive button
                    if st.button("✕", key=f"remove_contrib_qual_{i}", help=f"Remove {contrib['display_name']}"):
                        st.session_state.contributors.pop(i)
                        st.rerun()
    
    # Qualitative contribution description
    if st.session_state.contributors:
        st.markdown("### Contribution Descriptions")
        
        # Initialize qualitative descriptions if not exists
        if "qualitative_descriptions" not in st.session_state:
            st.session_state.qualitative_descriptions = {}
        
        # Get descriptions for each contributor
        for contrib in st.session_state.contributors:
            email = contrib["email"]
            name = contrib["display_name"]
            
            with st.expander(f"Describe {name}'s Contributions", expanded=email not in st.session_state.qualitative_descriptions):
                description = st.text_area(
                    f"What did {name} contribute to the project?",
                    value=st.session_state.qualitative_descriptions.get(email, ""),
                    placeholder=f"Describe {name}'s role and contributions. For example:\n"
                                f"• Led the technical architecture and implemented core algorithms\n"
                                f"• Spent approximately 40 hours on complex backend development\n"
                                f"• Conducted code reviews and mentored junior developers\n"
                                f"• Created technical documentation and API specifications",
                    height=150,
                    key=f"desc_{email}"
                )
                
                if st.button(f"Save Description for {name}", key=f"save_desc_{email}"):
                    if description.strip():
                        st.session_state.qualitative_descriptions[email] = description
                        st.success(f"Saved description for {name}")
                        st.rerun()
                    else:
                        st.error("Please provide a description")
        
        # AI Analysis of qualitative descriptions
        if len(st.session_state.qualitative_descriptions) == len(st.session_state.contributors):
            st.markdown("### AI Attribution Analysis")
            
            if st.button("Analyze Contribution Descriptions", key="analyze_qualitative"):
                with st.spinner("AI is analyzing contribution descriptions..."):
                    # Create prompt for LLM analysis
                    analysis_prompt = "Analyze the following contributor descriptions and provide fair attribution percentages:\n\n"
                    
                    for contrib in st.session_state.contributors:
                        email = contrib["email"]
                        name = contrib["display_name"]
                        desc = st.session_state.qualitative_descriptions.get(email, "")
                        analysis_prompt += f"**{name} ({email}):**\n{desc}\n\n"
                    
                    analysis_prompt += """
                    Based on these descriptions, please provide:
                    1. Fair attribution percentages for each contributor (must sum to 100%)
                    2. Rationale for each person's percentage
                    3. Consider factors like: technical complexity, time investment, leadership, creative input, risk-taking
                    
                    Use common IP attribution methodologies and be fair and objective.
                    """
                    
                    # Get AI analysis
                    response = asyncio.run(call_api_async(
                        "/v1/agents/ip-options",
                        data={
                            "asset_id": st.session_state.asset_id,
                            "questions": analysis_prompt,
                            "jurisdictions": st.session_state.jurisdictions,
                            "conversation_context": []
                        }
                    ))
                    
                    if response:
                        # Enhanced AI analysis with detailed rationale
                        attributions = []
                        total_weight = 0
                        
                        for contrib in st.session_state.contributors:
                            email = contrib["email"]
                            name = contrib["display_name"]
                            desc = st.session_state.qualitative_descriptions.get(email, "")
                            
                            # Comprehensive scoring with detailed rationale tracking
                            score_components = {
                                "base_contribution": 1.0,
                                "leadership_indicators": 0.0,
                                "technical_complexity": 0.0,
                                "time_investment": 0.0,
                                "creative_input": 0.0,
                                "project_impact": 0.0
                            }
                            
                            rationale_parts = []
                            
                            # Base score from description completeness
                            word_count = len(desc.split())
                            if word_count > 50:
                                score_components["base_contribution"] = 2.0
                                rationale_parts.append(f"Comprehensive description ({word_count} words)")
                            elif word_count > 20:
                                score_components["base_contribution"] = 1.5
                                rationale_parts.append(f"Detailed description ({word_count} words)")
                            else:
                                rationale_parts.append(f"Basic description ({word_count} words)")
                            
                            # Leadership and initiative indicators
                            leadership_keywords = ["led", "founded", "initiated", "managed", "directed", "coordinated", "organized"]
                            leadership_count = sum(1 for keyword in leadership_keywords if keyword.lower() in desc.lower())
                            if leadership_count > 0:
                                score_components["leadership_indicators"] = leadership_count * 1.5
                                rationale_parts.append(f"Leadership role identified ({leadership_count} indicators)")
                            
                            # Technical complexity and expertise
                            tech_keywords = ["architected", "designed", "implemented", "developed", "engineered", "algorithm", "complex", "advanced", "technical"]
                            tech_count = sum(1 for keyword in tech_keywords if keyword.lower() in desc.lower())
                            if tech_count > 0:
                                score_components["technical_complexity"] = tech_count * 1.2
                                rationale_parts.append(f"Technical expertise demonstrated ({tech_count} technical terms)")
                            
                            # Time and effort investment
                            time_indicators = ["hours", "weeks", "months", "full-time", "extensive", "significant", "substantial"]
                            effort_indicators = ["overtime", "dedicated", "intensive", "thorough", "comprehensive"]
                            time_count = sum(1 for indicator in time_indicators + effort_indicators if indicator.lower() in desc.lower())
                            if time_count > 0:
                                score_components["time_investment"] = time_count * 1.0
                                rationale_parts.append(f"Significant time investment indicated ({time_count} effort indicators)")
                            
                            # Creative and innovative input
                            creative_keywords = ["created", "invented", "innovated", "conceived", "originated", "pioneered", "breakthrough"]
                            creative_count = sum(1 for keyword in creative_keywords if keyword.lower() in desc.lower())
                            if creative_count > 0:
                                score_components["creative_input"] = creative_count * 1.8
                                rationale_parts.append(f"Creative innovation recognized ({creative_count} innovation indicators)")
                            
                            # Project impact and scope
                            impact_keywords = ["critical", "essential", "key", "core", "fundamental", "crucial", "vital", "primary"]
                            impact_count = sum(1 for keyword in impact_keywords if keyword.lower() in desc.lower())
                            if impact_count > 0:
                                score_components["project_impact"] = impact_count * 1.3
                                rationale_parts.append(f"High project impact identified ({impact_count} impact terms)")
                            
                            # Calculate total score
                            total_score = sum(score_components.values())
                            
                            # Create detailed rationale
                            detailed_rationale = f"AI Analysis for {name}:\n"
                            detailed_rationale += f"• Total Score: {total_score:.1f} points\n"
                            detailed_rationale += f"• Score Breakdown: "
                            detailed_rationale += f"Base ({score_components['base_contribution']:.1f}) + "
                            detailed_rationale += f"Leadership ({score_components['leadership_indicators']:.1f}) + "
                            detailed_rationale += f"Technical ({score_components['technical_complexity']:.1f}) + "
                            detailed_rationale += f"Time ({score_components['time_investment']:.1f}) + "
                            detailed_rationale += f"Creative ({score_components['creative_input']:.1f}) + "
                            detailed_rationale += f"Impact ({score_components['project_impact']:.1f})\n"
                            detailed_rationale += f"• Key Factors: {'; '.join(rationale_parts) if rationale_parts else 'Standard contribution'}\n"
                            detailed_rationale += f"• Methodology: Qualitative text analysis using IP attribution best practices"
                            
                            attributions.append({
                                "email": email,
                                "name": name,
                                "score": max(total_score, 1.0),
                                "description": desc,
                                "detailed_rationale": detailed_rationale,
                                "score_components": score_components
                            })
                            total_weight += max(total_score, 1.0)
                        
                        # Normalize to percentages
                        for attr in attributions:
                            attr["weight"] = attr["score"] / total_weight
                            attr["percentage"] = attr["weight"] * 100
                        
                        # Store in session state for editing
                        st.session_state.ai_suggested_attribution = attributions
                        st.session_state.qualitative_analysis_complete = True
                        st.rerun()
        
        # Display AI suggestions for review and editing
        if st.session_state.get("qualitative_analysis_complete") and st.session_state.get("ai_suggested_attribution"):
            st.markdown("### AI Attribution Suggestions")
            st.markdown("Review and adjust the AI's suggested attribution percentages:")
            
            # Create editable attribution table
            attributions = st.session_state.ai_suggested_attribution
            
            # Display current suggestions
            col_a, col_b = st.columns([2, 1])
            with col_a:
                st.markdown("**AI Suggested Attribution:**")
                for attr in attributions:
                    st.write(f"• **{attr['name']}**: {attr['percentage']:.1f}%")
                    with st.expander(f"Detailed AI Analysis for {attr['name']}"):
                        st.markdown("**AI Rationale:**")
                        st.text(attr['detailed_rationale'])
                        
                        st.markdown("**Original Description:**")
                        st.write(f'"{attr["description"]}"')
                        
                        if attr.get('score_components'):
                            st.markdown("**Score Components:**")
                            components = attr['score_components']
                            for component, score in components.items():
                                if score > 0:
                                    component_name = component.replace('_', ' ').title()
                                    st.write(f"• {component_name}: {score:.1f} points")
            
            with col_b:
                # Pie chart of suggestions
                names = [attr["name"] for attr in attributions]
                weights = [attr["weight"] for attr in attributions]
                
                fig = px.pie(
                    values=weights,
                    names=names,
                    title="AI Suggested Attribution",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Allow manual adjustments
            st.markdown("### Adjust Attribution (Optional)")
            
            adjusted_attributions = []
            total_percentage = 0
            
            for i, attr in enumerate(attributions):
                col_x, col_y = st.columns([2, 1])
                with col_x:
                    st.write(f"**{attr['name']}**")
                with col_y:
                    adjusted_percentage = st.number_input(
                        f"Percentage for {attr['name']}",
                        min_value=0.0,
                        max_value=100.0,
                        value=attr['percentage'],
                        step=0.1,
                        key=f"adjust_{attr['email']}"
                    )
                    adjusted_attributions.append({
                        "contributor_email": attr['email'],
                        "contributor_name": attr['name'],
                        "weight": adjusted_percentage / 100.0,
                        "rationale": f"Qualitative analysis: {attr['description'][:100]}...",
                        "breakdown": {"qualitative_analysis": adjusted_percentage / 100.0}
                    })
                    total_percentage += adjusted_percentage
            
            # Show total and normalize if needed
            if abs(total_percentage - 100.0) > 0.1:
                st.warning(f"Total percentage: {total_percentage:.1f}% (should equal 100%)")
                
                if st.button("Auto-Normalize to 100%", key="normalize_percentages"):
                    # Normalize the percentages
                    for attr in adjusted_attributions:
                        attr["weight"] = (attr["weight"] * 100) / total_percentage / 100
                    st.rerun()
            else:
                st.success(f"Total percentage: {total_percentage:.1f}% ✓")
            
            # Confirm attribution
            col_confirm, col_restart = st.columns(2)
            
            with col_confirm:
                if st.button("Confirm Attribution", key="confirm_qualitative"):
                    # Create final attribution results
                    final_results = {
                        "asset_id": st.session_state.asset_id,
                        "attributions": adjusted_attributions,
                        "total_weight": 1.0,
                        "methodology": "Qualitative analysis with AI interpretation and manual adjustment",
                        "confidence_score": 0.85
                    }
                    
                    st.session_state.attribution_results = final_results
                    st.success("Attribution confirmed! You can now proceed to the next stage.")
                    st.rerun()
            
            with col_restart:
                if st.button("Start Over", key="restart_qualitative"):
                    # Clear qualitative data
                    for key in ["qualitative_descriptions", "ai_suggested_attribution", "qualitative_analysis_complete"]:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()

def render_ownership_stage():
    """Stage 3: Ownership Arrangement"""
    st.markdown('<div class="stage-header">Ownership Arrangement</div>', unsafe_allow_html=True)
    
    # Stage description
    st.markdown("""
    **What is Ownership Arrangement?**
    
    This stage converts contribution analysis into formal ownership structure with legal shares and governance rights.
    Choose from different ownership policies based on your team's needs and agreements.
    
    **Ownership Policies:**
    - **Equal Split**: All contributors get equal shares regardless of contribution
    - **Weighted**: Shares proportional to contribution analysis from previous stage
    - **Funding-Based**: Combines contribution work with financial investment
    - **Time-Vested**: Shares vest over time with cliff periods
    
    **Output**: Formal ownership table with share counts, percentages, and governance rights.
    """)
    
    if not st.session_state.attribution_results:
        st.warning("Please complete the Contribution Attribution stage first.")
        return
    
    # Policy selection
    st.markdown("### Ownership Policy")
    
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
    
    # Generate ownership arrangement
    if st.button("Finalize Ownership Arrangement", key="finalize_ownership"):
        with st.spinner("Calculating ownership arrangement..."):
            response = asyncio.run(call_api_async(
                "/v1/agents/allocation/finalize",
                data={
                    "asset_id": st.session_state.asset_id,
                    "attribution_weights": st.session_state.attribution_results["attributions"],
                    "policy_type": policy_type,
                    "policy_params": {"total_shares": total_shares}
                }
            ))
            
            if response:
                st.session_state.ownership_arrangement = response
                st.success("Ownership arrangement finalized!")
                st.rerun()
    
    # Display ownership arrangement
    if st.session_state.ownership_arrangement:
        st.markdown("### Ownership Structure")
        
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
        
        st.info(f"**Governance:** {arrangement['governance_summary']}")

def render_contracts_stage():
    """Stage 4: Contract Drafting"""
    st.markdown('<div class="stage-header">Contract Drafting</div>', unsafe_allow_html=True)
    
    # Stage description
    st.markdown("""
    **What is Contract Drafting?**
    
    This stage generates professional legal agreements based on your ownership structure and IP requirements.
    Our AI-powered contract composer uses Jinja2 templates to create jurisdiction-specific legal documents.
    
    **Available Contract Types:**
    - **NDA (Non-Disclosure Agreement)**: Protect confidential information during discussions
    - **IP Assignment Agreement**: Formally assign intellectual property rights among contributors
    - **Joint Development Agreement (JDA)**: Structure collaborative development projects
    - **Revenue Sharing Addendum**: Define how profits will be distributed
    
    **Features**: Editable contracts, downloadable documents, and placeholder signing integration.
    """)
    
    if not st.session_state.ownership_arrangement:
        st.warning("Please complete the Ownership Arrangement stage first.")
        return
    
    # Contract type selection
    st.markdown("### Contract Generation")
    
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
            ["UK", "US", "EU", "CA", "AU"],
            index=0,
            key="jurisdiction_select"
        )
    
    # Generate contract
    if st.button(f"Generate {contract_types[selected_contract]}", key="generate_contract"):
        with st.spinner("Generating contract..."):
            response = asyncio.run(call_api_async(
                "/v1/agreements/generate",
                data={
                    "asset_id": st.session_state.asset_id,
                    "contract_type": selected_contract,
                    "ownership_arrangement": st.session_state.ownership_arrangement,
                    "additional_clauses": [],
                    "jurisdiction": jurisdiction
                }
            ))
            
            if response:
                st.session_state.generated_contracts[selected_contract] = response
                st.success(f"{contract_types[selected_contract]} generated successfully!")
                st.rerun()
    
    # Display generated contracts
    if st.session_state.generated_contracts:
        st.markdown("### Generated Contracts")
        
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
                        "Download Contract",
                        data=contract_data["draft_text"],
                        file_name=f"{contract_data['contract_type']}_agreement_{contract_data['agreement_id'][:8]}.txt",
                        mime="text/plain",
                        key=f"download_{contract_type}"
                    )
                    
                    # Sign URL (placeholder)
                    if st.button("Sign Contract", key=f"sign_{contract_type}"):
                        st.info("In production, this would redirect to DocuSign or HelloSign for electronic signature.")
                
                # Contract text (editable)
                edited_text = st.text_area(
                    "Contract Text (Editable)",
                    value=contract_data["draft_text"],
                    height=400,
                    key=f"contract_text_{contract_type}"
                )
                
                # Clauses
                st.write("**Included Clauses:**")
                for clause in contract_data["clauses"]:
                    st.write(f"• {clause}")

def render_licensing_stage():
    """Stage 5: License & Summary"""
    st.markdown('<div class="stage-header">License & Summary</div>', unsafe_allow_html=True)
    
    # Stage description
    st.markdown("""
    **What is License & Summary?**
    
    This final stage recommends appropriate licenses for your intellectual property based on your ownership structure,
    intended use, and dependency requirements. Our license engine analyzes compatibility and provides comprehensive guidance.
    
    **License Analysis Includes:**
    - **Compatibility Scoring**: How well each license fits your project
    - **Dependency Checking**: Ensures compatibility with existing licenses
    - **Usage Terms**: Clear explanation of permissions and restrictions
    - **Obligations**: What you must do to comply with the license
    
    **Popular Licenses**: MIT, Apache 2.0, GPL, BSD, Creative Commons, and Proprietary options.
    """)
    
    if not st.session_state.ownership_arrangement:
        st.warning("Please complete the Ownership Arrangement stage first.")
        return
    
    # License recommendation parameters
    st.markdown("### License Recommendation")
    
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
    
    # Display license recommendations
    if st.session_state.license_recommendations:
        st.markdown("### License Recommendations")
        
        recs = st.session_state.license_recommendations
        
        # Primary recommendation
        if recs.get("primary_recommendation"):
            primary = recs["primary_recommendation"]
            st.markdown("#### Primary Recommendation")
            
            col_a, col_b = st.columns([2, 1])
            with col_a:
                st.markdown(f"**{primary['license_name']}**")
                st.write(primary["rationale"])
                st.write(f"**Usage Terms:** {primary['usage_terms']}")
            with col_b:
                st.metric("Compatibility Score", f"{primary['compatibility_score']:.1%}")
        
        # All recommendations
        st.markdown("#### All Recommendations")
        
        rec_data = []
        for rec in recs["recommended_licenses"]:
            rec_data.append({
                "License": rec["license_name"],
                "Score": f"{rec['compatibility_score']:.1%}",
                "Rationale": rec["rationale"][:100] + "..." if len(rec["rationale"]) > 100 else rec["rationale"]
            })
        
        df = pd.DataFrame(rec_data)
        st.dataframe(df, use_container_width=True)

def render_general_chat():
    """Render general IP advice chat section"""
    st.markdown('<div class="stage-header">General IP Advice</div>', unsafe_allow_html=True)
    
    # Section description
    st.markdown("""
    **Your Personal IP Consultant**
    
    Get expert advice on any intellectual property topic without going through the structured pipeline.
    This is perfect for general questions, exploring IP concepts, or getting quick guidance.
    
    **Ask about:**
    - Patent vs. Trade Secret strategies
    - Copyright and licensing best practices  
    - Trademark registration and protection
    - IP valuation and commercialization
    - International IP protection strategies
    - Open source vs. proprietary licensing
    
    **Powered by our RAG system** with comprehensive IP law knowledge base.
    """)
    
    st.markdown("---")
    
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
        elif current_stage == 1:
            render_attribution_stage()
        elif current_stage == 2:
            render_ownership_stage()
        elif current_stage == 3:
            render_contracts_stage()
        elif current_stage == 4:
            render_licensing_stage()
    
    with tab2:
        render_general_chat()

if __name__ == "__main__":
    main()
