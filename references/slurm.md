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
| `sshare` | `sshare -U` | Fairshare scores for your projects. |
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
| `--account` | `--account=nesi99991` | The project the work belongs to (required by the Acceptable Use Policy). Optional only if you are in one project. Ask the user rather than guess. |
| `--job-name` | `--job-name=myjob` | Visible in `squeue`/`sacct`. |
| `--time` | `--time=00-01:00:00` | Wall time. Shorter jobs queue faster (backfill). |
| `--mem` | `--mem=4G` | Memory per node. Prefer this over `--mem-per-cpu` unless MPI with random placement. |
| `--mem-per-cpu` | `--mem-per-cpu=2G` | Use only for MPI with random task placement. SMT doubles per-CPU memory (see `parallel-computing.md`). |
| `--partition` | `--partition=milan` | `milan` (AMD 7713, 128 cores, A100), `genoa` (AMD 9634, 168 cores, RTX PRO 6000/H100/L4), or `hugemem` (Intel, huge memory, must be explicit). Often unnecessary, scheduler picks. |
| `--output` | `--output=log/%x.%j.out` | Log path. Tokens: `%j` jobid, `%x` jobname, `%a` array index. |
| `--error` | `--error=log/%x.%j.err` | Separate stderr; defaults to merging with `--output`. |
| `--mail-user` / `--mail-type` | `--mail-type=END,FAIL` | Notifications. `TIME_LIMIT_80` warns at 80 % walltime. |
| `--no-requeue` | | Don't requeue on node failure. |
| `--dependency` | `--dependency=afterok:1234567` | Run only after job N succeeds. See [Job dependencies](#job-dependencies). |
| `--qos` | `--qos=debug` | One-off tests only. See [Debug QoS](#debug-qos). |

### Parallel

| Directive | Example | Notes |
| --- | --- | --- |
| `--ntasks` | `--ntasks=8` | MPI tasks. Leave at 1 unless using MPI. |
| `--nodes` | `--nodes=2` | Spread tasks across N nodes. |
| `--ntasks-per-node` | `--ntasks-per-node=4` | Pin MPI tasks per node. |
| `--cpus-per-task` | `--cpus-per-task=8` | Threads per task (OpenMP, multiprocessing). |
| `--threads-per-core` | `--threads-per-core=2` | Enable SMT (free second logical CPU per core). `--hint=multithread` is equivalent. |
| `--gpus-per-node` | `--gpus-per-node=a100:1` | GPU request. Types (lower-case): `a100`, `pro_6000`, `h100`, `l4`. |
| `--gres=ssd` | | 1.5 TB NVMe scratch in `$JOB_SCRATCH_DIR`/`$TMPDIR`. One such job per node. |
| `--array` | `--array=1-100%10` | Array job, max 10 concurrent. See `slurm-examples.md`. |
| `--profile` | `--profile=task` | Generate `.h5` for `profile_plot`. Add `--acctg-freq=30`. |

Either `=` or whitespace separators. Never both: `--time=01:00:00` or `--time 01:00:00`, not `--time= 01:00:00`.

## Ways to run a command

| Command | Runs | Blocks |
| --- | --- | --- |
| `bash script.sh` | Immediately on the login node. Small tasks only. | Yes |
| `sbatch script.sl` | As a batch job when resources free up. | No |
| `sbatch --wait script.sl` | As a batch job. | Yes, until the job ends |
| `sbatch --wrap "COMMAND"` | One command as a batch job, no script file. | No |
| `srun COMMAND` inside a batch script | As a job step using the job's resources (own line in `sacct`). | Yes |
| `srun --pty bash` | Interactive shell on a compute node. | Yes |

`sbatch` with no filename reads the script from stdin, so a submitting script can use a heredoc. With `<<'EOF'` variables such as `${SLURM_JOB_ID}` expand when the job runs; with unquoted `<<EOF` they expand at submission.

```sh
sbatch <<'EOF'
#!/bin/bash -e
#SBATCH --job-name  heredoc-job
#SBATCH --account   nesi99991
#SBATCH --time      00:05:00
echo "This is job ${SLURM_JOB_ID}"
EOF
```

Do not poll `squeue` in a tight loop to wait for a job. Use `sbatch --wait`, `--dependency`, or `--mail-type`. If polling is unavoidable, leave about 60 s between `squeue --me` calls. Plain `squeue` lists every user's jobs; use `squeue --me`.

## Job dependencies

`--dependency=<condition>:<jobid>` queues a job immediately but holds it until the condition is met.

| Condition | Starts when the listed jobs have |
| --- | --- |
| `afterok` | finished successfully (exit 0). |
| `afternotok` | failed (non-zero exit, timeout, node failure). For arrays: all tasks finished and at least one failed. |
| `afterany` | finished in any state. |
| `after` | started or been cancelled. |
| `aftercorr` | Arrays only: each task starts when the same-index task of the listed array succeeds. |
| `singleton` | finished, for all your earlier jobs with the same `--job-name`. |

Combine job IDs with `:` (`afterok:111:222`), require all conditions with `,`, any one with `?`. Do not mix `,` and `?`.

If the dependency can never be met (e.g. `afterok` on a failed job), the job pends forever with reason `DependencyNeverSatisfied`, even if the failed job is rerun. Add `--kill-on-invalid-dep=yes` to have Slurm cancel it. Slurm forgets finished jobs after a short time, so submit the dependent job while the parent is queued, running, or just finished.

```sh
prepare=$(sbatch --parsable prepare.sl)
process=$(sbatch --parsable --dependency afterok:${prepare} process.sl)
sbatch --dependency afterok:${process} combine.sl
```

`--parsable` prints only the job ID. A running job can queue its successor with `sbatch --dependency afterok:${SLURM_JOB_ID} next.sl` near the top of the script.

Rerun only failed array tasks with a follow-up job:

```sh
array=$(sbatch --parsable process.sl)
sbatch --dependency afternotok:${array} --job-name resubmit --time 00:05:00 --mem 512M \
    --wrap "bash resubmit_failed.sh ${array}"
```

where `resubmit_failed.sh` collects the failed task IDs and resubmits them with more memory (command-line options override the script header):

```sh
#!/bin/bash -e
failed=$(sacct --jobs "$1" --array --allocations --noheader --parsable2 --format JobID,State |
    grep -E 'FAILED|OUT_OF_MEMORY|TIMEOUT' | cut -d '|' -f 1 | cut -d '_' -f 2 | paste -sd ,)
if [ -n "${failed}" ]; then
    sbatch --array "${failed}" --mem 4G process.sl
fi
```

## Debug QoS

`--qos=debug` adds 5000 priority, so a small job usually starts within minutes. Limits: 1 job per user (queued or running), 15 min walltime, 2 nodes, 168 cores, 512 GB, 2 GPUs. Everything else uses the `normal` QoS.

Use it only for one-off tests whose result you act on straight away: checking a new or changed script, module or input before the full run; rerunning a small part of a failed job; a one-off scaling test.

Do not use it for:

- regular or production work, or to make work start sooner;
- tests that are a routine part of a workflow (e.g. a short check before every run);
- jobs whose results nobody will look at immediately (overnight runs);
- automated submission (scripts or agents that submit the next debug job);
- idle interactive sessions, especially ones holding GPUs;
- getting more time than one debug job allows (cancel and resubmit, splitting a run into debug-sized pieces, chaining debug jobs with `--dependency`). Use the normal QoS with checkpointing or an array.

REANNZ monitors debug use (the limit went back from 2 h to 15 min in November 2026 after misuse, mostly by AI agents) and can revoke access, after which submissions fail with `Invalid qos specification`.

```sh
sbatch --qos=debug --time=00:15:00 my_job.sl
```

Remove `--qos` before using the script for real.

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

- **Fairshare** (largest factor, up to 1000): see below.
- **QoS**: `--qos=debug` adds 5000 (one-off tests only, see [Debug QoS](#debug-qos)).
- **Job age**: 1 point/hour, capped at 21 days.
- **Job size (TRES)**: slight boost for larger CPU/GPU/memory requests and whole-node jobs (shown as "site factor" in `sprio`).
- **Nice**: `--nice=N` or `scontrol update JobId=<jobid> Nice=N` lowers priority by N. Can only lower, not raise.

### Fairshare

Each project has a score between 0 and 1 (`sshare -U`, `FairShare` column), shared by all its members. It compares recent usage (`nn_corehour_usage`) with expected usage. Expected usage is the project's slice of its institution's share of the cluster, proportional to its allocation; institutions are compared first, then projects within them. Usage decays with a 14-day half-life.

- Submit at a steady rate through the allocation period. Priority cannot be banked by idling, and a burst lowers priority just when most jobs are waiting.
- After a burst, the score recovers on its own as usage decays.
- Exhausting the allocation does not stop jobs running, it only lowers the score.
- If other projects at the same institution get bigger allocations, your share shrinks.
- For an early allocation increase or a score that looks wrong, contact support.

`scontrol top <jobid>` boosts one of your jobs at the expense of your others in the same partition. `scontrol hold/release <jobid>` toggles a hold. Backfill lets small short jobs run early if they don't delay higher-priority work, so accurate `--time` is valuable.

## Hard limits

Per job:

- 10 nodes
- 21 node-days
- 21 days walltime

Per user:

- 2688 CPU cores occupied
- 3528 core-days booked
- 6 TB memory occupied, 31.5 TB-days booked
- 6 GPUs occupied, 14 GPU-days booked
- 1000 queued jobs maximum

Per array: max 1000 tasks (each task counts towards the 1000 queued jobs).

The 21-day walltime is deliberate: split longer work into checkpointed jobs chained with `--dependency`. Debug QoS limits are much smaller (see [Debug QoS](#debug-qos)).

## Recurring jobs: scron

`scron` is Slurm's cron. Edit entries with `scrontab -e` (uses `$EDITOR`, nano by default), list with `scrontab -l`. Entries use standard cron syntax with Slurm options on preceding `#SCRON` lines:

```scrontab
#SCRON --account=nesi99991
#SCRON --time=00:10:00
#SCRON --mem=1G
0 5 * * * /nesi/project/nesi99991/scripts/daily_task.sh
```

Runs on the Slurm controller's clock. Not all `sbatch` options are supported; see `man scrontab`.

Differences from cron:

- The schedule sets when the job becomes eligible; it then queues like any other job (`squeue` shows reason `BeginTime`).
- The next run is not submitted until the previous one finishes. Runs due in the meantime are skipped.
- Session environment variables are not passed. Load modules and set variables in the command or script.
- `scancel` on an scron job also cancels all future runs.

Use scron for genuinely periodic tasks, not to keep jobs permanently queued. An scron job that drives an AI agent counts as unsupervised agent use, which is not allowed without a service account (see `references/ai-agents.md`).

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
