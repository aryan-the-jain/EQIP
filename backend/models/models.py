from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from ..services.database import Base, engine
import uuid

# Check if we're using PostgreSQL or SQLite
try:
    from pgvector.sqlalchemy import Vector
    USE_PGVECTOR = True
except ImportError:
    USE_PGVECTOR = False

# Check database type
DATABASE_TYPE = str(engine.url).split('://')[0] if engine else 'sqlite'

class Asset(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)
    uri = Column(String, nullable=True)
    sha256 = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    disclosure_status = Column(String, default="undisclosed")
    confidentiality = Column(String, default="confidential")

class Contributor(Base):
    __tablename__ = "contributors"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    display_name = Column(String)
    org = Column(String)

class OwnershipShare(Base):
    __tablename__ = "ownership_shares"
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    contributor_id = Column(Integer, ForeignKey("contributors.id"))
    pct = Column(Float)
    policy_id = Column(Integer, nullable=True)
    effective_ts = Column(DateTime, default=datetime.utcnow)

class IPDocument(Base):
    __tablename__ = "ip_documents"
    
    if DATABASE_TYPE == 'postgresql':
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    else:
        id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    document_type = Column(String, nullable=False)  # 'patent', 'trademark', 'copyright', 'trade_secret', 'licensing'
    jurisdiction = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class IPDocumentChunk(Base):
    __tablename__ = "ip_document_chunks"
    
    if DATABASE_TYPE == 'postgresql' and USE_PGVECTOR:
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        document_id = Column(UUID(as_uuid=True), ForeignKey("ip_documents.id"), nullable=False)
        chunk_index = Column(Integer, nullable=False)
        content = Column(Text, nullable=False)
        embedding = Column(Vector(3072), nullable=False)  # text-embedding-3-large dimensions
        created_at = Column(DateTime, default=datetime.utcnow)
        
        # Index for vector similarity search
        __table_args__ = (
            Index('ix_ip_document_chunks_embedding', 'embedding', postgresql_using='ivfflat', postgresql_ops={'embedding': 'vector_cosine_ops'}),
        )
    else:
        # SQLite fallback - store embeddings as JSON text
        id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
        document_id = Column(String, ForeignKey("ip_documents.id"), nullable=False)
        chunk_index = Column(Integer, nullable=False)
        content = Column(Text, nullable=False)
        embedding = Column(Text, nullable=False)  # JSON string for SQLite
        created_at = Column(DateTime, default=datetime.utcnow)
        
        __table_args__ = ()
    
    # Relationship
    document = relationship("IPDocument", backref="chunks")
