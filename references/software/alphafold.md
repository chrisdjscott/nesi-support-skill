# AlphaFold

Protein structure prediction from DeepMind. Two families are available on Mahuika:

- AlphaFold 2 (proteins only): run as an environment module (recommended, v2.3.2+) or via Singularity/Apptainer (pre-2.3.2). Takes FASTA input.
- AlphaFold 3 (proteins, nucleic acids, ligands, ions): module `AlphaFold/3.x`. Takes JSON input. Predicts structure only, not binding affinities. You must obtain the model weights yourself (see below).

NeSI also maintains an extended AlphaFold 2 guide: <https://nesi.github.io/alphafold2-on-mahuika/>.

## AlphaFold 2 licence

- Code: Apache 2.0.
- Model parameters: CC BY-NC 4.0 (non-commercial only).
- Cite the AlphaFold paper (doi:10.1038/s41586-021-03819-2) in any work using it.

## AlphaFold 2 databases

Stored at `/opt/nesi/db/alphafold_db/`. Loaded as their own modules:

```bash
module spider AlphaFold2DB     # shows available versions (Year-Month)
module load AlphaFold2DB/2023-04
echo $AF2DB                    # /opt/nesi/db/alphafold_db/2023-04
```

## AlphaFold 2 module (v2.3.2+)

### Monomer

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      af2-monomer
#SBATCH --time          02:00:00
#SBATCH --mem           24G
#SBATCH --cpus-per-task 8
#SBATCH --gpus-per-node A100:1
#SBATCH --output        %j.out

module purge
module load AlphaFold2DB/2023-04
module load AlphaFold/2.3.2

INPUT=/nesi/project/nesi99991/alphafold/input
OUTPUT=/nesi/project/nesi99991/alphafold/results

run_alphafold.py \
  --use_gpu_relax \
  --data_dir=$AF2DB \
  --uniref90_database_path=$AF2DB/uniref90/uniref90.fasta \
  --mgnify_database_path=$AF2DB/mgnify/mgy_clusters_2022_05.fa \
  --bfd_database_path=$AF2DB/bfd/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt \
  --uniref30_database_path=$AF2DB/uniref30/UniRef30_2021_03 \
  --pdb70_database_path=$AF2DB/pdb70/pdb70 \
  --template_mmcif_dir=$AF2DB/pdb_mmcif/mmcif_files \
  --obsolete_pdbs_path=$AF2DB/pdb_mmcif/obsolete.dat \
  --model_preset=monomer \
  --max_template_date=2022-6-1 \
  --db_preset=full_dbs \
  --output_dir=$OUTPUT \
  --fasta_paths=$INPUT/my_protein.fasta
```

### Multimer

Same Slurm header (you may need more memory for large complexes), with `--model_preset=multimer` and an extra database path:

```bash
run_alphafold.py \
  --use_gpu_relax \
  --data_dir=$AF2DB \
  --model_preset=multimer \
  --uniprot_database_path=$AF2DB/uniprot/uniprot.fasta \
  --uniref90_database_path=$AF2DB/uniref90/uniref90.fasta \
  --mgnify_database_path=$AF2DB/mgnify/mgy_clusters_2022_05.fa \
  --bfd_database_path=$AF2DB/bfd/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt \
  --uniref30_database_path=$AF2DB/uniref30/UniRef30_2021_03 \
  --pdb_seqres_database_path=$AF2DB/pdb_seqres/pdb_seqres.txt \
  --template_mmcif_dir=$AF2DB/pdb_mmcif/mmcif_files \
  --obsolete_pdbs_path=$AF2DB/pdb_mmcif/obsolete.dat \
  --max_template_date=2022-6-1 \
  --db_preset=full_dbs \
  --output_dir=$OUTPUT \
  --fasta_paths=$INPUT/multimer.fasta
```

Multimer input fasta has one chain per FASTA record:

```text
>T1083
GAMGSEIEHIE...
>T1084
MAAHKGAEHHH...
```

## Singularity container (pre-2.3.2)

Older versions are run via Singularity. Image and definition at `/opt/nesi/containers/AlphaFold/`.

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      af2-monomer-sif
#SBATCH --time          02:00:00
#SBATCH --mem           30G
#SBATCH --cpus-per-task 6
#SBATCH --gpus-per-node A100:1
#SBATCH --output        slurmout.%j.out

module purge
module load AlphaFold2DB/2022-06
module load cuDNN/8.1.1.33-CUDA-11.2.0 Singularity/3.9.8

INPUT=/nesi/project/nesi99991/alphafold/input
OUTPUT=/nesi/project/nesi99991/alphafold/results
export SINGULARITY_BIND="$INPUT,$OUTPUT,$AF2DB"

singularity exec --nv /opt/nesi/containers/AlphaFold/alphafold_2.2.0.simg \
    python /app/alphafold/run_alphafold.py \
    --use_gpu_relax \
    --data_dir=$AF2DB \
    ...
```

`--nv` enables GPU access; `SINGULARITY_BIND` exposes the input/output dirs and database inside the container.

## AlphaFold 3

Folds complexes of proteins, DNA/RNA, ligands and ions. Input is a JSON file (a single model handles both monomers and multimers; what you fold is decided by the `sequences` list, not a model preset). The workflow splits into a CPU-bound data pipeline (genetic/template search) and a GPU-bound inference stage.

### Weights (you must request them)

The AlphaFold 3 parameters are not redistributed by Mahuika. Agree to the [Model Parameters Terms of Use](https://github.com/google-deepmind/alphafold3/blob/main/WEIGHTS_TERMS_OF_USE.md) and request access from Google DeepMind yourself (non-commercial only, no sharing). Store them under your own project space and point `--model_dir` at that directory.

Licence split: source code is Apache 2.0; the model parameters and any output generated with them carry the non-commercial terms above.

### Modules

```bash
module load AlphaFold/3.0.2
module load AlphaFold3DB/2024-12    # sets $AF3DB (database dir)
module load HMMER/3.4-GCC-12.3.0    # sets $HMMER_DIR (genetic-search binaries)
```

### Input JSON

A single `protein` block with one chain is a monomer; add more entries (each with its own `id`) for a multimer, or list several ids on one block (`"id": ["A","B"]`) for a homo-multimer. Blocks of type `dna`, `rna`, `ligand`, `ion` mix molecule types.

```json
{
  "name": "my_protein",
  "modelSeeds": [1],
  "sequences": [
    { "protein": { "id": "A", "sequence": "GMRESYANEN..." } }
  ],
  "dialect": "alphafold3",
  "version": 1
}
```

### Slurm script

AlphaFold 3 does not infer paths automatically: pass databases (under `$AF3DB`), HMMER binaries (under `$HMMER_DIR`), and your weights (`--model_dir`).

```sl
#!/bin/bash -e
#SBATCH --account       nesi99991
#SBATCH --job-name      af3
#SBATCH --time          02:00:00
#SBATCH --mem           24G
#SBATCH --cpus-per-task 8
#SBATCH --gpus-per-node A100:1
#SBATCH --output        %j.out

module purge
module load AlphaFold/3.0.2
module load AlphaFold3DB/2024-12
module load HMMER/3.4-GCC-12.3.0

run_alphafold.py \
  --json_path=/nesi/project/nesi99991/af3/fold_input.json \
  --model_dir=/nesi/project/nesi99991/af3/models \
  --output_dir=/nesi/project/nesi99991/af3/results \
  --db_dir=${AF3DB} \
  --uniref90_database_path=${AF3DB}/uniref90_2022_05.fa \
  --mgnify_database_path=${AF3DB}/mgy_clusters_2022_05.fa \
  --uniprot_cluster_annot_database_path=${AF3DB}/uniprot_all_2021_04.fa \
  --small_bfd_database_path=${AF3DB}/bfd-first_non_consensus_sequences.fasta \
  --pdb_database_path=${AF3DB}/mmcif_files \
  --seqres_database_path=${AF3DB}/pdb_seqres_2022_09_28.fasta \
  --hmmalign_binary_path=${HMMER_DIR}/hmmalign \
  --hmmbuild_binary_path=${HMMER_DIR}/hmmbuild \
  --hmmsearch_binary_path=${HMMER_DIR}/hmmsearch \
  --jackhmmer_binary_path=${HMMER_DIR}/jackhmmer \
  --nhmmer_binary_path=${HMMER_DIR}/nhmmer
```

For several inputs, use `--input_dir=/path/to/json_dir` instead of `--json_path`, or run one job per file (e.g. a job array).

### AlphaFold 3 tuning and troubleshooting

- To keep a GPU from sitting idle during the CPU search, split the stages: a CPU-only job with `--norun_inference` produces an enriched JSON (with MSAs), then a GPU job with `--norun_data_pipeline` runs inference on it.
- Default config fits ~5,120 tokens on an 80 GB GPU. For larger complexes or inference OOM, enable unified memory:

    ```bash
    export XLA_PYTHON_CLIENT_PREALLOCATE=true
    export XLA_PYTHON_CLIENT_MEM_FRACTION=0.95
    export XLA_CLIENT_MEM_FRACTION=0.95
    ```

- If the data-pipeline stage is killed, increase `--mem` (it is memory-hungry for large sequences).

## Resource sizing

The values above target small proteins (~100 residues, e.g. 3RGK). Scale `--mem` and `--time` with sequence length:

| Sequence length | Mem | GPU | Time |
| --- | --- | --- | --- |
| ~100 aa monomer | 24 GB | A100:1 | 2 h |
| ~500 aa monomer | 30 GB | A100:1 | 4-6 h |
| ~1500 aa monomer | 60 GB+ | A100:1 (80 GB) | 8-12 h |
| Multimer (total ~1000 aa) | 30 GB | A100:1 | 2-4 h |
| Large multimer | 60 GB+ | A100:1 (80 GB) | 6-12 h |

If you exceed L4 / 40 GB A100 VRAM, request `milan` partition for the 80 GB A100:

```sl
#SBATCH --partition     milan
#SBATCH --gpus-per-node A100:1
```

## Troubleshooting

### "RuntimeError: Resource exhausted: Out of memory"

Enable TensorFlow unified memory and reduce JAX's GPU memory fraction.

Module-based:

```bash
export TF_FORCE_UNIFIED_MEMORY=1
export XLA_PYTHON_CLIENT_MEM_FRACTION=4.0
```

Singularity-based (prefix `SINGULARITYENV_` so the var passes through):

```bash
export SINGULARITYENV_TF_FORCE_UNIFIED_MEMORY=1
export SINGULARITYENV_XLA_PYTHON_CLIENT_MEM_FRACTION=4.0
```

### Hangs at MSA search

CPU-bound stage (HHsearch/Jackhmmer). Increase `--cpus-per-task` to 8-16. Most of the GPU time is later in the structure-relaxation step.

### MSA cached but template search slow

`max_template_date` excludes templates after the date, use a recent date for best results unless you specifically want a benchmark cutoff.

## Upstream

- <https://github.com/deepmind/alphafold>
- <https://nesi.github.io/alphafold2-on-mahuika/>
