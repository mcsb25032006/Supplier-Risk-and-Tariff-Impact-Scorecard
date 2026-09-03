# Technical Interview Walkthrough & Defense Guide

This guide provides precise, senior-level explanations for explaining and defending every design decision in the **Supplier Risk & Tariff-Impact Scorecard** during technical interviews.

---

## 1. Project Objective & Core Business Problem

### Question: "What problem does this project solve?"
> **Senior Answer:**  
> "In supply chain procurement, sourcing managers often make decisions based strictly on quoted purchase price (FOB/EXW). However, in volatile trade environments, quoted price is misleading. For example, a datacenter hardware supplier in China might offer server chassis at \$14,000 unit price compared to \$18,000 from a US domestic supplier. Once you account for a 35% effective tariff surcharge (Section 301 + Section 122), 39-day average lead time with 15.4-day standard deviation, and customs clearance friction, the true *landed cost* and operational risk completely change the sourcing economics.  
> 
> This project builds an end-to-end data analytics system that calculates true landed costs, measures delivery reliability and lead-time volatility, generates explainable composite supplier risk scores, and simulates what-if tariff escalation scenarios across SQL, Excel, Python, and Power BI."

---

## 2. Architecture & Technology Stack Rationale

### Question: "Why did you choose this technology stack?"
> **Senior Answer:**  
> "We intentionally built a unified 4-tier computational model:
> 1. **SQL (SQLite / DDL / Views):** Acts as the relational diagnostic layer, allowing data engineers to audit data quality (duplicate POs, missing invoice costs) and write set-based analytical queries using window functions and aggregations.
> 2. **Python (`src/scorecard`):** Provides the production pipeline orchestrator with schema validation (Pydantic), data cleaning, statistical risk scoring, what-if scenario simulations, historical snapshot tracking, and automated reporting.
> 3. **Excel (`openpyxl` with dynamic formulas):** Sourcing committees and category managers live in Excel. We programmatically built an interactive workbook with live formulas (`INDEX/MATCH`, `SUMIFS`, `AVERAGEIFS`, `SUMPRODUCT`-based standard deviation) and dynamic dropdown toggles.
> 4. **Power BI & DAX:** Delivers executive dashboards with interactive slicers, star schema data modeling, and robust DAX measures for executive review."

---

## 3. Key Design Decisions & Parity Engineering

### Question: "How did you ensure consistency across SQL, Python, Excel, and Power BI?"
> **Senior Answer:**  
> "A major vulnerability in enterprise reporting is metric divergence—where SQL, Python, Excel, and BI tools report slightly different numbers due to subtle calculation differences. We enforced absolute mathematical parity through three rules:
> 1. **Deduplication Rule:** All four layers implement the exact same first-occurrence deduplication filter (`Is_First_Occurrence == 1`).
> 2. **Variance Calculation:** All four layers use the *population* standard deviation (degrees of freedom = 0; `STDEVX.P` in DAX, `std(ddof=0)` in Pandas, `SQRT(AVG(x^2) - AVG(x)^2)` in SQLite, and `SUMPRODUCT` in Excel).
> 3. **Standardized Risk Formula:** The 4-factor risk weights (30% On-Time, 20% Lead-Time Volatility with 20-day cap, 25% Tariff Exposure, 25% Quality) and RAG thresholds (<15 Green, 15–29.9 Yellow, $\ge 30$ Red) are strictly identical across every tool."

---

## 4. Key Sourcing Findings (The Data Story)

| Supplier | Origin / Region | On-Time % | Lead Time | Landed Spend | Tariff Exposure | Risk Score | RAG Status |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Bajio Precision Systems** | Mexico (Nearshore) | **86.8%** | 18.1d (±6.5) | \$17.24M | 0.0% | **11.7** | 🟢 **Green** |
| **TitanForge Components** | United States (Domestic) | 84.2% | 12.5d (±5.8) | \$15.41M | 0.0% | **11.9** | 🟢 **Green** |
| **Zhongxin Compute Mfg.** | China (Offshore) | 73.0% | 39.0d (±15.4) | \$15.80M | 35.0% | **33.5** | 🔴 **Red** |

### Key Takeaway:
- China's quoted price was significantly cheaper, but after \$4.10M in tariffs and high lead-time volatility, its risk score reached **33.5 (Red Tier)**.
- Mexico (Bajio) emerged as the overall lowest-risk sourcing partner (**11.7 Green**), benefiting from USMCA zero-tariff qualification and shorter transit lead times.

---

## 5. Limitations & Future Enhancements

### Existing Limitations:
1. **Synthetic Sample Size:** The current dataset models 3 suppliers and 340 POs across datacenter categories.
2. **Deterministic Tariff Schedules:** Tariff rates are based on published July 2026 conditions rather than live real-time CBP API integrations.

### Three Realistic Future Enhancements:
1. **Direct ERP & API Connectors:** Replace CSV drop ingestion with automated REST connectors to Coupa/SAP Ariba and live CBP/USTR tariff schedule APIs.
2. **Machine Learning Lead-Time Forecasting:** Implement XGBoost/LightGBM regression models to predict port congestion delays and lead-time anomalies based on seasonality and customs clearance historical trends.
3. **Multi-Echelon Safety Stock Optimizer:** Integrate the lead-time standard deviation metric directly into an inventory reorder point ($ROP = d \times L + z \times \sigma_L \times \sqrt{d}$) optimization engine.
