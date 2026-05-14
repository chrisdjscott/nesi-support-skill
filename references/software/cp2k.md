# CP2K

Quantum chemistry and solid state physics package for atomistic simulations of molecular, periodic, material, crystal, and biological systems. Supports DFT (GPW/GAPW), DFTB, MP2, RPA, semi-empirical methods, and classical force fields. Open source under GPL.

## Loading

```bash
module spider CP2K
module load CP2K/2025.2-foss-2023a       # example
```

The MPI+OpenMP binary is `cp2k.psmp`.

## Hybrid MPI + OpenMP (typical)

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      cp2k
#SBATCH --time          01:00:00
#SBATCH --nodes         1
#SBATCH --ntasks        8
#SBATCH --cpus-per-task 8
#SBATCH --mem-per-cpu   2G

module purge
module load CP2K/<version>

export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}
srun cp2k.psmp -i example.inp -o example.out
```

`--ntasks` sets MPI ranks, `--cpus-per-task` sets OpenMP threads per rank. See `../parallel-computing.md` for MPI/OpenMP guidance.

## Hybrid functionals

Hybrid functionals (e.g. PBE0, B3LYP via `&HF` block) have a known bug that requires OpenMP threads to be 1. Use MPI-only:

```sl
#SBATCH --nodes         1
#SBATCH --ntasks        64
#SBATCH --cpus-per-task 1
```

## Performance notes

- Orthorhombic cells are more efficient than non-orthorhombic.
- For HFX (Hartree-Fock exchange) set `MAX_MEMORY` in the `&MEMORY` block large enough for in-core operation; tune `EPS_SCHWARZ` for screening.
- Use the `OT` SCF method for non-metallic systems.

## Upstream

- <https://www.cp2k.org/>
- <https://manual.cp2k.org/>
