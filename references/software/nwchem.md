# NWChem

Scalable computational chemistry: biomolecules, nanostructures, solid-state, QM and classical, Gaussian basis or plane waves. Open source under the Educational Community Licence 2.0.

## Loading

```bash
module spider NWChem
module load NWChem/<version>
```

## Example Slurm script

```sl
#!/bin/bash -e
#SBATCH --account        nesi99991
#SBATCH --job-name       nwchem
#SBATCH --time           01:00:00
#SBATCH --ntasks         64
#SBATCH --cpus-per-task  1
#SBATCH --ntasks-per-node 16
#SBATCH --mem-per-cpu    4G
#SBATCH --output         nwchem.%j.out
#SBATCH --error          nwchem.%j.err

module purge
module load NWChem/<version>

srun nwchem NWChem_job.nw
```

## Shared memory (`ARMCI_DEFAULT_SHMMAX`)

NWChem allocates shared memory per node controlled by `ARMCI_DEFAULT_SHMMAX`. It must be at least the input file's `global` memory multiplied by the cores per node:

```bash
export ARMCI_DEFAULT_SHMMAX=$((1024 * ${SLURM_NTASKS_PER_NODE}))   # MB
```

Because of this, NWChem jobs must request the same number of cores on every node. Use `--ntasks-per-node` and `--cpus-per-task` to keep the layout regular.

Setting `--cpus-per-task > 1` forces shared-memory parallelisation; combined with `--ntasks > 1` you get hybrid MPI+OpenMP.

## Upstream

- <https://nwchemgit.github.io/>
