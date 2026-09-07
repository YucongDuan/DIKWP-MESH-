# Source-visible migration / 源码展开记录

Date: 2026-09-07.

The previous GitHub root contained `DIKWP_MESH2_MVP.zip`, README and LICENSE only.
The archive's single top-level directory is now flattened into the repository
root, making all analytical modules, tests, schemas and examples browsable.

- Original file: `DIKWP_MESH2_MVP.zip`
- Original SHA-256: `540189799a54f69a8050fda94cf064a057ac2a8fc202c0ca4a91653d59255d06`
- Archive: 64 entries; 2,114,035 uncompressed bytes.
- Traversal paths, absolute paths, symlinks, encrypted entries and duplicate
  case-folded paths were checked; none were present.
- The existing public Apache-2.0 LICENSE is preserved.
- The historical checksum manifest and `RUN_PROOF.json` have moved to
  `docs/source-import/`; they apply to the original archive, not the updated tree.

Analytical modules and the original fixture remain unchanged. Additions include
CI, a pinned reproduction environment, a fresh-result comparison runner, three
regression tests, English/Chinese navigation and evidence boundaries. The original
ZIP remains an archival artifact; no Git history is rewritten.

A clean-environment run revealed that NetworkX PageRank uses SciPy, which the
original dependency declarations omitted. `scipy>=1.11` is now explicit in both
`pyproject.toml` and `requirements.txt`; the Python 3.12 reproduction environment
pins SciPy 1.17.0. This fixes installation reproducibility without changing the
analytical algorithm.

中文：源码、测试和示例已直接展开；ZIP 只保留作历史交付快照。复现回执依据本次真实执行生成，
不会把旧 RUN_PROOF 当成新测试，也不会把示例中的特征共现称为普适不变量证明。
