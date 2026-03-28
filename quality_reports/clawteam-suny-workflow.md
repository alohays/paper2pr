# ClawTeam Workflow Guide for paper2pr

This guide explains how to use ClawTeam to coordinate parallel AI agents during the SUNY presentation review and QA workflow.

---

## What is ClawTeam

ClawTeam is a multi-agent coordination CLI that spawns AI agents (Claude Code instances) in tmux panes, assigns each agent an initial task prompt, and provides inter-agent messaging and task tracking. Agents run in isolated git worktrees so they cannot interfere with each other's working state. You monitor all agents from a shared kanban board, send them messages mid-run, and check their completion status without leaving the terminal. ClawTeam is installed via `uv tool install clawteam` from https://github.com/HKUDS/ClawTeam.

---

## Prerequisites

1. **ClawTeam installed**

   ```bash
   clawteam --version
   # Expected: clawteam v0.2.0 (or higher)
   ```

2. **tmux installed**

   ```bash
   tmux -V
   # Expected: tmux 3.x or higher
   ```

3. **Bash permission for clawteam** — ClawTeam commands must be allowed in `.claude/settings.json`. This file is protected and requires a manual edit. Add `"clawteam *"` to the `allowedTools` list under `Bash`:

   ```json
   {
     "permissions": {
       "allow": [
         "Bash(clawteam *)"
       ]
     }
   }
   ```

4. **Basic config already set** (run once after install):

   ```bash
   clawteam config set user "yunsung"
   clawteam config set default_backend tmux
   clawteam config set transport file
   ```

---

## Ad-Hoc Agent Spawning for SUNY Workflow

Each `clawteam spawn` call launches one Claude Code agent in a new tmux window, assigns it a team name (`-t`), an agent name (`-n`), and an initial task prompt (`--task`). Agents are automatically isolated in git worktrees so they work on separate copies of the repository.

**Spawn a visual audit agent:**

```bash
clawteam spawn claude -t suny-review -n auditor --task "Run visual audit on Slides/SUNY.tex checking for overflow, font consistency, and layout issues"
```

**Spawn a proofreading agent:**

```bash
clawteam spawn claude -t suny-review -n proofer --task "Run proofreading check on Slides/SUNY.tex for grammar, typos, and consistency"
```

**Spawn parallel QA agents (Beamer + Quarto simultaneously):**

```bash
clawteam spawn claude -t suny-qa -n beamer-checker --task "Compile and verify Slides/SUNY.tex with 3-pass XeLaTeX"
clawteam spawn claude -t suny-qa -n quarto-checker --task "Render and verify Quarto/SUNY.qmd"
```

Both agents start immediately and run in parallel. The kanban board (see below) shows their progress.

---

## Team Coordination

Once agents are running, use these commands to monitor and communicate with them.

**View current team state (snapshot):**

```bash
clawteam board show <team>
```

**Live auto-refreshing dashboard (Ctrl+C to stop):**

```bash
clawteam board live <team>
```

**Attach to tmux session with all agent windows tiled side by side:**

```bash
clawteam board attach <team>
```

**Send a message to a specific agent:**

```bash
clawteam inbox send <team> <agent> "message"
# Example:
clawteam inbox send suny-review auditor "Focus only on slide 12 onwards"
```

**Broadcast a message to all agents in a team:**

```bash
clawteam inbox broadcast <team> "message"
# Example:
clawteam inbox broadcast suny-review "Ignore the appendix slides"
```

**List all tasks and their status:**

```bash
clawteam task list <team>
```

**Check which agents are active:**

```bash
clawteam team status <team>
```

**Wait until all tasks in a team finish (blocks):**

```bash
clawteam task wait <team>
```

---

## Example Workflow: Pre-PR Quality Sweep

This workflow runs three review agents in parallel before opening a pull request, collects their reports, then cleans up.

```bash
# 1. Create a review team with 3 parallel agents
clawteam spawn claude -t pre-pr -n visual --task "Run /visual-audit on Slides/SUNY.tex and report findings"
clawteam spawn claude -t pre-pr -n pedagogy --task "Run /pedagogy-review on Slides/SUNY.tex and report findings"
clawteam spawn claude -t pre-pr -n proofreader --task "Run /proofread on Slides/SUNY.tex and report findings"

# 2. Monitor progress (auto-refreshes; Ctrl+C to exit)
clawteam board live pre-pr

# 3. Check completed tasks and their output
clawteam task list pre-pr

# 4. Clean up when done
clawteam team cleanup pre-pr
```

After cleanup, review any findings the agents wrote to their worktrees or printed to the board, then apply fixes manually to the main working tree before committing.

---

## Limitations (v0.2.0)

- **No `prompt_file` support in TOML templates** — agent prompts must be passed inline via `--task`. Deep template integration with project-specific instructions is deferred to a future release.
- **No automatic project context inheritance** — spawned agents work in isolated git worktrees. Launch `clawteam spawn` from inside the project directory so agents pick up `.claude/` rules and `AGENTS.md` automatically via the worktree copy.
- **File-based transport only by default** — peer-to-peer inter-agent messaging requires the optional `pyzmq` dependency (`pip install pyzmq`). The default file transport works without it.
- **Pre-1.0 software** — CLI flags and the TOML template schema may change between minor versions. Pin a version if stability is critical: `uv tool install clawteam==0.2.0`.

---

## Quick Reference

| Command | Description |
|---|---|
| `clawteam spawn claude -t <team> -n <name> --task "<prompt>"` | Spawn a new agent in a tmux window |
| `clawteam board show <team>` | Kanban snapshot for a team |
| `clawteam board live <team>` | Auto-refreshing kanban dashboard |
| `clawteam board attach <team>` | Tile all agent tmux windows side by side |
| `clawteam inbox send <team> <agent> "<msg>"` | Send message to one agent |
| `clawteam inbox broadcast <team> "<msg>"` | Broadcast message to all agents |
| `clawteam inbox peek <team>` | Peek at messages without consuming them |
| `clawteam task list <team>` | List all tasks and statuses |
| `clawteam task wait <team>` | Block until all tasks complete |
| `clawteam team status <team>` | Show active agents in a team |
| `clawteam team discover` | List all known teams |
| `clawteam team cleanup <team>` | Delete team and all its data |
| `clawteam team snapshot <team>` | Save a snapshot of full team state |
