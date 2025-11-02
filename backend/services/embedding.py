"""
OpenAI Embedding Service for RAG pipeline
"""
import asyncio
from typing import List, Optional
import openai
from openai import OpenAI
import tiktoken
from loguru import logger
from ..config import settings

class EmbeddingService:
    """Service for generating embeddings using OpenAI's text-embedding-3-large model"""
    
    def __init__(self):
        self.api_key_available = bool(settings.openai_api_key and settings.openai_api_key != "your_openai_api_key_here")
        
        if self.api_key_available:
            self.client = OpenAI(api_key=settings.openai_api_key)
        else:
            self.client = None
            logger.warning("OpenAI API key not available - using dummy embeddings for testing")
        
        self.model = settings.embedding_model
        self.dimensions = settings.embedding_dimensions
        self.encoding = tiktoken.get_encoding("cl100k_base")
        
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken"""
        return len(self.encoding.encode(text))
    
    def chunk_text(self, text: str, max_tokens: int = 8000) -> List[str]:
        """
        Split text into chunks that fit within token limits
        OpenAI's text-embedding-3-large has a context length of 8,191 tokens
        """
        chunks = []
        current_chunk = ""
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        for paragraph in paragraphs:
            paragraph_tokens = self.count_tokens(paragraph)
            current_tokens = self.count_tokens(current_chunk)
            
            # If adding this paragraph would exceed limit, save current chunk
            if current_tokens + paragraph_tokens > max_tokens and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Add the last chunk if it exists
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text"""
        if not self.api_key_available:
            # Return dummy embedding for testing
            import random
            random.seed(hash(text) % (2**32))  # Deterministic based on text
            return [random.random() for _ in range(self.dimensions)]
        
        try:
            # Check token count
            token_count = self.count_tokens(text)
            if token_count > 8000:
                logger.warning(f"Text has {token_count} tokens, which exceeds the limit. Truncating...")
                # Truncate to fit within limits
                tokens = self.encoding.encode(text)[:8000]
                text = self.encoding.decode(tokens)
            
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
                dimensions=self.dimensions
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    async def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts in batch"""
        if not self.api_key_available:
            # Return dummy embeddings for testing
            import random
            embeddings = []
            for text in texts:
                random.seed(hash(text) % (2**32))  # Deterministic based on text
                embeddings.append([random.random() for _ in range(self.dimensions)])
            return embeddings
        
        try:
            # Filter out empty texts and check token counts
            valid_texts = []
            for text in texts:
                if not text.strip():
                    continue
                    
                token_count = self.count_tokens(text)
                if token_count > 8000:
                    logger.warning(f"Text has {token_count} tokens, truncating...")
                    tokens = self.encoding.encode(text)[:8000]
                    text = self.encoding.decode(tokens)
                
                valid_texts.append(text)
            
            if not valid_texts:
                return []
            
            # OpenAI allows up to 2048 inputs per batch
            batch_size = 100  # Conservative batch size
            all_embeddings = []
            
            for i in range(0, len(valid_texts), batch_size):
                batch = valid_texts[i:i + batch_size]
                
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch,
                    dimensions=self.dimensions
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
            
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise

# Global instance
embedding_service = EmbeddingService()
