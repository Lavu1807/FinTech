"""
Graph Compilation and Singleton Factory.
Integrates MemorySaver checkpointing and metadata tracking.
"""
from datetime import datetime, timezone
from typing import Dict, Any
from pathlib import Path
from backend.utils.logger import logger

from langgraph.graph.state import CompiledStateGraph

from .graph_builder import build_workflow as create_finsight_graph

_compiled_graph = None

def create_graph():
    return create_finsight_graph()

def build_workflow() -> CompiledStateGraph:
    """Compiles the workflow with MemorySaver and exports diagrams."""
    global _compiled_graph
    if _compiled_graph is None:
        workflow = create_graph()
        _compiled_graph = workflow.compile()
        
        # Automatic Graph Export
        export_dir = Path(__file__).resolve().parent.parent / "exports" / "workflow"
        export_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            mermaid_text = _compiled_graph.get_graph().draw_mermaid()
            with open(export_dir / "workflow.mermaid", "w") as f:
                f.write(mermaid_text)
                
            # Attempt PNG generation, catch if pygraphviz/system deps are missing
            try:
                png_bytes = _compiled_graph.get_graph().draw_mermaid_png()
                with open(export_dir / "workflow.png", "wb") as f:
                    f.write(png_bytes)
            except Exception as e:
                logger.warning(f"Could not export graph PNG (likely missing system dependencies): {str(e)}")
                
        except Exception as e:
            logger.error(f"Graph compilation export failed: {str(e)}")
            
    return _compiled_graph

def run_graph(initial_state: Dict[str, Any], thread_id: str = "default", session_id: str = "default_session"):
    """
    Executes the compiled graph with configurable runtime metadata.
    """
    graph = build_workflow()
    
    config = {
        "configurable": {
            "thread_id": thread_id,
            "session_id": session_id,
            "workflow_version": "1.0.0",
            "compiled_at": datetime.now(timezone.utc).isoformat()
        }
    }
    
    return graph.invoke(initial_state, config=config)
