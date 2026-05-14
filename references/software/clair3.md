# Clair3

Germline small-variant caller for long-read sequencing (ONT, PacBio). Combines pileup calling and full-alignment for speed and accuracy at low coverage.

## Loading

```bash
module spider Clair3
module load Clair3/0.1.12-Miniconda3      # example
```

Models ship inside the module at `${CONDA_PREFIX}/bin/models/`.

## Example Slurm script

`INPUT_DIR` and `OUTPUT_DIR` must be absolute paths.

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      clair3
#SBATCH --mem           6G
#SBATCH --cpus-per-task 4
#SBATCH --time          01:00:00
#SBATCH --output        slurmout.%j.out

module purge
module load Clair3/<version>

INPUT_DIR=/nesi/nobackup/nesi99991/input          # absolute path required
OUTPUT_DIR=/nesi/nobackup/nesi99991/output        # absolute path required
REF=/nesi/project/nesi99991/reference/genome.fa
MODEL_NAME=r941_prom_hac_g360+g422                 # match your platform/basecaller

run_clair3.sh \
    --bam_fn=${INPUT_DIR}/sample.bam \
    --ref_fn=${REF} \
    --threads=${SLURM_CPUS_PER_TASK} \
    --platform=ont \
    --model_path=${CONDA_PREFIX}/bin/models/${MODEL_NAME} \
    --output=${OUTPUT_DIR} \
    --enable_phasing
```

Choose `MODEL_NAME` to match your platform and basecaller version; list available models with `ls ${CONDA_PREFIX}/bin/models/`.

## Upstream

- <https://github.com/HKU-BAL/Clair3>
