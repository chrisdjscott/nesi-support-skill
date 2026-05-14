# TensorFlow on CPUs

TensorFlow modules on Mahuika are GPU-optimised. If you need a CPU-only build (I/O-bound workloads, large-ensemble inference, or jobs that don't justify a GPU), install an Intel oneDNN-enabled wheel via conda. See `tensorflow_gpu.md` for the GPU build.

## Building a CPU-optimised environment

```bash
module purge
module load Miniforge3
conda create -p /nesi/project/nesi99991/conda_envs/tf_cpu tensorflow-mkl
source activate /nesi/project/nesi99991/conda_envs/tf_cpu
python -c "import tensorflow as tf; print(tf.__version__)"
```

Pin a specific version with `tensorflow-mkl==x.y.z`. Warnings of the form "The TensorFlow library was not compiled to use ... instructions" are harmless; oneMKL dispatches on the actual CPU at runtime.

## Slurm template

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      tensorflow-cpu
#SBATCH --time          02:00:00
#SBATCH --cpus-per-task 8
#SBATCH --mem           8G

# oneDNN threading
export KMP_BLOCKTIME=0
export KMP_AFFINITY=granularity=fine,compact,0,0

module purge
module load Miniforge3
source activate /nesi/project/nesi99991/conda_envs/tf_cpu

srun python my_tensorflow_program.py
```

See `../debugging-efficiency.md` for sizing `--cpus-per-task` and `--mem`, and `../parallel-computing.md` for thread placement guidance.

## Operator parallelism (TF 1.x)

```python
import os
num_threads = int(os.getenv("SLURM_CPUS_PER_TASK", 1))
num_inter = 1
assert num_threads % num_inter == 0
num_intra = num_threads // num_inter
os.environ["OMP_NUM_THREADS"] = str(num_intra)

import tensorflow as tf
config = tf.ConfigProto()
config.inter_op_parallelism_threads = num_inter
config.intra_op_parallelism_threads = num_intra
tf.Session(config=config)
```

In TF 2.x use `tf.config.threading.set_inter_op_parallelism_threads(...)` and `set_intra_op_parallelism_threads(...)` instead.

## Gotchas

- Don't `pip install tensorflow` on top of a `tensorflow-mkl` conda env; the wheel will overwrite the oneDNN build.
- For best CPU throughput on Mahuika Broadwell/Milan nodes, request whole sockets (`--cpus-per-task=18` or larger) and bind threads with `KMP_AFFINITY`.

## Upstream

- <https://www.tensorflow.org/>
- <https://software.intel.com/en-us/articles/intel-optimization-for-tensorflow-installation-guide>
