# OpenSees

Open System for Earthquake Engineering Simulation. Finite-element framework for structural and geotechnical seismic analysis. Driven by Tcl scripts.

## Loading

```bash
module spider OpenSees
module load OpenSees/<version>
```

Three binaries ship with each module:

- `OpenSees`: serial.
- `OpenSeesSP`: parallel solver for one very large model.
- `OpenSeesMP`: parallel parametric studies.

See <http://opensees.berkeley.edu/OpenSees/parallel/TNParallelProcessing.pdf> for the parallel modes.

## Serial

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      opensees-serial
#SBATCH --time          00:30:00
#SBATCH --cpus-per-task 1
#SBATCH --mem           512M

module load OpenSees/<version>
OpenSees frame.tcl
```

Often run as a job array for parameter sweeps. See `../slurm-examples.md` for array usage.

## Parallel (OpenSeesMP / OpenSeesSP)

```sl
#!/bin/bash -e
#SBATCH --account     nesi99991
#SBATCH --job-name    opensees-mp
#SBATCH --time        01:00:00
#SBATCH --ntasks      16
#SBATCH --mem-per-cpu 1G

module load OpenSees/<version>
srun OpenSeesMP frame.tcl
```

## Passing parameters from the shell to Tcl

```bash
export MY_VARIABLE="Hello World!"
```

```tcl
puts $::env(MY_VARIABLE)
```

Use this with `$SLURM_ARRAY_TASK_ID` to drive parameter sweeps.

## Upstream

- <https://opensees.berkeley.edu/>
