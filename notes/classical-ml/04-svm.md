# Support Vector Machines

Labels $y_i \in \{-1, +1\}$, score $f(x) = x^\top \theta$, margin $m_i = y_i\, x_i^\top \theta$.

```derivation
L_{\text{SVM}}(\theta) & = \sum_i \max\big(0,\ 1 - y_i\, x_i^\top \theta\big) + \lambda \lVert\theta\rVert^2 || || minimize the hinge loss + L2
& \Leftrightarrow\ \min_{\theta,\, \xi}\ \tfrac{1}{2}\lVert\theta\rVert^2 + C \sum_i \xi_i || || [!INTUITION] max margin :: The soft-margin SVM: slack $\xi_i$ is the hinge loss. The margin width is $2 / \lVert\theta\rVert$, so the L2 term maximizes the margin.
\text{s.t.} & \quad y_i\, x_i^\top\theta \geq 1 - \xi_i, \quad \xi_i \geq 0 || || slack $\xi_i$ per point
```

<figure>
  <img src="figures/svm-losses.svg" alt="Hinge, logistic, squared and 0-1 losses plotted against the margin">
  <figcaption>Losses vs. margin. Hinge is exactly 0 past m = 1. Logistic is never quite 0. Both grow linearly for badly misclassified points; squared loss grows quadratically (and also penalizes m &gt; 1).</figcaption>
</figure>

---

## SVM vs. logistic regression

| | SVM (hinge) | logistic regression (log loss) |
|---|---|---|
| loss at margin $m$ | $\max(0,\ 1 - m)$ | $\log(1 + e^{-m})$ |
| well classified ($m \geq 1$) | exactly 0: only support vectors shape the boundary | small but $> 0$: every point pulls a little |
| badly misclassified ($m \to -\infty$) | grows linearly | grows linearly |
| output | score / class only, **no probabilities** | calibrated-ish probability $\sigma(x^\top\theta)$ |

---

## Good questions

<details class="q">
<summary>Why do only the support vectors matter?</summary>

The hinge loss is flat (zero) for points past the margin, so they contribute no gradient. The solution is determined by points on or inside the margin.

</details>

<details class="q">
<summary>Why does minimizing ‖θ‖ maximize the margin?</summary>

The margin width is $2 / \lVert\theta\rVert$. With the constraint $y_i\, x_i^\top \theta \ge 1$ fixing the scale, a smaller $\theta$ means a wider margin.

</details>

<details class="q">
<summary>What does C control?</summary>

Margin width vs. violations. Large $C$: few violations, narrow margin, low bias, high variance (→ hard margin). Small $C$: wide margin, more violations tolerated.

</details>

<details class="q">
<summary>When would you pick an SVM over logistic regression?</summary>

The losses are close, so linear accuracy is usually similar. An SVM's solution depends only on a few points, which makes kernels cheap; it gives no probabilities. Logistic regression gives probabilities, and every point contributes.

</details>
