# Ollama

Local LLM runtime. Useful for ad-hoc inference and prototyping against open models on the REANNZ/NeSI GPUs. Note that running a single-user Ollama server is an inefficient use of a whole GPU; reserve this for test jobs rather than production batch inference.

Pre-cached open-weight GGUF model files (Llama 3.1, DeepSeek-R1, Qwen3, Qwen2.5, Gemma 3) live under `/opt/nesi/models/gguf/`. See `references/filesystems.md` for the size-to-GPU mapping.

## Loading

```bash
module purge
module load ollama
```

## Interactive: ollama as a Slurm job

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
unset CUDA_VISIBLE_DEVICES  # Slurm sets this to 0; ollama manages the GPU itself.

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

## Batch: one-shot prompt

Start `ollama serve` in the background, wait until it answers, run the prompt, exit. The job ending kills the server.

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      ollama-batch
#SBATCH --time          00:30:00
#SBATCH --mem           10G
#SBATCH --gpus-per-node l4:1

module purge
module load ollama
unset CUDA_VISIBLE_DEVICES

ollama serve &>/dev/null &
until ollama list &>/dev/null; do sleep 1; done

echo "What is the capital of France?" | ollama run llama3.1:8b
```

## Gotchas

- Model weights are cached under `$HOME/.ollama` by default. Set `OLLAMA_MODELS=/nesi/project/nesi99991/ollama-models` to keep them out of your 20 GB `/home` quota.
- Pre-cached GGUF files at `/opt/nesi/models/` are not picked up by `ollama pull`; consume them via a custom `Modelfile` (`FROM /opt/nesi/models/gguf/<...>.gguf`).
- For verbose server logs, set `OLLAMA_DEBUG=1` before `ollama serve`.
- Slurm sets `CUDA_VISIBLE_DEVICES=0` per task, which collides with ollama's own GPU selection. `unset CUDA_VISIBLE_DEVICES` before `ollama serve` (already in the templates above).
- One job, one GPU, one user, the server has no multi-tenancy. For shared inference use a properly hosted service.

## Upstream

- <https://ollama.com/>
- <https://github.com/ollama/ollama>
