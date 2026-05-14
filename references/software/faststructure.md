# fastStructure

Inference of population structure from large SNP data sets. The module ships Python scripts that are run as executables (not via `python`).

## Loading

```bash
module spider fastStructure
module load fastStructure/1.0-gimkl-2020a-Python-2.7.18
```

## Example Slurm script

```sl
#!/bin/bash -e
#SBATCH --account   nesi99991
#SBATCH --job-name  faststructure
#SBATCH --time      01:00:00
#SBATCH --mem       2G

module purge
module load fastStructure/<version>

structure.py -K 3 --input=<infile> --output=<outfile>
```

## Plotting with distruct.py

`distruct.py` tries to open a display window. Force matplotlib to write to a file:

```bash
env MPLBACKEND='svg' distruct.py --output myplot.svg
```

## Input formats

- `.bed`: standard PLINK binary genotype file.
- `.str`: fastStructure's `.str` format differs from the original Structure `.str`. No header row; the first 6 columns are ignored; two rows per sample. Pass `--format=str` and supply the filename **without** the extension (e.g. `--input=input`, not `--input=input.str`), or fastStructure will append `.str` again.

Example `input.str`:

```
#	#	#	#	Sample1	1	1	-9	0	1	0	1	1	1	1	0
#	#	#	#	Sample1	1	1	-9	1	0	1	0	0	0	0	1
#	#	#	#	Sample2	2	0	0	1	1	1	0	1	1	0	1
#	#	#	#	Sample2	2	1	0	1	0	1	1	0	1	0	1
```

`.str` output from `ipyrad` (see `./ipyrad.md`) works directly. For VCF input, convert to `.bed` first using another tool.

## Upstream

- <https://github.com/rajanil/fastStructure>
