# ORCA

General-purpose quantum chemistry suite with strong support for open-shell spectroscopy. Methods range from semi-empirical to DFT to multireference *ab initio*, with relativistic and solvation models.

## Licence

Free for academic research, closed-source. Each research group is expected to register with the ORCA developers. Contact NeSI support if you have eligibility questions.

## Loading

```bash
module spider ORCA
module load ORCA/<version>
```

## Example Slurm script

ORCA launches its own MPI workers; do not call it with `srun`. Always invoke it via its absolute path. The NUMA directives keep cores together and stop threads migrating (see `../parallel-computing.md#numa-domains`); `--cores-per-socket` is `21` on `genoa`, `16` on `milan`.

```sl
#!/bin/bash -e
#SBATCH --account          nesi99991
#SBATCH --job-name         orca
#SBATCH --time             01:00:00
#SBATCH --partition        genoa
#SBATCH --ntasks           16
#SBATCH --mem-per-cpu      1G
#SBATCH --cores-per-socket 21
#SBATCH --threads-per-core 1
#SBATCH --distribution     *:block:*
#SBATCH --mem-bind         local

module purge
module load ORCA/<version>

export OMP_PROC_BIND=true
export OMP_PLACES=cores

orca_exe=$(which orca)
${orca_exe} MyInput.inp
```

## Input file settings

```
%pal nprocs 16 end
%maxcore 800
```

- `nprocs` must equal `--ntasks`.
- `%maxcore` is MB per core. Set it to about 80 % of `--mem-per-cpu`, because ORCA can exceed it.

## Benchmarking

Past a certain core count extra cores add little speed but still consume allocation. The ORCA benchmarking tool runs one typical calculation across core counts and reports speed and CPU efficiency: <https://github.com/geoffreyweal/orca-benchmarking>.

## Checkpointing (`.gbw`)

Jobs longer than a day should checkpoint. ORCA writes a `.gbw` (geometry, basis, wavefunction) file named after the input, in the run directory. To restart:

1. Rename the `.gbw` so it does not share the input base name (or it will be overwritten).
2. Add to the new input:
   ```
   ! moread
   %moinp "checkpoint.gbw"
   ```
3. Resubmit.

Restarting from a `.gbw` written by an older ORCA version needs extra steps; see the ORCA manual on restarting SCF calculations.

## Upstream

- <https://www.faccts.de/orca/>
- <https://orcaforum.kofo.mpg.de/>
