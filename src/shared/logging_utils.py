import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict

class QueryFormationLogger:
    """Logger for query formation process with structured output."""
    
    def __init__(self, log_dir: str = "logs/query_formation"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create timestamp for log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Setup main logger
        self.logger = logging.getLogger("query_formation")
        self.logger.setLevel(logging.INFO)
        
        # Remove any existing handlers
        self.logger.handlers = []
        
        # Create single log file handler
        self.log_file = self.log_dir / f"query_formation_{timestamp}.log"
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler
        self.logger.addHandler(file_handler)
        
        # Store results for summary
        self.results = []
        
        # Store JSON results file path
        self.json_file = self.log_dir / f"query_formation_results_{timestamp}.json"

    def log_analysis(
        self,
        sentence: str,
        context: Dict[str, str],
        analysis_result: Dict[str, Any]
    ) -> None:
        """Log a single sentence analysis with its context."""
        
        # Create a nicely formatted log message
        log_message = (
            f"\nSentence Analysis:"
            f"\n==================="
            f"\nSentence: {sentence}"
            f"\nContext:"
            f"\n  Heading: {context.get('heading', '')}"
            f"\n  Subheading: {context.get('subheading', '')}"
            f"\n  Paragraph: {context.get('paragraph', '')}"
            f"\nAnalysis Result:"
            f"\n  Needs Verification: {analysis_result.get('needs_verification', False)}"
            f"\n  Query: {analysis_result.get('query', 'None')}"
            f"\n  Reasoning: {analysis_result.get('reasoning', 'None')}"
            f"\n-------------------\n"
        )
        
        self.logger.info(log_message)
        
        # Store structured result
        self.results.append({
            "sentence": sentence,
            "context": context,
            "analysis": analysis_result,
            "timestamp": datetime.now().isoformat()
        })

    def log_error(self, error_message: str, details: Dict[str, Any] = None) -> None:
        """Log error messages with optional details."""
        self.logger.error(
            f"Error: {error_message}"
            + (f"\nDetails: {json.dumps(details, indent=2)}" if details else "")
        )

    def save_results(self) -> None:
        """Save accumulated results to JSON file."""
        summary = self.get_summary()
        
        output = {
            "summary": summary,
            "results": self.results,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_entries": len(self.results)
            }
        }
        
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
            
        self.logger.info(f"Results saved to: {self.json_file}")

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of analyzed sentences."""
        total = len(self.results)
        needs_verification = sum(
            1 for r in self.results 
            if r["analysis"].get("needs_verification", False)
        )
        
        return {
            "total_sentences": total,
            "needs_verification": needs_verification,
            "verification_rate": f"{(needs_verification/total)*100:.2f}%" if total > 0 else "0%"
        } 