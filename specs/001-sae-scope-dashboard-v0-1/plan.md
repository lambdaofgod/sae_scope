# Implementation Plan: Feature Statistics in Features Tab

**Branch**: `001-sae-scope-dashboard-v0-1` | **Date**: 2025-12-18 | **Spec**: [spec.md](./spec.md)
**Input**: User request to add feature statistics visualization to Features tab

## Summary

Add dataset feature statistics to the Features tab:
1. Summary statistics via pandas `describe()` for frequency (normalized 0-1), std, and max columns
2. Top N features (user-configurable, default 10) ranked by each metric

Statistics are computed once on dataset load and cached. User can adjust how many top features to display via a number input.

Both the statistics and the existing search functionality will be wrapped in Gradio Accordions.

## Technical Context

**Language/Version**: Python 3.10
**Primary Dependencies**: Gradio 5.x, NumPy, Pandas
**Data Source**: `InterpEmbedDataset._latents` matrix (N documents x F features)
**Existing Code**: Features tab in `app.py` with search functionality

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| SOLID - Single Responsibility | PASS | Statistics computation in backend, UI in frontend |
| SOLID - Open/Closed | PASS | Extending Features tab, not modifying core functionality |
| DRY | PASS | Single compute method, statistics cached in dataset |
| Fail-First | PASS | Validate dataset exists before computing stats |
| Type Safety | PASS | Type hints throughout |

## UI Layout (ASCII Diagram)

```
+==============================================================================+
|                              Features Tab                                     |
+==============================================================================+
|                                                                              |
| [v] Feature Statistics  (Accordion - open by default)                        |
| +--------------------------------------------------------------------------+ |
| |                                                                          | |
| |  Summary Statistics (describe() output)                                  | |
| |  +--------------------------------------------------------------------+  | |
| |  |          | Frequency | Std Dev  | Max Value |                      |  | |
| |  |----------|-----------|----------|-----------|                      |  | |
| |  | count    | 16384     | 16384    | 16384     |                      |  | |
| |  | mean     | 0.042     | 0.15     | 2.31      |                      |  | |
| |  | std      | 0.128     | 0.23     | 1.87      |                      |  | |
| |  | min      | 0.000     | 0.00     | 0.00      |                      |  | |
| |  | 25%      | 0.002     | 0.02     | 0.41      |                      |  | |
| |  | 50%      | 0.008     | 0.08     | 1.22      |                      |  | |
| |  | 75%      | 0.031     | 0.19     | 3.05      |                      |  | |
| |  | max      | 0.452     | 2.41     | 18.7      |                      |  | |
| |  +--------------------------------------------------------------------+  | |
| |                                                                          | |
| |  Top N Features: [  10  ]                                                | |
| |                                                                          | |
| |  Top N by Frequency (normalized 0-1)                                     | |
| |  +--------------------------------------------------------------------+  | |
| |  | Index | Label                                          | Frequency |  | |
| |  |-------|------------------------------------------------|-----------|  | |
| |  | 42    | love                                           | 0.452     |  | |
| |  | 77    | joy                                            | 0.389     |  | |
| |  | 99    | anger                                          | 0.320     |  | |
| |  | ...   | ...                                            | ...       |  | |
| |  +--------------------------------------------------------------------+  | |
| |                                                                          | |
| |  Top N by Std Dev                                                        | |
| |  +--------------------------------------------------------------------+  | |
| |  | Index | Label                                          | Std Dev   |  | |
| |  |-------|------------------------------------------------|-----------|  | |
| |  | 99    | anger                                          | 2.41      |  | |
| |  | 42    | love                                           | 1.89      |  | |
| |  | 77    | joy                                            | 1.52      |  | |
| |  | ...   | ...                                            | ...       |  | |
| |  +--------------------------------------------------------------------+  | |
| |                                                                          | |
| |  Top N by Max Value                                                      | |
| |  +--------------------------------------------------------------------+  | |
| |  | Index | Label                                          | Max Value |  | |
| |  |-------|------------------------------------------------|-----------|  | |
| |  | 77    | joy                                            | 18.7      |  | |
| |  | 42    | love                                           | 15.2      |  | |
| |  | 99    | anger                                          | 12.8      |  | |
| |  | ...   | ...                                            | ...       |  | |
| |  +--------------------------------------------------------------------+  | |
| |                                                                          | |
| +--------------------------------------------------------------------------+ |
|                                                                              |
| [>] Search Features  (Accordion - closed by default)                         |
| +--------------------------------------------------------------------------+ |
| |  Search: [________________________]                                      | |
| |                                                                          | |
| |  +--------------------------------------------------------------------+  | |
| |  | Index | Label                                                      |  | |
| |  |-------|-----------------------------------------------------------|  | |
| |  | 42    | love                                                       |  | |
| |  | 77    | joy                                                        |  | |
| |  | ...   | ...                                                        |  | |
| |  +--------------------------------------------------------------------+  | |
| +--------------------------------------------------------------------------+ |
|                                                                              |
+==============================================================================+
```

## Design Overview

### Backend Changes

Add to `InterpEmbedDataset`:
- `compute_feature_statistics()` - computes and caches DataFrame with index, label, frequency (normalized), std, max for ALL features
- Frequency = count_nonzero / num_documents (normalized 0-1)
- Cache the full statistics DataFrame on dataset load
- Frontend slices top N as needed and calls describe() on columns

### Frontend Changes

Restructure Features tab with two accordions as shown in diagram above.

### Data Flow

1. On dataset load: compute all feature statistics once, cache in dataset
2. Display summary stats (describe() on frequency/std/max columns)
3. Display top N (default 10) for each metric in vertical layout
4. When user changes N: re-slice cached stats, update top N dataframes
5. Existing search remains unchanged in Search accordion

## Files to Modify

1. `src/sae_scope/backend/dataset.py` - Add abstract method signature
2. `src/sae_scope/backend/interp_dataset.py` - Implement statistics computation with caching
3. `src/sae_scope/frontend/app.py` - Add accordion UI, summary stats, number input, and wire everything

## Complexity Tracking

No constitution violations. This extends existing functionality without adding unnecessary complexity.
