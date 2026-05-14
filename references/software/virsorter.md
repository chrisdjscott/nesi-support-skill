# VirSorter

Detection of viral signal in microbial sequence data.

## Loading

```bash
module spider VirSorter
module load VirSorter/2.1-gimkl-2020a-Python-3.8.2      # example
```

## NeSI customisations

- Number of jobs must be supplied explicitly via `--jobs`.
- Defaults to `--skip-deps-install` and `--use-conda-off` (uses the module's bundled dependencies).
- Databases are not provided; run `virsorter setup` once before use.

For many runs, pass `--rm-tmpdir` so VirSorter removes its temp files (reduces file-count quota pressure).

## Local scratch

VirSorter defaults `LOCAL_SCRATCH` to `/tmp`, which is small on compute nodes. Point it at the job-local `$TMPDIR` via Snakemake rule config:

```
--config LOCAL_SCRATCH=${TMPDIR:-/tmp}
```

## Example Slurm script

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      virsorter
#SBATCH --cpus-per-task 8
#SBATCH --mem           16G
#SBATCH --time          02:00:00

module purge
module load VirSorter/<version>

virsorter run \
    --seqfile test.fasta \
    --jobs ${SLURM_CPUS_PER_TASK:-2} \
    --rm-tmpdir \
    all \
    --config LOCAL_SCRATCH=${TMPDIR:-/tmp}
```

## Upstream

- <https://github.com/jiarong/VirSorter2>
