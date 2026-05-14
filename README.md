# nesi-support-skill

Agent skill for running workloads on NeSI's Mahuika HPC cluster (operated by REANNZ). Condensed from the public [nesi/support-docs](https://github.com/nesi/support-docs).

Covers SSH access, Slurm job submission, the Lmod module system, filesystems (`/home`, `/nesi/project`, `/nesi/nobackup`), GPU usage, MPI/OpenMP, Apptainer containers, debugging job efficiency, and per-application guides for 55 supported scientific packages.

## What gets shipped

Only two paths are part of the skill itself:

- `SKILL.md`
- `references/`

Everything else (`support-docs/`, `AGENTS.md`, this README) is for maintenance and is not loaded by the agent.

## Install

Drop `SKILL.md` and `references/` into the skills directory your agent reads from. Common locations:

| Agent / runtime | Target |
| --- | --- |
| Claude Code, project scope | `.claude/skills/nesi-hpc/` |
| Claude Code, user scope | `~/.claude/skills/nesi-hpc/` |
| Supported by many agents, project scope | `.agents/skills/nesi-hpc/` |

Pick one and copy:

```bash
git clone https://github.com/<org>/nesi-support-skill.git
mkdir -p ~/.claude/skills/nesi-hpc
cp -r nesi-support-skill/SKILL.md nesi-support-skill/references ~/.claude/skills/nesi-hpc/
```

Or symlink during development so edits in the repo show up immediately:

```bash
ln -s "$PWD/nesi-support-skill/SKILL.md"   ~/.claude/skills/nesi-hpc/SKILL.md
ln -s "$PWD/nesi-support-skill/references" ~/.claude/skills/nesi-hpc/references
```

The directory name under `skills/` is arbitrary, but `nesi-hpc` matches the `name:` in `SKILL.md` frontmatter and is the easiest to recognise later.

## Updating from upstream

The `support-docs/` git submodule is the source of truth.

```bash
git submodule update --init --recursive          # first time
git submodule update --remote support-docs       # pull latest upstream
```

Then reconcile any drift into `references/` and `SKILL.md`. See `AGENTS.md` for the mapping between upstream pages and skill files.

## Triggering

The skill activates when a user asks an agent about Mahuika, NeSI, Slurm jobs, modules, GPUs on the cluster, or any of the 55 indexed scientific packages. See the `description:` field in `SKILL.md` for the exact match surface.

## License

Content is derived from [nesi/support-docs](https://github.com/nesi/support-docs); refer to that repository for upstream licensing.
