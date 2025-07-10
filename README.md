## AutoStat-Agent Project Specification

**Version 0.2 • Last updated July 10, 2025**

AutoStat-Agent is an intelligent research assistant designed to automate the lifecycle of statistical analysis for structured datasets. Given a high-level research question and dataset input, the system plans and executes a sequence of analytical steps such as data cleaning, statistical testing, visualization, and summarization. It produces both intermediate outputs (e.g., metrics, plots) and final deliverables (e.g., Markdown or PDF reports), using a combination of planning models, statistical toolchains, and large language models (LLMs).

The system follows the **Plan–Reflect–Execute** paradigm:

- **Plan**: Break down user intent into a structured sequence of analysis steps.
- **Reflect**: Validate and critique intermediate results through rule checks or optional LLM-based review.
- **Execute**: Invoke analytical tools to produce artefacts.

---

### 1. High-Level Architecture

```text
┌───────────────────────────┐
│ 1. Context Assembly       │  ← Ingest user query, datasets, preferences
└────────────┬──────────────┘
             │
    ┌────────▼─────────┐
    │ 2. Planner       │  ← Decompose goals into PlanSteps
    └────────┬─────────┘
             │
    ┌────────▼─────────┐
    │ 3. Executor      │  ← Invoke tools, produce artefacts
    └────────┬─────────┘
             │
    ┌────────▼─────────┐
    │ 4. Critic/Verifier│ ← Validate outputs, retry or repair
    └────────┬─────────┘
             │
    ┌────────▼─────────┐
    │ 5. Summarizer    │  ← Generate narrative reports
    └────────┬─────────┘
             │
    ┌────────▼─────────┐
    │ 6. Response & Log│  ← Stream results, persist audit trail
    └───────────────────┘
```

---

### 2. Component Specifications

#### 2.1 Context Assembly

- **Role:** Collect user input (research question), dataset metadata, and preferences.
- **Output:** `PromptState` (normalized model capturing datasets, question, options).

#### 2.2 Planner

- **Interface:**
  ```python
  def plan(prompt_state: PromptState) -> List[PlanStep]
  ```
- **Variants:** LLM-based for flexibility; rule-based fallback for common patterns.
- **Validation:** JSON-schema or Pydantic ensures each `PlanStep` meets required structure.

#### 2.3 Executor

- **Tool Registry:** Maps `tool_id` to executable backends (Python functions, SQL templates, ML pipelines).
- **Engine:** Runs steps either in-process (prototype) or in parallel via Ray tasks (production).
- **Artifacts:** DataFrames → Parquet/Arrow; charts → image files; text → structured strings.
- **Result Model:** `ExecutionResult(step_id, artifact_refs: Dict[str, str])`.

#### 2.4 Critic / Verifier

- **Checks:** Schema presence (e.g., required columns), file sanity (existence, size).
- **Optional LLM Critic:** Reviews narrative for coherence; flags anomalies.
- **Error Handling:** Retries with adjusted parameters or alternative tools; logs failures.

#### 2.5 Summarizer

- **Input:** Plan steps and execution results from the analysis pipeline.
- **Output:** Comprehensive markdown reports with executive summaries, detailed sections for each analysis step, embedded visualizations, and formatted statistical results.
- **Features:** Automatic narrative generation, error reporting, tabular data formatting, artifact embedding, and quick summary generation.
- **Interface:** `create_analysis_report()` for full reports, `quick_summary()` for brief status updates.

#### 2.6 Response & Logging

- **Streaming API:** Server-Sent Events or WebSocket for real-time feedback.
- **Audit Trail:** Serialized logs (e.g. JSON or SQLite) capturing run metadata, plans, tool outputs.

---

### 3. Module Responsibilities and File Structure

#### `api/`

- `main.py`: FastAPI app entry point; mounts routers and initializes core components.
- `routers/analyze.py`: Handles `/analyze` endpoint for submitting research prompts.
- `routers/datasets.py`: Manages dataset upload, metadata, and retrieval endpoints.
- `schemas.py`: Pydantic request and response models for all API routes.

#### `core/`

- `agent.py`: The central agent loop orchestrating planner → executor → summarizer.
- `state.py`: Shared data models such as `PromptState`, `RunResult`, etc.
- `registry.py`: Lazy-loaded registry access to planner, executor, and summarizer.

#### `planner/`

- `llm_planner.py`: Primary planner using LLM to break down high-level prompts.
- `schemas.py`: Pydantic models for `Plan`, `PlanStep`, and validation helpers.
- `parsing.py`: JSON parsing and plan creation utilities for LLM responses.
- `processing.py`: Plan post-processing utilities for deduplication and normalization.
- `prompting.py`: LLM prompt generation utilities for tool examples and demonstrations.
- `logging.py`: Logging utilities for plan generation and debugging.
- `utils.py`: Convenience module aggregating all planner utilities for easy imports.
- `prompts/system.prompt`: System prompt template for LLM-based planning.

#### `executor/`

- `registry.py`: Maps tool names to callable tool implementations.
- `runner.py`: Manages execution of a `PlanStep`, including artefact handling.
- `utils.py`: Utility functions for execution and artifact management.
- `schemas.py`: Pydantic models for execution results and tool specifications.
- `tools/eda.py`: Exploratory data analysis tools.
- `tools/stats.py`: Statistical test implementations (e.g., t-test, ANOVA).
- `tools/plotting.py`: Plot generators (e.g., boxplot, histogram).

#### `summarizer/`

- `manager.py`: Main orchestration functions for creating comprehensive analysis reports.
- `narrative.py`: Constructs final summary narratives and overview sections.
- `render.py`: HTML renderer and asset embedding logic.

#### `datasets/`

- `profile.py`: Runs dataset profiling (column types, nulls, distributions).
- `storage.py`: Manages local file paths, identifiers, and metadata indexing.

#### `cli/`

- `run.py`: CLI entry to run the full agent loop on a YAML prompt file.
- `profile.py`: CLI to upload and profile a dataset.
- `plan.py`: CLI to test planner output on a text prompt.

#### `spec/`

- `tool_specs.py`: Defines tool specifications and metadata for the available analysis tools.

#### `tests/`

- `test_executor.py`: Unit tests for executor functionality.
- `test_planner.py`: Unit tests for planner functionality.
- `test_summarizer.py`: Unit tests for summarizer functionality.

#### `artifacts/`

- Generated analysis artifacts including plots (PNG files) and statistical results (JSON files).
- Files are named with hash-based identifiers for uniqueness.

#### `logs/`

- Execution logs organized by plan ID in subdirectories.
- Contains detailed audit trails of plan execution steps.

#### `data_store/`

- Uploaded datasets with UUID-based filenames.
- Metadata files (`.meta.json`) containing dataset information and profiling results.

#### **Project Configuration**

- `pyproject.toml`: Poetry-based dependency management and project configuration.
- `poetry.lock`: Locked dependency versions for reproducible builds.
- `example_data.csv`, `vehicle_prices.csv`: Sample datasets for testing and demonstration.

---

### 4. Interaction Flow

1. **User Submits** research question with dataset references.
2. **Context Assembly** builds `PromptState`.
3. **Planner** generates ordered `PlanStep`s.
4. **Executor** invokes each tool, producing artefacts.
5. **Critic** validates outputs, triggers retries if needed.
6. **Summarizer** crafts narrative report.
7. **API/CLI** returns final artifacts.

---

### 5. Non-Functional Requirements

- **Reproducibility:** Deterministic checkpoints, versioned artefacts, and model hashes.
- **Scalability:** Modular Ray-based executor, pluggable backends, autoscaling support.
- **Extensibility:** Plugin-based tool registry, configurable pipelines, clear interfaces.
- **Security:** Sandboxed execution, credential management, least-privilege artefact access.
- **Testing:** Unit tests for each module, contract tests for planning outputs, end-to-end integration tests.