# FDS

Fire Dynamics Simulator (NIST). Large-eddy simulation of low-speed flows, focused on smoke and heat transport from fires. Hybrid MPI + OpenMP.

## Loading

```bash
module spider FDS
module load FDS/<version>
```

## Slurm template

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      fds
#SBATCH --time          02:00:00
#SBATCH --ntasks        4              # one task per mesh, no more
#SBATCH --cpus-per-task 2              # avoid more than 4 threads per task
#SBATCH --output        %x.out
#SBATCH --hint          nomultithread

module purge
module load FDS/<version>

srun fds /nesi/project/nesi99991/path/to/input.fds
```

## Recommendations

- Partition meshes first, parallelise with MPI second. `--ntasks=2 --cpus-per-task=1` beats `--ntasks=1 --cpus-per-task=2`.
- One MPI task per mesh. More tasks than meshes causes an error.
- OpenMP scaling drops sharply past 4 physical cores per task.
- Do not enable SMT (`--hint=multithread`).
- Full MPI is more efficient than hybrid MPI+OpenMP at equal total core count.

## Upstream

- <https://pages.nist.gov/fds-smv/>
