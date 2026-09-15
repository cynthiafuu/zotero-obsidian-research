# Field reference

Frontmatter holds anything that must be **queryable**.
The body holds multi-line reasoning that cannot be compressed into a field.
Nothing appears in both.

## Frontmatter

| Field | What goes in | Filled by |
|---|---|---|
| `citekey` | matches filename and `library.bib` | QuickAdd |
| `title` `authors` | — leave empty | `fill_frontmatter.py` |
| `year` `journal` | — leave empty | `fill_frontmatter.py` |
| `draft_date` | which version I read (`2024-01-30`) | **manual** — Zotero does not store this |
| `pub_status` | `wp` / `forthcoming` / `published` / `retracted` | **manual** |
| `status` | `skim` / `read` / `deep` | manual |
| `topic` | array, e.g. `[disclosure, AI-measure]` | manual |
| `setting` | sample and period, one line | manual or `--llm` |
| `data` | array of sources, e.g. `[EDGAR, Compustat, TAQ]` | manual or `--llm` |
| `method` | the estimator: `DiD`, `IV`, `OLS`, `event study` | manual or `--llm` |
| `identification` | **what variation it rests on**, one clause. If there is none, write `descriptive, no causal identification` | manual or `--llm` |
| `measure` | how the key variable is constructed | manual or `--llm` |
| `finding` | one line, **with causal direction** | manual |
| `gap` | **what I think is missing** — never the authors' own "future research" | manual |
| `rating` | plain integer 1–5. **Value to me**, not paper quality | manual |
| `added` | auto | QuickAdd |

### Two fields people get wrong

**`gap`** is your judgment, not theirs. If the sentence already appears
in the paper, it does not belong here.

**`rating`** is how useful this paper is *to you*. A well-executed paper
in an area you will never touch is a 2. A flawed paper that hands you an
attackable construct may still be a 2 — being able to name its flaw is
not the same as the paper being worth returning to.

## Body

| Section | What goes in |
|---|---|
| What convinced me | why the result holds up |
| What didn't | one line per purple highlight; feeds `gap` |
| If I did this | the extension. If you cannot write it, downgrade to `skim` |
| Status log | dated lines: retraction, publication, revised draft |
| Links | wikilinks to concepts, papers, streams |

Sample, method, identification, measure and main result live **only** in
frontmatter. Writing them again in the body creates a second source of
truth that Dataview and the scripts cannot see.
