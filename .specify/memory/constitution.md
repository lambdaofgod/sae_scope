<!--
SYNC IMPACT REPORT
==================
Version change: N/A (initial) -> 1.0.0
Modified principles: None (initial creation)
Added sections:
  - Core Principles (I. SOLID, II. DRY, III. Fail-First)
  - Code Quality Standards
  - Development Workflow
  - Governance
Removed sections: None
Templates requiring updates:
  - .specify/templates/plan-template.md: Constitution Check section references principles (pending manual review)
  - .specify/templates/spec-template.md: No direct principle references (no update needed)
  - .specify/templates/tasks-template.md: No direct principle references (no update needed)
  - .specify/templates/checklist-template.md: No direct principle references (no update needed)
  - .specify/templates/agent-file-template.md: No direct principle references (no update needed)
Follow-up TODOs: None
-->

# SAE Scope Constitution

## Core Principles

### I. SOLID Principles

All code MUST adhere to SOLID principles for maintainable, extensible design:

- **Single Responsibility**: Each module, class, or function MUST have exactly one reason to change. If a component handles multiple concerns, it MUST be split.
- **Open/Closed**: Code MUST be open for extension but closed for modification. New functionality MUST be added through extension, not by altering existing working code.
- **Liskov Substitution**: Subtypes MUST be substitutable for their base types without altering program correctness. Inheritance hierarchies MUST preserve behavioral contracts.
- **Interface Segregation**: Clients MUST NOT be forced to depend on interfaces they do not use. Large interfaces MUST be split into smaller, focused ones.
- **Dependency Inversion**: High-level modules MUST NOT depend on low-level modules. Both MUST depend on abstractions. Abstractions MUST NOT depend on details.

**Rationale**: SOLID principles prevent rigid, fragile, and immobile code. Violations lead to cascading changes, brittle tests, and unmaintainable systems.

### II. DRY (Don't Repeat Yourself)

Every piece of knowledge MUST have a single, unambiguous, authoritative representation:

- Duplicated logic MUST be extracted into shared functions or modules.
- Configuration values MUST be defined once and referenced everywhere.
- Magic numbers and strings MUST be replaced with named constants.
- If the same code pattern appears more than twice, it MUST be abstracted.

**Exceptions**: Trivial duplication (e.g., similar but semantically different validation) MAY remain if abstraction would obscure intent or introduce coupling. Such exceptions MUST be documented.

**Rationale**: Duplication creates maintenance burden, inconsistency risks, and bugs that must be fixed in multiple places.

### III. Fail-First (NON-NEGOTIABLE)

Code MUST fail explicitly and immediately when encountering unexpected conditions:

- **No Silent Failures**: Code MUST NOT swallow exceptions, return default values on errors, or continue execution after detecting invalid state.
- **No Hacky Fallbacks**: Code MUST NOT contain "just in case" fallbacks, defensive defaults, or "best effort" recovery logic that masks problems.
- **Explicit Error Propagation**: Errors MUST bubble up to the appropriate handler. Functions MUST NOT catch exceptions only to log and ignore them.
- **Validate Early**: Input validation MUST occur at system boundaries. Invalid data MUST be rejected immediately, not handled downstream.
- **Crash Over Corruption**: When state becomes inconsistent, the system MUST halt rather than attempt recovery that could corrupt data or produce incorrect results.

**Rationale**: Hacky fallbacks hide bugs, delay detection, and create subtle data corruption. Failing fast surfaces problems during development rather than production.

## Code Quality Standards

Code quality MUST be enforced through automated tooling and review processes:

- **Type Safety**: All code MUST use static typing where the language supports it. Dynamic typing MUST be avoided except where explicitly necessary.
- **Linting**: All code MUST pass configured linters with zero warnings. Linter rules MUST NOT be disabled without documented justification.
- **Formatting**: Code MUST be auto-formatted using project-standard tools. Formatting debates are resolved by the tool, not humans.
- **Complexity Limits**: Functions exceeding cyclomatic complexity thresholds MUST be refactored. Deep nesting (>3 levels) MUST be flattened.
- **Documentation**: Public APIs MUST have docstrings. Internal code SHOULD be self-documenting; comments explain "why", not "what".

## Development Workflow

All changes MUST follow this workflow:

- **Small, Focused Commits**: Each commit MUST represent a single logical change. Large changes MUST be broken into reviewable increments.
- **Meaningful Commit Messages**: Commit messages MUST describe what changed and why. Reference issue numbers where applicable.
- **Code Review**: All changes to shared code MUST be reviewed before merge. Reviews MUST verify principle compliance.
- **Testing**: New functionality MUST include tests. Bug fixes MUST include regression tests. Tests MUST be deterministic and isolated.

## Governance

This constitution supersedes all other development practices. Compliance is mandatory.

**Amendment Process**:
1. Proposed changes MUST be documented with rationale.
2. Changes MUST be reviewed by project stakeholders.
3. Approved changes MUST include a migration plan for existing code if applicable.
4. Version MUST be incremented per semantic versioning rules.

**Versioning Policy**:
- MAJOR: Principle removal or backward-incompatible redefinition.
- MINOR: New principle or materially expanded guidance.
- PATCH: Clarifications, wording fixes, non-semantic refinements.

**Compliance Review**:
- All PRs MUST verify adherence to core principles.
- Code reviews MUST flag violations explicitly.
- Violations MUST be resolved before merge unless formally exempted with documented justification.

**Version**: 1.0.0 | **Ratified**: 2025-12-18 | **Last Amended**: 2025-12-18
