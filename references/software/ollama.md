# Ollama

Local LLM runtime. Useful for ad-hoc inference and prototyping against open models on the REANNZ/NeSI GPUs. Note that running a single-user Ollama server is an inefficient use of a whole GPU; reserve this for test jobs rather than production batch inference.

## Loading

```bash
module purge
module load ollama
```

## Running ollama as a Slurm job

Start the server on a compute node and tunnel the port back to the login node:

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      ollama
#SBATCH --time          01:00:00
#SBATCH --mem           10G
#SBATCH --gpus-per-node l4:1

PORT=16000   # pick your own between 1024 and 49151

module purge
module load ollama

export OLLAMA_HOST=${HOSTNAME}:${PORT}
ssh -NfR ${PORT}:${HOSTNAME}:${PORT} ${SLURM_SUBMIT_HOST}

ollama serve
```

On the login node, point a client at the running server:

```bash
module purge
module load ollama
export OLLAMA_HOST=<nodename>:<port>
ollama list
ollama run llama3 "hello"
```

Find `<nodename>` with `squeue --me` or `sacct -j <jobid>`.

## Gotchas

- Model weights are cached under `$HOME/.ollama` by default. Set `OLLAMA_MODELS=/nesi/project/nesi99991/ollama-models` to keep them out of your 20 GB `/home` quota.
- For verbose logs, set `GIN_MODE=debug` before `ollama serve`.
- One job, one GPU, one user, the server has no multi-tenancy. For shared inference use a properly hosted service.

## Upstream

- <https://ollama.com/>
- <https://github.com/ollama/ollama>
