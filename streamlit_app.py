"""
Eqip.ai - Complete IP Lifecycle Pipeline (Streamlit Cloud Deployment)

This is the main entry point for Streamlit Cloud deployment.
Includes fallback functionality for demo mode when backend is not available.
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

# Configuration - Use secrets for production, fallback for demo
API_BASE = st.secrets.get("API_BASE", "http://localhost:8000")
DEMO_MODE = st.secrets.get("DEMO_MODE", "true").lower() == "true"

# Import the enhanced app functionality first
try:
    # Try to import from the enhanced app
    import sys
    sys.path.append('frontend')
    
    # Import everything except the page config
    import importlib.util
    spec = importlib.util.spec_from_file_location("streamlit_app_enhanced", "frontend/streamlit_app_enhanced.py")
    enhanced_module = importlib.util.module_from_spec(spec)
    
    # Set page config before importing
    st.set_page_config(
        page_title="Eqip.ai - Complete IP Pipeline", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Now execute the module
    spec.loader.exec_module(enhanced_module)
    
    # Import all functions we need
    from frontend.streamlit_app_enhanced import (
        initialize_session_state, render_progress_bar, render_stage_overview,
        render_ip_options_stage, render_attribution_stage, render_ownership_stage,
        render_contracts_stage, render_licensing_stage, render_general_chat,
        call_api_async
    )
    
    # Override API calls for demo mode
    if DEMO_MODE:
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
                        "Design Rights: Protect visual appearance and configuration"
                    ],
                    "risks": [
                        "Public disclosure may limit future patent options",
                        "Infringement monitoring required for enforcement"
                    ],
                    "next_steps": [
                        "Document creation and ownership details",
                        "Consider formal IP registration where applicable",
                        "Implement IP protection policies"
                    ],
                    "citations": [
                        "UK Intellectual Property Framework - gov.uk/ip-guidance",
                        "Copyright, Designs and Patents Act 1988"
                    ]
                }
            
            elif "/v1/agents/attribution/run" in endpoint:
                contributors = data.get("contributors", [])
                if not contributors:
                    contributors = [
                        {"email": "demo@example.com", "display_name": "Demo User", "org": "Demo Corp"}
                    ]
                
                return {
                    "asset_id": data.get("asset_id", 12345),
                    "attributions": [
                        {
                            "contributor_email": contrib["email"],
                            "contributor_name": contrib["display_name"],
                            "weight": 1.0 / len(contributors),
                            "rationale": f"Equal attribution in demo mode",
                            "breakdown": {"code": 0.4, "design": 0.3, "review": 0.2, "documentation": 0.1}
                        } for contrib in contributors
                    ],
                    "total_weight": 1.0,
                    "methodology": "Demo mode - equal distribution",
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
                            "governance_rights": "equal" if len(attributions) > 1 else "sole"
                        } for attr in attributions
                    ],
                    "total_shares": 1000000,
                    "governance_summary": f"Demo ownership structure with {len(attributions)} contributors",
                    "policy_applied": data.get("policy_type", "weighted")
                }
            
            elif "/v1/agreements/generate" in endpoint:
                import uuid
                return {
                    "agreement_id": str(uuid.uuid4()),
                    "contract_type": data.get("contract_type", "nda"),
                    "draft_text": f"DEMO {data.get('contract_type', 'NDA').upper()} AGREEMENT\n\nThis is a demonstration contract generated by Eqip.ai.\n\nIn production, this would contain a complete legal agreement based on your ownership structure and requirements.\n\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    "clauses": ["Demo Clause 1", "Demo Clause 2", "Demo Clause 3"],
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
                            "rationale": "Excellent for software projects with commercial potential",
                            "usage_terms": "Permits commercial use, modification, distribution, and private use",
                            "obligations": ["Include license text", "Include copyright notice"]
                        },
                        {
                            "license_name": "Apache License 2.0",
                            "compatibility_score": 0.90,
                            "rationale": "Good for enterprise software with patent considerations",
                            "usage_terms": "Permits commercial use with explicit patent grant",
                            "obligations": ["Include license text", "Include copyright notice", "State changes"]
                        }
                    ],
                    "primary_recommendation": {
                        "license_name": "MIT License",
                        "compatibility_score": 0.95,
                        "rationale": "Excellent for software projects with commercial potential",
                        "usage_terms": "Permits commercial use, modification, distribution, and private use",
                        "obligations": ["Include license text", "Include copyright notice"]
                    },
                    "compatibility_issues": []
                }
            
            else:
                return {"status": "demo_mode", "message": "This is a demo response"}
        
        # Replace the real API call function with demo version
        globals()['call_api_async'] = call_api_async_demo

except ImportError:
    st.error("Could not import enhanced app functionality. Please check your deployment.")
    st.stop()

# Main execution
if __name__ == "__main__":
    if DEMO_MODE:
        st.info("🎭 Running in Demo Mode - All API calls are mocked for demonstration")
    
    main()
