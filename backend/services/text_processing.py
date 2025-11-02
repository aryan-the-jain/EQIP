"""
Text processing utilities for RAG pipeline
"""
import re
from typing import List, Dict, Any
from loguru import logger
from ..config import settings

class TextProcessor:
    """Service for processing and chunking text documents"""
    
    def __init__(self):
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\"\'\/]', '', text)
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        return text.strip()
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """Extract different sections from legal/IP documents"""
        sections = {}
        
        # Common IP document section patterns
        section_patterns = {
            'abstract': r'(?i)abstract\s*:?\s*(.*?)(?=\n\s*\n|\n\s*[A-Z][^a-z]*:|\Z)',
            'claims': r'(?i)claims?\s*:?\s*(.*?)(?=\n\s*\n|\n\s*[A-Z][^a-z]*:|\Z)',
            'background': r'(?i)background\s*:?\s*(.*?)(?=\n\s*\n|\n\s*[A-Z][^a-z]*:|\Z)',
            'summary': r'(?i)summary\s*:?\s*(.*?)(?=\n\s*\n|\n\s*[A-Z][^a-z]*:|\Z)',
            'description': r'(?i)(?:detailed\s+)?description\s*:?\s*(.*?)(?=\n\s*\n|\n\s*[A-Z][^a-z]*:|\Z)',
        }
        
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, text, re.DOTALL)
            if match:
                sections[section_name] = self.clean_text(match.group(1))
        
        # If no sections found, use entire text
        if not sections:
            sections['content'] = self.clean_text(text)
        
        return sections
    
    def chunk_text_semantic(self, text: str) -> List[Dict[str, Any]]:
        """
        Create semantic chunks that respect document structure
        """
        chunks = []
        
        # First, try to extract sections
        sections = self.extract_sections(text)
        
        for section_name, section_text in sections.items():
            if not section_text.strip():
                continue
                
            # Split section into paragraphs
            paragraphs = [p.strip() for p in section_text.split('\n\n') if p.strip()]
            
            current_chunk = ""
            current_size = 0
            
            for paragraph in paragraphs:
                paragraph_size = len(paragraph)
                
                # If this paragraph alone exceeds chunk size, split it
                if paragraph_size > self.chunk_size:
                    # Save current chunk if it exists
                    if current_chunk:
                        chunks.append({
                            'content': current_chunk.strip(),
                            'section': section_name,
                            'size': current_size
                        })
                        current_chunk = ""
                        current_size = 0
                    
                    # Split large paragraph into sentences
                    sentences = self._split_into_sentences(paragraph)
                    temp_chunk = ""
                    temp_size = 0
                    
                    for sentence in sentences:
                        sentence_size = len(sentence)
                        if temp_size + sentence_size > self.chunk_size and temp_chunk:
                            chunks.append({
                                'content': temp_chunk.strip(),
                                'section': section_name,
                                'size': temp_size
                            })
                            temp_chunk = sentence
                            temp_size = sentence_size
                        else:
                            temp_chunk += " " + sentence if temp_chunk else sentence
                            temp_size += sentence_size
                    
                    if temp_chunk:
                        current_chunk = temp_chunk
                        current_size = temp_size
                
                # If adding this paragraph would exceed chunk size
                elif current_size + paragraph_size > self.chunk_size and current_chunk:
                    chunks.append({
                        'content': current_chunk.strip(),
                        'section': section_name,
                        'size': current_size
                    })
                    
                    # Start new chunk with overlap if configured
                    if self.chunk_overlap > 0:
                        overlap_text = self._get_overlap_text(current_chunk, self.chunk_overlap)
                        current_chunk = overlap_text + " " + paragraph
                        current_size = len(current_chunk)
                    else:
                        current_chunk = paragraph
                        current_size = paragraph_size
                else:
                    # Add paragraph to current chunk
                    if current_chunk:
                        current_chunk += "\n\n" + paragraph
                    else:
                        current_chunk = paragraph
                    current_size += paragraph_size
            
            # Add final chunk if it exists
            if current_chunk:
                chunks.append({
                    'content': current_chunk.strip(),
                    'section': section_name,
                    'size': current_size
                })
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting - could be improved with spaCy or NLTK
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_overlap_text(self, text: str, overlap_size: int) -> str:
        """Get the last N characters for overlap"""
        if len(text) <= overlap_size:
            return text
        
        # Try to break at word boundary
        overlap_text = text[-overlap_size:]
        space_index = overlap_text.find(' ')
        if space_index > 0:
            return overlap_text[space_index:].strip()
        
        return overlap_text
    
    def extract_metadata(self, text: str, document_type: str) -> Dict[str, Any]:
        """Extract metadata from document based on type"""
        metadata = {
            'document_type': document_type,
            'word_count': len(text.split()),
            'char_count': len(text)
        }
        
        # Patent-specific metadata
        if document_type == 'patent':
            # Extract patent number
            patent_match = re.search(r'(?:Patent|Application)\s+(?:No\.?\s*)?([A-Z0-9,]+)', text, re.IGNORECASE)
            if patent_match:
                metadata['patent_number'] = patent_match.group(1)
            
            # Extract inventor names
            inventor_match = re.search(r'Inventor[s]?\s*:?\s*([^\n]+)', text, re.IGNORECASE)
            if inventor_match:
                metadata['inventors'] = [name.strip() for name in inventor_match.group(1).split(',')]
        
        # Trademark-specific metadata
        elif document_type == 'trademark':
            # Extract trademark classes
            class_match = re.search(r'Class(?:es)?\s*:?\s*([0-9,\s]+)', text, re.IGNORECASE)
            if class_match:
                metadata['classes'] = [c.strip() for c in class_match.group(1).split(',')]
        
        return metadata

# Global instance
text_processor = TextProcessor()
