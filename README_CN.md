# DIKWP-MESH²：源码与复现入口

[English](README.md)

本仓库已由 ZIP-only 分发改为直接可浏览的源码树；`src/`、`tests/`、
`examples/`、`schemas/` 和复现脚本均在根目录下。原始 ZIP 仅作为历史快照保留。

推荐参考环境为 Python 3.12：

```bash
python -m venv .venv
# 激活 .venv 后执行：
python -m pip install -r requirements.lock
python scripts/reproduce.py
```

脚本执行测试、重新生成语义分析与离线看板、验证已知层级化反例，并与历史结果比较。
错误、超时或结果不一致将返回非零退出码，日志与带源码哈希的 JSON 回执保存在
`.reproduction/`。依赖装好后，分析过程不联网。离线安装方法及平台边界见
[复现指南](docs/REPRODUCIBILITY.md)。

这里的“不变量核”是针对给定观察者、输入与阈值计算的特征集合，不是普适数学证明。
项目不证明主观意识、独立于观察者的终极真理或生产环境有效性。

关联入口：[PACT](https://github.com/YucongDuan/DIKWP-PACT-v0.1.0)、
[VerityWeave](https://github.com/YucongDuan/DIKWP-VERITYWEAVE-v2.0.0)、
[完整研究组合](https://github.com/YucongDuan)。关联表示研究互补，不表示已经完成接口集成。
