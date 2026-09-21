# Fed-ZoomSIB — Federated Single-Index Bandits

**CS6007: Multi-Agent Machine Learning · IIT Bombay · Prof. Avishek Ghosh**

Cooperative contextual bandits in which **neither the index direction `θ*` nor the reward
link function `f` is known**, and agents must learn both while sharing very little.

```
y_{i,t} = f( <x_{i,t}, θ*> ) + η_{i,t}        f unknown, non-monotone, θ* unknown
```

---

## What this project is

**Single-index bandits** (Kang et al., ICLR 2026) drop the standard assumption that the
link function is known — an assumption whose violation causes *linear* regret, not graceful
degradation. **ZoomSIB-UCB** (Dey, Bhore & Ghosh, 2026) settles the single-agent question
with a matching `Θ̃(T^{2/3})` upper and lower bound for general non-monotone links.

Nobody has studied the **multi-agent** version. That gap is this project:

> What does collaboration buy in a single-index bandit, and at what communication cost?

The structure of ZoomSIB-UCB makes the question unusually clean. It has two phases that
share by *different mechanisms*:

- **Phase 1** estimates `θ*` with a truncated **Stein estimator** — which is a *sample
  mean*, so averaging across agents is algebraically identical to the centralized
  estimator on pooled data. Exact pooling, one message of `d` numbers.
- **Phase 2** runs a *sleeping* UCB over `O(T^{1/3})` bins of the projected index line,
  whose entire state is two scalars per bin. Cheap to share, but the pooling is statistical.

Whether those two mechanisms pay off differently is the project's central question.

See [docs/01-literature-and-problem.md](docs/01-literature-and-problem.md) for the papers
and the formal problem, and [docs/02-roadmap.md](docs/02-roadmap.md) for the baseline and
the planned improvements.

---

## Status

| Phase | Content | State |
|---|---|---|
| 0 | Project pitch (5 min) | deck builds; **needs names + roll numbers** |
| **1** | **Single-agent baseline and reproduction** | **complete** — [results](docs/03-phase1-results.md) |
| 2–5 | Federated Phase 1, cooperative Phase 2, communication ablations, one extension | not started |

Everything implemented so far is **reproduction**, not contribution: it is the measuring
stick against which "collaboration buys you X" will later be evaluated.

### Headline Phase-1 numbers

Final regret at `T = 20 000`, `d = 10`, `K = 20`, 20 trials (lower is better):

| | quadratic | asymmetric | zigzag | logistic *(monotone)* |
|---|---:|---:|---:|---:|
| **ZoomSIB-UCB** | **2657** | **1371** | **1358** | 906 |
| GSTOR | 10593 | 2325 | 7701 | 1910 |
| ESTOR | 21267 | 6304 | 2918 | 708 |
| IGP-UCB | 8510 | 7274 | 6642 | 5175 |
| LinUCB | 17865 | 5190 | 1063 | **127** |

- The Stein estimator converges at **exactly `n^{-1/2}`** (fitted −0.496…−0.501 over `d ∈ {5,10,20,40}`).
- Adaptive stopping exits Phase 1 at **1.67 %** of the horizon on the quadratic link,
  matching the ~1.8 % Dey et al. report; the measured optimum is ~2 %.
- ZoomSIB-UCB's fitted regret exponent is **0.294** on quadratic — close to the `T^{1/3}`
  that Corollary 4.8 predicts for a link with a unique well-separated maximum — and 0.602
  on the flattest link, approaching the `2/3` worst case.
- ESTOR, which assumes monotonicity, is *worse than LinUCB* on the quadratic link and best
  on the monotone one — the assumption made visible.

Full tables, figures and caveats: [docs/03-phase1-results.md](docs/03-phase1-results.md).

---

## Quick start

Requires Python ≥ 3.10 with **numpy** and **matplotlib** only (no scipy, no torch).

Wall-clock times are for a 12-core machine:

```bash
python experiments/exp01_stein_rate.py        # Stein convergence rate         ~1 min
python experiments/exp02_regret_curves.py     # main regret comparison         ~6 min
python experiments/exp03_loglog_slope.py      # log-log slopes (reuses exp02)  instant
python experiments/exp04_dim_scaling.py       # regret vs dimension           ~10 min
python experiments/exp05_explore_tradeoff.py  # Phase-1 exploration sweep     ~45 min
```

Figures are written to `results/` as both `.pdf` (for the deck) and `.png`.
exp02 and exp04 parallelise over trials with `ProcessPoolExecutor` (BLAS is pinned to one
thread per worker to avoid oversubscription); pass `workers=1` to `run_sweep` to debug
serially. **exp05 runs serially** and is the slowest.

exp03 needs no simulation — it reads exp02's cached arrays. exp04 and exp05 cache their
own results, so figures can be restyled without re-simulating:

```bash
python experiments/exp04_dim_scaling.py --replot
python experiments/exp05_explore_tradeoff.py --replot
```

The reference papers live in `papers/` (tracked). To re-download them:

```bash
python experiments/fetch_papers.py
```

Build the pitch deck:

```bash
cd slides/pitch && pdflatex main.tex
```

---

## Knowledge map

An interactive dependency graph of the seven reference papers plus this project's own
conjectures: **100 nodes** (assumptions, lemmas, theorems, algorithms, bounds, open
problems) joined by **165 typed edges**, 35 of which cross paper boundaries.

```bash
cd viz && python3 -m http.server 8000     # then open http://localhost:8000
node viz/tools/check.mjs                  # validate the data (schema, cycles, provenance)
node viz/tools/bake-layout.mjs            # re-bake positions after editing node data
```

Three views over the same data, because the x axis is **time in every one of them** --
switching modes only ever moves nodes vertically, so the chronology never reshuffles:

| View | Clusters are | Reading across a row |
|---|---|---|
| **Concept** (default) | the ten concept lanes | one idea evolving, 2017 → ours |
| **Timeline** | the eight papers | one paper's whole contribution |
| **Matrix** | concept × paper cells | the gap table, literally |

The collapsed Concept view is worth a look on its own: each lane is a full-width bar whose
shaded segments sit under exactly the papers that contributed to it, so the empty cells of
[`docs/01-literature-and-problem.md`](docs/01-literature-and-problem.md) §3 are visible at a
glance -- *Safety* is blank until Amani & Thrampoulidis 2021, *Index estimation* until Kang
et al. 2026.

Clicking a node opens its formal statement in LaTeX, its proof, the assumptions it consumes,
and a deep link into the source PDF at the right page. Cross-paper edges carry a prose
`note` saying **why** the relation holds -- those are the claims this project rests on. The
detail slider pulls in supporting lemmas; the search box expands whatever cluster hides a hit.

Authoring is plain `.js` under `viz/data/`, one file per paper plus `cross-edges.js`. Not
JSON: Chrome blocks `fetch()` of local files from a `file://` page, and `String.raw` lets
LaTeX be pasted verbatim from the source with no escaping. `viz/validate.js` runs on every
page load and reports dangling ids, cycles, misfiled edges and the proof-status census.

## Repository layout

```
src/
  envs.py        SIBEnv, link functions, score function S(x) = -grad log p(x)
  stein.py       truncated + l1-normalised Stein estimator
  zoomsib.py     ZoomSIB-UCB (Dey et al. Algorithm 1) + oracle-theta ablation
  baselines.py   Random, LinUCB, ESTOR, GSTOR, IGP-UCB
  base.py        algorithm interface and episode runner
  runner.py      parallel trial harness, CI helper, log-log slope fit
  plotting.py    shared figure styling

experiments/     one script per figure; seeds fixed
results/         generated figures (.npz caches are gitignored)
docs/            literature review, roadmap, Phase-1 results
slides/pitch/    5-minute pitch deck (LaTeX, course template)
papers/          reference PDFs (see fetch_papers.py)

viz/             interactive knowledge map (no build step, no npm install)
  data/          one .js per paper + cross-edges.js; hand-edited
  tools/         check.mjs (validate) · bake-layout.mjs · make-artifact.mjs
  vendor/        cytoscape, expand-collapse, KaTeX -- vendored for offline use
```

### Algorithms

| Key | Algorithm | Source |
|---|---|---|
| `zoomsib` | ZoomSIB-UCB | Dey, Bhore & Ghosh 2026 |
| `zoomsib_oracle` | ZoomSIB-UCB given the true `θ*` (ablation, not deployable) | — |
| `gstor` | Shape-agnostic explore-then-commit, kernel link estimate | Kang et al. ICLR 2026 |
| `estor` | Monotone-assuming Stein + greedy projection | Kang et al. ICLR 2026 |
| `igpucb` | GP-UCB on the full `d`-dimensional context | Chowdhury & Gopalan ICML 2017 |
| `linucb` | OFUL / LinUCB (misspecified here by construction) | Abbasi-Yadkori et al. 2011 |
| `random` | uniform arm choice | — |

`ESTOR` and `GSTOR` are our reimplementations following the templates in Kang et al.;
no reference code is public, so their exploration schedules use the rates that paper's
analysis prescribes, with the constants exposed as arguments.

---

## Two modelling decisions worth knowing

**The score function is assumed known.** Stein's identity needs `S(x) = -∇log p(x)`.
This assumption is inherited from the entire single-index-bandit literature; we state it
rather than hide it. Contexts are Gaussian throughout, so `S` is available in closed form.

**Contexts are scaled so the projected index has unit variance** (`index_scale=1.0`).
With `‖θ*‖₁ = 1` and plain standard-Gaussian contexts, the index `⟨x,θ*⟩` has standard
deviation `‖θ*‖₂ ≈ 0.36` at `d = 10` — a range on which the "non-monotone" links are
*effectively monotone*, so the benchmark would not test what it is meant to test. Details
and the measurement in [docs/03-phase1-results.md](docs/03-phase1-results.md).

---

## References

1. D. Dey, S. Bhore, A. Ghosh. *Optimal Regret for Single Index Bandits.* arXiv:2605.09454, 2026.
2. Y. Kang et al. *Single Index Bandits: Generalized Linear Contextual Bandits with Unknown Reward Functions.* ICLR 2026.
3. A. Dubey, A. Pentland. *Kernel Methods for Cooperative Multi-Agent Contextual Bandits.* ICML 2020.
4. S. Amani, C. Thrampoulidis. *Decentralized Multi-Agent Linear Bandits with Safety Constraints.* AAAI 2021.
5. S. Arya, S. Bhattacharjee, B. K. Sriperumbudur. *Kernel Single-Index Bandits.* arXiv:2603.18938, 2026.
6. S. R. Chowdhury, A. Gopalan. *On Kernelized Multi-armed Bandits.* ICML 2017.
7. A. Ghosh, J. Chung, D. Yin, K. Ramchandran. *An Efficient Framework for Clustered Federated Learning.* NeurIPS 2020.
8. A. Ghosh, S. R. Chowdhury, A. Gopalan. *Misspecified Linear Bandits.* AAAI 2017.
