# ABAQUS

Finite-element analysis suite (Dassault Systemes / SIMULIA). Commercial, network-licensed. Strong on non-linear mechanics and contact problems.

## Loading

```bash
module spider ABAQUS
module load ABAQUS/<version>
abaqus help          # list of commands
```

## Licensing

ABAQUS draws from a network licence server reachable from Mahuika. Required tokens follow roughly `floor(5 * N^0.422)` where `N` is the CPU count. Two licence pools exist: teaching and research. Pick one explicitly in an environment file:

```text
academic=TEACHING    # or RESEARCH
```

Enabling SMT (`--hint=multithread`) doubles your token usage; it is rarely worth it.

## Solver / parallelism matrix

|                   | Element ops | Iterative | Direct | Lanczos |
| ----------------- | ----------- | --------- | ------ | ------- |
| `mp_mode=threads` |             | yes       | yes    | yes     |
| `mp_mode=mpi`     | yes         | yes       |        |         |

## Serial (single CPU, e.g. inside an array)

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      abaqus-serial
#SBATCH --time          00:30:00
#SBATCH --cpus-per-task 1
#SBATCH --mem           2G

module purge
module load ABAQUS/<version>

abaqus job=propeller_s4rs_c3d8r verbose=2 interactive
```

## Shared memory (threads, one node)

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      abaqus-omp
#SBATCH --time          01:00:00
#SBATCH --cpus-per-task 8
#SBATCH --mem           4G

module purge
module load ABAQUS/<version>

abaqus job=propeller_s4rs_c3d8r cpus=${SLURM_CPUS_PER_TASK} \
    mp_mode=threads verbose=2 interactive
```

## Distributed memory (MPI, multi-node)

```sl
#!/bin/bash -e
#SBATCH --account     nesi99991
#SBATCH --job-name    abaqus-mpi
#SBATCH --time        02:00:00
#SBATCH --ntasks      16
#SBATCH --mem-per-cpu 1500M

module purge
module load ABAQUS/<version>

abaqus job=propeller_s4rs_c3d8r cpus=${SLURM_NTASKS} \
    mp_mode=mpi verbose=2 interactive
```

Add `--nodes=1` to keep all tasks on one node at the cost of longer queue time.

## GPU

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      abaqus-gpu
#SBATCH --time          01:00:00
#SBATCH --cpus-per-task 4
#SBATCH --mem           4G
#SBATCH --gpus-per-node 1

module purge
module load ABAQUS/<version>
module load CUDA

abaqus job=propeller_s4rs_c3d8r cpus=${SLURM_CPUS_PER_TASK} \
    gpus=${SLURM_GPUS_PER_NODE} mp_mode=threads verbose=2 interactive
```

GPU nodes cap at 16 CPUs; a GPU is only worth it if it replaces ~56 CPU-cores of work.

## User-defined functions (UDFs)

Compile Fortran or C UDFs at job start with `user=my_udf.f90`. Adjust compile commands in `abaqus_v6.env`. For MKL-based libraries load `imkl` alongside ABAQUS.

## Environment file precedence

1. `$ABAQUS_ROOT/SMA/site/abaqus_v6.env` (system, immutable)
2. `~/abaqus_v6.env` (applies to all your jobs)
3. `$PWD/abaqus_v6.env` (this job only)

Create per-job overrides with a heredoc inside the Slurm script and `rm` it at the end.

## Common issues

- "Unable to create temporary directory" when `job=/path/to/file.inp`. ABAQUS cannot create sub-directories. Use `input=/path/to/file.inp job=my_input` instead.
- Old input files: `abaqus -upgrade -job new_job_name -inp old.inp`.

## Upstream

- <https://www.3ds.com/products-services/simulia/products/abaqus/>
