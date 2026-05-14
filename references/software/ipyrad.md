# ipyrad

Interactive assembly and analysis toolkit for RAD-seq and related data types. GPLv3.

## Loading

```bash
module spider ipyrad
module load ipyrad/0.9.85-gimkl-2022a-Python-3.10.5     # example
```

## Initialising a parameters file

```bash
module load ipyrad/<version>
ipyrad -n data1                # creates params-data1.txt
```

Edit `params-data1.txt` to point to your raw reads, barcodes, etc.

## Example Slurm script (single node, multi-core)

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      ipyrad
#SBATCH --cpus-per-task 12
#SBATCH --time          00:05:00
#SBATCH --mem           10G
#SBATCH --output        ipyrad_output_%j.txt

module purge
module load ipyrad/<version>

assembly_name="data1"
jobdir="ipyrad_${SLURM_JOB_ID}"
params="params-${assembly_name}.txt"

mkdir "${jobdir}"
sed "s#$(pwd) #$(pwd)/${jobdir}#" "${params}" > "${jobdir}/${params}"
cd "${jobdir}"

srun ipyrad -p "${params}" -s 1234567 --force
```

`-s 1234567` runs steps 1 through 7. Substitute `-s 12` etc. to run only the steps you need.

## Upstream

- <https://ipyrad.readthedocs.io/>
