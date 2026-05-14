# Lambda Stack

Lambda Labs' deep-learning software stack (PyTorch, TensorFlow, CUDA, cuDNN) provided on Mahuika as Apptainer images at `/opt/nesi/containers/lambda-stack/`. Useful when you want a known-good combination of frameworks without managing modules and conda environments yourself.

## Available images

```bash
ls /opt/nesi/containers/lambda-stack/
# lambda-stack-focal-<date>.sif
# lambda-stack-focal-latest.sif
```

The `-latest` symlink points at the most recent build. See `../containers.md` for general Apptainer usage.

## Slurm template

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      lambdastack
#SBATCH --time          00:15:00
#SBATCH --ntasks        1
#SBATCH --cpus-per-task 1
#SBATCH --gpus-per-task 1
#SBATCH --mem           8G

SIF=/opt/nesi/containers/lambda-stack/lambda-stack-focal-latest.sif

module purge

CONTAINER="apptainer exec --nv -B ${PWD} ${SIF}"

${CONTAINER} python3 -c "import torch; print(torch.cuda.device_count())"
${CONTAINER} python3 my_script.py
```

`--nv` enables NVIDIA GPU access. Add extra `-B` binds for any directories under `/nesi/project` or `/nesi/nobackup` you need inside the container.

## Jupyter kernel

Register a kernel that launches the container so it shows up in <https://jupyter.nesi.org.nz/>:

```bash
export SIF=/opt/nesi/containers/lambda-stack/lambda-stack-focal-latest.sif
apptainer exec -B $HOME $SIF python -m ipykernel install --user \
    --name lambdastack --display-name="Lambda Stack Python 3"
```

Then in `$HOME/.local/share/jupyter/kernels/lambdastack/`, create `wrapper.sh`:

```bash
#!/usr/bin/env bash
SIF=/opt/nesi/containers/lambda-stack/lambda-stack-focal-latest.sif
module purge
homefull=$(readlink -e $HOME)
CONTAINER="apptainer exec --nv -B ${HOME},${homefull},${PWD} ${SIF}"
${CONTAINER} python3 "$@"
```

Make it executable (`chmod +x wrapper.sh`) and edit `kernel.json` so `argv[0]` points at the wrapper. The `homefull` bind is needed because `$HOME` is sometimes a symlink on Mahuika and Jupyter writes the connection file at the canonical path.

## Extending the container

To add packages without rebuilding, create a venv inside the container with `--system-site-packages`:

```bash
apptainer exec -B $PWD $SIF bash
virtualenv --system-site-packages myenv
source myenv/bin/activate
pip install <extra packages>
exit
```

Then activate `myenv` from inside the container in your job.

## Upstream

- <https://lambdalabs.com/lambda-stack-deep-learning-software>
- <https://github.com/lambdal/lambda-stack-dockerfiles>
