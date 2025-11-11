from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from src.a2a_utils import (
    create_agent_card,
    create_text_message,
    extract_text_from_message,
    get_data_part,
)
from src.agents.autogen_agent import run_autogen_visualizer
from src.agents.crewai_agent import run_crewai_analysis
from src.agents.langchain_agent import run_langchain_reader


def orchestrate_sales_insights(
    csv_path: str | Path,
    *,
    output_dir: str | Path = "artifacts",
    model_overrides: dict[str, str] | None = None,
    progress_callback: Callable[[str, dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    """Drive agent-to-agent collaboration using A2A message conventions."""
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset could not be located at {path}")

    models = {
        "langchain": "gpt-4o-mini",
        "crewai": "gpt-4o-mini",
        "autogen": "gpt-4o",
    }
    if model_overrides:
        models.update(model_overrides)

    artifacts_root = Path(output_dir)
    artifacts_root.mkdir(parents=True, exist_ok=True)

    agent_cards = {
        "reader": create_agent_card(
            name="LangChain Reader",
            description="Extracts structured insights from sales CSV files",
            skill_id="sales_csv_ingest",
            skill_name="Sales Document Ingestion",
            skill_description="Reads sales and marketing records and summarizes key signals.",
        ),
        "analyst": create_agent_card(
            name="CrewAI Analyst",
            description="Transforms raw metrics into strategic sales guidance",
            skill_id="sales_revops_analysis",
            skill_name="Revenue Analysis",
            skill_description="Produces narrative and quantitative insights for leadership decisions.",
        ),
        "visualizer": create_agent_card(
            name="AutoGen Visualizer",
            description="Builds visuals and recommendations from sales intelligence",
            skill_id="sales_visual_story",
            skill_name="Visualization & Fine Analytics",
            skill_description="Generates charts and fine-grained analytics for stakeholders.",
        ),
    }

    transcript: list[dict[str, Any]] = []

    request_message = create_text_message(
        content=(
            "Analyze the provided sales and marketing dataset and prepare executive-ready insights. "
            f"File path: {path}"
        )
    )
    transcript.append({"from": "coordinator", "message": request_message})

    reader_result = run_langchain_reader(path, llm_model=models["langchain"])
    transcript.append({"from": "LangChain Reader", "message": reader_result["message"]})
    if progress_callback:
        progress_callback("reader", reader_result)

    analyst_result = run_crewai_analysis(
        sales_records=reader_result["records"],
        reader_summary=reader_result["summary_text"],
        metrics=reader_result["metrics"],
        llm_model=models["crewai"],
    )
    transcript.append({"from": "CrewAI Analyst", "message": analyst_result["message"]})
    if progress_callback:
        progress_callback("analyst", analyst_result)

    visual_result = run_autogen_visualizer(
        sales_records=reader_result["records"],
        analysis_summary=analyst_result["analysis_text"],
        output_dir=artifacts_root / "autogen",
        llm_model=models["autogen"],
    )
    transcript.append({"from": "AutoGen Visualizer", "message": visual_result["message"]})
    if progress_callback:
        progress_callback("visualizer", visual_result)

    return {
        "cards": agent_cards,
        "transcript": transcript,
        "reader": {
            "summary": reader_result["summary_text"],
            "metrics": reader_result["metrics"],
            "records": reader_result["records"],
        },
        "analyst": {
            "analysis": analyst_result["analysis_text"],
            "structured": analyst_result["structured"],
        },
        "visualizer": {
            "insights": visual_result["visual_text"],
            "tool_outputs": visual_result["tool_outputs"],
            "artifacts_directory": str((artifacts_root / "autogen").resolve()),
            "raw_messages": visual_result["task_messages"],
        },
        "conversation_log": [
            {
                "speaker": entry["from"],
                "text": extract_text_from_message(entry["message"]),
                "data": get_data_part(entry["message"]),
            }
            for entry in transcript
        ],
    }
