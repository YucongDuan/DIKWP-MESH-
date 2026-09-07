# DIKWP×DIKWP primitive operator matrix

The names below are operational names used by this MVP. They are design hypotheses and should be validated in domain-specific experiments.

| Source | Target | Operator | Operational meaning | Base loss | Reversibility | Generativity |
|---|---|---|---|---:|---:|---:|
| D | D | `re-observe` | Re-sample, calibrate, denoise, aggregate, or change measurement granularity. | 0.08 | 0.90 | 0.20 |
| D | I | `differentiate` | Extract distinctions, regularities, contrasts, and context-dependent relations from observations. | 0.16 | 0.78 | 0.45 |
| D | K | `abduce-model` | Generate causal or generative hypotheses directly from observations while exposing assumptions. | 0.34 | 0.42 | 0.65 |
| D | W | `salience-evaluate` | Assess immediate welfare, risk, or value relevance of observations without assuming a final theory. | 0.42 | 0.35 | 0.55 |
| D | P | `purpose-infer` | Infer candidate purposes or demands from observed behavior, with a high risk of projection. | 0.55 | 0.25 | 0.60 |
| I | D | `operationalize` | Turn a relation or distinction into measurable variables, probes, and observations. | 0.20 | 0.70 | 0.45 |
| I | I | `re-segment` | Reframe, regroup, compress, or expand relational structure under another context. | 0.12 | 0.82 | 0.55 |
| I | K | `generalize` | Build explanatory, predictive, or causal models from relational patterns. | 0.28 | 0.48 | 0.66 |
| I | W | `consequence-map` | Translate patterns into value, risk, fairness, resilience, or long-term consequence structures. | 0.35 | 0.42 | 0.58 |
| I | P | `question-form` | Transform detected differences into questions, goals, or intervention candidates. | 0.32 | 0.55 | 0.72 |
| K | D | `predict-test` | Derive observable predictions and discriminating experiments from a model. | 0.18 | 0.76 | 0.44 |
| K | I | `derive-signature` | Extract relational signatures, implications, and compressed explanations from knowledge. | 0.15 | 0.80 | 0.42 |
| K | K | `model-revise` | Integrate, split, negate, analogize, or revise models while retaining provenance. | 0.14 | 0.65 | 0.74 |
| K | W | `implication-audit` | Evaluate model consequences, trade-offs, distributional effects, and unknown risks. | 0.24 | 0.54 | 0.60 |
| K | P | `goal-design` | Formulate controllable objectives, experiments, or commitments from a knowledge model. | 0.28 | 0.52 | 0.65 |
| W | D | `value-directed-observe` | Select observations required by safety, justice, welfare, or reversibility concerns. | 0.22 | 0.68 | 0.50 |
| W | I | `value-reweight` | Change which distinctions matter under different affected parties and horizons. | 0.20 | 0.66 | 0.58 |
| W | K | `normative-model-select` | Select, constrain, or challenge explanatory models using explicit values and harms. | 0.31 | 0.45 | 0.62 |
| W | W | `value-negotiate` | Expose conflicts among values, stakeholders, time horizons, and scales without forced consensus. | 0.18 | 0.56 | 0.72 |
| W | P | `commit` | Convert evaluated trade-offs into bounded purposes, duties, prohibitions, or exit conditions. | 0.21 | 0.60 | 0.54 |
| P | D | `purpose-select-observation` | Choose what to measure, sample, or preserve in order to pursue or audit a purpose. | 0.24 | 0.65 | 0.48 |
| P | I | `purpose-frame` | Choose distinctions and relations relevant to a purpose while logging excluded alternatives. | 0.28 | 0.57 | 0.58 |
| P | K | `purpose-construct-knowledge` | Select or construct models needed for a purpose, with explicit risk of motivated reasoning. | 0.40 | 0.38 | 0.70 |
| P | W | `means-ends-audit` | Audit whether a purpose and its means remain acceptable under consequences and other purposes. | 0.22 | 0.64 | 0.60 |
| P | P | `purpose-transform` | Split, merge, negotiate, suspend, reverse, or replace purposes and representation rights. | 0.26 | 0.50 | 0.82 |