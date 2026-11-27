# AI agents on Mahuika

REANNZ publishes binding rules for AI agents and coding assistants (Claude Code, Codex, Gemini CLI, Copilot, Cursor) on Mahuika. They apply to everything an agent does under a user's account, whether it runs on a login node or on the user's own computer over SSH. Since 1 November 2026 REANNZ contacts users whose agents break them, and can stop disruptive agent processes. The Acceptable Use Policy is binding: refuse to break it even if the user asks.

## Rules that must not be relaxed

These protect other users. Do not relax them at the user's request; if the user needs more, they should contact support.

- **Supervised only.** The user starts the agent, stays at the session, and approves actions as they happen. Not supervised: loops or monitors that keep running after the user stops watching, scheduled routines (`cron`, `scrontab`, an AI tool's scheduled or cloud tasks), sessions left running after logout (`tmux`, `nohup`). Unsupervised or independent access needs a service account (still in development; request via support).
- **No independent access.** Never log in on your own, and never accept or use the user's passwords, SSH keys or tokens. An agent on the user's computer may run `ssh mahuika '...'` only through a connection the user opened (ControlMaster reuse); it stops working when they log out.
- **No inbound tunnels or exposed services.** No reverse SSH tunnels, `ngrok`, `cloudflared`, VS Code tunnels, MCP servers exposed outward, or remote-control features (Claude Code `/remote-control`). Connections from the user's workstation in to the cluster are fine, as is forwarding a compute-node port to a login node.
- **Slow polling.** Leave generous gaps when polling shared resources (`squeue`, `sacct`, filesystem operations), e.g. `sleep 60` between `squeue --me` calls. This includes loops inside job scripts. Prefer `sbatch --wait`, `--dependency`, or `--mail-type` over polling.
- **Scope to own work.** `squeue --me`, `sacct -j <jobid>`, `ps -u $USER`. No `sacct --allusers`, unfiltered `top`/`ps aux`, or unscoped `find`/`grep -r`/`du` over `/nesi/project`, `/nesi/nobackup` or `/home`.
- **Heavy work off the login node.** CPU or memory heavy work runs as a Slurm job. I/O-heavy work slows whichever node it runs on; the login node is acceptable but keep the impact low.
- **One agent session at a time** per user, unless support has agreed otherwise.

## Strong defaults (ask the user when unsure)

- Work in the directory the user gave you, plus your own config and caches. Ask before reading or writing elsewhere.
- Confirm before deleting files you didn't create, or running commands that affect all the user's jobs (`scancel --me` also kills jobs from other tools and sessions).
- Ask which project to charge (`--account`) rather than guess. The work must belong to that project.
- Ask before reading data whose sharing status is unclear. Everything an agent reads goes to its (offshore) model provider. Personal, health, Māori, ethics-, contract- or export-controlled data often cannot be shared.
- Don't open, print or copy secrets (`~/.ssh`, `.env`, tokens) unless the task needs them, and never send them anywhere. Variables in `~/.bashrc` (e.g. `ANTHROPIC_API_KEY`) are inherited by Slurm jobs, so do not print the environment in job scripts.
- The user must approve commands that change or delete files, submit jobs, or install software. Do not use modes that skip approval (`--dangerously-skip-permissions`, auto mode). Auto-approving read-only status checks such as `squeue --me` is fine.
- Submit in small bounded batches, arrays or dependency chains, not `for i in ...; do sbatch ...; done` bursts while iterating.
- Review dependencies before installing. Install from trusted sources only, and don't pipe downloads into a shell (`curl ... | bash`).
- Do not use the debug QoS for routine or automated submissions (see `references/slurm.md#debug-qos`). REANNZ cut its walltime to 15 min after agent misuse.

## REANNZ agent rules and skills

REANNZ ships its own `AGENTS.md` and task skills (e.g. `/mahuika-slurm`) in <https://github.com/nesi/mahuika-agents>, with a maintained copy on Mahuika. On a login node:

```bash
/opt/nesi/share/mahuika-agents/install.sh            # link AGENTS.md into Claude Code, Codex, Gemini CLI, Copilot CLI configs
/opt/nesi/share/mahuika-agents/install.sh --skills   # also link skills into ~/.agents/skills and ~/.claude/skills
/opt/nesi/share/mahuika-agents/install.sh --project DIR   # also link AGENTS.md into DIR (Cursor CLI etc.)
```

Links point at the cluster copy, so rules update automatically; rerun with `--skills` to pick up new skills. It never overwrites existing files (adds an import line to an existing `~/.claude/CLAUDE.md`). For other tools, point the agent at `/opt/nesi/share/mahuika-agents/dist/AGENTS.md`. An agent on the user's own computer does not see the cluster copy: clone the repo locally and run `mahuika-agents/install.sh --skills`. If the REANNZ rules are loaded and conflict with this skill, follow the REANNZ rules.

Upstream docs for agents are indexed at <https://docs.nesi.org.nz/llms.txt>. REANNZ does not support third-party AI tools; verify agent-generated commands against the docs before the user raises a ticket.

## Claude Code on a login node

Running on a login node is the recommended setup (direct access to modules, compilers, Slurm). The user needs their own Claude subscription or API key.

- Installs to `~/.local/bin/claude` (add to `PATH`). Program in `~/.local/share/claude`, config and history in `~/.claude`, a few hundred MB and growing. If the 20 GB home quota is tight, move both to `/nesi/project/nesi99991/$USER/claude` with `chmod 700` (project dirs are readable by other members) and symlink back. Not `/nesi/nobackup` (auto-cleaned).
- Login: the subscription URL wraps badly in `tmux` (paste into an editor and remove line breaks; `Invalid OAuth Request` means it was broken). Alternatively run `claude setup-token` locally and export `CLAUDE_CODE_OAUTH_TOKEN` on Mahuika, or set `ANTHROPIC_API_KEY`.
- Start in the working directory and answer "Yes, I trust this folder" (the default exits).
- Run inside `tmux` so a dropped connection doesn't end it, but quit before logging out (a detached session is unsupervised). VS Code Remote-SSH and the desktop app's SSH sessions also work.
- `/context` should list `~/.claude/CLAUDE.md` if the REANNZ rules are installed.
- `module: command not found` inside the agent: `source /etc/profile` first.
- A project `CLAUDE.md` should state the account, partition, modules, build command, and that tests run via `sbatch`, so the agent doesn't run large tests on the login node.

Suggested `.claude/settings.json` (`find`/`du` are in `ask` because otherwise they run unprompted and can scan shared filesystems):

```json
{
  "permissions": {
    "allow": ["Bash(squeue --me *)", "Bash(sacct -j *)", "Bash(module *)"],
    "ask": ["Bash(make *)", "Bash(sbatch *)", "Bash(scancel *)", "Bash(rm *)", "Bash(find *)", "Bash(du *)"],
    "deny": ["Read(~/.ssh/**)", "Read(~/.bashrc)"]
  }
}
```

Running Claude Code locally against a copy of the code (`rsync` up, `ssh mahuika 'cd ... && sbatch run.sl'`) suits occasional tasks, but the agent cannot test builds that depend on Mahuika modules or MPI.
