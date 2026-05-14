# Containers on Mahuika (Apptainer)

Mahuika supports Apptainer (open-source fork of Singularity). Docker images are OCI-compatible and convert directly. Build/run as your normal user, no root needed.

## One-time setup

Apptainer caches in `~/.apptainer` by default, but `/home` is only 20 GB. Redirect to nobackup:

```bash
export APPTAINER_CACHEDIR=/nesi/nobackup/nesi99991/apptainer-cache
export APPTAINER_TMPDIR=$APPTAINER_CACHEDIR
mkdir -p $APPTAINER_CACHEDIR
```

Persist these in `~/.bashrc`:

```bash
echo 'export APPTAINER_CACHEDIR=/nesi/nobackup/nesi99991/apptainer-cache' >> ~/.bashrc
echo 'export APPTAINER_TMPDIR=$APPTAINER_CACHEDIR' >> ~/.bashrc
```

Replace `nesi99991` with your project code.

## Loading the module

```bash
module load Apptainer
```

## Pulling an image

Convert a Docker image to a `.sif` file:

```bash
apptainer pull mycontainer.sif docker://redis/redis-stack
```

Pulls from the registry, stores locally. Use `.sif` extension to make image files easy to spot.

## Building an image

`fakeroot` is enabled on login and compute nodes. Builds can be CPU/memory heavy, so do them in a Slurm job rather than on the login node.

Definition file (`my_container.def`):

```text
BootStrap: docker
From: ubuntu:24.04

%post
    apt-get -y update
    apt-get install -y wget python3
```

Build script (`build.sl`):

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      apptainer_build
#SBATCH --time          00:30:00
#SBATCH --mem           4G
#SBATCH --cpus-per-task 2

# Recent Apptainer modules set APPTAINER_BIND, which often breaks builds.
unset APPTAINER_BIND

export APPTAINER_CACHEDIR=/nesi/nobackup/$SLURM_JOB_ACCOUNT/$USER/apptainer_cache
export APPTAINER_TMPDIR=$APPTAINER_CACHEDIR
mkdir -p $APPTAINER_CACHEDIR

module load Apptainer
apptainer build --force --fakeroot my_container.sif my_container.def
```

`fakeroot` doesn't work for every image. If it errors, try a different base image or older tag, or contact `support@nesi.org.nz`.

Common error: `unsupported image-specific operation on artifact with type "application/vnd.docker.container.image.v1+json"`, usually a bad upstream image, try another version.

## Running

### Interactive shell

```bash
apptainer shell my_container.sif
# prompt becomes: Apptainer>
exit
```

### One-off command

```bash
apptainer exec my_container.sif python3 -V
apptainer exec my_container.sif my_script.py --help
```

### Default runscript

```bash
apptainer run my_container.sif
# or, if the .sif has +x and a runscript
./my_container.sif
```

### Inspecting metadata

```bash
apptainer inspect my_container.sif
```

### Inside a Slurm job

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      container-job
#SBATCH --time          01:00:00
#SBATCH --mem           4G
#SBATCH --cpus-per-task 4

module load Apptainer
apptainer run mycontainer.sif my_script.py some_arg
```

## GPU containers

Pass `--nv` to inject NVIDIA libraries and the GPU device:

```bash
apptainer exec --nv tensorflow-gpu.sif python3 train.py
```

In a Slurm job:

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --time          01:00:00
#SBATCH --ntasks        1
#SBATCH --cpus-per-task 8
#SBATCH --gpus-per-node A100:1
#SBATCH --mem           16G

module purge
module load Apptainer
apptainer exec --nv my-gpu.sif python3 train.py
```

## NVIDIA NGC containers

NVIDIA distributes optimised containers (PyTorch, TensorFlow, NAMD, GROMACS, ...) at <https://catalog.ngc.nvidia.com/containers>. Most run under Apptainer with minor adjustments.

Pull (no root required):

```bash
apptainer pull namd.sif docker://nvcr.io/hpc/namd:3.0-alpha9-singlenode
```

Run (NAMD example):

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      namd-gpu
#SBATCH --time          00:30:00
#SBATCH --ntasks        1
#SBATCH --cpus-per-task 8
#SBATCH --gpus-per-node A100:1
#SBATCH --mem           4G

module purge
module load Apptainer

NAMD_INPUT=apoa1_nve_cuda.namd
NAMD_SIF=namd.sif

apptainer exec --nv -B $(pwd):/host_pwd --pwd /host_pwd $NAMD_SIF \
    namd3 +ppn ${SLURM_CPUS_PER_TASK} +idlepoll $NAMD_INPUT
```

The `-B $(pwd):/host_pwd --pwd /host_pwd` binds the current host directory into the container and uses it as the working dir.

## MPI containers

Containerised MPI apps need the *container's* MPI to be ABI-compatible with the host MPI when launched via `srun`. In practice that often means matching OpenMPI major versions. If you can, build the container against the same OpenMPI version you'll run on (foss-2023a uses OpenMPI 4.1.x).

## Network and ports

By default Apptainer shares the host network. Use `--net --network=none` for isolation:

```bash
apptainer exec --net --network=none my_container.sif <cmd>
```

Services inside the container must bind to ports >1024 (unprivileged).

```bash
apptainer instance start nginx.sif nginx
# work with the running instance
apptainer instance stop nginx
```

## Tips

- Bind your output directory in (`-B /nesi/nobackup/...:/work --pwd /work`) so results land on the host filesystem, not inside the image.
- Keep images immutable, never write data into the `.sif`.
- If a container's MPI doesn't match the host's, run inside the container's own MPI (no `srun`) at the cost of giving up Slurm's rank tracking.
- Apptainer doesn't need privileged ports inside the container, but reserved ports below 1024 won't work even if root inside the container.
