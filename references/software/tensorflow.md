# TensorFlow

Machine-learning library, runs on CPUs and GPUs, callable from Python. Includes Keras (the high-level model-building API); there is no separate Keras module, `import tensorflow.keras`. For GPU partitions and devices see `../hardware.md`.

## Getting TensorFlow

Four options, in rough order of convenience.

### Environment module

```bash
module spider TensorFlow
module load TensorFlow/2.13.0-gimkl-2022a-Python-3.11.3
python -c "import tensorflow as tf; print(tf.__version__, tf.config.list_physical_devices('GPU'))"
```

The module pulls in the matching CUDA and cuDNN automatically, so it works on GPUs without loading anything else.

### Python virtual environment

The default `tensorflow` wheel is CPU-only. For GPU support install `tensorflow[and-cuda]`, which bundles the CUDA libraries (no CUDA/cuDNN module needed).

```bash
module purge
module load Python/3.11.6-foss-2023a
export PYTHONNOUSERSITE=1
python3 -m venv /nesi/project/nesi99991/<username>/tf_venv
source /nesi/project/nesi99991/<username>/tf_venv/bin/activate
pip install --upgrade pip
pip install tensorflow                # CPU-only
pip install 'tensorflow[and-cuda]'    # GPU (CUDA included)
```

`PYTHONNOUSERSITE=1` keeps stray `~/.local` packages out. Activate the venv again in your Slurm script after `module load`.

### Conda environment

For a specific Python/TensorFlow combination, via `Miniforge3` (see `miniforge3.md`):

```bash
module purge && module load Miniforge3/25.3.1-0
source $(conda info --base)/etc/profile.d/conda.sh
export PYTHONNOUSERSITE=1
conda create -p /nesi/project/nesi99991/<username>/tf_conda python=3.11
conda activate /nesi/project/nesi99991/<username>/tf_conda
pip install 'tensorflow[and-cuda]'    # or plain tensorflow for CPU-only
```

### NVIDIA container

For bleeding-edge or GPU-tuned builds, run the official NGC TensorFlow container via Apptainer. See `../containers.md`.

## CPU jobs

Prefer CPUs when the workflow is I/O-bound, spreads across many nodes for aggregate bandwidth, or trains a large ensemble of small models, where a GPU gives little benefit for the core-hour cost.

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      tensorflow-cpu
#SBATCH --time          01:00:00
#SBATCH --cpus-per-task 8
#SBATCH --mem           8G

export OMP_PROC_BIND=true
export OMP_PLACES=cores

module purge
module load Python/3.11.6-foss-2023a
source /nesi/project/nesi99991/<username>/tf_venv/bin/activate
srun python my_tensorflow_program.py
```

Pinning threads (`OMP_PROC_BIND`, `OMP_PLACES`) gives more consistent timings because nodes are shared. See `../parallel-computing.md` for placement and `../debugging-efficiency.md` for sizing.

### Controlling thread parallelism

TensorFlow chooses intra-op (one operator across threads) and inter-op (independent operators concurrently) parallelism automatically, but setting them explicitly can help. Before any operations run:

```python
import os
import tensorflow as tf

numThreads = int(os.getenv('SLURM_CPUS_PER_TASK', 1))
numInterOpThreads = 1
assert numThreads % numInterOpThreads == 0
numIntraOpThreads = numThreads // numInterOpThreads

tf.config.threading.set_inter_op_parallelism_threads(numInterOpThreads)
tf.config.threading.set_intra_op_parallelism_threads(numIntraOpThreads)
```

## GPU jobs

Set TensorFlow up with any method above (with `pip`, use `tensorflow[and-cuda]`), request a GPU, and confirm it is visible.

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      tensorflow-gpu
#SBATCH --time          01:00:00
#SBATCH --gpus-per-node L4:1
#SBATCH --cpus-per-task 2
#SBATCH --mem           8G

module purge
module load TensorFlow/2.13.0-gimkl-2022a-Python-3.11.3

python -c "import tensorflow as tf; print('GPUs:', tf.config.list_physical_devices('GPU'))"
python train.py
```

See `../slurm-examples.md#gpu-jobs` for GPU type selection.

## Gotchas

- `tf.config.list_physical_devices('GPU')` empty: you forgot `--gpus-per-node`, or a pip-installed CPU-only wheel is shadowing the GPU build (reinstall with `tensorflow[and-cuda]`).
- OOM at startup: model too large for the GPU (L4 has 24 GB). Request `--gpus-per-node A100:1` or shard with `tf.distribute.MirroredStrategy`.
- Do not `pip install tensorflow` on top of `tensorflow[and-cuda]`; the CPU wheel overwrites the GPU build.
- Reproducibility: `tf.keras.utils.set_random_seed(...)` and `tf.config.experimental.enable_op_determinism()`.

## Upstream

- <https://www.tensorflow.org/>
- <https://catalog.ngc.nvidia.com/orgs/nvidia/containers/tensorflow>
