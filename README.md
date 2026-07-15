# DIKWP-MESH²

**DIKWP-MESH²** is an offline-first reference implementation for treating DIKWP as a co-equal semantic network rather than a hierarchy.

Chinese name: **DIKWP网状语义生成、跨主体概念解缚与共知演化系统**

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

```bash
cd DIKWP_MESH2_MVP
python -m pip install -r requirements.txt
PYTHONPATH=src python -m dikwp_mesh2.cli analyze examples/life_semantic_bundle.json --out outputs
PYTHONPATH=src python -m dikwp_mesh2.cli route D W --top-k 5
PYTHONPATH=src python -m dikwp_mesh2.cli audit examples/hierarchical_spec.json --out outputs/bad_hierarchy_audit.json
PYTHONPATH=src pytest -q
```

Open `outputs/dashboard.html` after running the analysis.

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
