# Implementation Plan: Feature Search Modes

**Branch**: `002-feature-search-modes` | **Date**: 2025-12-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-feature-search-modes/spec.md`

## Summary

Add enhanced feature label search with three modes (Lexical, Vector, Hybrid) via an abstract Retriever component. First implementation uses Weaviate for vector search with text2vec embeddings, running in Docker containers.

## Technical Context

**Language/Version**: Python 3.10
**Primary Dependencies**: Gradio 5.x (existing), weaviate-client, rank_bm25
**Storage**: Weaviate (Docker container) for vector search, in-memory for BM25
**Testing**: pytest (existing)
**Target Platform**: Local development (macOS/Linux)
**Project Type**: Single project (existing structure)
**Performance Goals**: Search results within 2 seconds for 10,000+ feature labels
**Constraints**: Docker required for Weaviate; graceful fallback when unavailable
**Scale/Scope**: 10,000-100,000 feature labels per dataset

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| SOLID - Single Responsibility | PASS | Abstract Retriever separates search logic from UI |
| SOLID - Open/Closed | PASS | New retrievers extend base class without modification |
| SOLID - Dependency Inversion | PASS | Frontend depends on Retriever abstraction, not concrete implementations |
| DRY | PASS | Common search interface, shared result format |
| Fail-First | PASS | Explicit errors when Weaviate unavailable, no silent fallbacks |

## Project Structure

### Documentation (this feature)

```text
specs/002-feature-search-modes/
|-- plan.md              # This file
|-- research.md          # Phase 0 output
|-- data-model.md        # Phase 1 output
|-- quickstart.md        # Phase 1 output
|-- contracts/           # Phase 1 output (internal Python interface)
+-- tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/sae_scope/
|-- backend/
|   |-- dataset.py           # Existing
|   |-- features.py          # Existing
|   |-- interp_dataset.py    # Existing
|   +-- retriever/           # NEW - search component
|       |-- __init__.py
|       |-- base.py          # Abstract Retriever class
|       |-- lexical.py       # BM25 implementation
|       |-- vector.py        # Weaviate implementation
|       +-- hybrid.py        # Combined implementation
+-- frontend/
    +-- app.py               # Add search mode dropdown

docker-compose.yml           # NEW - Weaviate + text2vec
```

**Structure Decision**: Extends existing single-project structure. New `retriever/` subpackage in backend for search components. Docker Compose at repo root for Weaviate services.

## Complexity Tracking

No constitution violations requiring justification.
