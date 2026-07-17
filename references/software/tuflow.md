# TUFLOW

Hydrodynamic flood and hydraulics modelling. Licence-restricted (needs a CodeMeter licence). The `TUFLOW` module provides two solvers:

- TUFLOW Classic (`tuflow-idp`, `tuflow-isp`): 1D/2D structured-grid solver, driven by a `.tcf` control file. `tuflow-idp` is double precision, `tuflow-isp` single precision.
- TUFLOW FV (`tuflowfv`): flexible-mesh (finite-volume) 2D/3D solver, driven by a `.fvc` control file.

## Loading

```bash
module spider TUFLOW
module load TUFLOW/<version>
```

## Licence daemon

TUFLOW needs a background CodeMeter licence daemon started before the solver. For a network cloud licence, register it first:

```bash
CodeMeterLin -v &
sleep 10 && cmu --import --file ~/my_licence_key.wbc
```

Include these lines after `module load` in every job below.

## TUFLOW Classic

Set the solver mode in the `.tcf` file: `Solution Scheme == HPC` and `Hardware == CPU` (or `GPU`).

### Shared memory (CPU)

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      TUFLOW
#SBATCH --time          01:00:00
#SBATCH --cpus-per-task 8
#SBATCH --mem           4G

module purge
module load TUFLOW/<version>

CodeMeterLin -v &
sleep 10 && cmu --import --file ~/my_licence_key.wbc

tuflow-idp -nt $SLURM_CPUS_PER_TASK -b -nmb my_model.tcf
```

### GPU

Set `Hardware == GPU` in the `.tcf`.

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      TUFLOW
#SBATCH --time          01:00:00
#SBATCH --mem           4G
#SBATCH --gpus-per-node A100:1

module purge
module load CUDA
module load TUFLOW/<version>

CodeMeterLin -v &
sleep 10 && cmu --import --file ~/my_licence_key.wbc

tuflow-idp -b -nmb my_model.tcf
```

## TUFLOW FV

Set the solver mode in the `.fvc` file.

### Shared memory (CPU)

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      TUFLOW-FV
#SBATCH --time          01:00:00
#SBATCH --mem           4G

module purge
module load TUFLOW/<version>

CodeMeterLin -v &
sleep 10 && cmu --import --file ~/my_licence_key.wbc

tuflowfv my_model.fvc
```

### Distributed memory (MPI, multi-node)

```sl
#!/bin/bash -e
#SBATCH --account     nesi99991
#SBATCH --job-name    TUFLOW-FV
#SBATCH --time        01:00:00
#SBATCH --ntasks      8
#SBATCH --mem-per-cpu 2G

module purge
module load TUFLOW/<version>

CodeMeterLin -v &
sleep 10 && cmu --import --file ~/my_licence_key.wbc

srun tuflowfv my_model.fvc
```

For GPU, set `Hardware == GPU` in the `.fvc`, add `--gpus-per-node A100:1`, and `module load CUDA` as in the Classic GPU example.

## Upstream

- <https://docs.tuflow.com/>
