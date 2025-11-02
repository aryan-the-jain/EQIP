#!/usr/bin/env python3
"""
Test script for the RAG system
"""
import asyncio
import os
import sys

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.knowledge_base import knowledge_base_service
from backend.services.rag import rag_service
from backend.models.models import Base
from backend.services.database import engine

async def test_rag_system():
    """Test the complete RAG system"""
    print("🚀 Testing RAG System for IP Path Finder")
    print("=" * 50)
    
    try:
        # Create all tables
        print("📊 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        # Initialize knowledge base
        print("📚 Initializing knowledge base...")
        await knowledge_base_service.initialize_database()
        
        # Get stats
        stats = await knowledge_base_service.get_document_stats()
        print(f"📈 Knowledge base stats: {stats}")
        
        # Test queries
        test_queries = [
            "How should I protect my software invention?",
            "What are the risks of trade secret protection?",
            "Should I file a patent for my algorithm?",
            "What IP protection is available in the UK?",
            "How do I protect my dataset?"
        ]
        
        print("\n🔍 Testing RAG queries...")
        print("-" * 30)
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Query: {query}")
            
            try:
                result = await rag_service.search_and_generate(
                    query=query,
                    asset_type="software",
                    jurisdictions=["US", "UK"]
                )
                
                print(f"   Options: {result.get('options', [])[:2]}")  # Show first 2
                print(f"   Risks: {result.get('risks', [])[:2]}")      # Show first 2
                print(f"   Citations: {len(result.get('citations', []))}")
                print(f"   Context used: {result.get('context_used', 0)}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print("\n✅ RAG system test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Set a dummy OpenAI API key for testing (won't actually call OpenAI without real key)
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: No OpenAI API key found. Set OPENAI_API_KEY environment variable for full testing.")
        print("   The system will use fallback responses.")
    
    asyncio.run(test_rag_system())
