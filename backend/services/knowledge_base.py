"""
Knowledge Base Management Service for IP Documents
"""
import asyncio
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from loguru import logger

from ..models.models import IPDocument, IPDocumentChunk, DATABASE_TYPE, USE_PGVECTOR
import json
from ..services.database import SessionLocal, engine
from ..services.embedding import embedding_service
from ..services.text_processing import text_processor

class KnowledgeBaseService:
    """Service for managing IP knowledge base documents and embeddings"""
    
    def __init__(self):
        self.embedding_service = embedding_service
        self.text_processor = text_processor
    
    async def initialize_database(self):
        """Initialize database with pgvector extension (if PostgreSQL) and sample data"""
        try:
            if DATABASE_TYPE == 'postgresql' and USE_PGVECTOR:
                # Create pgvector extension
                with engine.connect() as conn:
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                    conn.commit()
                logger.info("Database initialized with pgvector extension")
            else:
                logger.info("Database initialized with SQLite fallback")
            
            # Load sample documents if none exist
            db = SessionLocal()
            try:
                doc_count = db.query(IPDocument).count()
                if doc_count == 0:
                    logger.info("Loading sample IP documents...")
                    await self.load_sample_documents()
                else:
                    logger.info(f"Knowledge base already contains {doc_count} documents")
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    async def add_document(
        self, 
        title: str, 
        content: str, 
        document_type: str,
        jurisdiction: str = None,
        source_url: str = None
    ) -> str:
        """Add a new document to the knowledge base with embeddings"""
        try:
            db = SessionLocal()
            
            try:
                # Create document record
                document = IPDocument(
                    title=title,
                    content=content,
                    document_type=document_type,
                    jurisdiction=jurisdiction,
                    source_url=source_url
                )
                
                db.add(document)
                db.flush()  # Get the ID
                
                # Process and chunk the document
                chunks = self.text_processor.chunk_text_semantic(content)
                
                # Generate embeddings for chunks
                chunk_texts = [chunk['content'] for chunk in chunks]
                embeddings = await self.embedding_service.get_embeddings_batch(chunk_texts)
                
                # Create chunk records with embeddings
                for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                    if DATABASE_TYPE == 'postgresql' and USE_PGVECTOR:
                        chunk_record = IPDocumentChunk(
                            document_id=document.id,
                            chunk_index=i,
                            content=chunk['content'],
                            embedding=embedding
                        )
                    else:
                        # Store embedding as JSON string for SQLite
                        chunk_record = IPDocumentChunk(
                            document_id=document.id,
                            chunk_index=i,
                            content=chunk['content'],
                            embedding=json.dumps(embedding)
                        )
                    db.add(chunk_record)
                
                db.commit()
                
                logger.info(f"Added document '{title}' with {len(chunks)} chunks")
                return str(document.id)
                
            except Exception as e:
                db.rollback()
                raise
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            raise
    
    async def load_sample_documents(self):
        """Load sample IP documents for testing and demonstration"""
        
        sample_documents = [
            {
                'title': 'Software Copyright Protection Guidelines',
                'content': '''
                Copyright Protection for Software

                Abstract:
                Software copyright protection provides automatic protection for original computer programs and source code. This protection extends to the expression of ideas in code, but not to the underlying algorithms or methods.

                Key Principles:
                1. Automatic Protection: Copyright protection begins immediately upon creation of original code
                2. Expression vs Ideas: Copyright protects the specific expression of code, not the underlying functionality
                3. Duration: Protection lasts for the life of the author plus 70 years (varies by jurisdiction)
                4. Registration Benefits: While not required, registration provides additional legal benefits

                Scope of Protection:
                - Source code and object code
                - User interfaces and screen displays
                - Documentation and comments
                - Database structures and schemas

                Limitations:
                - Does not protect algorithms or methods
                - Fair use exceptions apply
                - Reverse engineering for interoperability may be permitted
                - Independent creation is a valid defense

                Best Practices:
                1. Include copyright notices in all source files
                2. Maintain detailed development records
                3. Use version control systems with timestamps
                4. Consider registration for commercially important software
                5. Implement proper licensing terms

                Enforcement:
                Copyright owners can pursue remedies including injunctive relief, monetary damages, and attorney fees in cases of willful infringement.
                ''',
                'document_type': 'copyright',
                'jurisdiction': 'US',
                'source_url': 'https://example.com/software-copyright'
            },
            {
                'title': 'Patent Protection for Software Inventions',
                'content': '''
                Patent Protection for Software and Computer-Implemented Inventions

                Background:
                Software patents protect novel and non-obvious computer-implemented inventions. Unlike copyright, patents protect the functional aspects and methods embodied in software.

                Patentability Requirements:
                1. Subject Matter Eligibility: Must be more than an abstract idea
                2. Novelty: Must be new compared to prior art
                3. Non-obviousness: Must not be obvious to a person skilled in the art
                4. Utility: Must have a practical application

                Patent-Eligible Software:
                - Specific technical improvements to computer functionality
                - Methods that solve technical problems
                - Systems with novel hardware-software integration
                - Algorithms with specific technical applications

                Non-Eligible Subject Matter:
                - Abstract mathematical formulas
                - Mental processes
                - Business methods without technical implementation
                - Laws of nature

                Claims Drafting:
                Software patent claims should focus on:
                1. Technical implementation details
                2. Specific computer operations
                3. Improvements to computer functionality
                4. Integration with hardware components

                Prosecution Strategy:
                - Emphasize technical advantages
                - Distinguish from abstract ideas
                - Provide detailed technical specifications
                - Consider continuation applications

                International Considerations:
                Patent eligibility varies significantly by jurisdiction. European Patent Office requires technical character, while other jurisdictions may have different standards.

                Duration and Maintenance:
                Software patents typically last 20 years from filing date, subject to maintenance fee payments.
                ''',
                'document_type': 'patent',
                'jurisdiction': 'US',
                'source_url': 'https://example.com/software-patents'
            },
            {
                'title': 'Trade Secret Protection for Proprietary Algorithms',
                'content': '''
                Trade Secret Protection for Algorithms and Proprietary Technology

                Definition:
                Trade secrets protect confidential business information that derives economic value from not being generally known and is subject to reasonable efforts to maintain secrecy.

                Requirements for Trade Secret Protection:
                1. Information must be secret
                2. Must have economic value from secrecy
                3. Must take reasonable measures to protect secrecy

                Advantages of Trade Secret Protection:
                - No registration required
                - Indefinite duration if secrecy maintained
                - Immediate protection
                - No disclosure requirements
                - Protects against reverse engineering

                What Can Be Protected:
                - Proprietary algorithms and formulas
                - Source code and implementation details
                - Customer lists and databases
                - Manufacturing processes
                - Business strategies and methods

                Reasonable Measures to Protect:
                1. Non-disclosure agreements (NDAs)
                2. Employee confidentiality agreements
                3. Access controls and security measures
                4. Physical security of facilities
                5. Digital security and encryption
                6. Need-to-know basis for information sharing

                Employee Considerations:
                - Comprehensive confidentiality agreements
                - Exit interviews and return of materials
                - Non-compete agreements where enforceable
                - Training on confidentiality obligations

                Enforcement:
                Trade secret owners can seek:
                - Injunctive relief to prevent disclosure
                - Monetary damages including lost profits
                - Reasonable royalties
                - Attorney fees in cases of willful misappropriation

                Loss of Protection:
                Trade secret protection is lost when:
                - Information becomes publicly known
- Independent discovery by others
                - Reverse engineering of publicly available products
                - Failure to maintain reasonable secrecy measures

                International Protection:
                Many countries have trade secret laws, but enforcement and remedies vary significantly by jurisdiction.
                ''',
                'document_type': 'trade_secret',
                'jurisdiction': 'US',
                'source_url': 'https://example.com/trade-secrets'
            },
            {
                'title': 'UK Intellectual Property Framework',
                'content': '''
                United Kingdom Intellectual Property Protection Framework

                Overview:
                The UK provides comprehensive intellectual property protection through various statutes and common law principles, administered by the UK Intellectual Property Office (UKIPO).

                Copyright Protection:
                - Automatic protection for original works
                - Duration: Life of author plus 70 years
                - No registration required
                - Covers literary, dramatic, musical, and artistic works
                - Computer programs protected as literary works

                Patent Protection:
                - Registration required through UKIPO
                - 20-year protection from filing date
                - Must be novel, involve inventive step, and be capable of industrial application
                - Computer programs "as such" excluded, but technical applications may be patentable

                Trade Mark Protection:
                - Registration provides 10 years protection, renewable indefinitely
                - Protects distinctive signs used in trade
                - Common law rights may exist for unregistered marks
                - Madrid Protocol available for international registration

                Design Rights:
                - Registered designs: up to 25 years protection
                - Unregistered design rights: automatic protection for original designs
                - Community design rights available through EU system

                Trade Secrets:
                - Protected under common law and Trade Secrets Regulations 2018
                - No registration required
                - Protection against unlawful acquisition, use, or disclosure

                Enforcement:
                UK courts provide various remedies:
                - Injunctive relief
                - Damages or account of profits
                - Delivery up or destruction of infringing goods
                - Criminal penalties for certain IP crimes

                Brexit Implications:
                - UK no longer participates in EU unitary systems
                - Existing EU rights converted to UK equivalents
                - Separate applications now required for UK protection

                Key Legislation:
                - Copyright, Designs and Patents Act 1988
                - Patents Act 1977
                - Trade Marks Act 1994
                - Trade Secrets Regulations 2018
                ''',
                'document_type': 'licensing',
                'jurisdiction': 'UK',
                'source_url': 'https://example.com/uk-ip-framework'
            },
            {
                'title': 'Data Protection and IP Licensing Agreements',
                'content': '''
                Intellectual Property Licensing in the Data Protection Era

                Introduction:
                Modern IP licensing must consider data protection regulations, particularly when licensing involves personal data processing or cross-border data transfers.

                Key Considerations for IP Licensing:

                1. Data Processing Rights:
                - Licensee's right to process personal data
                - Compliance with GDPR, CCPA, and other regulations
                - Data controller vs processor responsibilities
                - Cross-border transfer mechanisms

                2. License Scope and Data:
                - Clear definition of licensed IP vs data rights
                - Restrictions on data use and processing
                - Data retention and deletion obligations
                - Audit rights for data protection compliance

                3. Technical and Organizational Measures:
                - Security requirements for licensed technology
                - Data protection by design and by default
                - Incident notification procedures
                - Regular security assessments

                Standard License Clauses:

                Data Protection Compliance:
                "Licensee shall comply with all applicable data protection laws and regulations in its use of the Licensed Technology, including but not limited to implementing appropriate technical and organizational measures to protect personal data."

                Cross-Border Transfers:
                "Any transfer of personal data outside the EEA in connection with the Licensed Technology shall be subject to appropriate safeguards as required by applicable data protection law."

                Liability and Indemnification:
                - Data breach liability allocation
                - Regulatory fine responsibility
                - Indemnification for data protection violations
                - Insurance requirements

                Termination and Data Return:
                - Data deletion obligations upon termination
                - Certification of data destruction
                - Survival of data protection obligations

                International Considerations:
                Different jurisdictions have varying data protection requirements that must be considered in licensing agreements:
                - EU GDPR requirements
                - California CCPA compliance
                - UK Data Protection Act 2018
                - Sectoral regulations (HIPAA, FERPA, etc.)

                Best Practices:
                1. Conduct data protection impact assessments
                2. Implement privacy by design principles
                3. Regular compliance audits and reviews
                4. Clear data processing documentation
                5. Incident response procedures
                ''',
                'document_type': 'licensing',
                'jurisdiction': 'EU',
                'source_url': 'https://example.com/data-protection-licensing'
            }
        ]
        
        # Add each sample document
        for doc in sample_documents:
            try:
                await self.add_document(
                    title=doc['title'],
                    content=doc['content'],
                    document_type=doc['document_type'],
                    jurisdiction=doc.get('jurisdiction'),
                    source_url=doc.get('source_url')
                )
            except Exception as e:
                logger.error(f"Error loading sample document '{doc['title']}': {e}")
        
        logger.info(f"Loaded {len(sample_documents)} sample documents")
    
    async def search_documents(
        self, 
        query: str, 
        document_type: str = None,
        jurisdiction: str = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search documents in the knowledge base"""
        try:
            db = SessionLocal()
            
            try:
                # Build query
                query_obj = db.query(IPDocument)
                
                if document_type:
                    query_obj = query_obj.filter(IPDocument.document_type == document_type)
                
                if jurisdiction:
                    query_obj = query_obj.filter(IPDocument.jurisdiction == jurisdiction)
                
                # Simple text search (could be enhanced with full-text search)
                if query:
                    query_obj = query_obj.filter(
                        IPDocument.content.contains(query) | 
                        IPDocument.title.contains(query)
                    )
                
                documents = query_obj.limit(limit).all()
                
                return [
                    {
                        'id': str(doc.id),
                        'title': doc.title,
                        'document_type': doc.document_type,
                        'jurisdiction': doc.jurisdiction,
                        'source_url': doc.source_url,
                        'created_at': doc.created_at.isoformat()
                    }
                    for doc in documents
                ]
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise
    
    async def get_document_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        try:
            db = SessionLocal()
            
            try:
                total_docs = db.query(IPDocument).count()
                total_chunks = db.query(IPDocumentChunk).count()
                
                # Count by document type
                type_counts = db.query(
                    IPDocument.document_type,
                    func.count(IPDocument.id)
                ).group_by(IPDocument.document_type).all()
                
                # Count by jurisdiction
                jurisdiction_counts = db.query(
                    IPDocument.jurisdiction,
                    func.count(IPDocument.id)
                ).group_by(IPDocument.jurisdiction).all()
                
                return {
                    'total_documents': total_docs,
                    'total_chunks': total_chunks,
                    'documents_by_type': dict(type_counts),
                    'documents_by_jurisdiction': dict(jurisdiction_counts)
                }
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error getting document stats: {e}")
            raise

# Global instance
knowledge_base_service = KnowledgeBaseService()
