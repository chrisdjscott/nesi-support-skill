# Cylc

General-purpose workflow engine with first-class support for cycling (repeated) workflows. Used in operational weather and climate forecasting. For non-cycling pipelines see `snakemake.md` or `nextflow.md`.

## Loading

Cylc is not provided as a centrally-managed module; install it into a conda environment under your project space.

```bash
module purge && module load Miniforge3
export CYLC_HOME=/nesi/project/nesi99991/$USER/environment/cylc-env
conda create --prefix $CYLC_HOME python=3.12
```

Then activate and install `cylc-flow`:

```bash
module purge && module load Miniforge3
conda activate $CYLC_HOME
conda install -c conda-forge cylc-flow
cylc --version       # expect 8.6.0 or later
```

See `./miniforge3.md` for conda environment hygiene on Mahuika.

## Wrapper script

A small wrapper is needed so `cylc` can be invoked through Slurm:

```bash
mkdir $CYLC_HOME/wrapper
cylc get-resources cylc $CYLC_HOME/wrapper
chmod +x $CYLC_HOME/wrapper/cylc
sed -i "s|CYLC_HOME_ROOT=\"\${CYLC_HOME_ROOT:-/opt}\"|CYLC_HOME_ROOT=\"\${CYLC_HOME_ROOT:-${CYLC_HOME}}\"|" \
    $CYLC_HOME/wrapper/cylc
```

Add to your shell init so new sessions find it:

```bash
export CYLC_HOME=/nesi/project/nesi99991/$USER/environment/cylc-env
export PATH=$CYLC_HOME/wrapper:$PATH
```

## Passwordless SSH (required)

Cylc starts schedulers on configured run hosts and submits jobs via SSH. All Mahuika login nodes share the same filesystem, so generate a key with no passphrase and authorise it:

```bash
ssh-keygen                                              # press enter on passphrase prompt
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 700 ~ ~/.ssh
chmod 600 ~/.ssh/authorized_keys ~/.ssh/id_rsa
```

Verify with `ssh login02` (should not prompt).

## Slurm platform configuration

Edit `~/.cylc/flow/global.cylc`:

```text
[platforms]
    [[mahuika-slurm]]
        hosts = login01, login02, login03
        install target = localhost
        job runner = slurm
```

## Running a workflow

From a directory containing a `flow.cylc` definition:

```bash
cylc vip .           # validate, install, play
squeue --me          # check that Slurm received tasks
cylc tui <workflow>  # interactive task monitor
cylc clean <workflow>
```

See `../slurm.md` for general Slurm usage.

## Upstream

- <https://cylc.github.io/>
- <https://cylc.github.io/documentation/>
