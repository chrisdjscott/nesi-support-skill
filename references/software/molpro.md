# Molpro

Commercial *ab initio* electronic structure suite for molecular calculations.

## Licence

Restricted. You may only use Molpro on Mahuika if you hold a valid institutional licence that permits cluster use. NeSI does not supply licence tokens; obtain yours from your supervisor or institutional procurement officer.

### Licence token

Either pass the token path on the command line with `-k /path/to/key` (some builds only), or place it at `~/.molpro/token`:

```bash
mkdir -p ~/.molpro
ln -s /path/to/your/licence/key ~/.molpro/token   # preferred
# or: cp /path/to/your/licence/key ~/.molpro/token
```

Symbolic links pick up administrator key replacements automatically.

## Loading

```bash
module spider Molpro
module load Molpro/mpp-2019.2.2.linux_x86_64_openmp     # example
```

## Example Slurm script

```sl
#!/bin/bash -e
#SBATCH --account     nesi99991
#SBATCH --job-name    molpro
#SBATCH --time        01:00:00
#SBATCH --mem-per-cpu 4G
#SBATCH --output      molpro.%j.out
#SBATCH --error       molpro.%j.err

module purge
module load Molpro/<version>

molpro -k /path/to/licence.key Molpro_job.inp
# or, if ~/.molpro/token is set up:
# molpro Molpro_job.inp
```

## Troubleshooting

### Serial test on the command line

To isolate Molpro issues from scheduler/MPI issues, run in serial:

```bash
module load Molpro/<version>
molpro -v --launcher "" Molpro_job.inp
```

Drop `--launcher ""` to test the MPI launch path.

### "!LICENCE! Password missing on licence token"

Token file is corrupt, or `-k` is unsupported by your build. Verify the key matches the master key for your group, or install it at `~/.molpro/token` and remove `-k` from the command line.

## Upstream

- <https://www.molpro.net/>
