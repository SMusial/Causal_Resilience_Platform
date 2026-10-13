# Chapter 13: Standardization and the Parametric G-Formula

**Applied Causal Inference Series**  
*Use Case: “Did the Retention Offer Actually Reduce Churn?”*

---

## Executive Summary

Chapters 11 and 12 introduced model-based causal inference, demonstrating how **Inverse Probability (IP) Weighting** models the treatment mechanism $f(A \mid L)$ (the propensity score) to create a pseudo-population where confounders $L$ are unassociated with treatment $A$.

**Chapter 13** presents the primary alternative approach to conditional adjustment: **Standardization** (also known as the **Parametric G-Formula**). Rather than modeling who receives treatment, standardization models the **outcome mechanism** $E[Y \mid A, L]$. Under conditional exchangeability, positivity, and consistency, the parametric g-formula fits an outcome regression model $\hat{E}[Y \mid A, L]$ and marginalizes (averages) predicted counterfactual outcomes across the empirical distribution of baseline customer covariates $L$.

### Core Takeaway
- **IP Weighting** models the *treatment process* $f(A \mid L)$.
- **Standardization / Parametric G-Formula** models the *outcome process* $E[Y \mid A, L]$.
- Both methods yield unbiased estimates of population counterfactual risks $E[Y^a]$ and Average Causal Effects (ACE) under exchangeability, positivity, consistency, and correct model specification.

---

## 13.1 Nonparametric vs. Parametric Standardization

### Nonparametric Standardization
In a discrete setting with a small vector of confounders $L$, the standardized risk under treatment level $a$ is computed by taking a weighted average of conditional outcome risks across confounder strata $l$:

$$\Pr[Y^a = 1] = \sum_l \Pr[Y = 1 \mid A = a, L = l] \times \Pr[L = l]$$

### The High-Dimensional Breakdown
In enterprise Customer Relationship Management (CRM) databases, baseline covariates $L = (L_1, L_2, \dots, L_p)$ include continuous variables (customer tenure, monthly bill, data usage) and multi-category traits (support ticket history, plan type).
- When $L$ is high-dimensional or continuous, most confounder strata $l$ contain zero or very few subscribers.
- Nonparametric conditional means $\hat{\Pr}[Y = 1 \mid A = a, L = l]$ cannot be computed ($0/0$).
- **Solution**: Replace the nonparametric stratum-specific means with a **parametric outcome regression model** $\hat{E}[Y \mid A, L]$.

---

## 13.2 Algorithm for the Parametric G-Formula

The parametric g-formula for a binary outcome (e.g., customer churn $Y \in \{0, 1\}$) and treatment (retention offer $A \in \{0, 1\}$) proceeds in three distinct computational steps:

### Step 1: Fit the Outcome Regression Model
Using the observed dataset of $n$ subscribers, fit a parametric model for the conditional expectation $E[Y \mid A, L]$ (e.g., a logistic regression model):

$$\text{logit} \,\Pr[Y = 1 \mid A, L] = \theta_0 + \theta_1 A + \boldsymbol{\theta}_2^T L + \theta_3 (A \times L)$$

where $\theta_1$ captures the main effect of the offer, $\boldsymbol{\theta}_2$ captures baseline covariate risk, and $\theta_3$ allows for treatment effect modification.

### Step 2: Predict Counterfactual Outcomes
For **every single subscriber $i$** in the database ($i = 1, \dots, n$), construct two counterfactual datasets:
1. **Force $A_i = 1$**: Predict $\hat{Y}_i^{a=1} = \hat{\Pr}[Y = 1 \mid A = 1, L_i]$ using subscriber $i$'s actual baseline covariates $L_i$.
2. **Force $A_i = 0$**: Predict $\hat{Y}_i^{a=0} = \hat{\Pr}[Y = 1 \mid A = 0, L_i]$ using subscriber $i$'s actual baseline covariates $L_i$.

### Step 3: Empirical Standardization (Averaging)
Average these predicted counterfactual outcomes across the entire sample of $n$ subscribers:

$$\widehat{\Pr}[Y^{a=1} = 1] = \frac{1}{n} \sum_{i=1}^n \hat{\Pr}[Y = 1 \mid A = 1, L_i]$$

$$\widehat{\Pr}[Y^{a=0} = 1] = \frac{1}{n} \sum_{i=1}^n \hat{\Pr}[Y = 1 \mid A = 0, L_i]$$

The estimated **Average Causal Risk Difference (RD)** is:

$$\widehat{RD} = \widehat{\Pr}[Y^{a=1} = 1] - \widehat{\Pr}[Y^{a=0} = 1]$$

---

## 13.3 CRM Applied Use Case: Evaluating Retention Offers

### Dataset Context
A telecom firm evaluates a retention discount $A \in \{0, 1\}$ targeted at subscribers. The CRM database tracks continuous tenure $L_1$ (months), monthly spend $L_2$ ($), and support tickets $L_3$. High-risk, low-tenure customers were disproportionately targeted.

### Model Specification & Results
1. **Outcome Model**:
   $$\text{logit} \,\Pr[Y = 1 \mid A, L] = -1.2 - 0.65 A - 0.04 L_1 + 0.01 L_2 + 0.35 L_3 - 0.02 (A \times L_1)$$

2. **Counterfactual Predictions**:
   - $\widehat{\Pr}[Y^{a=1} = 1] = 0.142$ (14.2% projected churn if ALL subscribers receive the offer).
   - $\widehat{\Pr}[Y^{a=0} = 1] = 0.228$ (22.8% projected churn if NO subscribers receive the offer).

3. **Causal Effect Estimates**:
   - **Risk Difference (RD)**: $0.142 - 0.228 = -0.086$ (8.6 percentage point absolute reduction in churn).
   - **Risk Ratio (RR)**: $0.142 / 0.228 = 0.623$ (37.7% relative churn reduction).

---

## 13.4 IP Weighting vs. Standardization: A Comparative Analysis

| Feature | Inverse Probability (IP) Weighting | Standardization (Parametric G-Formula) |
| :--- | :--- | :--- |
| **Primary Model Target** | Treatment Mechanism $f(A \mid L)$ (Propensity Score) | Outcome Mechanism $E[Y \mid A, L]$ |
| **Sensitivity to Positivity Near-Violations** | **High**: Extremely small propensity scores yield huge weights $W^A$, inflating variance. | **Low / Hidden**: Predicts via model extrapolation; avoids wild weights but risks structural misspecification. |
| **Effect Modification** | Requires fitting Moderated MSMs $SW^A(V)$. | Straightforward: Include interaction terms $(A \times V)$ in outcome regression. |
| **Continuous Treatments** | Requires density estimation $f(A \mid L)$ for weights. | Models response curves directly $E[Y \mid A=a, L]$ across continuous dosage $a$. |
| **Nuisance Model Requirement** | Unbiased if $f(A \mid L)$ is correctly specified. | Unbiased if $E[Y \mid A, L]$ is correctly specified. |

---

## 13.5 Doubly Robust Estimation: The Best of Both Worlds

When modeling observational data, we face a dilemma:
- If our propensity score model $f(A \mid L)$ is misspecified, IP weighting is biased.
- If our outcome regression model $E[Y \mid A, L]$ is misspecified, standardization is biased.

### Doubly Robust (DR) Estimator
A **Doubly Robust Estimator** (e.g., Augmented IPW or Targeted Maximum Likelihood Estimation / TMLE) combines both models:

$$\widehat{E}[Y^a]_{DR} = \frac{1}{n} \sum_{i=1}^n \left[ \frac{I(A_i = a) Y_i}{\hat{f}(A_i \mid L_i)} - \frac{I(A_i = a) - \hat{f}(a \mid L_i)}{\hat{f}(a \mid L_i)} \hat{E}[Y \mid A = a, L_i] \right]$$

### The Doubly Robust Property
The estimator $\widehat{E}[Y^a]_{DR}$ is **consistent for the true counterfactual mean $E[Y^a]$** if **EITHER** the propensity score model $\hat{f}(A \mid L)$ **OR** the outcome regression model $\hat{E}[Y \mid A, L]$ is correctly specified.

---

## Summary Checklist for Applied Analysts

1. **Choose the Nuisance Model**: Decide whether treatment assignment $f(A \mid L)$ or outcome determination $E[Y \mid A, L]$ is easier to model with domain knowledge.
2. **Check Positivity**: If propensity scores are near 0 or 1, standardization or doubly robust estimation is preferred over standard IP weighting.
3. **Use Bootstrap for CIs**: Obtain standard errors and 95% confidence intervals for g-formula estimates by nonparametrically bootstrapping the entire 3-step pipeline.
4. **Consider Doubly Robust Estimators**: In critical business or clinical decisions, deploy DR estimators to protect against single-model misspecification.
