"""
MaterCare Homes - Document Processor
====================================
Convert healthcare URLs to knowledge base content using Jina AI.
"""

from typing import Optional, Dict, List
import requests
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class JinaAIDocumentConverter:
    """Convert web pages to Markdown/JSON for RAG knowledge base."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or "jina_492c48beb31643e3b5a81c4052fa0628fS7ORRidO2zZAueI2W9OgX1QPDML"
        self.base_url = "https://r.jina.ai"
    
    def convert_url(
        self,
        url: str,
        use_readerlm_v2: bool = True,
        gather_links: bool = False
    ) -> Optional[str]:
        """Convert URL to Markdown content."""
        try:
            endpoint = f"{self.base_url}/v1/convert/url"
            
            payload = {
                "url": url,
                "reader": use_readerlm_v2,
                "gather_links": gather_links
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return response.text
            else:
                logger.error(f"Jina AI error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            return None
    
    def convert_to_json(self, url: str) -> Optional[Dict]:
        """Convert URL to structured JSON."""
        try:
            endpoint = f"{self.base_url}/v1/convert"
            
            payload = {
                "url": url,
                "output": "json"
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            logger.error(f"JSON conversion failed: {e}")
            return None
    
    def extract_content(self, url: str) -> Optional[Dict]:
        """Extract structured content from healthcare URL."""
        content = self.convert_url(url)
        
        if not content:
            return None
        
        return {
            "url": url,
            "content": content,
            "source": "jina_ai",
            "processed_at": str(datetime.now())
        }


def convert_url_to_markdown(url: str, api_key: Optional[str] = None) -> Optional[str]:
    """Quick function to convert URL to Markdown."""
    converter = JinaAIDocumentConverter(api_key)
    return converter.convert_url(url)


def convert_url_to_json(url: str, api_key: Optional[str] = None) -> Optional[Dict]:
    """Quick function to convert URL to JSON."""
    converter = JinaAIDocumentConverter(api_key)
    return converter.convert_to_json(url)


# Healthcare sources for knowledge base
HEALTHCARE_SOURCES = {
    "cdc_elder_health": "https://www.cdc.gov/aging/index.html",
    "nih_senior_health": "https://www.nih.gov/health-information",
    "alzheimer_association": "https://www.alz.org/",
    "mayo_clinic_geriatrics": "https://www.mayoclinic.org/departments-centers/geriatric-medicine",
    "medicare_basics": "https://www.medicare.gov/basics/get-started-with-medicare",
}


def build_knowledge_base(sources: Dict[str, str]) -> List[Dict]:
    """Build knowledge base from healthcare URLs."""
    converter = JinaAIDocumentConverter()
    
    documents = []
    for name, url in sources.items():
        logger.info(f"Processing: {name}")
        result = converter.extract_content(url)
        if result:
            documents.append({
                "name": name,
                "url": url,
                "content": result.get("content", "")
            })
    
    return documents
