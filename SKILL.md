---
name: nesi-hpc
description: Run computational workloads on NeSI's Mahuika HPC cluster (operated by REANNZ). Covers SSH access, Slurm job submission, the module system, filesystems (/home, /nesi/project, /nesi/nobackup), GPU usage, parallel/MPI/OpenMP, Apptainer containers, debugging job efficiency, and per-application guides for 56 supported scientific packages. Use when a user asks how to submit a job to Mahuika, run software on NeSI, request GPUs, configure Slurm directives, manage storage on the cluster, or troubleshoot HPC job failures (OOM kills, low priority, missing modules).
---

# NeSI Mahuika HPC

Mahuika is a CPU+GPU HPC cluster run by REANNZ (formerly NeSI) for New Zealand research. Workloads are submitted as Slurm batch jobs from login nodes; software is provided via Lmod environment modules.

## Quick orientation

- **Login**: `ssh mahuika` (after IAM/MFA + optional SSH key). See `references/access-and-login.md`. Users who followed old documentation may have `ssh nesi` configured.
- **Submit a job**: `sbatch myjob.sl`. Monitor with `squeue --me`, inspect with `sacct -j <id>` and `seff <id>`.
- **Load software**: `module spider <name>`, `module load <name>/<version>`.
- **Store data**: `/home` (20 GB, backed up, no jobs), `/nesi/project/<code>` (~100 GB, persistent, backed up), `/nesi/nobackup/<code>` (~10 TB, scratch, auto-cleaned after 90 days), Freezer (long-term tape).
- **Account**: every job needs `--account=<project_code>` (e.g. `nesi99991`).

## Minimum-viable batch script

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      myjob
#SBATCH --time          00:30:00
#SBATCH --mem           2G
#SBATCH --cpus-per-task 1
#SBATCH --output        log/%x.%j.out

module purge
module load <ModuleName>/<version>

<command>
```

The `-e` in the shebang makes the script exit on any failure (recommended; see `references/slurm.md`).

## Reference index

Load the matching reference file when the user's question lands in that area.

### Slurm and batch jobs

- **`references/slurm.md`**: Slurm command cheat sheet (`sbatch`, `squeue`, `sacct`, `scancel`, `sshare`, `sinfo`), all common `#SBATCH` directives, environment variables, fair share, prioritisation, hard limits, best practice. **Load for**: any question about writing a batch script, choosing directives, queue/priority issues, `sacct`/`squeue` usage.
- **`references/slurm-examples.md`**: Worked examples for job arrays (incl. multidimensional), GPU jobs, checkpointing, interactive sessions via `srun`/`salloc`, temporary directories (`$TMPDIR`, `--gres=ssd`, in-memory tmpfs). **Load for**: parameter sweeps, embarrassingly parallel work, GPU job templates, interactive shells, temp-file handling.
- **`references/hardware.md`**: Mahuika partitions (`milan`, `genoa`), node memory tiers, GPU types and counts (A100 80/40 GB, H100, L4), per-job and per-user limits. **Load for**: choosing a partition, selecting a GPU type, "why is my job pending", deciding `--mem` ratios.

### Storage

- **`references/filesystems.md`**: Quotas and policies for `/home`, `/nesi/project`, `/nesi/nobackup`, Freezer; snapshots; `storage_quota`; auto-cleaning of `nobackup` (`nn_doomed_list`); POSIX permissions and ACLs for sharing within a project; where to run jobs vs store outputs. **Load for**: quota errors, "where should I put X", missing/deleted files, shared-project access.

### Software stack

- **`references/modules.md`**: Lmod usage (`module load/avail/spider/purge/list`), version pinning, toolchain compatibility (`foss-2023a`, `intel-2020a`), installing your own software in `/nesi/project`, linking against EasyBuild libraries (`$EBROOT<NAME>`). **Load for**: missing software, toolchain conflicts, building from source, "which Python version".
- **`references/software/index.md`**: Categorised index of all 56 per-application pages. **Load this first** when a user names a specific package (e.g. GROMACS, AlphaFold, ANSYS); then load the specific `software/<package>.md`.

### Parallel and accelerated computing

- **`references/parallel-computing.md`**: Shared memory (OpenMP, `--cpus-per-task`), distributed memory (MPI, `--ntasks`, `srun`), hybrid jobs, simultaneous multithreading (SMT, `--threads-per-core=2`), thread placement (`OMP_PROC_BIND`, `OMP_PLACES`), Dask-MPI. **Load for**: multithreaded job setup, MPI launchers, OpenMP tuning, scaling questions.
- **`references/containers.md`**: Apptainer on Mahuika: cache setup (`APPTAINER_CACHEDIR` on nobackup), pulling Docker images, building with `--fakeroot` via Slurm, `apptainer exec --nv` for GPU containers, NVIDIA NGC examples. **Load for**: Docker/Singularity images, custom container builds, NGC images, GPU containers.

### Debugging and tuning

- **`references/debugging-efficiency.md`**: `seff`, `sacct --format`, `htop` over SSH on running nodes, OOM kills, `slurmstepd: oom-kill`, common crash causes, Slurm native profiling (`--profile=task`, `profile_plot`), job scaling analysis. **Load for**: failed jobs, OOM, low memory/CPU efficiency, profiling, "why does my job crash".

### Access and connectivity

- **`references/access-and-login.md`**: SSH config with `lander` jump host, IAM/MFA login flow, optional `mahuika_key` SSH key, trusted devices, VSCode Remote-SSH, MobaXterm/WSL/Git Bash on Windows, X11 forwarding. **Load for**: first-time login, SSH troubleshooting, "Account is not ready", connection drops.

## Conventions used in this skill

- Replace `nesi99991` (the example project code) with the user's actual project code.
- Replace `<username>` with the user's NeSI username.
- All paths are absolute on Mahuika unless prefixed with `~/`.
- `#SBATCH` directives can use either `=` or whitespace as separator (e.g. `--time=01:00:00` or `--time 01:00:00`), but never both.

## When unsure

The authoritative public docs are at <https://docs.nesi.org.nz/>. For account/allocation questions, billing, or anything not covered here, the user should contact `support@nesi.org.nz` or check <https://my.nesi.org.nz/>.
