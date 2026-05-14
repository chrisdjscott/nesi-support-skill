# ORCA

General-purpose quantum chemistry suite with strong support for open-shell spectroscopy. Methods range from semi-empirical to DFT to multireference *ab initio*, with relativistic and solvation models.

## Licence

Free for academic research, closed-source. Each research group is expected to register with the ORCA developers. Contact NeSI support if you have eligibility questions.

## Loading

```bash
module spider ORCA
module load ORCA/5.0.4-OpenMPI-4.1.5     # example
```

## Example Slurm script

ORCA launches its own MPI workers; do not call it with `srun`. Always invoke it via its absolute path.

```sl
#!/bin/bash -e
#SBATCH --account     nesi99991
#SBATCH --job-name    orca
#SBATCH --time        01:00:00
#SBATCH --ntasks      16
#SBATCH --mem-per-cpu 1G

module purge
module load ORCA/<version>

orca_exe=$(which orca)
${orca_exe} MyInput.inp
```

The input must also request the same number of processes via:

```
%pal nprocs 16 end
```

`<np>` here must equal the value of `--ntasks` from the Slurm script.

## Checkpointing (`.gbw`)

Jobs longer than a day should checkpoint. ORCA writes a `.gbw` (Geometry-Basis-Wavefunction) file next to the input. To restart:

1. Rename the `.gbw` so it does not share the input base name (or it will be overwritten).
2. Add to the new input:
   ```
   ! moread
   %moinp "checkpoint.gbw"
   ```
3. Resubmit.

## Upstream

- <https://www.faccts.de/orca/>
- <https://orcaforum.kofo.mpg.de/>
