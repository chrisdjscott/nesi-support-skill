# Slurm reference

Slurm is the scheduler for Mahuika. Submit work via `sbatch <script>`, monitor with `squeue` and `sacct`, cancel with `scancel`.

## Core commands

| Command | Example | Purpose |
| --- | --- | --- |
| `sbatch` | `sbatch submit.sl` | Submit a batch script. |
| `squeue` | `squeue --me` | Your queued/running jobs. `squeue -p milan` filters by partition. |
| `sacct` | `sacct -j 1234567` | Accounting info for a job. `sacct -S 2026-01-01` since a date. `sacct -X` parent only. `sacct --state=FAILED`. |
| `scancel` | `scancel 1234567` | Cancel a job. `scancel --me` cancels everything you own. |
| `seff` | `seff 1234567` | One-line efficiency summary (CPU %, mem %, walltime %). |
| `sshare` | `sshare -U` | Fair-share scores for your projects. |
| `sinfo` | `sinfo` | Partition state. |
| `sprio` | `sprio -u $USER` | Priority breakdown for pending jobs. |
| `scontrol` | `scontrol update jobid=N StartTime=now` | Modify a pending or running job. |

## Batch script template

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991       # project code (required)
#SBATCH --job-name      myjob           # shows in squeue/sacct
#SBATCH --time          00-01:00:00     # walltime DD-HH:MM:SS
#SBATCH --mem           4G              # memory per node
#SBATCH --cpus-per-task 4               # logical CPUs per task
#SBATCH --output        log/%x.%j.out   # %x=jobname, %j=jobid

cat $0          # echo script to log for reproducibility

module purge
module load <Module>/<version>

<commands>
```

Use `#!/bin/bash -e` so the job stops on the first failure (otherwise `sacct` may report COMPLETED on a broken job).

## `#SBATCH` directives

### General

| Directive | Example | Notes |
| --- | --- | --- |
| `--account` | `--account=nesi99991` | Required. Bills CPU/GPU/memory hours to that project. |
| `--job-name` | `--job-name=myjob` | Visible in `squeue`/`sacct`. |
| `--time` | `--time=00-01:00:00` | Wall time. Shorter jobs queue faster (backfill). |
| `--mem` | `--mem=4G` | Memory per node. Prefer this over `--mem-per-cpu` unless MPI with random placement. |
| `--mem-per-cpu` | `--mem-per-cpu=2G` | Use only for MPI with random task placement. SMT doubles per-CPU memory (see `parallel-computing.md`). |
| `--partition` | `--partition=milan` | `milan` (AMD 7713, 128 cores, A100 80GB) or `genoa` (AMD 9634, 168 cores, A100 40GB/H100/L4). Often unnecessary, scheduler picks. |
| `--output` | `--output=log/%x.%j.out` | Log path. Tokens: `%j` jobid, `%x` jobname, `%a` array index. |
| `--error` | `--error=log/%x.%j.err` | Separate stderr; defaults to merging with `--output`. |
| `--mail-user` / `--mail-type` | `--mail-type=END,FAIL` | Notifications. `TIME_LIMIT_80` warns at 80 % walltime. |
| `--no-requeue` | | Don't requeue on node failure. |
| `--dependency` | `--dependency=afterok:1234567` | Run only after job N succeeds. |
| `--qos` | `--qos=debug` | +5000 priority; max 15 min, 2 nodes, 1 job per user. |

### Parallel

| Directive | Example | Notes |
| --- | --- | --- |
| `--ntasks` | `--ntasks=8` | MPI tasks. Leave at 1 unless using MPI. |
| `--nodes` | `--nodes=2` | Spread tasks across N nodes. |
| `--ntasks-per-node` | `--ntasks-per-node=4` | Pin MPI tasks per node. |
| `--cpus-per-task` | `--cpus-per-task=8` | Threads per task (OpenMP, multiprocessing). |
| `--threads-per-core` | `--threads-per-core=2` | Enable SMT (free second logical CPU per core). `--hint=multithread` is equivalent. |
| `--gpus-per-node` | `--gpus-per-node=A100:1` | GPU request. Types: `A100`, `H100`, `L4`. |
| `--gres=ssd` | | 1.5 TB NVMe scratch in `$JOB_SCRATCH_DIR`/`$TMPDIR`. One such job per node. |
| `--array` | `--array=1-100%10` | Array job, max 10 concurrent. See `slurm-examples.md`. |
| `--profile` | `--profile=task` | Generate `.h5` for `profile_plot`. Add `--acctg-freq=30`. |

Either `=` or whitespace separators. Never both: `--time=01:00:00` or `--time 01:00:00`, not `--time= 01:00:00`.

## Useful environment variables

| Variable | Use |
| --- | --- |
| `$SLURM_JOB_ID` | Unique log/temp names. |
| `$SLURM_JOB_NAME` | Job name. |
| `$SLURM_ARRAY_TASK_ID` | Array index inside the job. |
| `$SLURM_ARRAY_TASK_COUNT` | Total tasks in the array. |
| `$SLURM_CPUS_PER_TASK` | Input to multi-threaded launchers (e.g. `omp_num_threads`, `--threads=$SLURM_CPUS_PER_TASK`). |
| `$SLURM_NTASKS` | MPI rank count. |
| `$SLURM_SUBMIT_DIR` | Directory `sbatch` was called from. |
| `$SLURM_JOB_ACCOUNT` | Active project code. |
| `$TMPDIR` | Per-job temp dir (RAM-backed `/tmp`, or SSD if `--gres=ssd`). |

Use `${SLURM_ARRAY_TASK_ID}` in quotes inside command strings to avoid interpolation surprises. `#SBATCH` headers do not expand env vars; use Slurm tokens (`%j`, `%a`, `%x`) instead.

## Memory: `--mem` vs `--mem-per-cpu`

Prefer `--mem` (per node, total). Use `--mem-per-cpu` only when an MPI job has tasks placed randomly across nodes.

| Job type | Preferred | Value |
| --- | --- | --- |
| Serial | `--mem` | peak RAM + small headroom |
| Multithreaded / OpenMP | `--mem` | peak RAM |
| MPI evenly split between nodes | `--mem` | (per-task peak) × (tasks per node) |
| MPI with random placement | `--mem-per-cpu` | per-task peak ÷ CPUs per task |

If you OOM (`slurmstepd: error: Detected 1 oom-kill event(s)`), bump `--mem`. Slurm samples accounting every 30 s so `sacct` MaxRSS can miss short spikes that still trigger OOM.

## Job prioritisation

Priority is computed from:

- **Fair share** (largest factor, up to 1000): decreases when your project uses more than its expected share. Check with `sshare`; see usage with `nn_corehour_usage`.
- **QoS**: `--qos=debug` adds 5000 (short jobs only).
- **Job age**: ~1 point/hour, capped at 3 weeks.
- **Job size (TRES)**: slight boost for larger CPU/GPU/memory requests and whole-node jobs.
- **Nice**: `--nice=N` or `scontrol update nice=N` subtracts from priority.

`scontrol top <jobid>` boosts one of your jobs at the expense of your others in the same partition. `scontrol hold/release <jobid>` toggles a hold. Backfill lets small short jobs run early if they don't delay higher-priority work, so accurate `--time` is valuable.

## Hard limits

Per job:

- 10 nodes
- 21 node-days
- 21 days walltime

Per user:

- 2688 CPU cores occupied
- 3528 core-days booked
- 6 TB memory occupied, 30 TB-days booked
- 6 GPUs occupied, 14 GPU-days booked
- 1000 queued jobs maximum

Per array: max 1000 tasks.

## Best practice

- Don't over-request. Excess CPU/memory/walltime lengthens queue time and burns core hours.
- Aim for hours, not days, where possible (checkpointing, more parallelism).
- Combine very short (<5 min) jobs into a loop or array to amortise startup.
- Only use `--ntasks>1` or `srun` for genuine MPI programs.
- Only use `--cpus-per-task>1` if the program is actually multithreaded.
- Set walltime as tight as you reasonably can to benefit from backfill.

## Checking resource usage

- `seff <jobid>`, quick efficiency summary after a job completes.
- `sacct --format=JobID,JobName,Elapsed,TotalCPU,AllocCPUS,MaxRSS,State -j <jobid>`, accounting columns. Set `SACCT_FORMAT` env var to make this the default.
- `nn_corehour_usage <project_code>`, month-by-month project usage. Use `-c` for calendar months, `-n N` for N months back.

See `references/debugging-efficiency.md` for in-depth tuning.
