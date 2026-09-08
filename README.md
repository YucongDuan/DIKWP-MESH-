# DIKWP-MESH²

Created by Yucong Duan (段玉聪).

DIKWP-MESH² is an offline-first reference implementation for treating DIKWP as a co-equal semantic network rather than a hierarchy.

Chinese name: DIKWP网状语义生成、跨主体概念解缚与共知演化系统

## What is corrected

- `D→I→K→W→P` is allowed as one traversal, but it is not the ontology of DIKWP.
- D/I/K/W/P are co-equal, mixed and mutually revisable semantic resource types.
- All 25 ordered DIKWP×DIKWP transformations are first-class operators.
- The 25-cell matrix is only a primitive alphabet. Real transformations are context-indexed, composable, cyclic and capable of proposing new semantic axes.
- Purpose is distributed and revisable. It is not a privileged top controller.
- A concept is an observer/context/purpose-indexed projection, not an observer-free final object.

## Main modules

- `SemanticMesh`: multi-observer typed semantic multigraph plus n-ary hyper-relations.
- `TransformRegistry`: all 25 primitive DIKWP×DIKWP operators.
- `TransformationRouter`: alternative non-hierarchical paths between semantic resource types.
- `TransformationTensor`: source, target, observer, context, time, modality, scale and provenance indexing.
- `SemanticGluingEngine`: local-to-global alignment that preserves obstructions.
- `InvariantMiner`: invariant kernel, branches, conflicts and residuals.
- `ConceptEscapeEngine`: proposes missing semantic dimensions.
- `MetaOperatorEvolutionEngine`: proposes higher-order operators with tests and rollback conditions.
- `SemanticContractCompiler`: task-indexed semantic contracts instead of a single definition.
- `HierarchyLeakageAudit`: detects pyramids, purpose monarchy, one-observer definition and poor transformation coverage.

## Quick start

The source tree is now directly available at the repository root. The original
ZIP is retained as a historical snapshot, not as the only way to inspect or run
the project. For the pinned Python 3.12 reproduction environment:

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install -r requirements.lock
python scripts/reproduce.py
```

The runner executes the test suite, regenerates semantic analysis and the offline
dashboard, checks the negative hierarchy fixture, and compares fresh semantic
metrics, conflicts, invariant features and transformation usage against the
historical snapshot. Failures return a nonzero exit code; fresh logs, dependency
versions and source hashes are stored in `.reproduction/`. Numeric comparison
uses a stated `1e-6` tolerance. PNG existence is checked, not byte-identical image
reproduction. No network is used after dependencies are installed.

Individual commands remain available:

```bash
PYTHONPATH=src python -m dikwp_mesh2.cli analyze examples/life_semantic_bundle.json --out outputs
PYTHONPATH=src python -m dikwp_mesh2.cli route D W --top-k 5
PYTHONPATH=src python -m dikwp_mesh2.cli audit examples/hierarchical_spec.json --out outputs/bad_hierarchy_audit.json
PYTHONPATH=src pytest -q
```

Open `outputs/dashboard.html` after running the analysis.

See [English reproduction guide](docs/REPRODUCIBILITY.md),
[中文说明](README_CN.md), and [archive provenance](docs/SOURCE_IMPORT.md).

## Demonstration bundle

`examples/life_semantic_bundle.json` contains ten paraphrased observer perspectives derived from the uploaded 2026 conversation on defining life. It includes:

- 40 multi-typed semantic atoms;
- all 25 primitive transformation classes;
- two explicit higher-order transformation paths;
- n-ary relations for invariants, conflicts and concept escape;
- conflicting stances on cellular exclusivity, observer dependence and substrate neutrality.

## Output semantics

The analyzer produces an auditable semantic bundle rather than a final definition:

1. intersubjective invariant kernel;
2. perspective branches;
3. irreducible conflicts;
4. untranslatable residuals;
5. candidate new semantic axes;
6. transformation tensor and provenance;
7. task-indexed semantic contracts;
8. hierarchy leakage audit;
9. higher-order operator proposals.

## Boundaries

This is a research and design prototype. It does not prove an observer-independent metaphysical truth, certify consciousness, or replace domain experts. Its purpose is to make semantic transformations, perspective dependencies, disagreements, power concentration and concept-compression losses inspectable.

An "invariant kernel" here is an algorithmically mined feature set relative to
the supplied observers, thresholds and fixture. It is not a formally proved
universal invariant. The historical `RUN_PROOF.json` and checksum manifest are
preserved under `docs/source-import/` and are not presented as fresh test results.

## Connected research entry points

- [PACT](https://github.com/YucongDuan/DIKWP-PACT-v0.1.0) supplies purpose/permission trace benchmarks.
- [VerityWeave](https://github.com/YucongDuan/DIKWP-VERITYWEAVE-v2.0.0) supplies evidence-sensitive resilience analysis.
- [Portfolio](https://github.com/YucongDuan) and [research homepage](https://yucong-duan-research.dikwp407.chatgpt.site) provide broader navigation.

These are research-scope links, not a claim of tested API integration or endorsement.

## Current interface presentation

[Open the interface source](outputs/dashboard.html) from the current repository download. See [interface and authorship notes](INTERFACE_NOTES.md) for English coverage, report generation and validation scope.
