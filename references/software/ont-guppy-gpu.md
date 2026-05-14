# ont-guppy-gpu

Oxford Nanopore's Guppy basecaller (GPU build). Performs basecalling, barcoding/demultiplexing, adapter trimming, alignment, and modified-base calling (5mC, 6mA, CpG) from raw FAST5 signal data. Available to ONT customers via <https://community.nanoporetech.com/>.

For new work, prefer `./dorado.md` (ONT's current basecaller). Guppy remains available for compatibility.

## Loading

```bash
module spider ont-guppy-gpu
module load ont-guppy-gpu/6.4.2       # example
```

Config files for each flowcell/kit combination ship inside the module at `/opt/nesi/CS400_centos7_bdw/ont-guppy-gpu/<version>/data/`.

## Example Slurm script (GPU)

CPU basecalling is not recommended. `--device auto` selects the GPU.

```sl
#!/bin/bash -e
#SBATCH --account        nesi99991
#SBATCH --job-name       guppy
#SBATCH --gpus-per-node  A100:1
#SBATCH --mem            6G
#SBATCH --cpus-per-task  4
#SBATCH --time           10:00:00
#SBATCH --output         slurmout.%j.out

module purge
module load ont-guppy-gpu/<version>

guppy_basecaller \
    -i /path/to/input/fast5 \
    -s /path/to/output/fastq \
    --config /opt/nesi/CS400_centos7_bdw/ont-guppy-gpu/<version>/data/<config>.cfg \
    --device auto --recursive --records_per_fastq 4000 \
    --calib_detect --calib_reference lambda_3.6kb.fasta \
    --detect_mid_strand_adapter
```

See `../hardware.md` for GPU types and `../slurm-examples.md#gpu-jobs`.

## Upstream

- <https://community.nanoporetech.com/>
