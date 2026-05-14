# BLAST

NCBI BLAST+ sequence similarity search.

## Loading

```bash
module spider BLAST
module load BLAST/<version>
```

## Databases

NeSI downloads the standard NCBI databases quarterly and exposes them as `BLASTDB/<yyyy-mm>` modules which set `$BLASTDB`:

```bash
module avail BLASTDB
module load BLASTDB/<yyyy-mm>
ls $BLASTDB
```

Only a few recent versions are kept; update the date in old job scripts as needed.

## Single-threaded (small jobs)

For jobs under 24 CPU-hours: small databases (< 10 GB), small query (< 1 GB), or fast searches like default `blastn` (megablast).

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      blast
#SBATCH --time          00:30:00     # ~10 CPU min / MB blastn query vs nt
#SBATCH --mem           30G
#SBATCH --cpus-per-task 2

module purge
module load BLAST/<version>
module load BLASTDB/<yyyy-mm>

QUERIES=$1
FORMAT="6 qseqid qstart qend qseq sseqid sgi sacc sstart send staxids sscinames stitle length evalue bitscore"
BLASTOPTS="-evalue 0.05 -max_target_seqs 10"
BLASTAPP=blastn
DB=nt

$BLASTAPP $BLASTOPTS -db $DB -query $QUERIES -outfmt "$FORMAT" \
    -out $QUERIES.$DB.$BLASTAPP -num_threads ${SLURM_CPUS_PER_TASK}
```

## Multi-threaded with local DB copy (large jobs)

Compute nodes have no local disk; `$TMPDIR` is in memory. The DB copy must be included in `--mem`. As of mid-2023: `nt` is ~283 GB, `refseq_protein` is ~157 GB.

Multi-threaded BLAST repeatedly reads the database from shared storage in batches, which becomes the bottleneck. Copying to `$TMPDIR` keeps the DB in RAM.

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      blast-large
#SBATCH --time          02:30:00
#SBATCH --mem           120G        # 30 GB + database size
#SBATCH --ntasks        1
#SBATCH --cpus-per-task 36          # half a node

module purge
module load BLAST/<version>
module load BLASTDB/<yyyy-mm>

QUERIES=$1
FORMAT="6 qseqid qstart qend qseq sseqid sgi sacc sstart send staxids sscinames stitle length evalue bitscore"
BLASTOPTS="-task blastn"
BLASTAPP=blastn
DB=nt

cp $BLASTDB/{$DB,taxdb}.* $TMPDIR/
export BLASTDB=$TMPDIR

$BLASTAPP $BLASTOPTS -db $DB -query $QUERIES -outfmt "$FORMAT" \
    -out $QUERIES.$DB.$BLASTAPP -num_threads ${SLURM_CPUS_PER_TASK}
```

If unsure, try single-threaded first.

## Upstream

- <https://blast.ncbi.nlm.nih.gov/Blast.cgi>
