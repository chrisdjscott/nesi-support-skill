# AGENTS.md

Guidance for agents who maintain or extend this skill.

## What this repo is

A Claude Code / Agent SDK skill that teaches an agent how to use NeSI's Mahuika HPC cluster (operated by REANNZ since 2025). It is a **condensed, progressive-disclosure** rewrite of the public NeSI support docs, not a mirror.

- `SKILL.md` is the entry point. Loaded eagerly by the agent runtime.
- `references/` holds topic files loaded on demand when the user's question lands in that area.
- `support-docs/` is a git submodule pinned to <https://github.com/nesi/support-docs> (the upstream MkDocs site). Treat it as the **source of truth** when reconciling facts.

## Repository layout

```
.
├── SKILL.md                     # Eager-loaded entry point (keep small)
├── README.md                    # One-liner for humans browsing GitHub
├── AGENTS.md                    # This file
├── .gitmodules                  # Pins support-docs submodule
├── references/
│   ├── access-and-login.md
│   ├── containers.md
│   ├── debugging-efficiency.md
│   ├── filesystems.md
│   ├── hardware.md
│   ├── modules.md
│   ├── parallel-computing.md
│   ├── slurm.md
│   ├── slurm-examples.md
│   └── software/
│       ├── index.md             # Categorised table of all 55 per-app files
│       └── <package>.md         # One file per centrally-installed package
└── support-docs/                # Submodule, do not edit in place
    └── docs/
        ├── Getting_Started/
        ├── Batch_Computing/
        ├── Storage/
        ├── Software/
        │   ├── Available_Applications/   # Upstream per-package pages
        │   ├── Parallel_Computing/
        │   ├── Containers/
        │   └── Profiling_and_Debugging/
        ├── Data_Transfer/
        ├── Interactive_Computing/
        ├── Service_Subscriptions/
        ├── Policy/
        └── Tutorials/
```

## How the skill is meant to be used by the runtime

1. The runtime always sees `SKILL.md`. Its frontmatter `description` is what the model uses to decide whether to engage the skill, so wording there is load-bearing.
2. `SKILL.md` lists every reference file with a one-line "Load for" hint. The model reads only the files relevant to the current question.
3. For per-application questions, the model is told to load `references/software/index.md` first, then the specific `software/<package>.md`.

Keep this layered model intact. Do not collapse references back into `SKILL.md`, and do not bloat `SKILL.md` with content that belongs in a reference.

## Source-of-truth mapping

Each `references/*.md` corresponds to a section of `support-docs/docs/`. When updating, read the upstream page first, then condense.

| Skill file | Upstream area (under `support-docs/docs/`) |
| --- | --- |
| `references/access-and-login.md` | `Getting_Started/Accessing_the_HPCs_-_NeSI_Mahuika/` |
| `references/slurm.md` | `Batch_Computing/Slurm/`, `Batch_Computing/Reference/` |
| `references/slurm-examples.md` | `Batch_Computing/Recipes/`, job array and GPU pages |
| `references/hardware.md` | `Batch_Computing/Hardware/`, partition and GPU pages |
| `references/filesystems.md` | `Storage/File_Systems_and_Quotas/`, `Long_Term_Storage/` |
| `references/modules.md` | `Software/` top-level Lmod and EasyBuild pages |
| `references/parallel-computing.md` | `Software/Parallel_Computing/` |
| `references/containers.md` | `Software/Containers/` (Apptainer) |
| `references/debugging-efficiency.md` | `Software/Profiling_and_Debugging/` |
| `references/software/<package>.md` | `Software/Available_Applications/<Package>.md` |

Filenames in `references/software/` are lower-case ASCII (e.g. `gromacs.md`, `cp2k.md`, `tensorflow_gpu.md`). Upstream uses mixed case (e.g. `GROMACS.md`, `TensorFlow_on_GPGPUs.md`). When adding a new package, use the lower-case form and underscores for spaces.

## Style rules for content

These are non-negotiable. The agent that consumes this skill is token-sensitive.

- **British English** spelling (specialise, behaviour, optimise).
- **No em dashes**, no en dashes, no spaced hyphens used as sentence interrupters. Use periods, commas, or parentheses.
- **No flowery language**, no "I'd be happy to", no "Great question!". Direct and technical only.
- **No emojis**, no decorative Unicode, no callout boxes copied from MkDocs (`!!! note` etc.). Translate them to plain prose or drop them.
- **Terse over verbose**. The upstream docs target newcomers; this skill targets an agent that already knows Slurm exists. Drop introductory paragraphs, marketing, and screenshots.
- **No comments in code blocks** unless the comment carries information the surrounding prose does not.
- **Absolute paths** on Mahuika unless `~/` is meaningful.
- **Example project code is `nesi99991`** everywhere. Example username is `<username>`. Do not invent other placeholders.

## Frontmatter rules for `SKILL.md`

```yaml
---
name: nesi-hpc
description: <single paragraph, ~50-80 words>
---
```

- `name` is stable. Do not rename without coordinating with whoever ships this skill.
- `description` is what the runtime matches against user prompts. It must mention: Mahuika, REANNZ/NeSI, Slurm, modules, GPU, the filesystem names, Apptainer, and the kinds of questions that should trigger loading (submit job, run software, request GPU, troubleshoot). If you add a new domain (e.g. workflow managers, Globus, Jupyter), extend the description so the runtime can match.
- Keep `description` to one paragraph. The runtime truncates aggressively.

Reference files (`references/**/*.md`) do not need frontmatter.

## Adding a new per-application reference

1. Read the upstream page: `support-docs/docs/Software/Available_Applications/<Package>.md`.
2. Create `references/software/<package>.md` (lower-case, underscores for spaces).
3. Structure: one-line summary, module name(s), minimum-viable batch script, package-specific gotchas (GPU support, licence restrictions, scratch directory needs), links to upstream only if a long worked example would bloat the file.
4. Add the package to `references/software/index.md` in the correct category table. Categories currently are: chemistry/MD/quantum, bioinformatics/structural/genomics, climate/earth/engineering, ML/AI, programming languages, workflow/utilities. If a new category is needed, add a new table heading and a one-line description.
5. Cross-reference from `SKILL.md` is not required for individual packages, only the `index.md` is named there.

## Updating an existing reference

1. `git -C support-docs pull` (or `git submodule update --remote support-docs`) to get latest upstream.
2. Diff the upstream page against the current reference. Most updates will be: version bumps, new partition names, changed quotas, new GPU types.
3. Preserve the layered structure (Quick orientation in `SKILL.md`, detail in `references/`). Do not move detail upward.
4. After editing, re-read `SKILL.md` to check the one-line "Load for" hint for that reference is still accurate.

## Updating the submodule pin

```bash
git submodule update --remote support-docs
git add support-docs
git commit -m "Bump support-docs submodule"
```

Do not commit changes made **inside** `support-docs/`. That tree is upstream-only.

## Things that drift and need watching

- **Operator name**: NeSI is now operated by REANNZ (transition in 2025). Older upstream pages may still say "NeSI" as the operator. The skill currently writes "NeSI's Mahuika HPC cluster (operated by REANNZ)". Keep that phrasing.
- **Login host**: `mahuika` via the `lander` jump host. Older docs reference `mahuika01`, `mahuika02`, or `ssh nesi`. Newer docs use `ssh mahuika`. Both still work for many users.
- **Partitions**: `milan` and `genoa` currently. The older `large` and `bigmem` partitions are gone. Do not reintroduce them.
- **GPU types**: A100 (80 GB and 40 GB), H100, L4. P100 was retired.
- **Filesystem quotas**: `/home` 20 GB, `/nesi/project` 100 GB soft / 110 GB hard, `/nesi/nobackup` 10 TB soft / 12 TB hard, `nobackup` auto-cleans files untouched for 90 days. Cross-check with `Storage/File_Systems_and_Quotas/` before changing.
- **Toolchains**: `foss-2023a`, `intel-2022a`, etc. Newer toolchains appear yearly. Update `references/modules.md` when EasyBuild rolls one out.
- **Example project code**: always `nesi99991`. Do not use real project codes.

## What not to add

- Account-management, billing, allocation-request, or governance workflows. Those belong in the upstream docs and route to `support@nesi.org.nz` or `my.nesi.org.nz`. The skill should say "ask NeSI support" rather than mirror policy text.
- Screenshots, GIFs, or any binary assets. The skill is text-only.
- Anything specific to one user's project, dataset, or pipeline.
- MkDocs-specific markup (`!!! tip`, `=== "Tab"`, snippet includes). Translate to plain Markdown.
- Tutorials. The skill is reference, not pedagogy. If a tutorial is essential, link to the upstream page instead of inlining.

## Sanity checks before committing

- `SKILL.md` is still under ~100 lines.
- Every file under `references/` is referenced from either `SKILL.md` or `references/software/index.md`.
- `references/software/index.md` lists every file in `references/software/` (except itself).
- No em dashes anywhere (`grep -nP "—|–| - " references/ SKILL.md`).
- No US spellings introduced (`grep -nE "specialize|behavior|optimize|color\b|center\b" references/ SKILL.md` and review).
- Example project code is `nesi99991`, not a real code.

## When in doubt

The upstream is authoritative. If `support-docs/` and a `references/*.md` disagree, the upstream wins and the reference needs updating. If the upstream is silent and you cannot verify a fact, write "check `module spider <name>`" or "see <https://docs.nesi.org.nz/>" rather than guess.
