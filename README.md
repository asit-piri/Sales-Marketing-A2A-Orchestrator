# Sales & Marketing A2A Orchestrator

This project showcases an agent-to-agent workflow that coordinates three distinct agents using the A2A SDK:

- **LangChain Reader** — ingests a sales and marketing dataset and emits structured insights.
- **CrewAI Analyst** — transforms the reader output into strategic recommendations.
- **AutoGen Visualizer** — generates charts and fine analytics, leveraging tool calls to produce visual artifacts.

Outputs from every agent are rendered in a Streamlit UI so you can inspect the entire conversation as well as agent-specific deliverables.

## Prerequisites

- Python 3.13 (managed automatically by [`uv`](https://docs.astral.sh/uv/))
- An OpenAI API key exported as `OPENAI_API_KEY`

```powershell
# Windows PowerShell example
env:OPENAI_API_KEY = "sk-..."
```

## Installation

```powershell
uv venv .venv
uv pip install -r pyproject.toml
```

> The project already includes a `pyproject.toml` with all required dependencies. Once installed, activate the environment if your shell does not automatically pick it up.

```powershell
.venv\Scripts\Activate.ps1
```

## Running the Streamlit UI

```powershell
streamlit run src/ui/app.py
```

The app loads a bundled sample dataset located at `data/sales_marketing.csv`. You can also upload your own CSV. Each agent run will produce:

1. A LangChain-generated synopsis and key metrics.
2. A CrewAI briefing with markdown narrative plus JSON analytics.
3. AutoGen-produced charts saved as JSON Plotly figures and an executive summary.

All intermediate A2A messages are available under the **Conversation** tab for auditing.

## Orchestration Flow

```
coordinator (A2A message) → LangChain Reader → CrewAI Analyst → AutoGen Visualizer → Streamlit UI
```

Each hand-off is represented as an A2A `Message`, complete with structured `DataPart` payloads that capture metrics, records, or tool outputs. The helper functions in `src/a2a_utils.py` keep the implementation function-based as requested.

## Sample Data

`data/sales_marketing.csv` contains a synthetic January 2025 pipeline covering sales, channel, and marketing spend metrics. Feel free to replace it with your own dataset as long as the headers align with the demo (Date, Region, Product, Channel, Sales, Marketing_Spend, Qualified_Leads, New_Customers).

## Notes

- AutoGen requires the environment variable `OPENAI_API_KEY`. Without it, the visualizer agent will raise an error.
- Plotly figures are persisted as JSON files under `artifacts/autogen`. Re-running the workflow will overwrite previous artifacts.
- All project code follows a function-based approach with no custom classes, using library primitives for agent construction.

## macOS (zsh) — recommended run steps

Use the bundled `.venv` so Streamlit and the project dependencies (for example `a2a`, `autogen-ext`) are picked up correctly. From the project root:

Activate the virtualenv, then run Streamlit:

```bash
source .venv/bin/activate
streamlit run src/ui/app.py
```

Alternatively, run Streamlit with the venv Python without activating the shell:

```bash
.venv/bin/python3.13 -m streamlit run src/ui/app.py
```

If you previously started Streamlit in a different environment (for example Conda `base`), stop that process (Ctrl+C in its terminal) before running from the project venv.

Helper script
-------------

There's a small convenience wrapper at `scripts/run_streamlit.sh` that activates the project's `.venv` (when present) and runs Streamlit from the repository root. From the project root you can run:

```bash
./scripts/run_streamlit.sh
```

If a Streamlit process is already running, stop it first (Ctrl+C) or find and kill the process listening on the Streamlit port (usually 8501) before using this script.


