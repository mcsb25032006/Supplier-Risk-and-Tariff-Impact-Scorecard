# Methodology & Risk Scoring Derivations

## Executive Summary

The **Supplier Risk & Tariff-Impact Scorecard** replaces subjective, opaque supplier ratings with an **explainable, deterministic mathematical model**. Sourcing decisions frequently rely on quoted unit prices while neglecting logistics delays, quality fallout, and tariff escalations. This methodology defines the rigorous mathematical formulas used across all project layers.

---

## 1. Core Key Performance Indicator (KPI) Definitions

### A. On-Time Delivery Rate
Measures the proportion of delivered orders received on or before the contractual promised delivery date:

$$\text{On-Time Delivery Rate} = \frac{\sum_{i=1}^{N_{\text{del}}} \mathbb{I}(\text{Actual\_Delivery\_Date}_i \le \text{Promised\_Delivery\_Date}_i)}{N_{\text{del}}}$$

*Where $N_{\text{del}}$ is the total number of delivered POs.*

### B. Lead-Time & Lead-Time Volatility
Lead time represents the calendar days elapsed between PO placement and warehouse receipt:

$$\text{Lead\_Time\_Days}_i = \text{Actual\_Delivery\_Date}_i - \text{PO\_Date}_i$$

$$\mu_{\text{LT}} = \frac{1}{N_{\text{del}}} \sum_{i=1}^{N_{\text{del}}} \text{Lead\_Time\_Days}_i$$

Lead-time unpredictability creates stockout risk and forces buffer inventory. We compute the **population standard deviation** ($\sigma_{\text{LT}}$, ddof = 0) to ensure mathematical alignment across Python, SQL (`VAR_POP`), DAX (`STDEVX.P`), and Excel:

$$\sigma_{\text{LT}} = \sqrt{\frac{1}{N_{\text{del}}} \sum_{i=1}^{N_{\text{del}}} (\text{Lead\_Time\_Days}_i - \mu_{\text{LT}})^2}$$

### C. Landed Cost & Tariff Exposure
The landed cost per unit accounts for customs duties and statutory trade surcharges:

$$\text{Landed\_Cost\_Per\_Unit} = \text{Unit\_Cost\_USD} \times (1 + \text{Base\_Effective\_Rate})$$

$$\text{Total Base Spend} = \sum (\text{Unit\_Cost\_USD} \times \text{Quantity})$$

$$\text{Total Landed Spend} = \sum (\text{Landed\_Cost\_Per\_Unit} \times \text{Quantity})$$

$$\text{Tariff Exposure \%} = \frac{\text{Total Landed Spend} - \text{Total Base Spend}}{\text{Total Base Spend}}$$

### D. Quality & Defect Rate
Calculates the proportion of purchase orders flagged with inspection failures:

$$\text{Defect Rate \%} = \frac{\sum \mathbb{I}(\text{Defect\_Flag} = \text{'Y'})}{N_{\text{del}}}$$

---

## 2. Composite Risk Score Formula

The Composite Supplier Risk Score maps multi-dimensional performance metrics to an explainable 0–100 risk index (where **0 = Lowest Risk / Top Performer**, and **100 = Maximum Risk / Unacceptable Performance**).

### Component Scoring & Normalization:
1. **Delivery Reliability Penalty ($C_{\text{OT}}$)**:
   $$C_{\text{OT}} = (1.0 - \text{On-Time Delivery Rate}) \times 100$$
2. **Lead-Time Volatility Penalty ($C_{\text{LT}}$)**:
   Normalized against a 20-day standard deviation cap ($20.0\text{ days} \implies 100\text{ penalty points}$):
   $$C_{\text{LT}} = \min\left(\frac{\sigma_{\text{LT}}}{20.0} \times 100, 100\right)$$
3. **Tariff Exposure Penalty ($C_{\text{Tariff}}$)**:
   $$C_{\text{Tariff}} = \text{Tariff Exposure \%} \times 100$$
4. **Defect Penalty ($C_{\text{Defect}}$)**:
   $$C_{\text{Defect}} = \text{Defect Rate \%} \times 100$$

### Weighted Aggregation:
$$\text{Composite Risk Score} = w_{\text{OT}} C_{\text{OT}} + w_{\text{LT}} C_{\text{LT}} + w_{\text{Tariff}} C_{\text{Tariff}} + w_{\text{Defect}} C_{\text{Defect}}$$

$$\text{Composite Risk Score} = 0.30 C_{\text{OT}} + 0.20 C_{\text{LT}} + 0.25 C_{\text{Tariff}} + 0.25 C_{\text{Defect}}$$

---

## 3. RAG Risk Tier Segmentation

| Score Range | RAG Tier | Business Action Required |
|:---:|:---:|:---|
| **0.0 – 14.9** | 🟢 **Green (Low Risk)** | Preferred supplier for core volume allocation and strategic partnerships. |
| **15.0 – 29.9** | 🟡 **Yellow (Moderate Risk)** | Acceptable supplier; requires buffer stock sizing and quarterly SLA monitoring. |
| **$\ge$ 30.0** | 🔴 **Red (Critical / High Risk)** | High-risk vendor; active tariff exposure mitigation and alternate supplier qualification required. |

---

## 4. Tariff What-If Scenario Modeling

For a given scenario $S$ with adjustment value $\Delta$ and adjustment type $T$:

- **Domestic (US)**: $\text{Rate}_S = 0.00$
- **Additive Scenario (Foreign)**:
  $$\text{Rate}_S = \max(0.00, \text{Base\_Effective\_Rate} + \Delta)$$
- **Absolute Scenario (Foreign)**:
  $$\text{Rate}_S = \Delta$$

$$\text{Scenario Landed Spend} = \text{Total Base Spend} \times (1 + \text{Rate}_S)$$

$$\text{Delta Spend} = \text{Scenario Landed Spend} - \text{Total Landed Spend}$$
