# Parallel computing on Mahuika

Requesting CPUs in Slurm does not magically parallelise a program. Check the application's docs first to see what kind of parallelism (if any) it supports.

## Vocabulary

- **CPU**: hardware unit that runs instructions. On Mahuika a *logical* CPU is one SMT thread; a *physical* CPU is one core (which has 2 logical CPUs).
- **Task**: one independent process. CPUs assigned to a task share memory.
- **Node**: physical machine. Each node has its own RAM.
- **Shared memory** parallelism, multiple CPUs in one task (OpenMP, pthreads, Python `multiprocessing`).
- **Distributed memory** parallelism, multiple tasks across nodes (MPI).

## Choosing a model

| Approach | Slurm | When |
| --- | --- | --- |
| Shared memory (OpenMP, multithreading) | `--cpus-per-task=N` | Program scales within a single node. Lowest overhead. |
| Distributed memory (MPI) | `--ntasks=N` (+ optionally `--nodes`, `--ntasks-per-node`) | Program needs more cores or memory than one node holds. |
| Hybrid | `--ntasks=N --cpus-per-task=M` | Each MPI rank is itself multithreaded. Uncommon. |
| Job array | `--array=...` | Independent jobs (parameter sweep). Scales without efficiency loss. See `slurm-examples.md`. |
| GPU | `--gpus-per-node=...` | Application has GPU support. See `slurm-examples.md` and `references/hardware.md`. |

## Shared memory / OpenMP

Single node, multiple threads sharing memory. Slurm:

```sl
#SBATCH --cpus-per-task=8
#SBATCH --mem=4G
```

At job start Slurm sets `OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK` if you haven't, so most OpenMP programs Just Work.

### Tuning thread placement

Default thread placement can be flaky on shared nodes. Two recommended configurations:

| `--threads-per-core` | `OMP_PROC_BIND` | `OMP_PLACES` | When |
| --- | --- | --- | --- |
| 1 (default) | `true` | `cores` | Cleaner, predictable. One thread per physical core. |
| 2 (SMT) | `true` | `threads` | More throughput when threads spend time waiting on memory, not crunching FP. |

Set in your job:

```bash
export OMP_PROC_BIND=true
export OMP_PLACES=cores
```

The default `OMP_PROC_BIND=false` lets threads migrate between cores, which is often slower on HPC.

### Maximum shared-memory size

- Milan node: 128 physical cores, up to 256 logical CPUs.
- Genoa node: 168 physical cores, up to 336 logical CPUs.

Once you need more than one node's worth of cores, you must switch to MPI.

## Simultaneous multithreading (SMT)

Each physical core has 2 logical CPUs. By default Slurm uses 1 per core. Opt in with:

```sl
#SBATCH --threads-per-core=2     # or equivalently --hint=multithread
```

With SMT enabled:

- Slurm packs your job onto half as many physical cores.
- You get charged for physical cores, the second logical CPU is "free".
- `--mem-per-cpu` is per *logical* CPU, so total memory doubles vs SMT off.
- `sacct` reports both CPUs as occupied either way.
- Licence-per-core software may count double cores.

Benefit varies. Many compute-bound workloads (FP-heavy) don't gain from SMT because the second thread contends for the same FPU. Memory-bound and I/O-heavy code often does benefit. Test before committing.

### Worked memory examples

```sl
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=1G
```

Gives 1 GB.

```sl
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=1G
#SBATCH --hint=multithread
```

Gives 2 GB (per-logical-CPU × 2 logical CPUs per physical core).

## Distributed memory / MPI

Multiple ranks, possibly across nodes, communicating via the MPI library.

```sl
#!/bin/bash -e
#SBATCH --account     nesi99991
#SBATCH --job-name    mpijob
#SBATCH --time        01:00:00
#SBATCH --ntasks      32
#SBATCH --mem-per-cpu 2G            # per-CPU, total = ntasks * mem-per-cpu
#SBATCH --cpus-per-task 1

module purge
module load foss/2023a              # toolchain provides OpenMPI

srun ./my_mpi_program
```

- Use `srun` (not `mpirun`) so Slurm tracks rank placement.
- For non-MPI programs, set `--ntasks=1` *or* don't use `srun` at all. `srun` with `--cpus-per-task=1` silently bumps `--ntasks` to 2.
- Memory: prefer `--mem-per-cpu` for MPI with random placement. For evenly-split MPI (`--ntasks-per-node` or `--nodes` set), `--mem` works and is the recommended form.

### `--ntasks` vs `--nodes` vs `--ntasks-per-node`

| Goal | Pattern |
| --- | --- |
| N MPI ranks, scheduler decides placement | `--ntasks=N` |
| N ranks, evenly across M nodes | `--nodes=M --ntasks-per-node=K` (N = M·K) |
| N ranks all on one node | `--ntasks=N --nodes=1` |
| One rank per node | `--ntasks=N --ntasks-per-node=1` |

If you set `-n`/`--ntasks` *and* `--ntasks-per-node`, `--ntasks-per-node` is silently ignored.

## Hybrid (MPI + threads)

Each MPI rank also runs threads:

```sl
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=512MB
```

Gives 4 ranks × 8 threads = 32 logical CPUs total. Set `OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK` inside the script if not already set. Support varies by application, check docs.

## Dask-MPI

`dask-mpi` lets a Dask cluster span multiple Mahuika nodes. Two ranks are reserved (scheduler + client); the rest are workers. Boot pattern:

```sl
#!/bin/bash -e
#SBATCH --account     nesi99991
#SBATCH --ntasks      8           # 6 workers + 1 scheduler + 1 client
#SBATCH --cpus-per-task 4
#SBATCH --mem-per-cpu 2G

module purge
module load Python/3.11.6-foss-2023a
source ~/dask-env/bin/activate

srun dask-mpi --nthreads $SLURM_CPUS_PER_TASK --memory-limit 8GB python my_dask_script.py
```

`my_dask_script.py` connects to the running scheduler with `Client('SCHEDULER-ADDR')` or, when started with `dask-mpi`, the address is shared via a JSON file.

## NUMA domains

Each Mahuika node is split into NUMA domains (a group of cores plus the memory closest to them). Slurm treats each NUMA domain as a socket, so "socket" in Slurm options and output means NUMA domain.

| Node type | NUMA domains | Cores per domain |
| --- | --- | --- |
| Genoa (CPU and GPU) | 8 | 21 |
| Genoa single-socket (`l13` to `l16`) | 1 | 84 |
| Milan CPU | 8 | 16 |
| Milan A100 80 GB | 4 | 16 |
| Milan A100 40 GB | 8 | 6 |
| Hugemem 1.5 TB / 6 TB | 2 / 4 | 20 / 22 |

Slurm reserves 2 cores per node for the filesystem client, taken from one or two domains, so those have fewer cores for jobs. Slurm does not guarantee a job's cores sit in one domain even when they would fit. Memory-bound multithreaded or MPI jobs then fetch data across domains and run slower, with runtime varying between identical runs. Most jobs can ignore this.

To keep each task within a domain (Genoa CPU example, use `16` for Milan):

```sl
#SBATCH --partition        genoa
#SBATCH --ntasks           8
#SBATCH --cpus-per-task    1
#SBATCH --mem-per-cpu      2G
#SBATCH --cores-per-socket 21
#SBATCH --threads-per-core 1
#SBATCH --distribution     *:block:*
#SBATCH --mem-bind         local

export OMP_PROC_BIND=true
export OMP_PLACES=cores
srun MY_PROGRAM
```

For GPU jobs add `--gres-flags enforce-binding` and `--gpu-bind closest` so the CPUs are near the GPU.

To check placement, run this before the program; compare each task's core IDs with the `NUMA node` lines from `lscpu`:

```bash
srun bash -c 'echo "Task $SLURM_PROCID on $(hostname): cores $(taskset -c -p $$ | awk "{print \$NF}")"; lscpu | grep -i numa'
```

## Job arrays (embarrassingly parallel)

For tasks with no dependency between iterations (parameter sweeps, batches of independent inputs). See `references/slurm-examples.md#job-arrays`.

## Validation: am I actually parallel?

Quick sanity checks:

```bash
# OpenMP threads on each task
srun bash -c 'taskset -c -p $$'

# Inside batch script
echo "SLURM_CPUS_PER_TASK=$SLURM_CPUS_PER_TASK OMP_NUM_THREADS=$OMP_NUM_THREADS SLURM_NTASKS=$SLURM_NTASKS"
```

After a job runs, `seff <jobid>` gives an average CPU utilisation. Anything <60 % suggests the parallelism isn't paying off, either reduce the request or check the program is configured for parallel execution. See `references/debugging-efficiency.md`.

## Scaling

Don't just check CPU efficiency at a single core count. Time the same workload at 1, 2, 4, 8, 16 CPUs and plot walltime: returns often go *negative* past a sweet spot. Documented at <https://docs.nesi.org.nz/Software/Profiling_and_Debugging/Job_Scaling_Ascertaining_job_dimensions/>.
