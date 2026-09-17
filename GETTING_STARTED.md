# MESH² · Semantic transformations — practical guide / 使用导读

[Project README](README.md) · [Detailed project record](https://github.com/YucongDuan/YucongDuan/blob/main/projects/1301387525.md) · [Research portfolio](https://github.com/YucongDuan)

Explore all 25 ordered D/I/K/W/P transformation classes, alternative semantic routes and observer disagreements.

探索D/I/K/W/P全部25类有序转换、多条语义路径与观察者分歧。

## First result / 第一个结果

Create a Python environment, install `requirements.lock`, then run `python scripts/reproduce.py`.

创建Python环境，安装`requirements.lock`后运行`python scripts/reproduce.py`。

[Inspect the entry file / 查看入口文件](docs/REPRODUCIBILITY.md)

```bash
python -m pip install -r requirements.lock
python scripts/reproduce.py
```

Run from the project root after downloading and extracting the source. For a ZIP-distributed project, enter the inner project directory first. Commands using `PYTHONPATH=src` use POSIX shell syntax; PowerShell users can set `$env:PYTHONPATH='src'` before the Python command.

下载解压后在项目根目录运行；以ZIP分发的项目先进入包内项目目录。含`PYTHONPATH=src`的命令使用POSIX语法，PowerShell可先设置`$env:PYTHONPATH='src'`。

## Inspect what changed / 检查变化

Keep one input and its assumptions, run the documented example, then change one condition and compare the actual output. Preserve both successful and unsuccessful results. Use the README's dependency and test instructions for full verification.

保留输入及其假设，运行文档示例，再改变一个条件并比较实际输出。成功与失败结果都应保留；完整验证按README中的依赖和测试说明执行。

## Next contribution / 下一步贡献

Add an observer perspective and inspect preserved conflicts. / 加入新的观察者视角，检查保留的冲突。

A useful public report includes the exact revision, environment, command, minimal input, expected result and observed result. Keep private data out of public examples.

公开报告应包含确切版本、环境、命令、最小输入、预期结果与实际结果。公开示例应去除私人数据。

## Research and collaboration / 研究与合作

[Written collaboration guide](https://github.com/YucongDuan/YucongDuan/blob/main/COLLABORATE.md) · [Citation guide](https://github.com/YucongDuan/YucongDuan/blob/main/CITING.md)

Choose a question, a data scope, a source revision, responsible people, a license and an inspectable deliverable. The project's original implementation scope, author notices and component licenses remain in its README and source.

合作请明确问题、数据范围、源码版本、责任人、许可与可审阅的交付物。项目实现范围、作者声明和组件许可见原README与源码。

Research basis: Yucong Duan (段玉聪). Guide updated 17 September 2026.
