from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from .agent import QueryFormationAgent
from .configuration import QueryFormationConfig
from .state import QueryContext
from shared.logging_utils import QueryFormationLogger

class QueryFormationProcessor:
    """Processes text documents to extract verifiable medical claims."""
    
    def __init__(self, config: QueryFormationConfig):
        self.config = config
        self.agent = QueryFormationAgent(config)
        self.logger = QueryFormationLogger()
        
    def process_markdown_sections(self, file_path: Path) -> List[Dict[str, Any]]:
        """Process a markdown file and extract verifiable claims."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        sections = self._read_markdown_sections(file_path)
        verified_claims = []
        
        for section in sections:
            if not section["paragraph"]:
                continue
                
            context = QueryContext(
                heading=section["heading"],
                subheading=section["subheading"],
                paragraph=section["paragraph"]
            )
            
            # Process sentences in the paragraph
            claims = self._process_section(section["paragraph"], context)
            verified_claims.extend(claims)
            
            # Check if we've reached the maximum sentences (if configured)
            if self.config.max_sentences and len(verified_claims) >= self.config.max_sentences:
                break
                
        return verified_claims
    
    def _read_markdown_sections(self, file_path: Path) -> List[Dict[str, str]]:
        """Read markdown file and split into sections with headings."""
        sections = []
        current_section = {
            "heading": "",
            "subheading": "",
            "content": [],
            "paragraph": ""
        }
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            if not line:
                if current_section["content"]:
                    current_section["paragraph"] = " ".join(current_section["content"])
                    sections.append(current_section.copy())
                    current_section["content"] = []
                continue
                
            if line.startswith('# '):
                if current_section["content"]:
                    current_section["paragraph"] = " ".join(current_section["content"])
                    sections.append(current_section.copy())
                current_section = {
                    "heading": line[2:],
                    "subheading": "",
                    "content": [],
                    "paragraph": ""
                }
            elif line.startswith('## '):
                current_section["subheading"] = line[3:]
            else:
                current_section["content"].append(line)
                
        # Add the last section if it has content
        if current_section["content"]:
            current_section["paragraph"] = " ".join(current_section["content"])
            sections.append(current_section)
            
        return sections
    
    def _process_section(self, text: str, context: QueryContext) -> List[Dict[str, Any]]:
        """Process a section of text and extract verifiable claims."""
        sentences = text.split(". ")
        claims = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            result = self.agent.analyze_sentence(sentence, context)
            self.logger.log_analysis(sentence, vars(context), result)
            
            if result["needs_verification"]:
                claims.append({
                    "sentence": sentence,
                    "query": result["query"],
                    "reasoning": result["reasoning"],
                    "context": vars(context)
                })
                
        return claims 