# 3D Donut

A CLI 3D donut animation presentation.

```shell
uv run main.py
```

---

## Quick Start Guide

1. **Install the Required Tools**
   - Refer to the [uv documentation](https://docs.astral.sh) and [pre-commit website](https://pre-commit.com) for installation instructions.
   - Alternatively, if you prefer another tool (such as [Poetry](https://python-poetry.org/)), ensure it is installed and configured accordingly.

2. **Set Up the Virtual Environment**
   - **Using uv (recommended):**
     ```bash
     uv venv create
     source .venv/bin/activate
     ```
   - **Alternative:** If using another tool (e.g., Poetry), create and activate the virtual environment as per that tool’s instructions.

3. **Install Dependencies**
   - **Using uv (recommended):**
     ```bash
     uv sync
     ```
   - **Alternative:** Use your chosen dependency management tool to install dependencies as specified in the `pyproject.toml` file.

4. **Run the Project**
   - Execute the sample main program:
     ```bash
     uv run main.py
     ```
     or use your preferred method if not using `uv`.

5. **Perform Code Quality Checks**
   - Run static code analysis and formatting checks using `ruff`:
     ```bash
     uv run ruff
     ```
     or run `ruff` directly if you are not using `uv` commands.

---