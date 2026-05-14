# uv

Fast Python package and project manager. Two main workflows: per-script dependencies, and project-scoped virtual environments. See `./python.md` for the centrally-managed Python module, and `./miniforge3.md` for conda.

## Loading

```bash
module spider uv
module load uv/<version>
```

## Cache location (essential)

`uv` always caches downloads. Redirect off `/home` so the 20 GB quota stays clear:

```bash
export UV_CACHE_DIR=/nesi/nobackup/nesi99991/$USER/uv_cache
```

Add to `~/.bashrc` to persist across sessions.

## Script-mode (inline dependencies)

Embed dependencies in the script's TOML header. `uv add --script` writes it for you:

```bash
uv add --script cities.py 'pandas'
```

Adds to the top of `cities.py`:

```python
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pandas>=2.3.3",
# ]
# ///
```

Then run with the env auto-managed:

```bash
uv run cities.py
```

## Project-mode

```bash
uv init                       # creates pyproject.toml, .python-version, main.py, ...
uv add numpy scipy            # adds and locks
uv run script.py              # ensures sync and runs
```

Two key files:

- `pyproject.toml` (editable): declared dependencies and project metadata.
- `uv.lock` (do not edit): exact resolved versions for reproducibility.

Activate the venv explicitly when you want a regular interactive session:

```bash
uv sync
source .venv/bin/activate
python script.py
```

## Slurm template

```sl
#!/bin/bash -e
#SBATCH --account   nesi99991
#SBATCH --job-name  uv-job
#SBATCH --time      01:00:00
#SBATCH --mem       2G

module purge
module load uv/<version>
export UV_CACHE_DIR=/nesi/nobackup/nesi99991/$USER/uv_cache

cd /nesi/project/nesi99991/my_uv_project
uv run python my_script.py
```

## Custom indexes / Git sources

Declare in `pyproject.toml`:

```toml
[tool.uv.sources]
my-package = { git = "https://github.com/my/package" }

[[tool.uv.index]]
name = "my-index"
url  = "https://link.to.my-index"
```

Or pass on the CLI:

```bash
uv add "my-package @ git+https://github.com/my/package"
```

## Importing/exporting

Share `pyproject.toml` for specs, `uv.lock` for exact reproducibility. Run `uv sync` in the directory to materialise the venv.

Migrate an existing `requirements.txt`:

```bash
uv add -r requirements.txt
```

Export to other formats:

```bash
uv export --format requirements.txt --output-file requirements.txt
uv export --format pylock.toml      --output-file pylock.toml
uv export --format cyclonedx1.5     --output-file sbom.json
```

## Upstream

- <https://docs.astral.sh/uv/>
