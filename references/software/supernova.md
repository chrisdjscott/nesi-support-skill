# Supernova

10x Genomics *de novo* diploid assembler for Chromium Linked-Reads. Three sub-commands:

- `supernova mkfastq`: demultiplex Chromium BCL to FASTQ.
- `supernova run`: build a graph-based diploid assembly.
- `supernova mkoutput`: emit FASTA for downstream use.

## Licence

10x Genomics Limited License. Check the developer's terms before running on Mahuika.

## Loading

```bash
module spider Supernova
module load Supernova/2.1.1
```

## Example Slurm script

Supernova is memory and time hungry; whole-genome runs commonly want a bigmem node and a multi-day walltime.

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      mySupernovajob
#SBATCH --ntasks        1
#SBATCH --cpus-per-task 16
#SBATCH --mem           460G
#SBATCH --time          168:00:00

module purge
module load Supernova/2.1.1

supernova run --id=${SLURM_JOB_NAME} \
    --localcores=${SLURM_CPUS_PER_TASK} \
    --localmem=450 \
    --fastqs=/nesi/project/nesi99991/fastq
```

- Pass `${SLURM_CPUS_PER_TASK}` via `--localcores`.
- `--localmem` (in GB) must be **less than** the total `--mem` requested.
- Tune `--maxreads` for your genome size (see <https://bioinformatics.uconn.edu/genome-size-estimation-tutorial/> and <http://qb.cshl.edu/genomescope/>).

## Resuming from checkpoint

Supernova checkpoints between pipeline stages. To resume, delete the `_lock` file inside the output directory (`<id>/_lock`) and rerun with the **same** Slurm and Supernova arguments.

## Tracking progress via the Martian UI

`supernova run` starts a web UI on the compute node. The URL appears near the top of the job's log file:

```
Serving UI at http://wbh001:37982?auth=<auth-string>
```

To view it, open an SSH tunnel from your local machine:

```bash
ssh -L 9999:wbh001:37982 -N mahuika
```

then in a browser: `http://localhost:9999/?auth=<auth-string>`.

See `../access-and-login.md` for SSH setup.

## Upstream

- <https://support.10xgenomics.com/de-novo-assembly/>
- <https://support.10xgenomics.com/de-novo-assembly/guidance/doc/achieving-success-with-de-novo-assembly>
