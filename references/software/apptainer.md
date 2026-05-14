# Apptainer

Container runtime on Mahuika (open-source fork of Singularity). For the full reference (cache configuration, building containers, NGC pulls, GPU usage, MPI containers, troubleshooting), see `../containers.md`.

## Loading

```bash
module load Apptainer
```

## Common commands

```bash
apptainer pull my.sif docker://org/image:tag    # pull and convert OCI image to SIF
apptainer shell my.sif                          # interactive shell inside container
apptainer exec my.sif command [args]            # run one command inside container
apptainer exec --nv my.sif command              # with NVIDIA GPU access
apptainer run my.sif                            # execute the container's %runscript
apptainer inspect my.sif                        # show metadata
apptainer build --fakeroot my.sif my.def        # build SIF from definition file
```

## Cache directory (essential)

By default Apptainer writes to `~/.apptainer`. Redirect to nobackup so you don't fill the 20 GB home quota.

```bash
export APPTAINER_CACHEDIR="/nesi/nobackup/nesi99991/$USER/apptainer-cache"
export APPTAINER_TMPDIR="${APPTAINER_CACHEDIR}"
mkdir -p "$APPTAINER_CACHEDIR"
```

See `../containers.md` for full details.

## Upstream

- <https://apptainer.org/>
