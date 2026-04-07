---
title: "Reading---Smart Predict then Optimize"
date: 2024-11-15 00:00:00 +0800
---

<!-- AUTO-GENERATED: scripts/blog_pipeline.py -->

## Background

在现实世界的优化应用中，机器学习与优化方法的结合已经成为决策分析的重要方法论。本文就是要讨论数据驱动下，带有不确定参数的优化问题。这种问题通常通过“Predict, then Optimize”的范式来解决。在涉及预测再优化问题中，机器学习方法的目的是最小化预测误差，并不关注如何将预测结果用于下游的优化问题中。

## 符号说明

$w\in \mathbb{R}^{d}$决策变量；$S\in\mathbb{R}^{d}$表示可行域；
$p$表示特征向量$x$的维度；$n$表示训练样本数量；
$W^{*}(c):=argmin_{w\in S}\{c^{T}w \}$表示优化问题的最优解集合~解集；
$w^{*}(c)$表示最优解，使得$w^{*}(c) \in W(c)$；

## Predict, then Optimize Framework

$SPO$架构的主旨在于，生成最小化决策误差而非预测误差的预测模型。转化为数学表述，决策者研究的目标：
$$
\min\limits_{w\in S}\mathbb{E}_{c\sim D_{x}}[c^{T}w|x]=\min\limits_{w\in S}\mathbb{E}_{c\sim D_{x}}[c|x]^{T}w
$$
给定特征$x$的实例下，$D_{x}$ 是$c$ 的条件分布，优化问题目标函数的期望值等于基于$\hat{c}$ (即表示为$\mathbb{E}_{c\sim D_{x}}[c|x]$)解决的优化问题的确定性版本的目标函数期望值。

1. 给定名义优化问题：

$$
\begin{aligned}
P(c):\quad z^{*}(c):= \min\limits_{w}c^Tw\\
s.t.\quad w\in S
\end{aligned}
$$

1. 训练数据形式$(x_{1},c_{1}),\cdots,(x_{n},c_{n})$
2. 成本向量$c$ 预测模型$f$ 使得$\hat{c}:=f(x)$并定义一个类$\cal{H}$有$f \in \cal{H}$
3. 定义损失函数$\cal{l}(\hat{c},c)$衡量成本向量预测值与真实成本向量的误差。
即求解优化问题确定最佳预测模型$f^{*}$根据经验风险最小化原则，需要满足：

$$
\min\limits_{f \in \cal{H}}\frac{1}{n}\sum\limits_{i=1}^{n}l(f(x_{i}),c_{i})
$$
$$
w^{*}(f^{*}(x))
$$
$$
\min\limits_{B}\frac{1}{n}\sum\limits_{i=1}^{n}||Bx_i-c_{i}||^{2}
$$
$$
w^{*}(B^{*}x)
$$

- 给定真实成本向量 $c$,  最可能的决策是 $w^*(c)$ 得到 $c^T w^*(c)$
- 给定预测的成本向量 $\hat{c}$, 做出的决策是 $w^*(\hat{c})$得到 $c^T w^*(\hat{c})$
- SPO损失函数定义为：

$$
\ell^{w^{*}}_{\mathrm{SPO}}(\hat{c}, c):=c^T w^*(\hat{c})-c^T w^*(c)
$$

- Alternate definition with no oracle dependence is also given, we break ties with worst-case (this avoids predicting 0 all for everything)

## SPO损失函数

$SPO$损失函数：衡量由于成本向量预测不精确而做出次优决策时产生的超额成本。
$$
\ell_{\mathrm{SPO}}(\hat{c}, c):=max_{w \in W^{*}(\hat{c})} \{c^Tw\}-z^*(c)
$$

根据$PO$范式，$SPOloss$计算流程：

- 给定成本向量预测值$\hat{c}$；
- 求解$P(\hat{c})$得到决策$w^{*}(\hat{c})$；
- 计算$SPO loss:=c^{T}w^{*}(\hat{c})-z^{*}(c)$；

但由于$SPO$损失函数在计算过程中，可能的非凸性和不连续性，提出$SPO+$损失函数作为$SPO$的凸替代，$SPO+$的几点性质如下：

- $\ell_{\mathrm{SPO}}(\hat{c}, c) \leq \ell_{\mathrm{SPO}+}(\hat{c}, c)$；
- $\ell_{\mathrm{SPO}+}(\hat{c}, c)$是关于 $\hat{c}$ 的凸函数；
- 给定$\hat{c}$，$\ell_{\mathrm{SPO}+}(\cdot)$ 在$\hat{c}$处的次梯度为 $2\left(w^*(c)-\right.$ $\left.w^*(2 \hat{c}-c)\right) \in \partial \ell_{\mathrm{SPO}+}(\hat{c}, c)$

### SPO+计算

求解SPO+ERM问题的方法：1. 基于对偶理论的凸优化方法；2. 基于梯度下降；
假设可行域为一个多面体区域 $S=\{w: A w \geq b\}$，正则化$SPO+ERM$问题等价：
$$

\begin{aligned}

\min _{B, p} & \frac{1}{n} \sum_{i=1}^n\left[-b^T p_i+2\left(w^*\left(c_i\right) x_i^T\right) \bullet B-z^*\left(c_i\right)\right]+\lambda \Omega(B) \\

& \text { s.t. } A^T p_i=2 B x_i-c_i \quad \text { for all } i \in\{1, \ldots, n\} \\

& p_i \in \mathbb{R}^{m, p_i \geq 0 \quad \text { for all } i \in\{1, \ldots, n\}}\\

& B \in \mathbb{R}^{d \times p}

\end{aligned}

$$
$$
\ell_{\mathrm{SPO}}(\hat{c}, c)=\max _{w \in W^*(\dot{c})}\left\{c^T w-\alpha \hat{c}^T w\right\}+\alpha z^*(\hat{c})-z^*(c)
$$

16
Elmachtoub and Grigns: Smart -Prodiet, then Optimize"
since $z^*(\hat{c})=\hat{c}^T w$ for all $w \in W^*(\hat{c})$. Clearly, replacing the constraint $w \in W^*(\hat{c})$ with $w \in S$ in (il) results in an upper bound. Since this is true for all values of $\alpha$, then

$$
\ell_{\mathrm{SPO}}(\hat{c}, c) \leq \inf _\alpha\left\{\max _{w \in S}\left\{c^T w-\alpha \hat{c}^T w\right\}+\alpha z^*(\hat{c})\right\}-z^*(c) .
$$

In fact, one can show that inequality (治) is actually an equality using duality theory, and moreover, the optimal value of $\alpha$ tends to $\infty$. Intuitively, one can see that as $\alpha$ gets large, then the term $c^T w$ in the inner maximization objective becomes negligible and the solution tends to $w^*(\alpha \hat{c})=w^*(\hat{c})$. Thus, as $\alpha$ tends to $\infty$, the inner maximization over $S$ can be replaced with maximization over $W^*(\hat{c})$, which recovers (5i). We formalize this equivalence in Proposition below.

Proposition 2 (Dual Representation of SPO Loss). For any cost vector prediction $\hat{c} \in \mathbb{R}^d$ and realized cost vector $c \in \mathbb{R}^d$, the function $\alpha \mapsto \max _{w \in S}\left\{c^T w-\alpha \hat{c}^T w\right\}+\alpha z^*(\hat{c})$ is monotone decreasing on $\mathbb{R}$, and the true SPO loss function may be expressed as

$$
\ell_{\mathrm{SPO}}(\hat{c}, c)=\lim _{\alpha \rightarrow \infty}\left\{\max _{w \in \mathcal{S}}\left\{c^T w-\alpha \hat{c}^T w\right\}+\alpha z^*(\hat{c})\right\}-z^*(c) .
$$

Using Proposition we shall now revist the SPO ERM problem (四) which can be written as

$$
\begin{aligned}
& \min _{f \in \mathcal{H}} \frac{1}{n} \sum_{i=1}^n \lim _{i_i \rightarrow \infty}\left\{\max _{w \in S}\left\{c_i^T w-\alpha_i f\left(x_i\right)^T w\right\}+\alpha_i z^*\left(f\left(x_i\right)\right)\right\}-z^*\left(c_i\right) \\
= & \min _{f \in \mathcal{H}} \frac{1}{n} \sum_{i=1}^n \lim _{i_i \rightarrow \infty}\left\{\max _{w \in \mathcal{S}}\left\{c_i^T w-\alpha_i f\left(x_i\right)^T w\right\}+\alpha_i f\left(x_i\right)^T w^*\left(\alpha_i f\left(x_i\right)\right)\right\}-z^*\left(c_i\right) \\
= & \min _{f \in \mathcal{H}} \frac{1}{n} \lim _{a \rightarrow \infty}\left\{\sum_{i=1}^n \max _{w \in S}\left\{c_i^T w-\alpha f\left(x_i\right)^T w\right\}+\alpha f\left(x_i\right)^T w^*\left(\alpha f\left(x_i\right)\right)-z^*\left(c_i\right)\right\} \\
\leq & \min _{f \in \mathcal{H}} \frac{1}{n} \sum_{i=1}^n \max _{w \in S}\left\{c_i^T w-2 f\left(x_i\right)^T w\right\}+2 f\left(x_i\right)^T w^*\left(2 f\left(x_i\right)\right)-z^*\left(c_i\right) \\
\leq & \min _{f \in \mathcal{H}} \frac{1}{n} \sum_{i=1}^n \max _{w \in S}\left\{c_i^T w-2 f\left(x_i\right)^T w\right\}+2 f\left(x_i\right)^T w^*\left(c_i\right)-z^*\left(c_i\right) .
\end{aligned}
$$

第一个等式来自以下事实：对于任何 $\alpha_i>0, \mathrm{z}^*\left(\alpha_i \mathrm{f}(\mathrm{x}\right.$ $i))=\alpha_i \mathrm{Z}^*\left(\mathrm{f}\left(\mathrm{x}_i\right)\right)$ 。第二个等式来自以下观察：所有 $\alpha_i$ 个变量都趋向于相同的值，因此我们可以用一个变量替换它们，我们称之为 $\alpha$ 。第一个不等式来自命题 2 ，具体来说, 在 (6) 中设置 $\alpha=2$ 会导致 SPO 损失的上限（我们将在下文中重新讨论这个特定的选择）。最后，第二个不等式来自以下事实：
 $\mathrm{w}^*\left(\mathrm{c}_i\right)$ 是 $\mathrm{P}\left(2 \mathrm{f}\left(\mathrm{x}_i\right)\right)$ 的可行解。
（9）中的加数表达式正是我们所说的 SPO+ 损失函数 ，我们在定义 3 中对其进行了正式陈述。

定义 3 (SPO+ Loss)。给定成本向量预测 c 和实际成本向量 $\mathrm{c}, \mathrm{SPO}+$ 损失定义为
$$\left.\ell_{\mathrm{SPO}+}(\hat{c}, \mathrm{c}\right) :=\max _{w \in S}\left\{\mathrm{c}^T \mathrm{w}-2 \hat{\mathrm{c}}^T \mathrm{w}\right\}+2 \hat{\mathbf{c}}^T \mathrm{w}^*(\mathrm{c})-\mathrm{z}^*(\mathrm{c})
$$

回想一下， $\xi_S(\cdot)$ 是 S 的支持函数，即$\xi_S(\mathrm{c}):=\max$ $w \in S\left\{c^T \mathbf{w}\right\}$
使用此符号, SPO+ 损失可以等效地表示为 $\ell_{\mathrm{SPO}+}(\hat{\mathrm{c}}, \mathrm{c})=\xi_{\mathrm{s}}(\mathrm{c}-2 \hat{\mathrm{c}})+2 \hat{\mathrm{c}}^T \mathrm{w}^*(\mathrm{c})-\mathrm{z}^*(\mathrm{c}) 。$

凸代理 SPO+ 损失函数推导的最后一步 (9) 涉及使用一阶展开式近似凹 (非凸) 函数 $z^*(\cdot)$ 。也就是说，我们
应用边界 $\mathrm{z}^*\left(2 \mathrm{f}\left(\mathrm{x}_i\right)\right)=2 \mathrm{z}^*\left(\mathrm{f}\left(\mathrm{x}_i\right)\right) \leq 2 \mathrm{f}\left(\mathrm{x}_i\right)^T \mathrm{w}^*\left(\mathrm{c}_i\right)$
这可以看作是基于在 $\mathrm{c}_i$ (处计算的超梯度对 $\mathrm{z}^*\left(\mathrm{f}\left(\mathrm{x}_i\right)\right)$ 的一阶近似，即 $\mathrm{w}^*\left(\mathrm{c}_i\right) \in \partial \mathrm{z}^*\left(\mathrm{c}_i\right)$ )。请注意，如果 $\mathrm{f}\left(\mathrm{x}_i\right)=\mathrm{c}_i$则 $\ell_{\mathrm{SPO}}\left(\mathrm{f}\left(\mathrm{x}_i\right), \mathrm{c}_i\right)=\ell_{\mathrm{SPO}+}\left(\mathrm{f}\left(\mathrm{x}_i\right), \mathrm{c}_i\right)=0$, 这意味着当最小化 SPO+ 时, 直观地讲, 我们试图让 $\mathrm{f}\left(\mathrm{x}_i\right)$ 接近 $\mathrm{c}_i$

因此，人们可能期望 $\mathrm{w}^*\left(\mathrm{c}_i\right)$ 是 $\mathrm{P}\left(2 \mathrm{f}\left(\mathrm{x}_{\mathrm{i}}\right)\right)$ 的近乎最优解，因此，不等式 (9) 将是一个合理的近似值。事实上第 4 节在某些假设下提供了一致性属性，这些假设表明, 如果预测模型在足够大的数据集上进行训练, 则预测 $\mathrm{f}\left(\mathrm{x}_i\right)$ 确实合理接近 $\mathrm{c}_i$ 的预期值。

更正式地，我们让 D 表示 $(\mathrm{x}, \mathrm{c})$ 的分布，即 $(\mathrm{x}, \mathrm{c}) \sim$ D, 并考虑真实 SPO 风险（贝叶斯风险）最小化问题的总体版本:
$$
\min _f \mathbb{E}_{(x, c) \sim \mathcal{D}}\left[\ell_{\mathrm{SPO}}(f(x), c)\right],
$$
以及 SPO+ 风险最小化问题的人口版本:
$$
\min _f \mathbb{E}_{(x, c) \sim \mathcal{D}}\left[\ell_{\mathrm{SPO}+}(f(x), c)\right]
$$
注意这里我们对 $\mathrm{f}(\cdot)$ 没有任何限制，这意味着 H 由任何将特征映射到成本向量的可测函数组成。
定义4（费希尔一致性）。如果 $\arg _{\min }^f \mathrm{E}_{(x, c) \sim \mathcal{D}}[\ell(\mathrm{f}(\mathrm{x}), \mathrm{c})]$ ( $\ell$ 的贝叶斯风险的最小化器集合) 也最小化 (11)，则损失函数 $\ell(,$,$) 被认为与 SPO 损失具有费希尔一致性。$

为了直观理解，我们让 $\mathrm{f}_{\mathrm{SPO}}^*$ 和 $\mathrm{f}_{\mathrm{SPO}+}^*$ 分别表示 (11)和 (12) 的任意最优解。从 (1) 可以看出， $\mathrm{f}_{\mathrm{SPO}}^*(\mathrm{x})$ 的理想值就是 $E[c \mid x]$ 。事实上, 只要 $P(E[c \mid x])$ 的最优解以概率 1 唯一（在 $x \in X$ 的分布上），即几乎肯定唯一，那么 $\mathrm{E}[\mathrm{c} \mid \mathrm{x}]$ 确实是 (11) 的最小化器（参见命题 5）。此外 , 任何几乎肯定等于 $\mathrm{E}[\mathrm{c} \mid \mathrm{x}]$ 的函数也是 (11) 的最小化器。在定理1中, 我们表明, 在假设 1 下, SPO+ 人口风险 (12) 的任何最小化器都必须几乎肯定满足 $\mathrm{f}_{\mathrm{SPO}+}^*(\mathrm{x}$ $)=\mathrm{E}[\mathrm{c} \mid \mathrm{x}]$ ，因此也最小化了 SPO 风险（11）。总之，在假设 1 下, SPO+ 损失与 SPO 损失是 Fisher 一致的。
