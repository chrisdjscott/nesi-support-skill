# Miniforge3

Provides `conda` and `mamba` for environment and package management. Miniforge replaces Miniconda; the Anaconda `defaults` channel is blocked because of its licence terms.

## Loading

```bash
module purge && module load Miniforge3
source $(conda info --base)/etc/profile.d/conda.sh
export PYTHONNOUSERSITE=1
```

What each line does:

- `module purge` then `module load Miniforge3` keeps other modules (especially `Python`) from leaking `PYTHONPATH` into the conda env.
- `source .../conda.sh` enables `conda activate`.
- `PYTHONNOUSERSITE=1` blocks `~/.local/lib/pythonX.Y/site-packages` so user-installed packages do not contaminate the env.

Do not run `conda init`; it writes a snippet to `~/.bashrc` that freezes the conda version and bypasses the module system, and is known to break accounts.

## Channels

The `defaults` channel is blocked. If you see "Failed to create Conda environment / The channel is not accessible or is invalid", remove it:

```bash
conda config --remove channels defaults
```

For `environment.yml` files, remove `defaults` from the `channels:` list. Use `conda-forge` (and `bioconda` where relevant).

## Don't fill /home

Conda environments and the package cache can be tens of GB; `/home` is capped at 20 GB. Redirect both.

### Move the package cache to nobackup

```bash
conda config --add pkgs_dirs /nesi/nobackup/nesi99991/$USER/conda_pkgs
```

Saved to `~/.condarc`. The cache is subject to nobackup autodelete, which is fine since it is regenerable. See `../filesystems.md`.

### Put environments in /nesi/project

Use `--prefix` rather than `--name` so the location is explicit:

```bash
conda create --prefix /nesi/project/nesi99991/my_conda_env python=3.11
conda activate /nesi/project/nesi99991/my_conda_env
```

From an `environment.yml`:

```bash
conda env create -f environment.yml -p /nesi/project/nesi99991/my_conda_env
```

To shorten the prompt prefix (otherwise the full path is shown):

```bash
conda config --set env_prompt '({name})'
```

## Slurm template

```sl
#!/bin/bash -e
#SBATCH --account   nesi99991
#SBATCH --job-name  conda-job
#SBATCH --time      01:00:00
#SBATCH --mem       2G

module purge && module load Miniforge3
source $(conda info --base)/etc/profile.d/conda.sh
export PYTHONNOUSERSITE=1

conda activate /nesi/project/nesi99991/my_conda_env
python script.py
```

## Alternatives

- For just Python + standard scientific stack (numpy, scipy, mpi4py, etc.) the centrally-managed `Python` module is faster to load and properly optimised. See `./python.md`.
- For reproducible, isolated environments consider Apptainer (`../containers.md`).
- For Python-only project management with very fast resolution, see `./uv.md`.

## Upstream

- <https://conda.io/projects/conda/en/latest/>
- <https://mamba.readthedocs.io/>
- <https://github.com/conda-forge/miniforge>
