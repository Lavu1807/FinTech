# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-18

### Added
- **Dynamic Planner**: Analyzes datasets and creates autonomous analytical roadmaps.
- **Business Analytics Engine**: Computes KPIs, segmentations, and statistical anomalies natively.
- **AI Insights Agent**: Interprets numerical results into strategic summaries and business risks.
- **Validation Agent**: Mathematically fact-checks LLM insights against source data to eliminate hallucinations.
- **Visualization Agent**: Generates dynamic matplotlib charts.
- **Executive PDF Engine**: Native ReportLab integration for consulting-grade deliverables.
- **Enterprise Dashboard**: Generates responsive, standalone HTML/CSS BI dashboards.
- **Artifact Packaging**: Bundles all generated files (PDF, HTML, Charts, JSON traces) into a downloadable ZIP.
- **Evaluation Framework**: Includes a bulk CI/CD benchmarking script for dataset evaluations.
- **Explainability Trace Viewer**: Detailed timeline parsing and agent-level debugging UI.
- Comprehensive REST APIs built on FastAPI.

### Changed
- **LLM Gateway Migration:** Decoupled architecture from Gemini and migrated fully to Mistral AI via dynamic `ProviderFactory`.
- **Python Modernization:** Refactored entire codebase to strict Python 3.11+ timezone-aware `datetime.now(timezone.utc)` standards, eliminating all deprecation warnings.
- Replaced fragile HTML-to-PDF generation with deterministic ReportLab flowables.
- Refactored entire global artifact system into workflow-specific isolated directories.
- Refined Dashboard generator to be purely static and dependency-free.

### Security
- Hardened Path Traversal defenses in artifact downloading.
- Standardized CORS and robust error handling globally.
