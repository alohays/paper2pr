---
paths:
  - "Slides/**/*.tex"
  - "Quarto/**/*.qmd"
---

# Paper Review Knowledge Base: Paper2PR

## Notation Registry (General AI/ML Conventions)

| Rule | Convention | Example | Anti-Pattern |
|------|-----------|---------|-------------|
| Bold lowercase for vectors | Vectors are bold lowercase | $\mathbf{o}$, $\mathbf{a}$, $\mathbf{z}$ | $O$, $A$ (uppercase for vectors) |
| Uppercase for matrices | Matrices are bold uppercase | $\mathbf{W}$, $\mathbf{K}$ | $w$, $k$ (lowercase for matrices) |
| Greek for parameters | Model parameters use Greek letters | $\theta$, $\phi$, $\psi$ | $p$, $q$ (Latin for parameters) |
| Calligraphic for losses/sets | Losses and sets use calligraphic | $\mathcal{L}$, $\mathcal{D}$ | $L$, $D$ (plain for losses) |
| Subscript for time | Time index as subscript | $\mathbf{o}_t$, $\mathbf{a}_{t:t+H}$ | $o(t)$ (functional notation) |

**Per-paper notation:** Document paper-specific conventions in a "Notation" section at the start of each slide deck. Different papers may use different conventions — always follow the original paper's notation.

## Symbol Reference (Common AI/ML)

| Symbol | Meaning | Common Usage |
|--------|---------|-------------|
| $\theta$ | Model parameters | Network weights |
| $\pi$ | Policy | RL/robotics decision function |
| $\mathcal{L}$ | Loss function | Training objective |
| $\mathbf{o}$ | Observation | Sensory input (image, state) |
| $\mathbf{a}$ | Action | Robot/agent output |
| $\mathbf{z}$ | Latent variable | Encoded representation |
| $H$ | Horizon | Prediction/planning horizon |
| $T$ | Time steps / Temperature | Context-dependent |

## Paper Review Progression

| # | Paper | Key Topic | Key Architecture | Status |
|---|-------|-----------|-----------------|--------|
| 1 | DreamZero (NVIDIA, 2025) | WAM as zero-shot robot policy | Joint video-action diffusion | In progress |

## Key Acronyms

| Acronym | Full Name | Context |
|---------|-----------|---------|
| WAM | World Action Model | Joint video + action prediction |
| VLA | Vision-Language-Action model | Language-conditioned robot policy |
| IDM | Inverse Dynamics Model | Action prediction from video |
| VLM | Vision-Language Model | Multimodal understanding |
| RL | Reinforcement Learning | Learning from rewards |
| RLHF | RL from Human Feedback | Alignment technique |
| DiT | Diffusion Transformer | Transformer-based diffusion model |
| LoRA | Low-Rank Adaptation | Parameter-efficient fine-tuning |

## Design Principles for Paper Reviews

| Principle | Rationale |
|-----------|----------|
| Follow the paper's own notation | Prevents confusion when audience reads the paper |
| Distinguish paper claims from personal insights | Intellectual honesty; mark your opinions clearly |
| Show figures from the paper with attribution | Visual evidence > paraphrased descriptions |
| Include failure cases when paper discusses them | Balanced review, not advertising |
| Note implementation details from code when available | Added value beyond the paper |

## Anti-Patterns (Don't Do This)

| Anti-Pattern | What Goes Wrong | Correction |
|-------------|----------------|-----------|
| Overstating results | Audience trusts inflated claims | Quote exact numbers from paper |
| Ignoring baselines | No context for claimed improvements | Always show what was compared against |
| Mixing sim and real results | Misleading performance picture | Clearly label evaluation environment |
| Using different notation than paper | Confuses audience who reads paper | Match paper notation exactly |
