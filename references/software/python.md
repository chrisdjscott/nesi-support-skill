# Python

Mahuika provides multiple Python versions via Lmod modules. The system Python is too old, always load a module.

## Loading

```bash
module spider Python
module load Python/3.11.6-foss-2023a       # pick a versioned module
```

Mahuika modules include optimised builds of common scientific packages (numpy, scipy, matplotlib, pandas, mpi4py).

### Mahuika-specific patches

- `multiprocessing.cpu_count()` returns CPUs available to the *job*, not the whole node. Use this directly, no need to read `$SLURM_CPUS_PER_TASK` first.
- `PYTHONUSERBASE` includes the toolchain string in its path, so user-installed packages from different builds don't collide. Don't override it.

## Virtual environments

Strongly recommended over `pip install --user`. Put venvs in `/nesi/project` so they're shareable and not subject to the 20 GB `/home` quota.

```bash
module load Python/3.11.6-foss-2023a
python3 -m venv /nesi/project/nesi99991/my_venv
source /nesi/project/nesi99991/my_venv/bin/activate
pip install -r requirements.txt
```

In a Slurm script:

```sl
#!/bin/bash -e
#SBATCH --account   nesi99991
#SBATCH --job-name  my_python_job
#SBATCH --time      01:00:00
#SBATCH --mem       2G

module purge
module load Python/3.11.6-foss-2023a
source /nesi/project/nesi99991/my_venv/bin/activate

python my_script.py
```

### Inheriting Mahuika's pre-built packages

By default venvs are isolated from the module's site-packages. To use Mahuika's optimised numpy/scipy/etc:

```bash
python3 -m venv --system-site-packages /nesi/project/nesi99991/my_venv
```

Combined with this, also block your `~/.local` user-site packages so they don't sneak in:

```bash
source /nesi/project/nesi99991/my_venv/bin/activate
export PYTHONNOUSERSITE=1
python my_script.py
```

### Listing installed packages

```bash
module load Python/3.11.6-foss-2023a
python -c "help('modules')"
pip list
```

## Serial Slurm template

```sl
#!/bin/bash -e
#SBATCH --account   nesi99991
#SBATCH --job-name  python-serial
#SBATCH --time      01:00:00
#SBATCH --mem       1G

module purge
module load Python/3.11.6-foss-2023a

python my_script.py
```

## Multiprocessing (shared memory)

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      python-mp
#SBATCH --time          00:30:00
#SBATCH --cpus-per-task 8
#SBATCH --mem-per-cpu   512M

module purge
module load Python/3.11.6-foss-2023a

python my_script.py
```

In the script, use `multiprocessing.cpu_count()` to size the pool, the patched module returns the right number for the Slurm allocation. Don't use the `threading` module for CPU-bound work; the GIL serialises it.

## mpi4py (distributed memory)

```sl
#!/bin/bash -e
#SBATCH --account     nesi99991
#SBATCH --job-name    python-mpi
#SBATCH --ntasks      8
#SBATCH --time        00:30:00
#SBATCH --mem-per-cpu 512M

module purge
module load Python/3.11.6-foss-2023a       # includes mpi4py

srun python my_mpi_script.py
```

```python
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# do work split by rank, e.g.
data = list(range(rank, 100, size))
result = sum(data)
gathered = comm.gather(result, root=0)

if rank == 0:
    print(f"total = {sum(gathered)}")
```

## Job arrays with Python

```sl
#!/bin/bash -e
#SBATCH --account   nesi99991
#SBATCH --job-name  python-array
#SBATCH --time      00:30:00
#SBATCH --mem       1G
#SBATCH --array     1-10

module purge
module load Python/3.11.6-foss-2023a

python my_script.py --id "$SLURM_ARRAY_TASK_ID"
```

Inside the script:

```python
import os
task_id = int(os.environ["SLURM_ARRAY_TASK_ID"])
```

## conda / mamba

Use the `Miniforge3` module (see `software/miniforge3.md`). Put environments in `/nesi/project`, not `/home` (they get large).

## uv

A faster alternative for project-local environments. See `software/uv.md`.

## IPython

Most Python modules include IPython. `ipython` to start an interactive shell. Use `<TAB>` for completion, `obj?` for help, `obj??` for source.

## Common issues

- Long import times of large packages (e.g. tensorflow), try a `--gres=ssd` job and copy your venv onto local SSD first.
- "ImportError: numpy.core.multiarray failed to import" after `pip install`, toolchain mismatch. `module purge`, reload the matching Python, recreate the venv.
- Slow `pip install` on login nodes, request an interactive job for installs, or use `--gres=ssd` for compile-heavy packages.
- Process count mismatch in a Slurm array, `$SLURM_ARRAY_TASK_COUNT` for total, `$SLURM_ARRAY_TASK_ID` for current.

## Upstream

- <https://docs.python.org/>
- <https://numpy.org/>, <https://scipy.org/>, <https://mpi4py.readthedocs.io/>
