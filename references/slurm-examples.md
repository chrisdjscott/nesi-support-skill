# Slurm worked examples

Templates for common Mahuika job patterns. Edit project code (`nesi99991`), times, and resource counts before submitting.

## Job arrays

Use for embarrassingly parallel work (parameter sweeps, independent inputs). Array max is 1000 tasks.

### Basic array

```sl
#!/bin/bash -e
#SBATCH --account   nesi99991
#SBATCH --job-name  arrayjob
#SBATCH --time      00:10:00
#SBATCH --mem       1G
#SBATCH --array     1-20

echo "Task ${SLURM_ARRAY_TASK_ID} of ${SLURM_ARRAY_TASK_COUNT}"
```

### Throttled (max N concurrent)

```sl
#SBATCH --array=1-1000%50    # 1000 tasks, no more than 50 running at once
```

### Stepped range

```sl
#SBATCH --array=0-100:5      # 0, 5, 10, ..., 100
```

### Using the task ID

```bash
# direct input
matlab -nodisplay -r "myFunction(${SLURM_ARRAY_TASK_ID})"

# index into a bash array
inputs=(small medium large xlarge)
input=${inputs[$SLURM_ARRAY_TASK_ID]}

# pick input file
infile=inputs/run_${SLURM_ARRAY_TASK_ID}.dat

# RNG seed (R)
task_id = as.numeric(Sys.getenv("SLURM_ARRAY_TASK_ID"))
set.seed(task_id)

# files from a glob (zero-based: use --array=0-N)
files=( inputs/*.dat )
infile=${files[$SLURM_ARRAY_TASK_ID]}
```

### Per-task output directories

Env vars do not expand in `#SBATCH`; use Slurm tokens (`%a`).

```sl
#SBATCH --output  outputs/run_%a/slurm.out
#SBATCH --error   outputs/run_%a/slurm.err
```

### Multidimensional sweep

```sl
#SBATCH --array  0-167          # 7 days x 24 hours

arr_time=({00..23})
arr_day=(Mon Tue Wed Thu Fri Sat Sun)

n_time=${arr_time[$((SLURM_ARRAY_TASK_ID % ${#arr_time[@]}))]}
n_day=${arr_day[$((SLURM_ARRAY_TASK_ID / ${#arr_time[@]}))]}

echo "$n_day $n_time:00"
```

### Avoiding write conflicts

Array tasks may run simultaneously and trample shared files. Isolate per-task state:

```bash
mkdir -p .tmp/run_${SLURM_ARRAY_TASK_ID}
export TMPDIR=.tmp/run_${SLURM_ARRAY_TASK_ID}
```

## GPU jobs

Request a specific GPU type explicitly. Without a type, Slurm may assign any GPU including ones unsuitable for your workload.

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      gpujob
#SBATCH --time          01:00:00
#SBATCH --partition     genoa
#SBATCH --gpus-per-node A100:1     # or H100:1, L4:1, a100:2, etc.
#SBATCH --cpus-per-task 4
#SBATCH --mem           16G

module purge
module load CUDA/12.5.0
nvidia-smi
echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES}"

<gpu workload>
```

GPU type - partition:

| Request | Partition | Notes |
| --- | --- | --- |
| `A100:1` (80 GB) | `milan` | HGX A100, 4 per node |
| `A100:1` (40 GB) | `genoa` | PCIe A100, 2 per node |
| `H100:1` | `genoa` | 96 GB, 2 per node |
| `L4:1` | `genoa` | 24 GB, no fp64, 4 per node |

`$CUDA_VISIBLE_DEVICES` is auto-set by Slurm, never hard-code GPU indices in your code.

### Choosing the right GPU

Before committing to a GPU type for production, run a short test job on each candidate and compare `seff` output (GPU utilisation, VRAM, walltime) against the compute-unit cost. Use the `debug` QoS so the test starts quickly, and profile at high frequency:

```sl
#SBATCH --time         00:15:00
#SBATCH --gpus-per-node <type>:1
#SBATCH --qos          debug
#SBATCH --profile      task      # testing only
#SBATCH --acctg-freq   1         # testing only
```

`--qos=debug` allows one short job at a time. See `references/debugging-efficiency.md` for reading the results.

Application-specific GPU pages: ABAQUS, GROMACS, Lambda_Stack, MATLAB, TensorFlow. See `references/software/<package>.md`.

## Interactive sessions

For testing, GUIs, or debugging on a compute node. Always exit when done, the job runs (and bills) for the full requested walltime.

### `srun` (drops you on the compute node)

```bash
srun --account nesi99991 \
     --job-name interactive \
     --cpus-per-task 4 --mem 8G --time 01:00:00 \
     --pty bash
```

Prompt changes to e.g. `[c004 ~ ]$` once allocated. Omit `--pty` and you'll get bash in background (not useful).

### GPU interactive

```bash
srun --account nesi99991 --partition genoa \
     --gpus-per-node L4:1 --cpus-per-task 8 --mem 4G --time 00:30:00 \
     --pty bash
```

### `salloc` (keeps you on the login node, allocates compute node for ssh)

```bash
salloc --account nesi99991 --cpus-per-task 8 --mem 16G --time 02:00:00
```

After it allocates, ssh into the listed node (e.g. `ssh c038`). Useful when you want to run a GUI on the login node and compute on the compute node.

### Tips

- Use `tmux` on the login node so you can detach if the SSH connection drops.
- `--x11` with `--pty` for X-forwarded GUIs (X server on your laptop required).
- Use `scontrol update jobid=N StartTime=tomorrowT09:30:00` to postpone a pending interactive job (e.g. you submitted at 4 pm and want it to run next morning instead of overnight). `StartTime=now` brings it forward.
- Cancel everything pending with: `squeue --me -t PD -h -o %A | xargs -r scancel`.

## Temporary directories

Each Slurm job gets its own `/tmp` set as `$TMPDIR`.

| Location | Set by | Backing | Size | Notes |
| --- | --- | --- | --- | --- |
| `$TMPDIR` (default) | Slurm auto | tmpfs (RAM) | counted against job memory | Fastest. Files removed at job end. |
| `$JOB_SCRATCH_DIR` / `$TMPDIR` | `#SBATCH --gres=ssd` | NVMe SSD | 1.5 TB | One such job per node (whole device). Memory request need not cover it. |
| Custom on `/nesi/nobackup` | `export TMPDIR=...` | WEKA scratch | per quota | Slowest, especially for many small files. Persists after job ends; clean up manually. |

```bash
# In-RAM default
mkdir -p $TMPDIR/work && cd $TMPDIR/work

# 1.5 TB SSD scratch
#SBATCH --gres=ssd
# Slurm sets $JOB_SCRATCH_DIR and $TMPDIR for you.

# Custom on nobackup (slow but huge and shared across nodes if you point all tasks at it)
export TMPDIR=/nesi/nobackup/$SLURM_JOB_ACCOUNT/tmp/$SLURM_JOB_ID
mkdir -p $TMPDIR
```

`/tmp` and `$JOB_SCRATCH_DIR` are node-local. Multi-node MPI jobs do not share them.

### Copying input data to local SSD

For repeatedly-read databases (e.g. Kraken2), copy onto local SSD once at job start:

```bash
#SBATCH --gres=ssd

module load Kraken2
cp -pr $KRAKEN2_DEFAULT_DB/* $TMPDIR
export KRAKEN2_DEFAULT_DB=$TMPDIR
```

### On login nodes

`$TMPDIR` is not set on login nodes. If a workflow needs it:

```bash
TMPDIR=${TMPDIR:=/tmp}
```

## Checkpointing

Long jobs should checkpoint periodically so a node failure doesn't waste days of work. Most scientific packages have a native checkpoint mode (e.g. GROMACS `-cpi`, LAMMPS `restart`). For generic processes, `dmtcp` can be used. See application docs in `references/software/`.

## Combining short jobs

If individual computations take <5 minutes, wrap many of them in a single Slurm script (a bash loop or a job array of batches) to amortise per-job overhead.

```bash
for i in $(seq 1 100); do
    process_one $i
done
```
