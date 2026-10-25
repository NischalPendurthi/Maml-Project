# Remarks on `serverless.tex` — points to verify

Issues noticed while walking through the proofs in `docs/proofs/serverless.tex` step by step.
Each entry says where it is, what the concern is, why it matters, and possible fixes.
Status: `open` (not yet checked), `verified` (checked, no problem), `fixed` (tex updated).

Lemma numbers and line numbers in R1–R6 refer to the version at commit `b2c2af8`. Since 2026-10-24 remarks have
their own counter, and new results were added, so numbers moved (e.g. old Theorem 9 → 17, old Theorem 18 → 22).
Each resolution line gives the stable `\label` names.

---

## R1. Phase 1 i.i.d. claim needs i.i.d. noise — `fixed`

**Where.** Lemma 7 (Phase 1 is exactly centralised), `serverless.tex` line 302; proof at line 308.
Uses Lemma 3 (Stein estimator, DBG Lemma B.1 with Lemma 2.1), line 114; Assumption 1(i), line 78.

**Context.** The proof says the Phase-1 pairs $(x_{k,t}, y_{k,t})$ are i.i.d. across all $(k,t)$, and then
applies the Stein lemma, which is stated for $n$ i.i.d. pairs. The contexts are fine: the $K$ contexts are
i.i.d. from $\mathcal D$, the arm is chosen uniformly and independently, so the chosen context has law
$\mathcal D$, independently across agents and rounds.

**Concern.** $y = f(\langle x,\theta^*\rangle) + \eta$, so the pairs are i.i.d. only if the noise is too.
Assumption 1(i) only says $\eta_{i,t}$ is independent of the contexts and *conditionally* $\sigma$-sub-Gaussian
given $\mathcal F_{t,i}$. That allows noise whose law depends on the history (e.g. variance that changes with
past rewards), so the pairs need not be identically distributed or independent.

**Why it matters.** If the Stein lemma really needs i.i.d. pairs, Lemma 7 (and so $E_\theta$, the projection
term in Theorem 14, and Corollary 15) rests on an assumption that is not stated.

**Possible fixes.**
1. Add "the $\eta_{i,t}$ are i.i.d." to Assumption 1(i). Check first whether DBG already assume this
   (likely); then it is just a missing line in our statement of the assumptions.
2. Check whether the truncated-Stein concentration (DBG Lemma B.1) goes through with martingale-difference
   noise. The truncation + Bernstein-type argument may only need conditional moment bounds, in which case
   Assumption 1(i) is enough and the proof should say so.

**To verify.** Read DBG's exact Assumption 1 and the proof of Lemma B.1.

**Resolution (2026-10-24).** Checked against DBG: their Assumption 1 is only conditional sub-Gaussianity, but their
Lemma B.1 (cited from Kang et al.) is stated for i.i.d. pairs, so DBG have the same gap. Fix 1 was chosen, since
it is the simplest. Assumption `ass`(i) now says the noise is i.i.d., σ-sub-Gaussian and independent of contexts and
randomness. A note after the assumption explains why, and that DBG's hard instance (i.i.d. N(0,1)) satisfies it.
`lem:exact` cites it. Fix 2 (a Freedman version of the Stein bound) was rejected as heavier than needed.

---

## R2. Point $-W$ falls in no bin — `fixed` (minor)

**Where.** Bin definition in Section 3 table, line 206 ($I_j = (-W+(j-1)\Delta,\,-W+j\Delta]$);
Lemma 8(i) (bin geometry), line 323.

**Context.** Lemma 8(i) shows $|\langle x,\hat\theta_k\rangle| \le W$ and concludes that every arm falls in a bin.

**Concern.** The bins are half-open, so together they cover $(-W, W']$ with $W' \ge W$, but not the point $-W$
itself. An arm with $\langle x,\hat\theta_k\rangle = -W$ exactly is in no bin.

**Why it matters.** Probability zero for continuous context distributions, so it does not affect the bounds,
but the lemma as stated is false at that point.

**Fix.** Make the first bin closed: $I_1 = [-W, -W+\Delta]$. One-line change.

**Resolution (2026-10-24).** Done in the notation table of Section 3.

---

## R3. Lower bound holds over instances with $K$ growing with $NT$ — `fixed` (wording)

**Where.** Theorem 5 (lower bound), line 143; uses Lemma 4 (DBG Theorem 5.1), line 124.

**Context.** The reduction simulates the $N$-agent algorithm by one agent with horizon $n = NT$, then applies
DBG's single-agent lower bound. DBG's hard instances have $d=1$, Gaussian contexts, and a number of arms
that may grow logarithmically with $n$.

**Concern.** With $n = NT$, the hard instances may have $K \sim \log(NT)$. So Theorem 5 is "there exist hard
instances (with $K$ allowed to grow like $\log NT$)", not a bound for every fixed $K$. The theorem statement
says "sup over instances" without making this explicit.

**Why it matters.** A reviewer may read the theorem as holding for fixed $K$ (e.g. $K=2$).

**Fix.** State the instance class in Theorem 5 (or in a remark): $d=1$, Gaussian contexts,
$K = O(\log NT)$. Check DBG Theorem 5.1 for the exact dependence of $K$ on $n$.

**Resolution (2026-10-24).** DBG Thm 5.1 actually has $K=\lceil 4\lceil n^{1/3}\rceil\log n/\phi(1)\rceil$, so $K$
grows like $n^{1/3}\log n$, not $\log n$. Also $\mu^*\ge c_1/(2\log n)$, and $|f|\le1$ everywhere. `lem:dbglower` now
states this exact class. `thm:lower` says the sup is over these instances with $n=NT$. New `rem:hard` says it is not a
fixed-$K$ bound, and that our upper bound loses only logs on these instances ($K$ via $X_{\max}$, $1/\mu^*$ via $\varepsilon_0$).

---

## R5. Filtration in the confidence lemma is stated loosely — `fixed` (rigour)

**Where.** Lemma 10 (confidence), `serverless.tex` line 355; the "Prefixes" paragraph at line 368.
Uses Lemma 4 (Azuma–Hoeffding), line 130, and Assumption 1(i), line 78.

**Context.** The proof lets $\xi_m$ be the noise of the $m$-th Phase-2 pull into bin $j$ (lexicographic order),
and $\mathcal H_m$ "the information up to and including the choice of that pull". It then applies Azuma with
$\mathbb E[e^{\lambda\xi_m}\mid\mathcal H_{m-1}]\le e^{\lambda^2\sigma^2/2}$.

**Concern.** Two small gaps in how this is written.
1. With $\mathcal H_m$ defined as information up to the *choice* of pull $m$, $\xi_m$ is not
   $\mathcal H_m$-measurable (the noise is revealed after the choice), so $(\xi_m)$ is not adapted to
   $(\mathcal H_m)$ as Lemma 4 requires. The right filtration is $\mathcal H_m$ = everything up to and including
   the *reward* of pull $m$, and the condition needed is sub-Gaussianity given $\mathcal G_m$ = everything up to
   the choice of pull $m$ ($\mathcal H_{m-1}\subseteq\mathcal G_m$, then use the tower property).
2. The $m$-th pull into bin $j$ happens at a *random* position $(t,i)$. Assumption 1(i) gives sub-Gaussianity
   given $\mathcal F_{t,i}$ at a *fixed* $(t,i)$. Moving this to the random position is the standard optional
   skipping argument (Doob), or follows from a "stack of rewards" construction. The proof uses it without saying so.
   The same applies to the "own blocks" subsequence.

**Why it matters.** The result is correct and standard, but a careful referee may ask for it.

**Fix.** Define the two σ-fields as above and add one sentence citing optional skipping (e.g. Doob 1953,
Thm. III.5.2; or Lattimore & Szepesvári, *Bandit Algorithms*, Sec. 4.6 stack-of-rewards model). If R1 is
fixed by assuming i.i.d. noise, the stack-of-rewards construction is the simplest route.

**Resolution (2026-10-24).** `lem:conf` now defines $\mathcal G_m$ (up to the choice) and $\mathcal H_m$ (up to the
reward). It handles the random position by splitting on $\{m\text{-th pull at }(t,i)\}$, where $\xi_m=\eta_{i,t}$ is
independent of $(\mathcal F_{t,i},a_{i,t})$, and cites Lattimore & Szepesvári Sec. 4.6.

---

## R6. Trigger could compare against $G(\epsilon_m)$ instead of $G(\epsilon'_m)$ — `fixed` (simplification adopted)

**Where.** Trigger rule (eq. `trigger`), `serverless.tex` line 233; Lemma 6(i) (well defined), line 263;
Lemma 12 (unseen pulls), line 423; Lemma 17 (number of epochs), line 540.

**Context.** At slot boundary $\beta_m$, agent $l$ alarms if its own pulls into bin $j$ since
$\epsilon_m$ (last epoch $\le\beta_{m-1}$) exceed $\gamma\max(G_j(\epsilon'_m),1)$, where $\epsilon'_m$ is the
last epoch $\le\beta_{m-2}$. Lemma 6(i) justifies that $G(\epsilon'_m)$ is known at step $\beta_m$ by applying
Lemma 6(ii) to $m-1$.

**Observation.** $G(\epsilon_m)$ also seems to be known at step $\beta_m$: $\epsilon_m\le\beta_{m-1}$, and by the
timing in the proof of Lemma 6, the snapshots of an epoch $e$ are complete by step $e+2\Lambda-1\le\beta_{m-1}+L-1=\beta_m-1$.

**If correct, using $G(\epsilon_m)$ would:**
1. simplify Lemma 12 (the failed trigger at $\beta_{m-1}$ would directly give the bound with $G(e(t))$, no
   monotonicity step);
2. give growth by $(1+\gamma)$ between *consecutive* alarm epochs of a bin in Lemma 17, instead of every
   second one, halving the bound on $|A_j|$ and hence the communication constant in Theorem 18.

**To verify.** Re-check the timing in Lemma 6 (in particular that snapshots of $\epsilon_m$ are complete
*before* the alarm is evaluated in the communication step of $\beta_m$, not during it). Maybe the authors chose
$\epsilon'_m$ deliberately as a safety margin; if so, add a sentence saying why.

**Resolution (2026-10-24).** The timing checks out: snapshots of epoch $\beta_{m'}$ are complete by step
$\beta_{m'+1}-1$, so $G(\epsilon_m)$ is known before round $\beta_m$. Eq. `trigger` now uses $G_j(\epsilon_m)$, and
$\epsilon'_m$ is gone. Changed: `lem:welldef` (sharper (ii): "by the end of round $\beta_m-1$"), `lem:unseen` (no
monotonicity step), and `lem:epochs`. The last one now has growth by $(1+\gamma)$ between consecutive alarm epochs.
Since every alarm epoch already has $g_p\ge1$, it gives $|A_j|\le1+\log_{1+\gamma}(NT)$, down from
$2(2+\log_{1+\gamma}NT)$. This is a bit better than the halving predicted above. The code (`flood.py`) is a different
protocol, so no experiment is affected.

---

## R4. Flooding forwards one hop per step — `fixed` (implicit, harmless)

**Where.** Lemma 1 (flooding on a static graph), line 100; communication model, line 88.

**Context.** The proof uses that a message received in step $r$ is forwarded in step $r+1$, so it moves one
hop per communication step. This is not stated in the communication model.

**Assessment.** If messages could be relayed several hops within one step, delivery would only be faster,
so $\Lambda = D$ is still a valid upper bound. No change needed; optionally add one sentence to the
communication model ("a message received in step $s$ is forwarded in step $s+1$").

**Resolution (2026-10-24).** Sentence added to the communication model.

---

## R7. The bad-event step needs $f$ bounded everywhere — `fixed`

**Where.** Theorem `thm:regret` (old Theorem 9), the "Bad event" paragraph; Assumption `ass`(iii).

**Context.** The old proof bounded the regret off $E$ by $2L_fNT$ and added $3\delta\cdot2L_fNT=6L_f$.

**Concern.** Assumption 1(iii) bounds $|f|\le L_f$ only on $|z|\le X_{\max}$. Off $E_x$ a context can have
$|z|>X_{\max}$, where $f$ is not controlled, so "regret $\le 2L_fNT$ always" is unjustified. DBG do not assume $f$
bounded globally either; they avoid the issue by stating their upper bound (Thm C.1) with high probability.

**Why it matters.** The expectation bound, and so the "matches the lower bound" claim, rested on an unstated assumption.

**Resolution (2026-10-24).** `thm:regret` and `cor:rate` are now stated with probability $\ge1-3\delta$, as in DBG. The
bad-event paragraph and the $+6L_f$ are gone. New `rem:expect`: if $|f|\le L_f$ on all of $\mathbb R$ (true on DBG's hard
instances, Lemma F.1(a)), the expectation bound $+6L_f$ follows. That is the form compared with `thm:lower`.

---

## R8. Delivery time under union connectivity was wrong — `fixed` (real error)

**Where.** Lemma `lem:delivery`(ii) (old Lemma 19(ii)), Corollary `cor:robust`; the same claim appears as
"B·D" in `docs/proof-plan.md` and `docs/report-server-vs-serverless.md`.

**Concern.** The old claim was $\Lambda=B(D_B+1)$ when every $B$-window's union graph is connected with diameter $\le D_B$.
The proof assumed the informed set grows by one hop of *the same* graph per window, but the union graph changes
from window to window. Counterexample: in window $r$, the only edges form a star centred at an uninformed agent $c_r$, and
they all appear at the window's last step. Each union graph has diameter 2, but only $c_r$ is informed per window, so
delivery takes $B(N-1)$ steps. A scratchpad simulation (persistent flooding, $(N,B)\in\{(5,1),(5,3),(10,4),(20,2),(50,5)\}$)
gives exactly $B(N-1)$ every time, against the old bound of $3B$.

**Resolution (2026-10-24).** Split into two correct cases:
- (ii) union connectivity with persistent flooding gives $\Lambda=B(N-1)$. Proof: each window adds at least one agent.
  The star shows this is tight.
- (iii) every $B$-window contains a connected spanning subgraph present at every step, of diameter $D_B\le B$.
  Plain flooding then gives $\Lambda=D_B$, by Lemma `lem:flood` inside the window.

Link delays moved to (iv). New `rem:star` gives the counterexample. `cor:robust` now says the regret cost is
$\tilde O(N^2B(NT)^{1/3})$ in case (ii) and $\tilde O(ND_B(NT)^{1/3})$ in case (iii).

---

## R9. Agreement theorem stated "on an event" for an expectation bound — `fixed` (wording)

**Where.** Theorem `thm:agree` (old Theorem 21).

**Concern.** The old statement was "On the event $\{\eta\le\bar\eta\}$, Theorem 9 holds…". Theorem 9 was an expectation
bound, so "on an event" had no meaning.

**Resolution (2026-10-24).** With R7's high-probability form, the new statement reads: if $P(\eta>\bar\eta)\le\delta$,
then with probability $\ge1-3\delta$ the bound holds with the projection term $4L_{f'}X_{\max}\bar\eta NT$. The second
part takes $\bar\eta=\varepsilon_0(NT_0)+\eta_{\rm agree}$, which is valid on $E_\theta$.

---

## R10. "Logarithmic in $T$" communication claim at the rate-optimal parameters — `fixed` (honesty)

**Where.** Abstract (3); Theorem `thm:comm` (old Theorem 18).

**Concern.** The rate uses $\Delta=(NT)^{-1/3}$ and $\gamma=\gamma_0/N$. Then $N_b=\tilde O((NT)^{1/3})$ and
$\log_{1+\gamma}(NT)\approx N\log(NT)/\gamma_0$, so the bound is $\tilde O(|E|N^2(NT)^{2/3})$, which is polynomial in $T$.
"Logarithmic in $T$" is only true for a fixed grid and a fixed $\gamma$.

**Resolution (2026-10-24).** The abstract and `thm:comm` now say "for a fixed grid". New `rem:commrate` states the
rate-optimal count, and notes that it beats per-round sharing once $T\gtrsim N^{7/2}$. It also explains the $\gamma$
trade-off: a constant $\gamma$ gives $N\times$ fewer epochs but a $\sqrt N$ regret factor. Finally, it adds a simple cap:
snapshot traffic is $O(|E|NT)$ whatever $\gamma$ is, since each snapshot entry is charged to a distinct pull.

---

## R11. "An agreement pass is enough" corollary was vacuous — `fixed` (wording)

**Where.** Old Corollary 22 (`cor:agreepass`).

**Concern.** The approximate method's sums $b'_k$ were never used. The corollary was just the base protocol (flood the
local sums) with $\Lambda$ extra rounds.

**Resolution (2026-10-24).** Rewritten as `rem:agreepass`. It says that any approximate Phase 1 becomes exact after one
flood of the local sums, at a cost of $\Lambda$ rounds, $2L_fN\Lambda$ regret and $2|E|N(d+1)$ scalars. It also says
plainly that the approximate method only helps if agents must start Phase 2 before the flood completes. The E28 remark
now points to it.

---

# New results of 2026-10-24: points to verify

These are new proofs, not gaps found in old ones. Each lists what to check in a walkthrough.

## R12. Graph lower bound reuses DBG's Appendix F — `open` (verify)

**Where.** Lemma `lem:cone`, Theorem `thm:conelower`, Corollary `cor:ringlower`.

**What to check.**
1. The induction in `lem:cone`: what $u$ knows after step $s$ depends only on pulls with $d(u,v)\le s-s'+1$. It
   uses the forwarding convention of R4: one hop per step.
2. The "one instance for all cones" step. For each cone, $J_i$ (rarely pulled bins under the null) has
   $\ge M/2$ bins, and $B_i$ (bins pulled $\ge n/2$ times w.p. $>1/(4e)$) has $<8e$. A bin in $J_i\setminus B_i$ for
   $\ge|S|/4$ cones then exists by counting. Check that DBG's Prop F.1 (KL $\le2\varepsilon^2N_j$) applies to the
   cone policy $\pi_i$, whose randomness includes the algorithm's seed.
3. DBG's Case A needs $2n^{-2/3}\le1/(8e)$, and $M\ge32e$ needs $n\ge(32e)^3$. Both are covered by "n large enough".

**Why it matters.** It is the only graph-dependent lower bound; Dubey & Pentland list this as open.

## R13. Sharper delay term vs measurement — `verified` (no contradiction)

**Where.** Theorem `thm:sharp`, Corollary `cor:sharp`; E31.

**Observation.** The bound's shape in $D$ is $\sqrt{\gamma+4D}$ (slope 0.48), but E31's measured excess for the epoch
protocol has slope 0.90. The measurement stays 12–37$\times$ below even the constant-free bound. The reason: at
these sizes a bin gets $\approx$400 pulls, below $c_{N,\Lambda}\approx$970, so all of its life is inside the delay window.
The bound is valid; it just does not describe the measured shape. Don't claim it "explains" E23/E31.

## R14. Serverless stopping rule — `verified` (E33)

**Where.** Proposition `prop:stop`; engine `stop_rule="pooled"`.

**Check.** It needs the checkpoints to be fixed in advance (they are geometric in the pooled size $N\cdot t$) and the
rule to be deterministic. The truncation level at a checkpoint uses $n=N c_m$, which every agent knows. In E33 the
pooled rule stopped exactly $D$ rounds after the server's rule in every paired trial, with zero disagreement.

## R15. Private Phase 1 — `open` (scope)

**Where.** Theorem `thm:private`; engine option `dp_eps`.

**What to check.**
1. The DP claim covers "everything the network does" because Phase 2 uses Phase 1 only through
   $\hat\theta_0$ (built from the noisy sums) and the window $W=X_{\max}$, which is a constant in the proofs.
   **The code computes $W$ by max-consensus over Phase-1 contexts**, which is data-dependent, so E35's code is not
   covered by the DP claim as it stands. Fix in code: use $W=X_{\max}$ (or a privatised max) when `dp_eps` is set.
2. The theorem protects Phase-1 samples only. Phase-2 rewards leak through actions (stated in the remark).
3. The constants: $\kappa=\sqrt{6dN\log(1.25/\delta_p)}/\varepsilon_p$ uses $C_\theta\ge2\sqrt2\sqrt{M(\sigma^2+L_f^2)}$.
4. **Measured (E35):** κ understates the cost. τ is set from the worst-case $L_f$ (48 for the quadratic link on
   $|z|\le6$), about 20× the typical summand, so the noise is huge; $\varepsilon_p\le32$ gives a random direction.
   The code now uses $W=X_{\max}$ when `dp_eps` is set (fixed 2026-10-25), so E35 is covered by the DP claim.
   Open: a smaller clipping level (bias vs noise).

## R16. Tree-aggregated epochs (bounded memory) — `open` (verify)

**Where.** Proposition `prop:memory`(ii).

**Check.** The timing $L=\Lambda+2h$: everyone knows of the alarm by $\beta_m+\Lambda-1$. Leaves send in step $\beta_m+\Lambda$,
the root has everything after $h$ steps, and the broadcast takes $h$ more, so $G(e)$ is everywhere by
$\beta_m+\Lambda+2h-1=\beta_{m+1}-1$. Then Lemmas `lem:unseen` and `lem:stale` hold with $2L$ in place of $4\Lambda$. This
variant is not implemented or measured.

---

# Results of 2026-10-25: making the delay story complete

## R17. Horizon-free delay term for the epoch protocol — `open` (verify)

**Where.** Lemma `lem:avail`, Theorem `thm:hfree`, Corollary `cor:hfree`.

**What to check.**
1. Availability indicators are independent Bernoulli$(q_j)$ *given the frozen direction*. They are, because Phase-2
   contexts are fresh. Under the agreement setting (different $\hat\theta_k$), $q$ depends on the agent; the Chernoff
   step still works with a sum of different means.
2. The early/late split. A late pull has $k-1>2U_J+N\gamma$, which forces $n\ge1$ and $(1+N\gamma)n\ge(k-1)/2$.
3. $\sum_j q_j\le\min(K,N_b)$: the expected number of distinct bins among the $K$ arms.
4. The constant 8 in the UCB term (instead of $4\sqrt2$) comes from the factor-2 slack of the split.

**Supersedes** R13's worry: the shape is now $N\Lambda K$, flat in $T$. In E31, excess/(NDK) is 0.86–1.1 on all graphs.
**E36 (2026-10-25):** excess/(NDK) is 0.86–1.15; an 8× longer $T$ gives only ×1.2. The excess grows like $K^{0.44}$, so
the linear $K$ in the bound is loose (stated as open in the tex).

## R18. Published-only relay — `open` (verify carefully; main new proof)

**Where.** Section `sec:pubrelay`: Lemmas `lem:causal`, `lem:pubconf`, `lem:pubstale`, Theorem `thm:pubrelay`; code
`FloodTables(own=False)`.

**What to check.**
1. **Causality.** Rewards reach decisions only through records. Triggers use counts only, and counts depend on
   actions, not on rewards. The publisher must not use its own unpublished rewards; that is the one-line change
   (`own=False`).
2. **Ordering key** $\kappa_i(m)=(s_m+\max(d(i,k_m),1), s_m, k_m, r_m)$. If $\eta_m$ influences a decision about $m'$,
   then $\kappa_i(m')>\kappa_i(m)$. Use $\max(a,1)+\max(b,1)\ge\max(a+b,1)$, and break ties by $s$, since $s_{m'}\ge\tau>s_m$.
   Check the timing convention: a record published at step $s$ is usable at distance $d$ from round $s+\max(d,1)$,
   which matches `relay()` in the code.
3. **Martingale over the full order** (all bins), then optional skipping to bin $j$. The identity of the next pull
   must be a function of earlier noises, contexts and randomness only.
4. **Stale counts** need $N\gamma\le1/2$ (the theorem uses $\gamma=1/(2N)$). The unpublished count of $l$ is $\le\gamma\max(V_{l,J},1)$
   after every step, and $V_{l,J}\le k-1$.
5. The communication remark: $V_{l,j}$ grows by a factor $>1+\gamma$ between two triggers of $l$ for $j$. It needs
   $V$ to include $l$'s own record (it does: own records are usable from $s+1$).

**Why it matters.** It removes the "we prove one protocol and run another" gap. E36: at $\gamma=0.5$ it equals the
E23 relay; at the proved $\gamma=1/(2N)$ it has lower excess on every graph (ring 381 vs 528), for 7–8× more scalars.

## R19. "Why the light-cone bound grows like $D^{1/3}$" is a heuristic — `open` (wording)

**Where.** The remark after `rem:conelower`.

**Note.** The smoothness argument explains why our technique gives $n^{2/3}$ per cone. It does **not** prove that
no linear-in-$D$ lower bound exists; the remark says so ("we do not know such instances"). Do not present it as an
impossibility result.
