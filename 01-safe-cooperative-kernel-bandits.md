# Safe Cooperative Kernelized Single-Index Bandits for Multi-Robot Skill Selection

## One-sentence pitch

Can a team of robots safely learn which high-level motion skill to execute from local observations, while sharing only limited information with nearby teammates and handling a nonlinear, initially unknown reward function?

## Problem statement

Consider a fleet of `N` mobile robots navigating to assigned goals in a cluttered, partially observed workspace.  At every decision epoch, robot `i` observes a local context `x_i,t` (goal direction, range-sensor summary, velocity, and relative neighbor positions) and chooses one of `K` short-horizon motion primitives `a_i,t` such as *go-to-goal*, *turn left/right*, *slow down*, *yield*, or *explore*.  Executing the primitive returns a noisy utility signal and may violate a safety requirement such as a minimum collision clearance.

The utility is nonlinear and unknown.  We model it as a kernelized single-index reward:

`E[r_i,t | x_i,t, a_i,t] = g_a(theta_a^T phi(x_i,t))`,

where the index parameter `theta_a` captures an interpretable task-relevant direction and `g_a` is an unknown, smooth link function in an RKHS.  Robots can exchange compact learning statistics with graph neighbors only every `C` steps.

**Goal:** design and evaluate a decentralized, safety-filtered cooperative bandit algorithm that maximizes team utility while maintaining a prescribed clearance constraint and a fixed communication budget.

## Why this is a robot-learning project

Bandits are appropriate here because the decision is a high-level, short-horizon choice.  A conventional local controller executes the selected primitive; the learner adapts *which primitive is appropriate in the current situation*.  This avoids claiming that a contextual bandit solves full long-horizon control, while retaining the central robot-learning questions of safe exploration, online adaptation, partial observability, and multi-robot coordination.

The project is especially well aligned with CS6007 because every robot is a learning agent, information moves through a communication graph, and the learning objective includes cooperation under limited communication.

## Proposed method

Implement a practical **Safe Coop-KSIB** algorithm:

1. Estimate each action's single-index direction from locally collected contexts and rewards.
2. Fit a kernel-ridge reward model on the resulting one-dimensional index.
3. Form an upper-confidence estimate of reward for each candidate primitive.
4. Form a conservative lower-confidence estimate of clearance (or collision cost).
5. Select the highest-UCB action in the safe set; fall back to a certified braking/yield primitive if the set is empty.
6. Every `C` decisions, send a compressed set of sufficient statistics / landmark features to graph neighbors and fuse received information.

The intended contribution is **not** a full new regret proof for the entire nonlinear, decentralized, safe setting.  The contribution is a clearly defined algorithmic combination, communication ablation, and empirical evidence.  A small supplementary result in a simplified linear-reward setting is optional.

## Hypotheses

- Cooperative information sharing reaches a target success rate with fewer environment interactions than independent learners.
- A kernelized/single-index reward model performs better than linear UCB when congestion and clearance effects are nonlinear.
- The safety filter substantially reduces collisions at a modest cost in return.
- Event-triggered or periodic compressed communication retains most of the benefit of centralized pooling at much lower bandwidth.

## Experimental plan

Start with a custom 2-D simulator: circular robots, static obstacles, random start-goal pairs, noisy range sensors, and 2--6 robots.  This makes collision geometry, safety, and communication topology controllable.  If time permits, port the final algorithm to a Gymnasium/PettingZoo-compatible navigation environment.

Vary:

- number of robots: 2, 4, 6;
- communication graph: complete, ring, random connected graph;
- communication interval / byte budget;
- observation noise and robot-speed heterogeneity;
- obstacle density and goal conflicts.

## Baselines

1. Hand-designed safe heuristic (go-to-goal with braking/yield rule).
2. Independent LinUCB with the same safety filter.
3. Independent kernel-UCB / Gaussian-process UCB.
4. Centralized pooled kernel-UCB (an upper-bound reference, not a deployable policy).
5. Cooperative linear UCB, if implementation time allows.

## Metrics

- team return and per-robot return;
- success rate and time-to-goal;
- collision rate and minimum inter-robot/obstacle clearance;
- cumulative regret against an oracle available in simulation;
- samples needed to reach a fixed success rate;
- messages, bytes, and performance per transmitted byte;
- fairness: variance/minimum of individual robot returns.

## Deliverables ladder

**Minimum viable project:** reproducible simulator, independent linear and kernel bandit baselines, safety filter, and a clean empirical comparison.

**Strong project:** decentralized statistic sharing, communication and heterogeneity ablations, and 20+ random seeds with confidence intervals.

**Excellent project:** adaptive/event-triggered communication, an interpretable learned index analysis, or a small hardware/ROS demonstration after the simulation study is complete.

## Risks and scope controls

- Do not start with end-to-end deep RL; it obscures the bandit question and introduces unstable training.
- Keep actions discrete motion primitives.  Continuous-action kernel optimization is a separate research problem.
- Use a conservative geometric safety shield initially; learning an unknown safety model is an extension, not a dependency.
- Treat hardware as optional validation, never as the critical path.

## Core references

- Kang et al., *Single Index Bandits: Generalized Linear Contextual Bandits with Unknown Reward Functions*, ICLR 2026.
- Arya, Bhattacharjee, Sriperumbudur, *Kernel Single-Index Bandits: Estimation, Inference, and Learning*, 2026.
- Dubey and Pentland, *Kernel Methods for Cooperative Multi-Agent Contextual Bandits*, ICML 2020.
- Amani and Thrampoulidis, *Decentralized Multi-Agent Linear Bandits with Safety Constraints*, AAAI 2021.
