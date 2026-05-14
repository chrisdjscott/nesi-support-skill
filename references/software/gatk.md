# GATK

Broad Institute's Genome Analysis Toolkit. Industry standard for SNP/indel discovery and genotyping in germline DNA and RNA-Seq. Includes the Picard toolkit (from GATK 4.0+).

## Loading

```bash
module spider GATK
module load GATK/4.3.0.0-gimkl-2022a       # example
```

GATK bundles the correct Java; do not load a Java module.

## Example Slurm script

```sl
#!/bin/bash -e
#SBATCH --account   nesi99991
#SBATCH --job-name  MarkDuplicates
#SBATCH --output    %x_%j.out
#SBATCH --error     %x_%j.err
#SBATCH --time      02:00:00
#SBATCH --mem       30G

module purge
module load GATK/<version>

# Redirect Java's temp files off the small node /tmp filesystem
TMPDIR=/nesi/nobackup/nesi99991/GATK_tmp
mkdir -p "${TMPDIR}"
export _JAVA_OPTIONS=-Djava.io.tmpdir=${TMPDIR}

gatk MarkDuplicates I=input.bam O=marked_duplicates.bam M=marked_dup_metrics.txt
```

## Picard

From GATK 4.0 onwards, Picard tools are invoked via `gatk` directly. Replace `java -jar picard.jar <Tool>` from upstream Picard docs with:

```bash
gatk <PicardTool> <options>
```

Flag names sometimes differ between Picard and GATK; check both.

## Common issues

### `IOException: No space left on device`

Java's default `/tmp` on compute nodes is very small. Set a project-space tempdir as in the template above (do it **after** `module load GATK` but **before** running `gatk`).

### "File is not a supported reference file type"

GATK requires reference files to end in `.fasta` or `.fa`. Rename accordingly.

## Upstream

- <https://gatk.broadinstitute.org/>
