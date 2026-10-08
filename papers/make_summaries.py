"""Generate one LaTeX summary (00-summary.tex) per papers/ subfolder.

    python3 papers/make_summaries.py
    cd papers/<folder> && latexmk -pdf 00-summary.tex && latexmk -c

Edit FOLDERS below to add a paper or move one between folders.
"""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parent

PRE = r"""\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{enumitem}
\usepackage{xcolor}
\usepackage[colorlinks=true,linkcolor=blue!50!black,urlcolor=blue!50!black]{hyperref}
\setlist{nosep,leftmargin=1.4em}
\newcommand{\stated}{\textcolor{green!40!black}{\textbf{Stated by the authors:}}}
\newcommand{\ours}{\textcolor{orange!80!black}{\textbf{Our reading:}}}
\usepackage{xurl}
\newcommand{\file}[1]{\url{#1}}
\sloppy
\setlength{\parindent}{0pt}\setlength{\parskip}{4pt}
"""


def doc(title, subtitle, intro, papers, cross):
    out = [PRE, r"\title{" + title + r"\\[2pt]\large " + subtitle + "}",
           r"\author{CS6007 project notes}", r"\date{October 2026}", r"\begin{document}",
           r"\maketitle", intro, r"\tableofcontents", r"\bigskip"]
    for p in papers:
        out.append(r"\section{" + p["short"] + "}")
        out.append(r"\textbf{" + p["cite"] + r"}\\ File: \file{" + p["file"] + "}")
        for key, head in (("setting", "Setting"), ("did", "What they did"),
                          ("results", "Main results"), ("us", "Why it matters for our project")):
            out.append(r"\paragraph{" + head + ".}")
            out.append(r"\begin{itemize}" + "".join(r"\item " + x for x in p[key]) + r"\end{itemize}")
        out.append(r"\paragraph{Open problems.}")
        items = [r"\item \stated{} " + x for x in p.get("stated", [])]
        items += [r"\item \ours{} " + x for x in p.get("ours", [])]
        out.append(r"\begin{itemize}" + "".join(items) + r"\end{itemize}")
    out.append(r"\section{Open problems across this folder}")
    out.append(r"\begin{itemize}" + "".join(r"\item " + x for x in cross) + r"\end{itemize}")
    out.append(r"\end{document}")
    return "\n".join(out)


FOLDERS = {}

# ------------------------------------------------------------------ 01
FOLDERS["01-single-index-bandits"] = dict(
    title="Single-Index Bandits",
    subtitle="Bandits whose reward is an unknown function of an unknown projection",
    intro=r"""\textbf{What this folder is about.} All five papers study rewards of the form
$y=f(\langle x,\theta^*\rangle)+\eta$ (or an extension) where \emph{both} the direction $\theta^*$ and
the link $f$ are unknown, so a linear or GLM bandit would be misspecified. They are all
\textbf{single-agent} (one is batched). Our whole project extends this line to many agents, so
this folder is our base: ZoomSIB-UCB is the algorithm we federate and decentralise.

\textbf{Common machinery.} Every paper estimates $\theta^*$ with a \emph{Stein-type} estimator: for
contexts with density $p$ and score $S(x)=-\nabla\log p(x)$, Stein's identity gives
$\mathbb{E}[y\,S(x)]=\mu^*\theta^*$ with $\mu^*=\mathbb{E}[f'(\langle x,\theta^*\rangle)]$. This needs
$\mu^*\neq 0$, an assumption that recurs below as an open problem.""",
    papers=[
        dict(short="Dey, Bhore \\& Ghosh (2026): ZoomSIB-UCB, optimal regret",
             cite="D. Dey, S. Bhore, A. Ghosh. Optimal Regret for Single Index Bandits. arXiv:2605.09454, 2026.",
             file="2605.09454-Dey-Bhore-Ghosh-Optimal-Regret-Single-Index-Bandits.pdf",
             setting=["One agent; $K$ i.i.d.\\ contexts per round; $f$ bounded and Lipschitz, possibly \\emph{non-monotone}; $\\|\\theta^*\\|_1=1$.",
                      "Assumes $\\mu^*\\ge c_0/\\mathrm{polylog}$ (bounded away from 0)."],
             did=["\\textbf{Phase 1:} explore uniformly; estimate $\\theta^*$ by a normalised, truncated Stein estimator.",
                  "\\textbf{Phase 2:} project arms onto $\\hat\\theta$, cut the index line into $\\sim T^{1/3}$ bins, and run \\emph{sleeping} UCB over the bins available each round.",
                  "Experiments use an adaptive stopping rule for Phase 1; real-data tests on KDD Cup 99 and Forest Cover."],
             results=["Regret $\\tilde O(T^{2/3})$ ($\\tilde O(d^2T^{2/3})$ with dimension), improving GSTOR's $\\tilde O(T^{3/4})$.",
                      "A matching minimax lower bound $\\tilde\\Omega(T^{2/3})$ for non-monotone links (built in $d=1$).",
                      "Sample splitting: $\\hat\\theta_0$ uses only Phase-1 data, so Phase 2's martingale argument holds."],
             us=["Our base algorithm. Fed-ZoomSIB and Dec-ZoomSIB-Relay federate its two phases; our server proofs reuse its Stein lemma and lower bound.",
                 "E29 tests exactly its $\\mu^*\\neq0$ assumption across heterogeneous agents."],
             stated=["Remove the requirement $\\mu^*\\neq0$ (``can an alternative technique be developed?'').",
                     "Go beyond bounded Lipschitz $f$.",
                     "The multi-index setting $y=f(B^\\top x)$."],
             ours=["The grid is fixed (one-shot binning), so the rate is $T^{2/3}$ on every instance; truly adaptive (zooming) bins could give instance-dependent rates. Our E3 measured exponents 0.29--0.60."]),
        dict(short="Kang et al.\\ (2025/ICLR 2026): introducing single-index bandits",
             cite="Y. Kang, M. Liu, B. Yi, J. Lyu, Z. Zhang, D. Zhou, Y. Li. Single Index Bandits: Generalized Linear Contextual Bandits with Unknown Reward Functions. ICLR 2026 (arXiv:2506.12751).",
             file="arxiv-2506.12751.pdf",
             setting=["GLM bandits where the link is unknown (``single index bandits''). Motivation: a misspecified link can give linear regret for every existing GLM method."],
             did=["\\textbf{STOR} and \\textbf{ESTOR} for \\emph{monotone} $f$: Stein-based estimation of $\\theta^*$, then explore-then-commit.",
                  "A sparse high-dimensional extension.",
                  "\\textbf{GSTOR} for general $f$ under Gaussian design: double exploration, kernel regression for $f$.",
                  "Baselines: LinUCB, LinTS, UCB-GLM, GLM-TSL, including deliberately misspecified versions."],
             results=["ESTOR: nearly optimal $\\tilde O(\\sqrt T)$ for monotone $f$; the same rate with sparsity in high dimension.",
                      "GSTOR: sublinear regret for general $f$ ($\\tilde O(T^{3/4})$, later improved to $T^{2/3}$ by Dey et al.)."],
             us=["First paper of the area; source of the truncated Stein estimator and of ESTOR/GSTOR, which are our single-agent baselines."],
             stated=[],
             ours=["The $T^{3/4}$ rate for general $f$ was not optimal (resolved by Dey et al.).",
                   "GSTOR's guarantees use a Gaussian design; its double exploration is costly in practice (Dey et al.\\ report 79--90\\% exploration on real data)."]),
        dict(short="Arya, Bhattacharjee \\& Sriperumbudur (2026): kernel single-index bandits with inference",
             cite="S. Arya, S. Bhattacharjee, B. K. Sriperumbudur. Kernel Single-Index Bandits: Estimation, Inference, and Learning. arXiv:2603.18938, 2026.",
             file="arxiv-2603.18938.pdf",
             setting=["Finitely many arms, each with its \\emph{own} index parameter, and an unknown link; covariates evolve under the bandit policy (adaptively collected data)."],
             did=["A kernelised $\\varepsilon$-greedy policy: Stein-based index estimation plus inverse-propensity-weighted kernel ridge regression for the reward functions."],
             results=["Asymptotic normality of the index estimator under adaptive sampling (valid confidence regions).",
                      "A directional functional CLT in an RKHS for the link estimate (pointwise confidence intervals).",
                      "Finite-time regret, including $\\tilde O(\\sqrt T)$ under common-link Lipschitz conditions."],
             us=["Different goal (statistical inference, not optimal regret) and a different model (arm-specific indices). Related work, not a baseline."],
             stated=["Multi-index or partially linear reward structures.",
                     "Uniform or anytime-valid confidence bands for sequential monitoring.",
                     "Robustness to model misspecification.",
                     "Exploration strategies that explicitly preserve inferential guarantees."],
             ours=[]),
        dict(short="Liu, Kang \\& Lee (Sep 2026): low-rank single-index bandits",
             cite="Z. Liu, Y. Kang, T. C. M. Lee. Low-Rank Single-Index Bandits with Unknown Links: From Matrices to Tensors. arXiv:2609.33025, 2026.",
             file="2609.33025v1.pdf",
             setting=["Matrix and tensor bandits with a \\emph{low-rank} index parameter and an unknown shared Lipschitz link; known regular candidate distributions; finite-variance noise."],
             did=["\\textbf{T-ESTOR} for monotone links: robust, rank-adaptive Stein estimation plus epoch-based greedy selection.",
                  "\\textbf{T-BSTOR} for non-monotone links: structured estimation plus robust bin-based learning (ZoomSIB-like)."],
             results=["Monotone: square-root regret with dimension dependence set by the rank, and a matching lower bound (rank, dimension, horizon) at large horizons.",
                      "Non-monotone: the optimal $\\tilde O(T^{2/3})$ horizon rate for fixed dimensions."],
             us=["Shows the Kang group is actively extending single-index bandits; a scooping-risk signal for multi-agent work.",
                 "Independent confirmation that ``zero first-order Stein signal'' ($\\mu^*=0$) is open, the case E29 studies."],
             stated=["Certify learned (not exactly known) selected scores.",
                     "\\textbf{Handle zero first-order signals} ($\\mu^*=0$).",
                     "Guarantees for the adaptive exploration used in their experiments."],
             ours=[]),
        dict(short="Arya \\& Song (2025): batched single-index bandits",
             cite="S. Arya, H. Song. Batched Single-Index Global Multi-Armed Bandits with Covariates. arXiv:2503.00565, 2025.",
             file="2503.00565v3.pdf",
             setting=["$K$ arms with rewards related through a shared single-index direction; feedback arrives in $M$ batches (policy updated only between batches)."],
             did=["\\textbf{BIDS}: batched successive arm elimination with \\emph{dynamic binning} along the index direction.",
                  "Two regimes: a pilot direction is given, or the direction is estimated from data."],
             results=["A lower bound for the $K$-armed problem, and an upper bound matching it (fixed $K$) given an accurate pilot direction.",
                      "With $M\\gtrsim\\log\\log T$ batches the bound simplifies to $(K\\log T)^{(1+\\alpha)/3}T^{1-(1+\\alpha)/3}$, avoiding the curse of dimensionality (a $d=1$ rate)."],
             us=["The closest single-index work to \\emph{limited communication}: a batch is like a sync round. Relevant to our E27, where fixed batch schedules did \\emph{not} match per-round sync for our UCB agents."],
             stated=["The upper bound depends polynomially on $K$ while the lower bound is only logarithmic in $K$ (Remark 4.3).",
                     "Without a pilot, matching rates hold only when the margin parameter and batch size lie in restricted ranges."],
             ours=[]),
    ],
    cross=["\\textbf{$\\mu^*=0$ is open in two papers} (Dey et al.; Liu--Kang--Lee). Second-order Stein (our E25) and multi-agent pooling (our E29) are two routes.",
           "\\textbf{Multi-index} rewards are open (Dey et al.; Arya et al.).",
           "\\textbf{No multi-agent single-index work exists} in this folder; batching (Arya \\& Song) is the closest communication-limited setting.",
           "\\textbf{Adaptivity}: a fixed grid gives worst-case $T^{2/3}$; instance-dependent (zooming) rates are not studied."])

# ------------------------------------------------------------------ 02
FOLDERS["02-single-agent-foundations"] = dict(
    title="Single-Agent Foundations",
    subtitle="Kernelised bandits and misspecified linear bandits",
    intro=r"""\textbf{What this folder is about.} Two single-agent papers that motivate and benchmark
single-index bandits: one handles a fully \emph{nonparametric} reward (kernels), the other shows
what goes wrong when a \emph{linear} reward is assumed but false. Both are by authors close to
our project (A.~Gopalan; A.~Ghosh is our instructor).""",
    papers=[
        dict(short="Chowdhury \\& Gopalan (2017): kernelised multi-armed bandits",
             cite="S. R. Chowdhury, A. Gopalan. On Kernelized Multi-armed Bandits. ICML 2017 (arXiv:1704.00445).",
             file="arxiv-1704.00445.pdf",
             setting=["Maximise an unknown function $f$ in a reproducing kernel Hilbert space (RKHS) from noisy evaluations; no parametric form."],
             did=["\\textbf{IGP-UCB}: an improved GP-UCB whose confidence width is smaller by roughly $\\ln^{3/2}t$.",
                  "\\textbf{GP-TS}: a GP-based Thompson sampling algorithm."],
             results=["Regret bounds in terms of the information gain $\\gamma_T$ of the kernel; IGP-UCB improves GP-UCB in theory and practice.",
                      "The first frequentist regret bound for Thompson sampling on fixed, unknown RKHS functions."],
             us=["IGP-UCB is one of our single-agent baselines (E2, E4): it degrades with dimension $d$ because $\\gamma_T$ grows with $d$, which single-index structure avoids.",
                 "Coop-KernelUCB (folder 04) is built on its confidence bounds."],
             stated=["Learn the kernel adaptively when it is unknown.",
                     "Time-varying functions from the RKHS.",
                     "Reinforcement learning with GP techniques.",
                     "Computational cost of optimising functions drawn from GPs."],
             ours=[]),
        dict(short="Ghosh, Chowdhury \\& Gopalan (2017): misspecified linear bandits",
             cite="A. Ghosh, S. R. Chowdhury, A. Gopalan. Misspecified Linear Bandits. AAAI 2017 (arXiv:1704.06880).",
             file="arxiv-1704.06880.pdf",
             setting=["Linear bandits where the true reward deviates from linearity (sparse deviations)."],
             did=["Shows OFUL, a state-of-the-art linear bandit algorithm, is not robust to such deviations.",
                  "Proposes \\textbf{RLB}: test for linearity on the fly and fall back to a non-parametric UCB when the test fails."],
             results=["A formal regret upper bound for RLB; experiments (synthetic and real) show real feature-to-reward maps are often far from linear."],
             us=["The motivation for unknown links: assuming the wrong model can give linear regret. Dey et al.\\ cite it for exactly this."],
             stated=["Other non-linearity structures than sparse deviations.",
                     "Information-theoretic regret lower bounds for general bandits with given feature sets.",
                     "Thompson sampling on linear bandits with deviations."],
             ours=[]),
    ],
    cross=["Both papers pay for flexibility: kernels pay in dimension (through $\\gamma_T$), robust tests pay by falling back to unstructured UCB. Single-index models sit between them.",
           "Neither studies multiple agents; multi-agent versions of both exist (Coop-KernelUCB in folder 04)."])

# ------------------------------------------------------------------ 03
FOLDERS["03-federated-bandits-server"] = dict(
    title="Federated Bandits with a Server",
    subtitle="Near-optimal regret with little communication",
    intro=r"""\textbf{What this folder is about.} $M$ agents play the \emph{same} bandit and talk only
through a central server. The question is how little communication still gives the regret of
one agent with all the data. These papers define the regret--communication trade-off for linear
and multi-armed bandits that our server results mirror.""",
    papers=[
        dict(short="Wang, Hu, Chen \\& Wang (2019/ICLR 2020): distributed bandit learning",
             cite="Y. Wang, J. Hu, X. Chen, L. Wang. Distributed Bandit Learning: Near-Optimal Regret with Efficient Communication. ICLR 2020 (arXiv:1904.06309).",
             file="1904.06309v2.pdf",
             setting=["$M$ agents, one server; communication measured as the total amount of transmitted data."],
             did=["\\textbf{DEMAB} for multi-armed bandits (distributed elimination).",
                  "\\textbf{DELB} for linear bandits with a fixed action set (phased elimination with optimal design).",
                  "\\textbf{DisLinUCB} for linear bandits with time-varying action sets: sync when a log-determinant ratio of the Gram matrix crosses a threshold (event-triggered)."],
             results=["DEMAB: near-optimal regret with $O(M\\log(MK))$ communication, independent of $T$, matching a lower bound up to a log factor.",
                      "DELB: regret $O(d\\sqrt{TM}\\log)$ with communication $O((Md+d\\log\\log d)\\log T)$.",
                      "DisLinUCB: regret $O(d\\sqrt{MT}\\log^2T)$ with communication $O(M^{1.5}d^3)$."],
             us=["Our event-triggered sync is the per-bin analogue of DisLinUCB's determinant trigger; our Theorem 12 mirrors their counting argument."],
             stated=[],
             ours=["DisLinUCB's communication is worse in $M$ and $d$ than DELB's; closing that gap for time-varying action sets was left open (addressed by later work).",
                   "Communication is counted in transmitted numbers, not bits (Salgia \\& Zhao, below, counts bits)."]),
        dict(short="Salgia \\& Zhao (2022): distributed linear bandits under communication constraints",
             cite="S. Salgia, Q. Zhao. Distributed Linear Bandits under Communication Constraints. arXiv:2211.02212, 2022.",
             file="2211.02212v1.pdf",
             setting=["Distributed linear bandits with a server; uplink and downlink channels have fixed capacity (bits per use)."],
             did=["Information-theoretic \\textbf{lower bounds} on the bits needed for sublinear regret.",
                  "\\textbf{PLS} (Progressive Learning and Sharing): learn and share the unknown vector one bit at a time.",
                  "A variant for sparse linear bandits."],
             results=["PLS is order-optimal in regret using $O(d\\log T)$ uplink bits and $O(d(\\log M+\\log T))$ downlink bits.",
                      "These communication costs match the lower bounds; sparsity improves the trade-off further."],
             us=["The model for a \\emph{communication lower bound}, which we identified as the theory missing from our server results (our sync bound is 60--75$\\times$ loose)."],
             stated=[],
             ours=["Only a server setting; bit-level lower bounds over graphs are open.",
                   "Linear rewards only; nonlinear or unknown-link versions are open."]),
    ],
    cross=["\\textbf{Matching communication lower bounds} exist for linear bandits (bits) and MAB (messages), but not for nonparametric or single-index bandits.",
           "Event-triggered sync is analysed in the worst case; instance-dependent communication bounds are not.",
           "All agents are identical here; folder 05 covers what changes when they are not."])

# ------------------------------------------------------------------ 04
FOLDERS["04-decentralized-bandits-graph"] = dict(
    title="Decentralised Bandits on a Graph",
    subtitle="No server: agents talk only to neighbours",
    intro=r"""\textbf{What this folder is about.} Agents sit on a communication graph and exchange
information with neighbours. The graph enters regret through quantities such as the diameter,
spectral gap, clique-cover or independence numbers. Two protocol families appear: \emph{relaying}
exact information (Kolla et al., Dubey \& Pentland) and \emph{gossip / consensus averaging}
(Chawla et al., Amani \& Thrampoulidis). Our Paper A lives here.""",
    papers=[
        dict(short="Kolla, Jagannathan \\& Gopalan (2016/2018): bandits over a social network",
             cite="R. K. Kolla, K. Jagannathan, A. Gopalan. Collaborative Learning of Stochastic Bandits over a Social Network. IEEE/ACM Trans.\\ Networking 2018 (arXiv:1602.08886).",
             file="1602.08886v2.pdf",
             setting=["Agents on a social network play the same stochastic MAB; each reward is seen instantly by the agent \\emph{and its neighbours} (one-hop sharing)."],
             did=["Analyses \\textbf{UCB-Network} (every agent runs UCB on all observed rewards).",
                  "Defines non-altruistic, individually consistent (NAIC) policies and lower-bounds their regret.",
                  "Proposes a \\textbf{dominating-set leader--follower} policy that exploits the network structure."],
             results=["An upper bound for UCB-Network with a graph-dependent constant (a combinatorial optimisation), specialised to complete and star graphs.",
                      "A universal network-independent lower bound for reasonable policies, and a graph-dependent one.",
                      "Natural extensions of single-agent policies can perform badly; leader--follower policies on dominating sets do much better."],
             us=["An early proof that ``just run the single-agent algorithm on shared data'' is not enough on a graph."],
             stated=[],
             ours=["Sharing is one-hop and instantaneous: no relaying, no delays, no communication budget.",
                   "Gaps remain between the upper and lower bounds on general graphs."]),
        dict(short="Chawla, Sankararaman, Ganesh \\& Shakkottai (AISTATS 2020): gossiping insert-eliminate",
             cite="R. Chawla, A. Sankararaman, A. Ganesh, S. Shakkottai. The Gossiping Insert-Eliminate Algorithm for Multi-Agent Bandits. AISTATS 2020 (arXiv:2001.05452).",
             file="2001.05452v4.pdf",
             setting=["$N$ agents on an arbitrary connected graph solve the same MAB; pairwise gossip with a communication budget."],
             did=["Each agent plays only a small \\emph{subset} of arms; agents gossip only \\textbf{arm IDs} (recommendations), not samples, and update their subsets (insert/eliminate)."],
             results=["If agents communicate $\\Omega(\\log T)$ times, every agent's regret is about $N$ times smaller than without collaboration.",
                      "Communication constraints only affect a second-order term, with explicit regret--communication trade-off bounds."],
             us=["A clear example of redesigning \\emph{what} is communicated (IDs, $O(\\log K)$ bits) rather than federating an existing algorithm.",
                 "Suggests a ``recommend-then-pull'' variant for bins in our Phase 2."],
             stated=[],
             ours=["Relies on all agents sharing the same best arm; heterogeneous agents or malicious recommenders break it (see Vial et al., folder 05).",
                   "Multi-armed only; contextual or structured arms are not covered."]),
        dict(short="Amani \\& Thrampoulidis (AAAI 2021): decentralised linear bandits (DLUCB)",
             cite="S. Amani, C. Thrampoulidis. Decentralized Multi-Agent Linear Bandits with Safety Constraints. AAAI 2021 (arXiv:2012.00314).",
             file="arxiv-2012.00314.pdf",
             setting=["$N$ agents on an arbitrary fixed graph; linear bandit; gossip through a doubly stochastic communication matrix; no server."],
             did=["\\textbf{DLUCB}: UCB plus accelerated (Chebyshev) consensus run in cycles.",
                  "\\textbf{RC-DLUCB}: rare communication.",
                  "\\textbf{Safe-DLUCB}: linear safety constraints."],
             results=["Regret $\\tilde O(d\\log(NT)\\sqrt{NT})$, the centralised rate, plus a small additive ``\\textbf{regret of delay}'' that depends on the spectral gap.",
                      "Communication $O(dN^2)$ per round for DLUCB; RC-DLUCB trades a little regret for much less communication."],
             us=["The template for tightening our delay term: their delay cost is additive and only logarithmic, while ours is $N\\cdot D\\cdot N_{\\mathrm{bins}}$.",
                 "One of the protocols we compare against (Chebyshev gossip in E14--E20)."],
             stated=["Decentralised algorithms with guarantees on \\textbf{time-varying networks}.",
                     "Extensions to \\textbf{nonlinear settings}.",
                     "Other types of safety constraints."],
             ours=[]),
        dict(short="Dubey \\& Pentland (ICML 2020): cooperative kernel bandits (Coop-KernelUCB)",
             cite="A. Dubey, A. Pentland. Kernel Methods for Cooperative Multi-Agent Contextual Bandits. ICML 2020 (arXiv:2008.06220).",
             file="arxiv-2008.06220.pdf",
             setting=["Agents on a graph with delays; kernelised contextual bandits; agents may have different but related reward functions, linked by a network kernel."],
             did=["\\textbf{Coop-KernelUCB}: message passing (the LOCAL protocol) where observations are forwarded hop by hop with a time-to-live $\\gamma$; product kernels for heterogeneous agents.",
                  "A variant, EAGER-KernelUCB, that performs better in experiments but has no proof."],
             results=["Average pseudo-regret $\\tilde O(\\sqrt{\\bar\\chi(G_\\gamma)T/V})$, where $\\bar\\chi(G_\\gamma)$ is a clique-cover number of the $\\gamma$-th graph power.",
                      "Outperforms single-agent and naive cooperative baselines on synthetic and real networks."],
             us=["The closest prior work to Paper A: distributed, unknown reward, a graph, and a \\emph{relay} protocol. It argues, as we found, that averaging is biased and message passing is preferable.",
                 "Our main candidate for a baseline that can learn an unknown non-linear reward."],
             stated=["\\textbf{Lower bounds} on group regret in cooperative decision-making with delays (the limits of cooperation).",
                     "Prove a guarantee for EAGER-KernelUCB (conjectured $\\tilde O(\\sqrt{(\\gamma+\\alpha(G_\\gamma))T/V})$ in the linear case).",
                     "Extend to the Bayesian case."],
             ours=["Communication grows linearly with $T$ (raw observations every round); event-triggered relaying is not studied."]),
    ],
    cross=["\\textbf{Graph-dependent lower bounds} are open (Dubey \\& Pentland state this).",
           "\\textbf{Time-varying graphs} and \\textbf{nonlinear rewards} are open for gossip methods (Amani \\& Thrampoulidis state this).",
           "Delay costs appear in very different forms: additive with the spectral gap (DLUCB), a clique cover under a square root (Coop-Kernel). No paper gives a tight additive delay term for nonparametric or sleeping bandits.",
           "Nothing here combines an unknown link with an index direction on a graph: the gap our project fills."])

# ------------------------------------------------------------------ 05
FOLDERS["05-beyond-homogeneous-agents"] = dict(
    title="Beyond Homogeneous Agents",
    subtitle="Heterogeneity, incentives, adversaries and collisions",
    intro=r"""\textbf{What this folder is about.} When agents are identical and cooperative, a network
of $N$ agents is ``one agent with $N$ times the data'', which we proved for our setting. The
papers here study what makes multi-agent bandits \emph{genuinely different}: agents that differ
(heterogeneous or clustered models), agents with their own interests (incentives), agents that
lie (malicious recommendations), and agents that compete for the same arms (collisions). This is
the folder to read for new research directions; E29 (heterogeneous slopes) belongs here.""",
    papers=[
        dict(short="Shi \\& Shen (AAAI 2021): federated multi-armed bandits",
             cite="C. Shi, C. Shen. Federated Multi-Armed Bandits. AAAI 2021 (arXiv:2101.12204).",
             file="2101.12204v2.pdf",
             setting=["Clients have \\emph{heterogeneous local} bandit models; the goal is the \\emph{global} model. In the approximate model, local models are random realisations of the global one, so the global model is uncertain even if local models were known."],
             did=["\\textbf{Fed2-UCB}: a ``double UCB'' accounting for both arm-sampling and client-sampling uncertainty, admitting clients gradually.",
                  "\\textbf{Fed1-UCB} for an exact model where the global model is the average of local ones."],
             results=["$O(\\log T)$ regret for the approximate model while controlling communication; admitting clients gradually is critical for that rate.",
                      "An order-optimal exact-model result that trades convergence time against the number of clients."],
             us=["A clean example of a \\emph{new source of uncertainty} that exists only with many agents (client sampling): the kind of contribution we are looking for."],
             stated=["The risk when synchronisation breaks is noted as ``an interesting research problem for future investigation''."],
             ours=["Multi-armed only; contextual or structured (e.g.\\ single-index) versions with heterogeneous clients are open."]),
        dict(short="Ghosh, Chung, Yin \\& Ramchandran (NeurIPS 2020): clustered federated learning (IFCA)",
             cite="A. Ghosh, J. Chung, D. Yin, K. Ramchandran. An Efficient Framework for Clustered Federated Learning. NeurIPS 2020 (arXiv:2006.04088).",
             file="2006.04088v2.pdf",
             setting=["Federated learning (supervised, not bandits) where users belong to unknown clusters, each with its own model."],
             did=["\\textbf{IFCA}: alternately estimate each user's cluster identity and update each cluster's model by gradient descent."],
             results=["Convergence guarantees for linear models with squared loss and for strongly convex smooth losses, given good initialisation; a discussion of optimal statistical error.",
                      "In practice, random initialisation with restarts works, including beyond the convex regime."],
             us=["Written by our instructor. The natural template for \\emph{clustered single-index bandits}: agents with different $\\theta^*_i$, where naive pooling hurts (our E12)."],
             stated=["Weakly convex and non-convex losses.",
                     "Stochastic gradients on the workers.",
                     "Only a small subset of devices participating."],
             ours=["Not a bandit paper: clustering while \\emph{also} exploring (online, with partial feedback) is open."]),
        dict(short="Wei, Li, Xu \\& Wang (2023): incentivised communication for federated bandits",
             cite="Z. Wei, C. Li, H. Xu, H. Wang. Incentivized Communication for Federated Bandits. arXiv:2309.11702, 2023.",
             file="2309.11702v2.pdf",
             setting=["Federated linear contextual bandits where clients are \\emph{self-interested} and share data only if it benefits them; the server must pay incentives."],
             did=["\\textbf{Inc-FedUCB}: a general framework with two implementations, data incentives and monetary incentives."],
             results=["Customisable near-optimal regret with guarantees on both communication and payment costs; experiments across environments."],
             us=["A multi-agent question with no single-agent counterpart. Exploration in our Phase 1 is a pure cost to the explorer, so the same free-riding issue applies."],
             stated=["Clients currently report their costs truthfully; with strategic misreporting a \\textbf{truthful incentive mechanism} is needed."],
             ours=[]),
        dict(short="Vial, Shakkottai \\& Srikant (2021): robust multi-agent bandits",
             cite="D. Vial, S. Shakkottai, R. Srikant. Robust Multi-Agent Multi-Armed Bandits. arXiv:2007.03812, 2020 (v3 2021).",
             file="2007.03812v3.pdf",
             setting=["$n$ honest and $m$ malicious agents; honest agents recommend their best-arm estimates, malicious ones recommend arbitrary arms."],
             did=["Shows existing collaborative algorithms lose all benefit with even \\emph{one} malicious agent.",
                  "Proposes \\textbf{blocking}: honest agents learn who is malicious and reduce communication with them."],
             results=["With blocking, collaboration again reduces regret below the single-agent baseline, assuming $m$ is small compared with $K$ and without assumptions on malicious behaviour."],
             us=["Shows recommendation-based protocols (like Chawla et al.) are fragile; any relay of statistics in our protocol has the same vulnerability."],
             stated=[],
             ours=["Multi-armed only; robustness for contextual or single-index bandits (where malicious agents could send poisoned statistics) is open.",
                   "Graph-structured versions exist in later work by the same authors."]),
        dict(short="Proutière \\& Wang (2019): optimal multiplayer bandits with collisions (DPE)",
             cite="A. Proutière, P.-A. Wang. An Optimal Algorithm for Multiplayer Multi-Armed Bandits. arXiv:1909.13079, 2019.",
             file="1909.13079v2.pdf",
             setting=["$M$ players choose among $K$ arms; if several players pick the same arm they \\emph{collide} and get nothing; players observe collisions. Not all players know $M$."],
             did=["\\textbf{DPE} (Decentralized Parsimonious Exploration): a leader--follower algorithm in which players communicate only through deliberate collisions."],
             results=["Regret asymptotically matching the optimal \\emph{centralised} algorithm, better than SIC-MMAB.",
                      "The expected number of rounds used for communication is finite."],
             us=["A completely different multi-agent problem (competition for arms, communication through actions). Its leader-announced commit time is a template for our Phase-1 agreement problem."],
             stated=[],
             ours=["Players share the same arm means; player-dependent rewards and the no-sensing (collisions not observed) variant need different ideas."]),
    ],
    cross=["\\textbf{Contextual or structured versions} of every idea here are mostly open: heterogeneous clients, clustering, incentives, robustness, all studied for MAB or linear models only.",
           "\\textbf{Clustered online learning} (IFCA while exploring) is open, and fits single-index bandits with different $\\theta^*_i$.",
           "\\textbf{Heterogeneous identifiability} (our E29): agents whose own slopes $\\mu_i$ differ in sign or vanish can identify $\\theta^*$ only together. None of these papers covers it, because none uses an index model."])


def main():
    for folder, spec in FOLDERS.items():
        tex = doc(spec["title"], spec["subtitle"], spec["intro"], spec["papers"], spec["cross"])
        (ROOT / folder / "00-summary.tex").write_text(tex)
        print("wrote", folder)


if __name__ == "__main__":
    main()
