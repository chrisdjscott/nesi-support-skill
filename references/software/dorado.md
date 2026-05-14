# Dorado

Oxford Nanopore basecaller. GPU-based; uses libtorch with custom CUDA optimisations. Supports modified-base (Remora) and duplex basecalling, with POD5 as the preferred input format.

## Licence

Oxford Nanopore Technologies Public License v1.0.

## Loading

```bash
module spider Dorado
module load Dorado/0.4.3      # example
```

Models are not bundled with the module; download them with `dorado download --model <name>` into the working directory before basecalling.

## Example Slurm script (GPU)

CPU basecalling is too slow to be useful; always request a GPU. `--device 'cuda:all'` picks up the GPU automatically.

```sl
#!/bin/bash -e
#SBATCH --account        nesi99991
#SBATCH --job-name       dorado
#SBATCH --gpus-per-node  A100:1
#SBATCH --mem            6G
#SBATCH --cpus-per-task  4
#SBATCH --time           00:10:00
#SBATCH --output         slurmout.%j.out

module purge
module load Dorado/<version>

MODEL=dna_r10.4.1_e8.2_400bps_hac@v4.1.0

dorado download --model ${MODEL}
dorado basecaller --device 'cuda:all' ${MODEL} pod5s/ > calls.bam
```

Multi-GPU scales linearly. See `../hardware.md` for available GPU types and `../slurm-examples.md#gpu-jobs`.

## Upstream

- <https://github.com/nanoporetech/dorado>
