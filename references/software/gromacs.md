# GROMACS

Classical molecular dynamics. Standard for biomolecular simulation (proteins, lipids, nucleic acids), also widely used for polymers.

## Loading

```bash
module spider GROMACS                 # see installed versions
module load GROMACS/2025.2-foss-2023a-cuda-12.5.0-hybrid     # example
```

Each module ships two binaries:

- `gmx`, shared-memory (OpenMP) build. Single-node.
- `gmx_mpi`, MPI build. Multi-node.

**Version caveat**: in `GROMACS/<2025.2-foss-2023a-cuda-12.5.0-hybrid` (older modules) the shared-memory binary is named `gmx_serial` rather than `gmx`. Check the module.

## Serial (single CPU, e.g. inside an array job)

```sl
#!/bin/bash -e
#SBATCH --account   nesi99991
#SBATCH --job-name  gromacs-serial
#SBATCH --time      00:30:00
#SBATCH --mem       2G

module purge
module load GROMACS/<version>

srun gmx mdrun -s input.tpr -o trajectory.trr -c struct.gro -e energies.edr
```

## Shared memory (OpenMP, single node)

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      gromacs-omp
#SBATCH --time          01:00:00
#SBATCH --cpus-per-task 16
#SBATCH --mem           4G

module purge
module load GROMACS/<version>

srun gmx mdrun -ntomp ${SLURM_CPUS_PER_TASK} \
    -s input.tpr -o trajectory.trr -c struct.gro -e energies.edr
```

## Multi-node (MPI + OpenMP hybrid)

Use only when you need more cores than fit on one node.

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      gromacs-mpi
#SBATCH --time          02:00:00
#SBATCH --nodes         2
#SBATCH --ntasks        4
#SBATCH --cpus-per-task 32
#SBATCH --mem-per-cpu   1G

module purge
module load GROMACS/<version>

srun gmx_mpi mdrun -ntomp ${SLURM_CPUS_PER_TASK} \
    -s input.tpr -o trajectory.trr -c struct.gro -e energies.edr
```

Hybrid parallelism (MPI + threads, `--cpus-per-task>1`) is usually more efficient than MPI-only. Always pass `-ntomp ${SLURM_CPUS_PER_TASK}`.

## GPU

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      gromacs-gpu
#SBATCH --time          02:00:00
#SBATCH --partition     genoa
#SBATCH --gpus-per-node A100:1
#SBATCH --cpus-per-task 8
#SBATCH --mem           8G

module purge
module load GROMACS/<version>

srun gmx mdrun -ntomp ${SLURM_CPUS_PER_TASK} \
    -s input.tpr -o trajectory.trr -c struct.gro -e energies.edr
```

CUDA is compiled in but optional, the same binary runs CPU-only if no GPU is requested.

## Performance knobs

- Particle-Particle vs Particle-Mesh-Ewald rank balance (`-npme`).
- Load balancing (`-dlb yes`).
- DD grid (`-dd nx ny nz`).
- Pin threads: GROMACS does this by default, leave it alone unless tuning specifically.

See <https://manual.gromacs.org/> for the full option list.

## Checkpointing (essential for long jobs)

```bash
gmx mdrun -cpt 30 ...           # write checkpoint every 30 minutes
gmx mdrun -cpi state.cpt ...    # restart from checkpoint
```

Jobs running >24 hours **must** checkpoint. Mahuika job walltime is hard-limited at 21 days; in practice splitting a run into chained dependency jobs (`--dependency=afterok:`) is more robust against node failures.

## Common issues

- "command not found: gmx", older module; use `gmx_serial` instead, or load a newer version.
- Mixed toolchain conflicts after loading other modules (CUDA, OpenMPI), `module purge` first, then load GROMACS only.
- Slow performance on multi-node MPI, try fewer MPI ranks with more OpenMP threads each, and run `gmx tune_pme` to find the optimal PME split.

## Upstream

- <https://www.gromacs.org/>
- <https://manual.gromacs.org/>
