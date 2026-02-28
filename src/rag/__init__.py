"""
MaterCare Homes - RAG Knowledge Base
====================================
Retrieval-Augmented Generation for healthcare knowledge.
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import os
import logging

logger = logging.getLogger(__name__)

try:
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
except ImportError:
    logger.warning("LangChain not installed. RAG features limited.")


@dataclass
class KnowledgeSource:
    """Knowledge source for RAG."""
    name: str
    content: str
    source_type: str  # "url", "file", "manual"


@dataclass
class RetrievedContext:
    """Retrieved context from knowledge base."""
    content: str
    source: str
    score: float


class KnowledgeBase:
    """Healthcare knowledge base with RAG."""
    
    DEFAULT_SOURCES = [
        {
            "name": "CDC Elder Health",
            "content": """
            # Elder Health Guidelines
            
            ## Dehydration Signs in Elderly
            - Dry mouth, lips, tongue
            - Dark urine or decreased urination
            - Confusion, irritability
            - Dizziness, headaches
            - Sunken eyes, decreased skin elasticity
            
            ## Fall Prevention
            - Remove throw rugs or secure with non-slip
            - Install grab bars in bathroom
            - Ensure adequate lighting
            - Keep floors clear of clutter
            - Use non-slip mats in tub/shower
            
            ## Warning Signs of Stroke (BE FAST)
            - Balance: Sudden loss of balance
            - Eyes: Vision changes
            - Face: Face drooping
            - Arm: Arm weakness
            - Speech: Slurred speech
            - Time: Call 911 immediately
            """,
            "source_type": "manual"
        },
        {
            "name": "Medication Management",
            "content": """
            # Medication Guidelines for Seniors
            
            ## Common Drug Interactions
            - Warfarin + NSAIDs = bleeding risk
            - ACE inhibitors + potassium = high potassium
            - Metformin + contrast dye = lactic acidosis
            
            ## Medication Adherence Tips
            - Use pill organizers
            - Take medications same time daily
            - Never crush extended-release without approval
            - Review medications with doctor regularly
            
            ## Signs of Adverse Reactions
            - Dizziness or falls
            - Confusion
            - Rash or itching
            - Swelling
            - Difficulty breathing (emergency)
            """,
            "source_type": "manual"
        },
        {
            "name": "Dementia Care",
            "content": """
            # Dementia Care Guidelines
            
            ## Stages of Alzheimer's
            Early: Memory lapses, difficulty with complex tasks
            Middle: Confusion about time/place, personality changes
            Late: Loss of communication, total dependence
            
            ## Communication Tips
            - Use simple, clear language
            - Maintain eye contact
            - Listen patiently
            - Don't argue or correct
            
            ## Safety Precautions
            - Remove dangerous items
            - Install locks on cabinets
            - Use GPS tracking for wandering
            - Consider emergency response system
            
            ## Caregiver Support
            - Take regular breaks
            - Seek support groups
            - Maintain own health
            - Ask for help when needed
            """,
            "source_type": "manual"
        }
    ]
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.vectorstore = None
        self.embeddings = None
        self._initialized = False
    
    def _initialize(self):
        """Initialize embeddings and vectorstore."""
        if self._initialized:
            return
        
        try:
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
            
            sources = self.DEFAULT_SOURCES
            documents = []
            
            for source in sources:
                doc = Document(
                    page_content=source["content"],
                    metadata={"source": source["name"], "type": source["source_type"]}
                )
                documents.append(doc)
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50
            )
            splits = text_splitter.split_documents(documents)
            
            self.vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
            
            self._initialized = True
            logger.info("Knowledge base initialized with default sources")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG: {e}")
            self._initialized = True
    
    def add_source(self, source: KnowledgeSource):
        """Add a new knowledge source."""
        self._initialize()
        
        doc = Document(
            page_content=source.content,
            metadata={"source": source.name, "type": source.source_type}
        )
        
        if self.vectorstore:
            self.vectorstore.add_documents([doc])
            logger.info(f"Added source: {source.name}")
    
    def retrieve(self, query: str, k: int = 3) -> List[RetrievedContext]:
        """Retrieve relevant context for a query."""
        self._initialize()
        
        if not self.vectorstore:
            return []
        
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        
        contexts = []
        for doc, score in results:
            contexts.append(RetrievedContext(
                content=doc.page_content,
                source=doc.metadata.get("source", "unknown"),
                score=score
            ))
        
        return contexts
    
    def format_context(self, query: str) -> str:
        """Format retrieved context for LLM prompt."""
        contexts = self.retrieve(query)
        
        if not contexts:
            return "No relevant context found."
        
        formatted = "Relevant healthcare information:\n\n"
        for ctx in contexts:
            formatted += f"[Source: {ctx.source}]\n{ctx.content}\n\n"
        
        return formatted


def create_knowledge_base() -> KnowledgeBase:
    """Factory function to create knowledge base."""
    return KnowledgeBase()
