import asyncio
from typing import Dict, Any
from loguru import logger

from ..schemas.schemas import IPOptionsIn, IPOptionsOut
from ..services.rag import rag_service
from ..services.knowledge_base import knowledge_base_service

async def run_async(payload: IPOptionsIn) -> IPOptionsOut:
    """
    Real IP path finder using RAG pipeline with OpenAI embeddings and pgvector
    """
    try:
        # Initialize knowledge base if needed
        await knowledge_base_service.initialize_database()
        
        # Construct query from payload with conversation context
        query_parts = []
        
        if payload.questions:
            query_parts.append(payload.questions)
        else:
            query_parts.append("What IP protection strategies should I consider?")
        
        # Add conversation context if available
        if payload.conversation_context:
            context_summary = "Previous conversation context: "
            recent_messages = payload.conversation_context[-4:]  # Last 4 messages
            for msg in recent_messages:
                context_summary += f"{msg.role}: {msg.content[:100]}... "
            query_parts.append(context_summary)
        
        # Add asset context if available (would need to fetch from database)
        query_parts.append("I need advice on intellectual property protection strategies.")
        
        query = " ".join(query_parts)
        
        # Use RAG service to get recommendations
        recommendations = await rag_service.search_and_generate(
            query=query,
            asset_type=None,  # Could be enhanced to fetch from asset_id
            jurisdictions=payload.jurisdictions if payload.jurisdictions else None
        )
        
        # Format response according to schema
        return IPOptionsOut(
            options=recommendations.get('options', []),
            risks=recommendations.get('risks', []),
            next_steps=recommendations.get('next_steps', []),
            citations=recommendations.get('citations', [])
        )
        
    except Exception as e:
        logger.error(f"Error in IP path finder: {e}")
        
        # Fallback to basic recommendations
        return IPOptionsOut(
            options=["Consult with IP attorney", "Consider copyright protection", "Evaluate trade secret protection"],
            risks=["Insufficient information for detailed analysis"],
            next_steps=["Provide more specific details about your asset", "Consult with IP professionals"],
            citations=["General IP guidance - consult professional for specific advice"]
        )

def run(payload: IPOptionsIn) -> IPOptionsOut:
    """
    Synchronous wrapper for the async IP path finder
    """
    try:
        # Run the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(run_async(payload))
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"Error running IP path finder: {e}")
        
        # Fallback response
        return IPOptionsOut(
            options=["Consult with IP attorney"],
            risks=["System temporarily unavailable"],
            next_steps=["Try again later or consult with IP professionals"],
            citations=["System error - professional consultation recommended"]
        )
