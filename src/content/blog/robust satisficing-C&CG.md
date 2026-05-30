---
title: "两阶段 robust satisficing（RS）模型及其 CCG（column-and-constraint generation） 求解"
date: 2026-5-30 11:28:00 +0800
---

## 设定

设一阶段决策为 $x\in X\subseteq \mathbb R^{n_x}$，二阶段线性递补值函数为
$$
Q(x,\xi):=\min_{y\ge 0}\Bigl\{q^\top y:\ Wy\ge h+H\xi-Tx\Bigr\},
$$
其中 $\xi\in\Xi=[\underline\xi,\overline\xi]\subseteq\mathbb R^m$。给定目标值 $Z\in\mathbb R$，定义超额损失
$$
F(x,\xi):=c^\top x+Q(x,\xi)-Z.
$$
经验参考分布取为
$$
\widehat P_N=\frac1N\sum_{i=1}^N\delta_{\widehat\xi^{\,i}},
\qquad \widehat\xi^{\,i}\in\Xi,\ i=1,\dots,N.
$$

---

## 原问题

### 定义 1（标准两阶段 $l_1$-Wasserstein RS 模型）

原始模型写为
$$
\boxed{
\begin{array}{rl}
\min_{x\in X,\ \rho\ge 0}\quad & \rho\\
\text{s.t.}\quad &
\sup_{P\in\mathcal P(\Xi)}
\Bigl\{
\mathbb E_P[F(x,\tilde\xi)]-\rho\,W_1(P,\widehat P_N)
\Bigr\}\le 0
\end{array}}
\tag{RS-W1}
$$

其中 $W_1(\cdot,\cdot)$ 为基于 $l_1$-范数的 Wasserstein 距离。

---

## 精确重构

### 定理 1（经验分布中心下的精确重构）

对任意给定 $(x,\rho)$，约束
$$
\sup_{P\in\mathcal P(\Xi)}
\Bigl\{
\mathbb E_P[F(x,\tilde\xi)]-\rho\,W_1(P,\widehat P_N)
\Bigr\}\le 0
$$
等价于
$$
\boxed{
\frac1N\sum_{i=1}^N
\sup_{\xi\in\Xi}
\Bigl\{
F(x,\xi)-\rho\|\xi-\widehat\xi^{\,i}\|_1
\Bigr\}\le 0.}
\tag{1}
$$

#### 证明

由 Wasserstein 距离定义，
$$
W_1(P,\widehat P_N)
=
\inf_{\Pi\in\Gamma(P,\widehat P_N)}
\int_{\Xi\times\Xi}\|\xi-\zeta\|_1\,\Pi(d\xi,d\zeta).
$$
故
$$
\sup_{P}
\Bigl\{
\mathbb E_P[F(x,\tilde\xi)]-\rho W_1(P,\widehat P_N)
\Bigr\}
$$
$$
=
\sup_{\Pi:\,\Pi_\zeta=\widehat P_N}
\int_{\Xi\times\Xi}
\Bigl(F(x,\xi)-\rho\|\xi-\zeta\|_1\Bigr)\,\Pi(d\xi,d\zeta).
$$
由于
$$
\widehat P_N=\frac1N\sum_{i=1}^N\delta_{\widehat\xi^{\,i}},
$$
任意满足 $\Pi_\zeta=\widehat P_N$ 的联合分布均可写为
$$
\Pi(d\xi,d\zeta)=\frac1N\sum_{i=1}^N \nu_i(d\xi)\,\delta_{\widehat\xi^{\,i}}(d\zeta),
$$
其中 $\nu_i\in\mathcal P(\Xi)$。于是上式化为
$$
\frac1N\sum_{i=1}^N
\sup_{\nu_i\in\mathcal P(\Xi)}
\int_\Xi
\Bigl(F(x,\xi)-\rho\|\xi-\widehat\xi^{\,i}\|_1\Bigr)\nu_i(d\xi).
$$
对每个 $i$，最优 $\nu_i$ 可退化为单点分布，从而得到
$$
\frac1N\sum_{i=1}^N
\sup_{\xi\in\Xi}
\Bigl\{
F(x,\xi)-\rho\|\xi-\widehat\xi^{\,i}\|_1
\Bigr\}.
$$
证毕。

---

### 命题 1（半无限规划形式）

模型 $(RS\text{-}W1)$ 等价于如下半无限规划：
$$
\boxed{
\begin{array}{rl}
\min_{x,\rho,\eta}\quad & \rho\\
\text{s.t.}\quad & \frac1N\sum_{i=1}^N \eta_i\le 0,\\
& \eta_i\ge c^\top x+Q(x,\xi)-Z-\rho\|\xi-\widehat\xi^{\,i}\|_1,
\quad \forall \xi\in\Xi,\ \forall i=1,\dots,N,\\
& x\in X,\ \rho\ge 0
\end{array}}
\tag{SIP}
$$

#### 证明（命题 1）

由定理 1，原问题约束等价于
$$
\frac1N\sum_{i=1}^N \sup_{\xi\in\Xi}
\Bigl\{
c^\top x+Q(x,\xi)-Z-\rho\|\xi-\widehat\xi^{\,i}\|_1
\Bigr\}\le 0.
$$
对每个样本 $i$ 引入上图变量 $\eta_i$，使其逐点上界对应的 supremum，即得结论。证毕。

---

## CCG 主问题

设第 $k$ 次迭代时，样本 $i$ 已生成场景集合为
$$
\Omega_i^k=\{\xi_i^1,\dots,\xi_i^{L_i^k}\}\subseteq\Xi.
$$

### 命题 2（受限主问题）

在 $\Omega_i^k$ 上截断半无限约束，得到 CCG 的主问题：
$$
\boxed{
\begin{array}{rl}
\min_{x,\rho,\eta,\{y_i^\ell\}}\quad & \rho\\
\text{s.t.}\quad & \frac1N\sum_{i=1}^N \eta_i\le 0,\\
& \eta_i\ge c^\top x+q^\top y_i^\ell-Z-\rho\|\xi_i^\ell-\widehat\xi^{\,i}\|_1,
\quad \forall i,\ \forall \ell=1,\dots,L_i^k,\\
& Wy_i^\ell\ge h+H\xi_i^\ell-Tx,
\quad y_i^\ell\ge 0,
\quad \forall i,\ \forall \ell=1,\dots,L_i^k,\\
& x\in X,\ \rho\ge 0
\end{array}}
\tag{MP_k}
$$

#### 证明（命题 2）

对半无限约束
$$
\eta_i\ge c^\top x+Q(x,\xi)-Z-\rho\|\xi-\widehat\xi^{\,i}\|_1
$$
仅在 $\Omega_i^k$ 上保留。又因
$$
Q(x,\xi_i^\ell)=\min_{y\ge 0}\{q^\top y:\ Wy\ge h+H\xi_i^\ell-Tx\},
$$
故对每个已生成场景复制一套二阶段变量 $y_i^\ell$，即得主问题。证毕。

---

## 分离子问题

设 $(x^k,\rho^k,\eta^k)$ 为 $MP_k$ 的最优解。

### 命题 3（分离子问题的原始形式）

对每个样本 $i$，其最坏违反值由下式给出：
$$
\boxed{
\Psi_i(x^k,\rho^k):=
\max_{\xi\in\Xi}
\Bigl\{
c^\top x^k+Q(x^k,\xi)-Z-\rho^k\|\xi-\widehat\xi^{\,i}\|_1
\Bigr\}.}
\tag{SP_i}
$$
若
$$
\Psi_i(x^k,\rho^k)>\eta_i^k,
$$
则对应最优场景 $\xi_i^\star$ 产生一条被违反的半无限约束，应加入 $\Omega_i^k$。

#### 证明（命题 3）

这是半无限约束的直接可行性检验：当前解对样本 $i$ 可行，当且仅当
$$
\eta_i^k\ge
\sup_{\xi\in\Xi}
\Bigl\{
c^\top x^k+Q(x^k,\xi)-Z-\rho^k\|\xi-\widehat\xi^{\,i}\|_1
\Bigr\}.
$$
证毕。

---

### 命题 4（分离子问题的对偶化）

若二阶段问题满足强对偶，则
$$
Q(x,\xi)=\max_{\pi\in\Pi}\ \pi^\top(h+H\xi-Tx),
\qquad
\Pi:=\{\pi\ge 0:\ W^\top\pi\le q\}.
$$
因此，$(SP_i)$ 等价于
$$
\boxed{
\begin{array}{rl}
\Psi_i(x^k,\rho^k)=\ c^\top x^k-Z+\max_{\pi,\xi,u}\quad &
\pi^\top(h+H\xi-Tx^k)-\rho^k\mathbf 1^\top u\\
\text{s.t.}\quad & W^\top\pi\le q,\ \pi\ge 0,\\
& u\ge \xi-\widehat\xi^{\,i},\quad
u\ge \widehat\xi^{\,i}-\xi,\quad
u\ge 0,\\
& \underline\xi\le \xi\le \overline\xi
\end{array}}
\tag{DSP_i}
$$

#### 证明（命题 4）

由二阶段线性规划强对偶，
$$
Q(x^k,\xi)=\max_{\pi\ge 0,\ W^\top\pi\le q}\pi^\top(h+H\xi-Tx^k).
$$
同时，
$$
\|\xi-\widehat\xi^{\,i}\|_1
=
\min_{u\ge 0}
\{\mathbf1^\top u:\ u\ge \xi-\widehat\xi^{\,i},\ u\ge \widehat\xi^{\,i}-\xi\}.
$$
代入 $(SP_i)$ 即得。证毕。

---

## 最坏场景结构

### 命题 5（坐标三点结构）

固定 $(x^k,\rho^k)$ 与任意 $\pi\in\Pi$，记
$$
a_j(\pi):=(H^\top\pi)_j,\qquad j=1,\dots,m.
$$
则 $(DSP_i)$ 中给定 $\pi$ 后，每个坐标 $\xi_j$ 的最优取值满足
$$
\xi_j^\star\in\{\underline\xi_j,\ \widehat\xi_j^{\,i},\ \overline\xi_j\},
$$
且显式为
$$
\boxed{
\xi_j^\star=
\begin{cases}
\overline\xi_j, & a_j(\pi)>\rho^k,\\[1mm]
\widehat\xi_j^{\,i}, & |a_j(\pi)|\le \rho^k,\\[1mm]
\underline\xi_j, & a_j(\pi)<-\rho^k.
\end{cases}}
\tag{2}
$$

#### 证明（命题 5）

固定 $\pi$ 后，目标函数关于单个坐标 $\xi_j$ 的部分为
$$
\phi_j(\xi_j)=a_j(\pi)\xi_j-\rho^k|\xi_j-\widehat\xi_j^{\,i}|,
\qquad \underline\xi_j\le \xi_j\le \overline\xi_j.
$$
这是一个在 $\widehat\xi_j^{\,i}$ 处折点的分段线性函数。其左右斜率分别为
$$
a_j(\pi)+\rho^k,\qquad a_j(\pi)-\rho^k.
$$
故：

- 当 $a_j(\pi)>\rho^k$ 时，左右斜率均为正，最优点为 $\overline\xi_j$；
- 当 $a_j(\pi)<-\rho^k$ 时，左右斜率均为负，最优点为 $\underline\xi_j$；
- 当 $|a_j(\pi)|\le \rho^k$ 时，左斜率非负、右斜率非正，最优点为 $\widehat\xi_j^{\,i}$。

证毕。

---

### 推论 1（有限候选场景集）

对每个样本 $i$，分离子问题只需在有限集合
$$
\mathcal E_i=
\{\underline\xi_1,\widehat\xi_1^{\,i},\overline\xi_1\}
\times\cdots\times
\{\underline\xi_m,\widehat\xi_m^{\,i},\overline\xi_m\}
$$
上寻找最坏场景，故
$$
|\mathcal E_i|\le 3^m.
$$

---

## 收敛性

### 定理 2（最优性判别）

若第 $k$ 次迭代的主问题最优解 $(x^k,\rho^k,\eta^k)$ 满足
$$
\Psi_i(x^k,\rho^k)\le \eta_i^k,\qquad \forall i=1,\dots,N,
$$
则 $(x^k,\rho^k)$ 为原始模型 $(RS\text{-}W1)$ 的最优解。

#### 证明（定理 2）

上述条件表明当前解满足半无限约束的全部约束，因此对 $(SIP)$ 可行，也即对原问题可行。另一方面，$MP_k$ 是 $(SIP)$ 的松弛，其最优值不大于原问题最优值；而当前解既是 $MP_k$ 的最优解，又对原问题可行，故二者目标值相等，从而当前解即为原问题最优解。证毕。

---

### 定理 3（有限终止）

若算法每次对任一被违反的样本 $i$ 至少加入一个新场景 $\xi_i^\star\notin\Omega_i^k$，则 CCG 在有限步内终止。

#### 证明（定理 3）

由推论 1，对每个样本 $i$ 可加入的候选场景集合 $\mathcal E_i$ 有限，且
$$
|\mathcal E_i|\le 3^m.
$$
因此总可加入场景数有限。算法每次未终止时至少加入一个新场景，故只能有限次更新，必有限终止。终止时由定理 2 得最优性。证毕。

---

## 算法

**算法 1：两阶段 $l_1$-Wasserstein RS 的 CCG**

---

| 步骤 | 内容 |
|:---:|:---|
| 0 | **初始化**：对每个 $i=1,\dots,N$，置 $\Omega_i^0=\{\widehat\xi^{\,i}\}$，令 $k=0$。 |
| 1 | **求解主问题**：求解 $MP_k$，得到最优解 $(x^k,\rho^k,\eta^k)$。 |
| 2 | **分离**：对每个 $i=1,\dots,N$，求解分离子问题 $SP_i$（或其对偶形式 $DSP_i$），得到 $\Psi_i(x^k,\rho^k)$ 及最坏场景 $\xi_i^\star$。 |
| 3 | **最优性检验**：若对所有 $i$ 都有 $\Psi_i(x^k,\rho^k)\le \eta_i^k$，则停止，并输出 $(x^k,\rho^k)$。 |
| 4 | **场景扩充**：对所有满足 $\Psi_i(x^k,\rho^k)>\eta_i^k$ 的样本 $i$，更新 $\Omega_i^{k+1}=\Omega_i^k\cup\{\xi_i^\star\}$；其余样本令 $\Omega_i^{k+1}=\Omega_i^k$。 |
| 5 | **迭代**：令 $k\leftarrow k+1$，返回步骤 1。 |
