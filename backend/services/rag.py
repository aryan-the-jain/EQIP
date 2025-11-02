"""
RAG (Retrieval-Augmented Generation) Service for IP Path Finding
"""
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text, func
import openai
from openai import OpenAI
from loguru import logger

from ..models.models import IPDocument, IPDocumentChunk, DATABASE_TYPE, USE_PGVECTOR
import json
from ..services.database import SessionLocal
from ..services.embedding import embedding_service
from ..config import settings

class RAGService:
    """Service for retrieval-augmented generation in IP domain"""
    
    def __init__(self):
        self.api_key_available = bool(settings.openai_api_key and settings.openai_api_key != "your_openai_api_key_here")
        
        if self.api_key_available:
            self.client = OpenAI(api_key=settings.openai_api_key)
        else:
            self.client = None
            logger.warning("OpenAI API key not available - using fallback responses")
        
        self.embedding_service = embedding_service
        
    async def retrieve_relevant_chunks(
        self, 
        query: str, 
        asset_type: str = None,
        jurisdictions: List[str] = None,
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant document chunks using vector similarity search
        """
        try:
            # Generate embedding for the query
            query_embedding = await self.embedding_service.get_embedding(query)
            
            # Create database session
            db = SessionLocal()
            
            try:
                if DATABASE_TYPE == 'postgresql' and USE_PGVECTOR:
                    # Use pgvector for similarity search
                    similarity_query = text("""
                        SELECT 
                            c.id,
                            c.content,
                            c.chunk_index,
                            d.title,
                            d.document_type,
                            d.jurisdiction,
                            d.source_url,
                            1 - (c.embedding <=> :query_embedding) as similarity
                        FROM ip_document_chunks c
                        JOIN ip_documents d ON c.document_id = d.id
                        WHERE 1 - (c.embedding <=> :query_embedding) > :threshold
                    """)
                    
                    params = {
                        'query_embedding': str(query_embedding),
                        'threshold': similarity_threshold
                    }
                else:
                    # SQLite fallback - flexible text search with keywords
                    query_keywords = [word.strip().lower() for word in query.split() if len(word.strip()) > 2]
                    
                    # Add common IP-related terms to increase matches
                    ip_terms = ['protection', 'intellectual', 'property', 'copyright', 'patent', 'trademark', 'secret', 'license']
                    
                    # If no good keywords found, use IP terms
                    if not query_keywords:
                        query_keywords = ip_terms[:3]
                    else:
                        # Add relevant IP terms based on query context
                        if any(term in query.lower() for term in ['app', 'software', 'code', 'program']):
                            query_keywords.extend(['software', 'copyright', 'patent'])
                        if any(term in query.lower() for term in ['algorithm', 'method', 'process']):
                            query_keywords.extend(['patent', 'secret'])
                        if any(term in query.lower() for term in ['brand', 'name', 'logo']):
                            query_keywords.extend(['trademark'])
                    
                    # Remove duplicates and limit
                    query_keywords = list(set(query_keywords))[:5]
                    
                    # Build LIKE conditions for each keyword
                    like_conditions = []
                    params = {}
                    for i, keyword in enumerate(query_keywords):
                        like_conditions.append(f"(LOWER(c.content) LIKE :keyword_{i} OR LOWER(d.title) LIKE :keyword_{i})")
                        params[f'keyword_{i}'] = f'%{keyword}%'
                    
                    where_clause = " OR ".join(like_conditions)
                    
                    similarity_query = text(f"""
                        SELECT 
                            c.id,
                            c.content,
                            c.chunk_index,
                            d.title,
                            d.document_type,
                            d.jurisdiction,
                            d.source_url,
                            0.8 as similarity
                        FROM ip_document_chunks c
                        JOIN ip_documents d ON c.document_id = d.id
                        WHERE {where_clause}
                    """)
                
                # Add filters if provided
                if DATABASE_TYPE == 'postgresql':
                    if jurisdictions:
                        similarity_query = text(str(similarity_query) + " AND d.jurisdiction = ANY(:jurisdictions)")
                        params['jurisdictions'] = jurisdictions
                    
                    # Add document type filter based on asset type
                    if asset_type:
                        doc_type_mapping = {
                            'software': ['copyright', 'patent', 'trade_secret'],
                            'dataset': ['copyright', 'trade_secret'],
                            'invention': ['patent', 'trade_secret'],
                            'media': ['copyright', 'trademark']
                        }
                        relevant_types = doc_type_mapping.get(asset_type, ['patent', 'copyright', 'trademark', 'trade_secret'])
                        similarity_query = text(str(similarity_query) + " AND d.document_type = ANY(:doc_types)")
                        params['doc_types'] = relevant_types
                else:
                    # SQLite-compatible filters
                    if jurisdictions:
                        jurisdiction_filter = " AND (" + " OR ".join([f"d.jurisdiction = :jurisdiction_{i}" for i in range(len(jurisdictions))]) + ")"
                        similarity_query = text(str(similarity_query) + jurisdiction_filter)
                        for i, jurisdiction in enumerate(jurisdictions):
                            params[f'jurisdiction_{i}'] = jurisdiction
                    
                    # Add document type filter based on asset type
                    if asset_type:
                        doc_type_mapping = {
                            'software': ['copyright', 'patent', 'trade_secret'],
                            'dataset': ['copyright', 'trade_secret'],
                            'invention': ['patent', 'trade_secret'],
                            'media': ['copyright', 'trademark']
                        }
                        relevant_types = doc_type_mapping.get(asset_type, ['patent', 'copyright', 'trademark', 'trade_secret'])
                        type_filter = " AND (" + " OR ".join([f"d.document_type = :doc_type_{i}" for i in range(len(relevant_types))]) + ")"
                        similarity_query = text(str(similarity_query) + type_filter)
                        for i, doc_type in enumerate(relevant_types):
                            params[f'doc_type_{i}'] = doc_type
                
                # Add ordering and limit
                similarity_query = text(str(similarity_query) + " ORDER BY similarity DESC LIMIT :limit")
                params['limit'] = limit
                
                # Execute query
                result = db.execute(similarity_query, params)
                chunks = result.fetchall()
                
                # Format results
                relevant_chunks = []
                for chunk in chunks:
                    relevant_chunks.append({
                        'id': str(chunk.id),
                        'content': chunk.content,
                        'chunk_index': chunk.chunk_index,
                        'document_title': chunk.title,
                        'document_type': chunk.document_type,
                        'jurisdiction': chunk.jurisdiction,
                        'source_url': chunk.source_url,
                        'similarity': float(chunk.similarity)
                    })
                
                return relevant_chunks
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error retrieving relevant chunks: {e}")
            raise
    
    async def generate_ip_recommendations(
        self, 
        query: str, 
        relevant_chunks: List[Dict[str, Any]],
        asset_type: str = None,
        jurisdictions: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate IP recommendations using retrieved context
        """
        try:
            # Prepare context from retrieved chunks
            context_parts = []
            citations = []
            
            for i, chunk in enumerate(relevant_chunks):
                context_parts.append(f"Source {i+1} ({chunk['document_type']} - {chunk['jurisdiction'] or 'General'}):\n{chunk['content']}")
                
                citation = f"{chunk['document_title']}"
                if chunk['jurisdiction']:
                    citation += f" ({chunk['jurisdiction']})"
                if chunk['source_url']:
                    citation += f" - {chunk['source_url']}"
                citations.append(citation)
            
            context = "\n\n".join(context_parts)
            
            if not self.api_key_available:
                # Fallback response when no OpenAI API key
                content = f"""Based on the query "{query}" and available context, here are general IP recommendations:

1. IP Protection Strategies:
- Consider copyright protection for creative works and software
- Evaluate patent protection for novel inventions and processes
- Implement trade secret protection for confidential information
- Register trademarks for brand elements

2. Risk Considerations:
- Public disclosure may limit patent options
- Trade secrets require ongoing confidentiality measures
- Copyright has limited scope of protection
- International protection requires separate filings

3. Next Steps:
- Conduct prior art search
- Consult with IP attorney
- Prepare disclosure documents
- Evaluate commercial potential

This is a general response. For specific legal advice, consult with a qualified IP attorney."""
            else:
                # Create the prompt
                system_prompt = """You are an expert IP consultant specializing in intellectual property strategy. 
                Based on the provided legal documents and context, provide comprehensive IP recommendations.
                
                Your response should be structured and include:
                1. Recommended IP protection strategies
                2. Potential risks and considerations
                3. Next steps and timeline
                4. Jurisdiction-specific advice when applicable
                
                Be specific, actionable, and cite relevant legal principles from the provided context."""
                
                user_prompt = f"""
                Asset Type: {asset_type or 'Not specified'}
                Jurisdictions of Interest: {', '.join(jurisdictions) if jurisdictions else 'Not specified'}
                
                Question: {query}
                
                Relevant Legal Context:
                {context}
                
                Please provide detailed IP recommendations based on this context.
                """
                
                # Generate response using OpenAI
                response = self.client.chat.completions.create(
                    model="gpt-4o",  # Using GPT-4 for better reasoning
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3,  # Lower temperature for more consistent legal advice
                    max_tokens=2000
                )
                
                # Parse the response
                content = response.choices[0].message.content
            
            # Extract structured information (simple parsing - could be improved)
            options = self._extract_options(content)
            risks = self._extract_risks(content)
            next_steps = self._extract_next_steps(content)
            
            return {
                'options': options,
                'risks': risks,
                'next_steps': next_steps,
                'detailed_analysis': content,
                'citations': citations,
                'context_used': len(relevant_chunks)
            }
            
        except Exception as e:
            logger.error(f"Error generating IP recommendations: {e}")
            raise
    
    def _extract_options(self, content: str) -> List[str]:
        """Extract IP protection options from generated content"""
        options = []
        
        # Look for common IP protection types
        ip_types = ['patent', 'copyright', 'trademark', 'trade secret', 'licensing', 'nda']
        
        for ip_type in ip_types:
            if ip_type.lower() in content.lower():
                # Try to extract the relevant sentence
                sentences = content.split('.')
                for sentence in sentences:
                    if ip_type.lower() in sentence.lower() and ('recommend' in sentence.lower() or 'consider' in sentence.lower()):
                        options.append(sentence.strip())
                        break
                else:
                    # Fallback: just add the IP type
                    options.append(ip_type.title())
        
        return options[:5]  # Limit to top 5
    
    def _extract_risks(self, content: str) -> List[str]:
        """Extract risks from generated content"""
        risks = []
        
        # Look for risk indicators
        risk_indicators = ['risk', 'danger', 'concern', 'issue', 'problem', 'challenge']
        
        sentences = content.split('.')
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(indicator in sentence_lower for indicator in risk_indicators):
                risks.append(sentence.strip())
        
        return risks[:5]  # Limit to top 5
    
    def _extract_next_steps(self, content: str) -> List[str]:
        """Extract next steps from generated content"""
        next_steps = []
        
        # Look for action indicators
        action_indicators = ['should', 'must', 'need to', 'recommend', 'suggest', 'file', 'register', 'prepare']
        
        sentences = content.split('.')
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(indicator in sentence_lower for indicator in action_indicators):
                next_steps.append(sentence.strip())
        
        return next_steps[:5]  # Limit to top 5
    
    async def search_and_generate(
        self, 
        query: str, 
        asset_type: str = None,
        jurisdictions: List[str] = None
    ) -> Dict[str, Any]:
        """
        Complete RAG pipeline: retrieve relevant chunks and generate recommendations
        """
        try:
            # Step 1: Retrieve relevant chunks
            relevant_chunks = await self.retrieve_relevant_chunks(
                query=query,
                asset_type=asset_type,
                jurisdictions=jurisdictions,
                limit=5
            )
            
            if not relevant_chunks:
                logger.warning("No relevant chunks found for query")
                return {
                    'options': ['Consider consulting with an IP attorney for specific guidance'],
                    'risks': ['Insufficient legal precedent data available'],
                    'next_steps': ['Gather more specific information about your asset', 'Consult with IP professionals'],
                    'detailed_analysis': 'No specific legal precedents found in our database for this query.',
                    'citations': [],
                    'context_used': 0
                }
            
            # Step 2: Generate recommendations
            recommendations = await self.generate_ip_recommendations(
                query=query,
                relevant_chunks=relevant_chunks,
                asset_type=asset_type,
                jurisdictions=jurisdictions
            )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}")
            raise

# Global instance
rag_service = RAGService()
