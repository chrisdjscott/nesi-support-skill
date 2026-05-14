# Keras

High-level neural-network API shipped inside TensorFlow. On Mahuika, load a TensorFlow module (CPU or GPU build) and `import tensorflow.keras` (or `import keras` for standalone). See `tensorflow_gpu.md` and `tensorflow_cpu.md` for full details on TensorFlow itself.

## Loading

```bash
module spider TensorFlow
module load TensorFlow/<version>
python -c "from tensorflow import keras; print(keras.__version__)"
```

There is no separate `Keras` module; use the TensorFlow module.

## GPU Slurm template

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      keras-gpu
#SBATCH --time          00:30:00
#SBATCH --gpus-per-node 1
#SBATCH --cpus-per-task 2
#SBATCH --mem           4G

module purge
module load TensorFlow/<version>

srun python train.py
```

## CPU Slurm template

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      keras-cpu
#SBATCH --time          01:00:00
#SBATCH --cpus-per-task 8
#SBATCH --mem           8G

export KMP_BLOCKTIME=0
export KMP_AFFINITY=granularity=fine,compact,0,0

module purge
module load TensorFlow/<version>

srun python train.py
```

## Gotchas

- Standalone `keras` (pip-installed) and `tensorflow.keras` are no longer fully interchangeable in TF 2.16+. Prefer `tensorflow.keras` when using the Mahuika TensorFlow module.
- Reproducibility: set seeds via `tf.keras.utils.set_random_seed(...)` and (for full determinism on GPU) `tf.config.experimental.enable_op_determinism()`.
- For large datasets use `tf.data.Dataset` pipelines, not Python generators, to avoid being I/O-bound.

## Upstream

- <https://keras.io/>
- <https://www.tensorflow.org/guide/keras>
