# Snakemake

Python-based workflow engine. Alternatives on Mahuika include Nextflow and Cylc.

## Loading

```bash
module spider snakemake
module load snakemake/<version>
```

## Job grouping

Use Snakemake's [job grouping](https://snakemake.readthedocs.io/en/stable/executing/grouping.html) so each Slurm submission runs for at least 30 minutes. Submitting many short jobs is poor scheduler etiquette.

## Interactive session

Request an interactive Slurm session sized for any `localrules`:

```bash
srun --account nesi99991 --pty bash
module load snakemake/<version>
snakemake -pr --keep-going -j 4 all
```

See `../slurm-examples.md` for interactive job patterns.

## Batch job

The main batch job needs the resources required by any rules tagged `localrules`. Worker rules can be dispatched as separate Slurm jobs using the Snakemake Slurm executor plugin.

```sl
#!/bin/bash -e
#SBATCH --account   nesi99991
#SBATCH --job-name  snakemake
#SBATCH --time      01:00:00
#SBATCH --mem       2G

module purge
module load snakemake/<version>

snakemake -pr --keep-going -j ${SLURM_CPUS_PER_TASK} all
```

## Slurm executor plugin

For dispatching individual rule executions as Slurm jobs (including MPI):

<https://snakemake.github.io/snakemake-plugin-catalog/plugins/executor/slurm.html>

## Community resources

- Snakemake Wrappers (versioned rules for common steps): <https://snakemake-wrappers.readthedocs.io/>
- Snakemake Workflows (complete reusable pipelines): <https://snakemake.github.io/snakemake-workflow-catalog/>

## Upstream

- <https://snakemake.readthedocs.io/>
