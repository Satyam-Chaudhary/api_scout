# 🔭 API Scout — Integration Atlas

**An autonomous, evidence-driven SaaS API and MCP research agent for integration discovery, evaluation, and prioritization.**

API Scout researches SaaS applications, discovers their API and Model Context Protocol (MCP) capabilities, evaluates integration feasibility, validates evidence, and ranks applications for potential integration development.

It transforms scattered developer documentation, API references, authentication guides, MCP implementations, and web search results into a structured research dataset and an interactive dashboard.

---

## Overview

Building integrations with hundreds of SaaS applications requires manually investigating:

- Does the application provide a public API?
- What authentication methods are supported?
- Can developers access the API without contacting sales?
- What functionality does the API expose?
- Does the application offer an official MCP server?
- What are the technical or access barriers to integration?
- How reliable is the available evidence?
- Which integrations should be prioritized for development?

API Scout automates much of this investigation using web search, webpage retrieval, LLM-based structured extraction, evidence tracking, deterministic evaluation, analytics, and an interactive HTML dashboard.

The final output is **Integration Atlas**, a research dashboard designed to help integration teams make more informed decisions about which SaaS applications to investigate and build next.

---

## Key Features

### 1. Automated SaaS Research

API Scout automatically investigates applications using multiple targeted search queries.

The research pipeline searches for:

- Official API documentation
- API authentication documentation
- Developer access requirements
- Official MCP documentation
- MCP server implementations and repositories

It gathers relevant search results, retrieves webpages, extracts readable content, and prepares the information for structured analysis.

### 2. Structured Information Extraction

The research agent extracts structured information about each application, including:

| Field | Description |
|---|---|
| Application | SaaS application name |
| Category | Application category |
| Description | Summary of the application |
| Public API | Whether a public API exists |
| Authentication | Supported authentication methods |
| Developer Access | Self-serve, gated, hybrid, or unknown |
| Access Requirements | Requirements to obtain API access |
| API Types | Major API capabilities |
| API Breadth | Estimated breadth of API coverage |
| Official MCP | Availability of an official MCP implementation |
| MCP URL | Relevant MCP documentation or endpoint |
| Buildability | Integration feasibility assessment |
| Primary Blocker | Main identified integration obstacle |
| Evidence | Supporting evidence for extracted claims |
| Confidence | Research quality score |
| Verification | Verification status |

The extraction process uses structured Pydantic models rather than relying exclusively on unstructured text responses.

---

### 3. API and Developer Access Evaluation

API Scout distinguishes between API availability and developer accessibility.

An application having an API does not necessarily mean that developers can immediately build integrations.

Developer access is classified into:

- **Self-serve:** Developers can generally obtain API access through a developer portal or standard onboarding process.
- **Gated:** Access requires approval, outreach, partnership, or other restrictions.
- **Hybrid:** Different API capabilities or access paths have different requirements.
- **Unknown:** Available evidence is insufficient to determine the access model.

This distinction helps identify potential integration barriers beyond simply discovering an API.

---

### 4. MCP Discovery

API Scout investigates whether applications provide official Model Context Protocol support.

The research process searches for:

- Official MCP documentation
- Hosted MCP endpoints
- Official MCP server repositories
- MCP setup and authentication instructions
- MCP implementation details

MCP availability is classified as:

- Yes
- No
- Unknown

MCP discovery is treated separately from API availability.

An application may have an API without an MCP server, and an MCP server may introduce its own authentication or access requirements.

API Scout attempts to distinguish official implementations from third-party or community implementations.

---

### 5. Evidence-Based Research

API Scout associates extracted claims with supporting sources.

Instead of allowing the LLM to generate arbitrary evidence URLs, source identifiers are mapped back to actual sources retrieved during the research process.

Evidence records contain information such as:

- Claim
- Source URL
- Source type
- Supporting excerpt
- Retrieval timestamp

This makes the research more traceable and allows users to inspect the sources behind individual findings.

Evidence validation checks whether important extracted claims have corresponding evidence records.

**Important:** Evidence association is not equivalent to independently verifying the truth of a claim. The system checks evidence coverage and provenance, not necessarily whether the source conclusively proves every claim.

---

### 6. Integration Buildability Assessment

API Scout includes a deterministic buildability engine that evaluates integration feasibility using the research findings.

The engine considers factors such as:

- API availability
- MCP availability
- Developer access restrictions
- API breadth
- Authentication and access constraints

The resulting classifications are:

| Classification | Meaning |
|---|---|
| `build` | Integration appears reasonably feasible |
| `build_with_constraints` | Integration appears feasible, but constraints exist |
| `outreach_required` | Additional access, approval, or outreach may be required |
| `blocked` | Available findings indicate significant barriers |
| `unknown` | Insufficient information to make a meaningful assessment |

The buildability engine is deterministic.

It does not rely on the LLM to directly determine the final buildability classification.

This separation helps make feasibility assessments more consistent and testable.

---

### 7. Confidence Scoring

API Scout calculates a research confidence score based on multiple research-quality indicators.

The scoring framework considers:

| Component | Maximum Contribution |
|---|---:|
| Source quantity | 20 |
| Source quality | 25 |
| Claim coverage | 30 |
| Evidence richness | 15 |
| Review penalty | Up to -10 |

The resulting score is normalized to a 0–1 range.

The confidence score represents the quality and completeness of the research process, not a statistically calibrated probability that the extracted claims are correct.

---

### 8. Research Verification

The verification pipeline evaluates whether important research fields have sufficient coverage.

Critical fields include:

- Public API availability
- Developer access
- API breadth
- Official MCP availability

The verification process also considers:

- Missing supporting sources
- Source quantity
- Evidence coverage

Research may be marked as requiring human review.

API Scout does not automatically treat an application as verified merely because an LLM successfully generated a research result.

---

### 9. Integration Prioritization

API Scout ranks applications using a heuristic prioritization model.

The current scoring framework is:

| Criterion | Maximum Score |
|---|---:|
| Buildability | 30 |
| API Availability | 25 |
| MCP Availability | 15 |
| API Breadth | 20 |
| Confidence | 10 |
| **Total** | **100** |

The prioritization engine generates a score to help compare applications based on their technical integration potential and research findings.

**The current score is a technical feasibility prioritization heuristic. It is not a measure of market demand, customer usage, revenue potential, or business impact.**

Those factors would require additional data.

---

## Architecture

```text
                         API SCOUT
                            |
                            v
                 +----------------------+
                 |   Dataset Input      |
                 |     apps.json        |
                 +----------------------+
                            |
                            v
                 +----------------------+
                 |   Batch Runner       |
                 |  Resume / Retry      |
                 +----------------------+
                            |
                            v
                 +----------------------+
                 |   Research Agent     |
                 +----------------------+
                            |
             +--------------+--------------+
             |              |              |
             v              v              v
       +-----------+  +-----------+  +-----------+
       | Web Search|  | Web Fetch |  | LLM       |
       | Tavily    |  | HTTPX     |  | Extraction|
       +-----------+  +-----------+  +-----------+
             |              |              |
             +--------------+--------------+
                            |
                            v
                 +----------------------+
                 | Source Processing    |
                 | Parsing & Ranking    |
                 +----------------------+
                            |
                            v
                 +----------------------+
                 | Structured Research  |
                 | Pydantic Models     |
                 +----------------------+
                            |
              +-------------+-------------+
              |             |             |
              v             v             v
       +------------+ +-------------+ +-------------+
       | Evidence   | | Buildability| | Verification|
       | Validation | | Engine      | | Pipeline    |
       +------------+ +-------------+ +-------------+
              |             |             |
              +-------------+-------------+
                            |
                            v
                 +----------------------+
                 | Research Dataset    |
                 | JSON Results        |
                 +----------------------+
                            |
              +-------------+-------------+
              |             |             |
              v             v             v
       +------------+ +-------------+ +-------------+
       | Confidence | | Analytics   | | Prioritizer|
       | Scoring    | | Generation  | |            |
       +------------+ +-------------+ +-------------+
              |             |             |
              +-------------+-------------+
                            |
                            v
                 +----------------------+
                 | Integration Atlas    |
                 | HTML Dashboard       |
                 +----------------------+
                            |
                            v
                 +----------------------+
                 | GitHub Pages        |
                 | Public Dashboard     |
                 +----------------------+
```

---

## Project Structure

```text
api_scout/
│
├── agents/
│   └── research_agent.py
│
├── analytics/
│   ├── confidence.py
│   ├── dashboard_data.py
│   ├── prioritization.py
│   └── quality_audit.py
│
├── data/
│   ├── apps.json
│   └── results/
│       ├── batch_results.json
│       ├── failed_apps.json
│       ├── analytics.json
│       └── priorities.json
│
├── models/
│   ├── app_research.py
│   ├── source.py
│   ├── extraction.py
│   └── claim_support.py
│
├── pipeline/
│   ├── researcher.py
│   ├── evidence_validator.py
│   ├── buildability_engine.py
│   ├── batch_runner.py
│   ├── verification.py
│   └── dataset_validator.py
│
├── report/
│   └── generate_report.py
│
├── tools/
│   ├── llm.py
│   ├── research.py
│   ├── fetcher.py
│   ├── parser.py
│   └── source_ranker.py
│
├── tests/
│
├── docs/
│   └── index.html
│
├── output/
│   └── integration_atlas.html
│
├── .env
├── .env.example
├── .gitignore
├── pytest.ini
├── pyproject.toml
├── README.md
└── run.py
```

### Directory Explanation

#### `agents/`

Contains the research agent responsible for coordinating the research process and converting gathered information into structured application research.

#### `analytics/`

Contains analytical modules for:

- Research confidence
- Dashboard analytics
- Integration prioritization
- Research quality analysis

#### `data/`

Contains the application dataset and generated research results.

#### `models/`

Contains Pydantic models used to represent application research, sources, evidence, and extraction results.

#### `pipeline/`

Contains the main processing pipeline:

- Research orchestration
- Batch processing
- Evidence validation
- Buildability evaluation
- Dataset validation
- Research verification

#### `report/`

Contains the report generator responsible for producing the interactive Integration Atlas dashboard.

#### `tools/`

Contains integrations and utilities used by the research pipeline.

- `llm.py` — LLM provider abstraction
- `research.py` — Web search
- `fetcher.py` — Webpage retrieval
- `parser.py` — HTML content extraction
- `source_ranker.py` — Source ranking and heuristics

#### `tests/`

Contains automated tests for the application's core logic.

#### `docs/`

Contains the public-facing dashboard entry point for GitHub Pages.

#### `output/`

Contains generated dashboard artifacts.

---

# Installation

## Prerequisites

You need:

- Python 3.12 or newer
- Git
- Internet connectivity
- An LLM provider API key
- A Tavily API key

Python 3.12+ is recommended.

---

## 1. Clone the Repository

```bash
git clone https://github.com/Satyam-Chaudhary/api_scout.git
```

Navigate into the project:

```bash
cd api_scout
```

---

## 2. Create a Virtual Environment

### Linux / macOS

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

### Windows

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install --upgrade pip
```

Install the project:

```bash
pip install -e .
```

---

## 4. Configure Environment Variables

Create a `.env` file using the provided example:

```bash
cp .env.example .env
```

Configure the required environment variables.

Example configuration:

```env
LLM_PROVIDER=requesty

REQUESTY_API_KEY=your_requesty_api_key
REQUESTY_MODEL=your_model_name

TAVILY_API_KEY=your_tavily_api_key
```

The exact configuration depends on the selected LLM provider.

API keys should never be committed to Git.

---

## LLM Provider Configuration

API Scout supports multiple LLM provider configurations through its provider abstraction.

### Requesty

```env
LLM_PROVIDER=requesty
REQUESTY_API_KEY=your_requesty_api_key
REQUESTY_MODEL=your_model_name
REQUESTY_BASE_URL=https://router.requesty.ai/v1
```

### OpenRouter

```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=your_model_name
```

### Ollama

For locally hosted models:

```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=your_local_model
OLLAMA_BASE_URL=http://localhost:11434
```

Provider-specific settings may vary depending on the implementation and configured model.

---

# Running API Scout Locally

## Option 1: Run the Complete Pipeline

The main entry point is:

```bash
python run.py
```

The orchestration script runs the pipeline stages sequentially.

### Stage 1: Dataset Validation

Validates the application dataset for issues such as:

- Missing application names
- Duplicate application names
- Duplicate IDs
- Missing categories

### Stage 2: Research Batch

Researches applications from the dataset.

The batch runner:

- Reads applications from `data/apps.json`
- Skips applications already marked as completed in existing results
- Researches applications individually
- Saves results incrementally
- Tracks failed applications
- Supports retries for certain failures
- Preserves progress for subsequent runs

### Stage 3: Analytics

Generates dataset-wide analytical information.

### Stage 4: Prioritization

Calculates prioritization scores for applications.

### Stage 5: Report Generation

Generates the Integration Atlas HTML report.

The pipeline stops if a stage fails.

---

## Option 2: Run Individual Pipeline Stages

You can run each component independently.

### Validate the Dataset

```bash
python -m pipeline.dataset_validator
```

### Run Research

```bash
python -m pipeline.batch_runner
```

### Run a Limited Research Batch

For testing:

```bash
python -m pipeline.batch_runner --limit 3
```

This limits the number of applications processed in a batch run.

### Generate Analytics

```bash
python -m analytics.dashboard_data
```

### Generate Prioritization

```bash
python -m analytics.prioritization
```

### Generate the Dashboard

```bash
python -m report.generate_report
```

---

# Research Dataset

The application dataset is stored in:

```text
data/apps.json
```

Applications are represented as structured records.

Example:

```json
[
  {
    "id": 1,
    "app_name": "Salesforce",
    "category": "CRM",
    "research_status": "pending"
  },
  {
    "id": 2,
    "app_name": "HubSpot",
    "category": "CRM",
    "research_status": "pending"
  }
]
```

The dataset can be extended by adding new applications.

Each application should have a unique ID, application name, and category.

---

# Batch Processing and Resume Capability

API Scout's batch runner is designed to preserve research progress.

Research results are stored in:

```text
data/results/batch_results.json
```

Failed applications are stored in:

```text
data/results/failed_apps.json
```

### Resuming Research

The batch runner loads existing results and skips applications already marked as completed.

This allows research to resume after:

- Interrupted execution
- Provider rate limits
- Network failures
- Temporary service outages

### Rate Limits

LLM providers may enforce rate limits.

When rate limits are encountered, research may be interrupted.

API Scout preserves completed results so that subsequent executions can continue without unnecessarily repeating completed research.

Provider-specific rate limits and availability may affect batch execution.

---

# Output

## Research Results

```text
data/results/batch_results.json
```

Contains structured research results for individual applications.

## Failed Applications

```text
data/results/failed_apps.json
```

Contains information about applications that could not be successfully researched.

## Analytics

```text
data/results/analytics.json
```

Contains aggregated research analytics.

## Prioritization

```text
data/results/priorities.json
```

Contains application prioritization results.

## Interactive Dashboard

```text
output/integration_atlas.html
```

The generated report is a standalone HTML dashboard.

It can be opened directly in a browser.

---

# Integration Atlas

Integration Atlas is the visualization and exploration layer of API Scout.

It provides an interactive overview of the research dataset.

### Dashboard Capabilities

- Research overview
- Integration prioritization
- Application exploration
- Search and filtering
- Application-level research details
- Evidence links
- Category analysis
- API availability
- MCP availability
- Integration feasibility

The report is designed to be self-contained, allowing it to run without a backend server.

---

## Running the Dashboard

After generating the report:

```bash
xdg-open output/integration_atlas.html
```

On macOS:

```bash
open output/integration_atlas.html
```

On Windows:

```powershell
start output/integration_atlas.html
```

Alternatively, open the HTML file manually in your browser.

---

# Testing

API Scout uses pytest for automated testing.

Run the entire test suite:

```bash
pytest
```

Run tests with verbose output:

```bash
pytest -v
```

Run a specific test module:

```bash
pytest tests/test_buildability_engine.py -v
```

Run evidence validation tests:

```bash
pytest tests/test_evidence_validator.py -v
```

Tests cover components such as:

- Evidence validation
- Buildability decisions
- Research logic
- Data validation
- Analytical components

The test suite helps ensure that deterministic components behave consistently.

---

# Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application |
| Pydantic | Structured data validation |
| HTTPX | Asynchronous HTTP requests |
| BeautifulSoup | HTML parsing |
| Tavily | Web search |
| LLM Providers | Research extraction and structured analysis |
| asyncio | Asynchronous execution |
| Pandas | Data analysis |
| Jinja2 | Report generation |
| HTML | Dashboard structure |
| CSS | Dashboard styling |
| JavaScript | Dashboard interaction |
| pytest | Automated testing |
| GitHub Pages | Dashboard hosting |

---

# Design Principles

## 1. Structured Data over Unstructured Output

Research results are represented using typed data models.

This improves consistency, validation, serialization, and downstream analytics.

## 2. Evidence Traceability

Claims are associated with retrieved sources.

Evidence records are constructed using source references rather than trusting the LLM to invent URLs.

## 3. Conservative Research

When available sources do not provide sufficient information, the system should prefer unknown rather than making unsupported assumptions.

## 4. Separation of Responsibilities

Research extraction, evidence validation, buildability assessment, confidence scoring, prioritization, and visualization are handled by separate modules.

## 5. Deterministic Decision Components

Buildability assessment and prioritization are based on defined rules and scoring systems rather than allowing the LLM to make every downstream decision.

## 6. Resumable Execution

Research results are saved incrementally to reduce data loss and unnecessary repeated work.

## 7. Human Review

Automated research can be incomplete or incorrect.

API Scout identifies research requiring additional review rather than treating every result as authoritative.

---

# Limitations

API Scout is an automated research system and should not be treated as an authoritative source of API availability or integration feasibility.

### Source Quality

Search results may contain outdated, incomplete, third-party, or inaccurate information.

### Evidence Validation

Evidence validation checks evidence association and coverage. It does not guarantee that every claim is conclusively supported by its source.

### Source Ranking

Source ranking uses heuristics. A high-ranked source is not necessarily authoritative or correct.

### API Breadth

API breadth is an assessment based on available documentation and extracted information. It is not a complete inventory of an application's API capabilities.

### MCP Discovery

Failure to discover an MCP server does not prove that one does not exist.

### Buildability

Buildability represents an estimated technical feasibility assessment. Actual integration requirements may depend on API quotas, licensing, account permissions, contractual requirements, API stability, and additional factors.

### Confidence

Confidence scoring measures research quality and coverage using heuristics. It is not a calibrated probability of correctness.

### Prioritization

The prioritization model currently focuses on technical feasibility and research indicators. It does not incorporate customer demand, revenue potential, usage statistics, or strategic business value.

### LLM Dependence

Research quality may vary depending on the selected LLM, provider availability, context limits, rate limits, and extraction accuracy.

---

# Future Improvements

Potential future improvements include:

- Multi-agent research workflows
- Better source credibility classification
- Claim-level verification
- Independent evidence verification
- API endpoint coverage analysis
- Authentication complexity scoring
- API rate-limit analysis
- SDK availability detection
- API documentation quality scoring
- MCP server quality evaluation
- Automated MCP compatibility testing
- Customer-demand-based prioritization
- Integration maintenance risk scoring
- Historical research comparison
- Research freshness monitoring
- Automated re-research of outdated applications
- Human feedback and correction workflows
- Research quality calibration
- Confidence calibration
- Integration cost estimation
- Integration coverage analysis

---

# Deployment

Integration Atlas is hosted using GitHub Pages.

The public dashboard is available at:

**https://Satyam-Chaudhary.github.io/api_scout/**

The deployment uses the repository's `docs/` directory.

The dashboard is generated as a static HTML artifact and does not require a backend server.

---

# License

Add your project's license here.

---

# Author

**Satyam Chaudhary**

GitHub: https://github.com/Satyam-Chaudhary

---

> API Scout — Turning fragmented SaaS documentation into actionable integration intelligence.