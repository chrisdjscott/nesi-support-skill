# LAMMPS

Classical molecular dynamics for materials modelling (metals, semiconductors, polymers, biomolecules, coarse-grained systems). Open source under GPLv2. Parallelises via MPI (domain decomposition) and OpenMP (particle decomposition); CUDA support is compiled in but optional.

## Loading

```bash
module spider LAMMPS
module load LAMMPS/<version>
```

Binary is `lmp`.

## Serial (single CPU, array jobs)

```sl
#!/bin/bash -e
#SBATCH --account   nesi99991
#SBATCH --job-name  lammps-serial
#SBATCH --time      00:05:00
#SBATCH --mem       1500

module purge
module load LAMMPS/<version>

srun lmp -in lj.in -sf omp
```

## Parallel (MPI + OpenMP)

```sl
#!/bin/bash -e
#SBATCH --account         nesi99991
#SBATCH --job-name        lammps-parallel
#SBATCH --time            00:05:00
#SBATCH --ntasks-per-node 12
#SBATCH --cpus-per-task   2
#SBATCH --mem             1500

module purge
module load LAMMPS/<version>

export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}
srun lmp -in lj.in -sf omp -pk omp ${OMP_NUM_THREADS}
```

## GPU (Kokkos)

```sl
#!/bin/bash -e
#SBATCH --account         nesi99991
#SBATCH --job-name        lammps-gpu
#SBATCH --time            00:05:00
#SBATCH --ntasks-per-node 12
#SBATCH --cpus-per-task   2
#SBATCH --gpus-per-node   1
#SBATCH --mem             1500

module purge
module load LAMMPS/<version>

export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}
srun lmp -in in.lammps -k on g 1 -pk kokkos -sf kk -pk omp ${OMP_NUM_THREADS}
```

See `../slurm-examples.md#gpu-jobs` and `../hardware.md` for GPU partitions.

## Decomposition strategy

- Dense, homogeneous systems with many atoms: MPI-only or low OpenMP ratio.
- Inhomogeneous systems with empty space: mix MPI and OpenMP.
- GPU runs typically use 1 MPI rank per GPU with Kokkos acceleration.

Test before scaling up.

## Upstream

- <https://www.lammps.org/>
- <https://docs.lammps.org/Manual.html>
