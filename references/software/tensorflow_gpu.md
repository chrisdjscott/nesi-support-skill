# TensorFlow on GPUs

Deep-learning framework, GPU-accelerated. Mahuika modules ship CUDA and cuDNN dependencies pre-wired. For CPU-only builds see `tensorflow_cpu.md`. For GPU partitions and devices see `../hardware.md`.

## Loading

```bash
module spider TensorFlow
module load TensorFlow/<version>     # pulls in matching CUDA + cuDNN
python -c "import tensorflow as tf; print(tf.__version__, tf.config.list_physical_devices('GPU'))"
```

## Slurm template (single GPU)

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      tensorflow-gpu
#SBATCH --time          01:00:00
#SBATCH --gpus-per-node 1
#SBATCH --cpus-per-task 2
#SBATCH --mem           8G

module purge
module load TensorFlow/<version>

srun python train.py
```

## Virtual environment on top of the module

```bash
module load TensorFlow/<version>
export PYTHONNOUSERSITE=1
python3 -m venv --system-site-packages /nesi/project/nesi99991/tf_venv
source /nesi/project/nesi99991/tf_venv/bin/activate
pip install <extra packages>     # e.g. scikeras, tensorflow-hub
```

`--system-site-packages` lets the venv reuse the module's TensorFlow. `PYTHONNOUSERSITE=1` blocks stray `~/.local` packages from leaking in. Activate the venv in your Slurm script after `module load`.

## Conda alternative

```bash
module purge
module load Miniforge3/25.3.1-0
export PYTHONNOUSERSITE=1
conda create -p /nesi/project/nesi99991/conda_envs/tf python=3.10
source $(conda info --base)/etc/profile.d/conda.sh
conda activate /nesi/project/nesi99991/conda_envs/tf
pip install tensorflow==2.15
module load cuDNN/<version>   # match TF's tested cuDNN/CUDA combo
```

Check <https://www.tensorflow.org/install/source#gpu> for the tested TF/CUDA/cuDNN matrix.

## NVIDIA container (NGC)

For bleeding-edge or A100/H100-tuned builds, use the official NGC TensorFlow container via Apptainer. See `../containers.md`.

## A100 notes

- TensorFlow 1.x: only the NGC TF1 container supports Ampere. Stock TF1 wheels will crash or silently fall back to CPU.
- TensorFlow 2.x: 2.4 and newer support A100 out of the box.

## Gotchas

- `tf.config.list_physical_devices('GPU')` returns empty: you forgot `--gpus-per-node`, or you loaded the wrong cuDNN/CUDA module.
- OOM at startup: large models on small GPUs (L4, P100). Either request `--gpus-per-node A100:1` or shard with `tf.distribute.MirroredStrategy`.
- Long compile delays on first step: XLA JIT. Set `TF_XLA_FLAGS=--tf_xla_auto_jit=2` to enable, or disable with `--tf_xla_auto_jit=0` if it's hurting you.

## Upstream

- <https://www.tensorflow.org/>
- <https://catalog.ngc.nvidia.com/orgs/nvidia/containers/tensorflow>
