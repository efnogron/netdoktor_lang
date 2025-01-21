from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.box import ROUNDED
from typing import Dict, Any, List
from pathlib import Path

class VerificationOutputFormatter:
    """Format verification results for console output."""
    
    def __init__(self):
        self.console = Console()
        
    def format_claim(self, claim_data: Dict[str, Any], claim_number: int) -> None:
        """Format a single claim verification result."""
        # Create header
        self.console.print(f"\n[bold cyan]Claim #{claim_number}[/bold cyan]", soft_wrap=True, crop=False)
        
        # Original text panel
        original_text = Panel(
            Text(claim_data["original_sentence"], style="yellow"),
            title="Original Text",
            box=ROUNDED
        )
        self.console.print(original_text, soft_wrap=True, crop=False)
        
        # Context
        if "context_paragraph" in claim_data:
            context = Panel(
                Text(claim_data["context_paragraph"], style="dim"),
                title="Context",
                box=ROUNDED
            )
            self.console.print(context, soft_wrap=True, crop=False)
        
        # Verification Query
        query = Panel(
            Text(claim_data["verification_query"], style="green"),
            title="Verification Query",
            box=ROUNDED
        )
        self.console.print(query, soft_wrap=True, crop=False)
        
        # Evidence Table
        if claim_data["retrieved_chunks"]:
            table = Table(
                title="Retrieved Evidence",
                box=ROUNDED,
                show_header=True,
                header_style="bold magenta",
                show_lines=True
            )
            table.add_column("Score", style="cyan", justify="right", width=8)
            table.add_column("Content", style="green")  # Remove fixed width to allow wrapping
            table.add_column("Source", style="dim", width=30)
            
            for chunk in claim_data["retrieved_chunks"]:
                content = chunk["content"]
                source = Path(chunk["metadata"]["source"]).name
                score = f"{chunk['score']:.3f}"
                table.add_row(score, content, source)
            
            self.console.print(table, soft_wrap=True, crop=False)
        else:
            self.console.print("[yellow]No evidence chunks retrieved[/yellow]", soft_wrap=True, crop=False)
        
        # Verification Result
        if "verification_result" in claim_data:
            result = claim_data["verification_result"]
            result_panel = Panel(
                Text("\n".join(result["messages"]), style="bold white"),
                title=f"Verification Result ({result['status']})",
                box=ROUNDED,
                border_style="green" if result["status"] == "SUCCESS" else "red"
            )
            self.console.print(result_panel, soft_wrap=True, crop=False)
        
        # Separator
        self.console.print("\n" + "="*80 + "\n", soft_wrap=True, crop=False)

def format_verification_results(results_dir: Path) -> None:
    """Format all verification results from a directory."""
    import json
    
    formatter = VerificationOutputFormatter()
    console = Console()
    
    # Get all claim files
    claim_files = sorted(results_dir.glob("claim_*.json"))
    
    console.print(f"\n[bold]Processing {len(claim_files)} claims from {results_dir.name}[/bold]\n", 
                 soft_wrap=True, crop=False)
    
    for i, claim_file in enumerate(claim_files, 1):
        with open(claim_file, 'r', encoding='utf-8') as f:
            claim_data = json.load(f)
        formatter.format_claim(claim_data, i) 