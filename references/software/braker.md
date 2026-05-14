# BRAKER

Automated gene structure annotation pipeline combining GeneMark and AUGUSTUS. BRAKER1 uses RNA-Seq, BRAKER2 uses protein homology, BRAKER3 uses both. Source under the Artistic Licence.

## Prerequisites

### GeneMark licence key

GeneMark-ES/ET (a BRAKER dependency) requires a free academic licence:

1. Download `gm_key_64.gz` from <http://topaz.gatech.edu/genemark/license_download.cgi>.
2. `gunzip gm_key_64.gz`
3. Move to `~/.gm_key` (note the leading dot).

### Writable AUGUSTUS config

AUGUSTUS writes species training data into its config directory. Copy the module's config to a writable location:

```bash
cp -r /opt/nesi/CS400_centos7_bdw/AUGUSTUS/3.4.0-gimkl-2022a/config /nesi/project/nesi99991/augustus_config
```

Adjust the source path for your AUGUSTUS version (`module show AUGUSTUS/...`).

## Loading

```bash
module spider BRAKER
module load BRAKER/3.0.2-gimkl-2022a-Perl-5.34.1     # example
```

## Example Slurm script

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      braker
#SBATCH --cpus-per-task 4
#SBATCH --mem           1G
#SBATCH --time          02:00:00
#SBATCH --output        slurmlogs/%x.%j.out
#SBATCH --error         slurmlogs/%x.%j.err

module purge
module load BRAKER/<version>

export AUGUSTUS_CONFIG_PATH=/nesi/project/nesi99991/augustus_config

srun braker.pl --threads=${SLURM_CPUS_PER_TASK} \
    --genome=genome.fa --prot_seq=proteins.fa
```

Output appears in `./braker/`, including `braker.gtf`, hints files, and AUGUSTUS predictions.

## Upstream

- <https://github.com/Gaius-Augustus/BRAKER>
