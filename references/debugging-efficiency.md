# Debugging and job efficiency

## Post-mortem: did my job use what I asked for?

### `seff <jobid>`

Quick efficiency check after a job finishes.

```bash
seff 1234567
```

```text
Job ID: 1234567
State: COMPLETED (exit code 0)
Cores: 1
Tasks: 1
Nodes: 1
Job Wall-time: 7.67% 00:01:09 of 00:15:00 time limit
CPU Efficiency: 98.55% 00:01:08 of 00:01:09 core-walltime
Mem Efficiency: 10.84% 111.00 MB of 1.00 GB
```

Reading this:

- **Wall-time %**: how much of `--time` you used. Aim for 60-90 %.
- **CPU efficiency**: average utilisation across cores. Low means you over-requested CPUs *or* the program isn't parallel for that workload.
- **Mem efficiency**: peak RSS vs `--mem`. Aim for 60-80 %. Below 30 % means you're wasting headroom; above 95 % is risky.

### `sacct` columns

```bash
sacct --format="JobID,JobName,Elapsed,AveCPU,MinCPU,TotalCPU,AllocCPUS,NTasks,MaxRSS,State" -j 1234567
```

Persist this as your default:

```bash
echo 'export SACCT_FORMAT="JobID,JobName,Elapsed,AveCPU,MinCPU,TotalCPU,Alloc%2,NTask%2,MaxRSS,State"' >> ~/.bash_profile
```

Key columns:

- **Elapsed**: walltime. Tune `--time` to ~elapsed + 20%.
- **TotalCPU**: sum of CPU time across all allocated CPUs. Ideal = Elapsed × AllocCPUS.
- **MaxRSS**: peak resident memory. Tune `--mem` to MaxRSS + 1-2 GB headroom.
- **State**: `COMPLETED`, `FAILED`, `OUT_OF_MEMORY`, `TIMEOUT`, `CANCELLED`, `PREEMPTED`, `NODE_FAIL`.

Caveats:

- Slurm samples every 30 s. Short memory spikes can OOM-kill without showing in MaxRSS.
- MaxRSS excludes tmpfs files in `/tmp` or `$TMPDIR` (in-RAM). If your job writes large temp files there, account for them in `--mem`.

## Live: watching a running job

`squeue --me` shows running jobs and their nodes. Drill in with htop on the compute node:

```bash
# Get node name
squeue -h -o '%N' -j 1234567

# SSH to it and run htop scoped to your processes
ssh -t wbn175 htop -u $USER
```

(If first connect: type `yes` to accept the host key, `y` alone doesn't work.)

In htop:

- **RES**: current memory (same notion as `MaxRSS`).
- **S**: state. `R` running, `S`/`D` sleeping (D usually blocked on I/O).
- **CPU%**: percentage of one core. Sum across threads to estimate utilisation.

If the job ends while you're connected, htop drops; type `reset` to clear the garbled terminal.

## OOM (Out-Of-Memory) kills

```text
slurmstepd: error: Detected 1 oom-kill event(s) in step 370626.batch cgroup
```

Means your job tried to use more RAM than `--mem` allowed. cgroups enforce instantly, but `sacct` MaxRSS only samples every 30 s, a transient spike can OOM without `MaxRSS` reflecting it. Tmpfs files in `$TMPDIR` count against your memory too.

Two fixes:

1. **Easy**: bump `--mem` (and `--mem-per-cpu` if applicable).
2. **Better**: profile and reduce peak memory (chunk inputs, stream rather than load, use `--gres=ssd` for temp files instead of in-RAM `$TMPDIR`).

## Slurm native profiling

Inject sampling into your job:

```sl
#SBATCH --profile     task
#SBATCH --acctg-freq  30        # sample every 30 s
```

After completion:

```bash
profile_plot 1234567
```

Produces PNG plots of CPU, memory, I/O over time. Useful for spotting which phase of the job needs more (or less) of a resource.

## "Why is my job pending forever?"

Run `sprio -u $USER` to see priority breakdown, and `squeue --me -t PD -o "%i %j %r %S"` to see start-time estimates and reason codes:

| Reason | Meaning |
| --- | --- |
| `Priority` | Lower priority than other pending work, wait or boost fair share. |
| `Resources` | Resources not yet available. |
| `AssocGrpCpuLimit` / `*MemLimit` | You hit a per-user limit. Wait or cancel another running job. |
| `QOSMaxJobsPerUserLimit` | `--qos=debug` allows only 1 job at a time. |
| `BeginTime` | You set `--begin`. |
| `Dependency` | Waiting on `--dependency=`. |
| `PartitionDown` | Partition is offline. Check `sinfo`. |
| `JobHeldUser` / `JobHeldAdmin` | Held. Release with `scontrol release <id>`. |

If `Reason` is `(launch failed requeued held)` or `(BadConstraints)`, the job will never start without intervention, `scontrol show jobid <id>` to see why.

## Common crashes

- **`oom-kill`**: see OOM section above.
- **`DUE TO TIME LIMIT`**: walltime exceeded. Increase `--time` and consider checkpointing.
- **`Segmentation fault`**: program bug or library mismatch. Check toolchains (`references/modules.md`). For your own code, rebuild with `-g` and try `--cpus-per-task=1` to rule out races.
- **`Cannot allocate memory`** mid-job, over-fragmented heap or hit cgroup limit. Reduce concurrency or bump `--mem`.
- **`Killed`** with no message, often OOM. Check `dmesg`-like info via support, or just bump `--mem` and rerun.
- **`/lib64/libstdc++.so.6: version 'GLIBCXX_3.4.X' not found`**: the binary was built against a newer toolchain than the one currently loaded. Re-`module load` the same toolchain you built/ran with originally.
- **`error: Detected 1 oom-kill event(s)` immediately at start**: first allocation is too large for any node satisfying your constraints. Check `--mem` vs node memory tiers (`references/hardware.md`).
- **`No such file or directory: module ...`**: module not loaded inside the job. `module purge && module load <name>/<version>` at the top of the script.

## Job scaling

CPU efficiency alone doesn't tell you the optimum number of cores. Time the same workload at, say, 1/2/4/8/16/32 cores and plot walltime. Common shape: walltime drops sharply at first, then plateaus, then *increases* past some core count (overhead dominates). Pick the smallest count near the plateau.

See <https://docs.nesi.org.nz/Software/Profiling_and_Debugging/Job_Scaling_Ascertaining_job_dimensions/>.

## Asking for help

If you contact `support@nesi.org.nz` about a failed job, include:

- Job ID(s).
- The batch script and exact `sbatch` invocation.
- Stdout/stderr (or the relevant tail).
- `seff <id>` and `sacct -j <id> -o ...` output.
- Which login node you were on if SSH/login-related.
- Any non-default env (custom Python install, your own modulefile, etc.).

Office Hours: weekly drop-in (see <https://docs.nesi.org.nz/Getting_Started/Weekly_Online_Office_Hours/>).
