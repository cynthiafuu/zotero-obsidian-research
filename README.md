# zotero-obsidian-research

A literature workflow for empirical accounting/finance PhD work: Zotero holds
the papers and highlights, Obsidian holds the thinking, and a handful of
scripts connect the two.

> **Status: assembled September 2026, not yet battle-tested.** This has run
> end-to-end on one real library, but it hasn't been used over a full reading
> cycle (months, hundreds of papers, actual paper-writing). Treat it as a
> working draft, not a mature tool. See "Verified / not verified" below for
> specifics.

## What problem this solves

Zotero is good at storing papers and highlights; it is not a place to think.
Obsidian is good for thinking and linking ideas; it is a bad place to store
PDFs and annotations, and re-typing highlights into notes by hand doesn't
scale past a few dozen papers. This repo's scripts pull structured data
(citekeys, dates, highlight colors, annotation text) out of Zotero's local
API and push it into an Obsidian vault as frontmatter and markdown, so the
literature note is where you actually write your judgment about a paper, not
where you re-transcribe it.

## Architecture

```
Zotero (papers, annotations)
        │  local API, read-only, http://127.0.0.1:23119
        ▼
Scripts (this repo)
        │  citekey / date / color / comment extraction
        ▼
Obsidian vault (10-Literature/, frontmatter, prompts)
```

Zotero is the system of record for papers and raw highlights. The vault is
the system of record for your own notes, ratings, and gaps. The scripts are
a one-way bridge from the former to the latter — they read Zotero and write
(or dry-run) into the vault; nothing here writes back into Zotero.

## Five-color highlight convention

| Color | Hex | Meaning |
|---|---|---|
| Yellow | `#ffd400` | Key finding |
| Red | `#ff6666` | Identification strategy |
| Green | `#5fb236` | Reusable method |
| Blue | `#2ea8e5` | Institutional background |
| Purple | `#a28ae5` | Your own doubt / disagreement |

Purple is the important one and the reason `export_purple.py` exists: it's
not "this seems important," it's "I don't buy this, or I don't understand
it yet." **A purple highlight without a comment is close to useless** — six
months later you will remember that you flagged something, not what your
objection was. The scripts don't enforce this (Zotero doesn't have a way to
require a comment on a highlight), so it's a discipline you have to keep
yourself: no bare purple highlights.

## Quick start

1. Install [Zotero](https://www.zotero.org/) and the
   [Better BibTeX](https://retorque.re/zotero-better-bibtex/) plugin (for
   stable citekeys), and the ZotFlow community plugin in Obsidian for the
   Zotero-to-vault sync. In Zotero, enable the local API under
   Settings → Advanced.
2. Build the vault skeleton:
   ```bash
   bash setup_vault.sh ~/Documents/research
   ```
   Safe to re-run — it won't overwrite files that already exist.
3. With Zotero running, verify the scripts' assumptions hold against your
   own library before trusting them with real data:
   ```bash
   cd ~/Documents/research/70-Meta/scripts
   python3 verify_setup.py
   ```
   This is read-only — it imports and exercises the real functions in
   `export_purple.py` against your actual Zotero data, but never writes
   anything.

## Scripts

| Script | What it does | Zotero writes? |
|---|---|---|
| `setup_vault.sh` | Creates the vault folder structure, templates, prompts, and copies the scripts in. Idempotent. | No — doesn't touch Zotero at all |
| `scripts/zotero_probe.py` | Probes the local API to confirm field names, color codes, and date formats before you rely on them. | No, read-only |
| `scripts/export_purple.py` | Exports all highlights of a given color (default purple), grouped by paper, to markdown. | No, read-only |
| `scripts/verify_setup.py` | Runs the real functions from `export_purple.py` against your live library and reports pass/fail per assumption. | No, fully read-only, writes nothing anywhere |
| `scripts/backup_zotero.sh` | Tars up `~/Zotero` after checking Zotero is closed (a backup taken while it's running can be silently corrupt), warns if the output looks too small, and prunes backups older than 90 days (keeps the last 3). | Reads `~/Zotero`, never writes into it; writes the archive elsewhere |

## Verified / not verified

**Verified**, on my own machine and one real Zotero library (673 items):

- `setup_vault.sh` end-to-end and idempotent (running it twice does not
  duplicate or overwrite anything)
- `export_purple.py`: color filtering, and the two-level
  annotation → attachment → parent-item resolution
- `verify_setup.py`: 15 of 15 checks passing against that 673-item library

**Not verified**:

- Zotero 10 compatibility — as of this writing, Better BibTeX (up to v9.0.63)
  still only declares support for Zotero 8 / 9 beta, so this hasn't been
  tried against Zotero 10 at all

## Known limitations

- ZotFlow is an active but young third-party plugin; its behavior (path
  templates, sync semantics) may change between versions.
- The local API is read-only. Anything that needs to change Zotero's own
  metadata (titles, tags, collections) still has to be done by hand in
  Zotero — nothing here writes back into it.
