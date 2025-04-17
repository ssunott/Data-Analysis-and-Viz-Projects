# 📊 Data Visualization Projects

This repository showcases two Power BI dashboards developed as part of a college-level data analytics course. Each project focuses on transforming raw data into actionable insights using end-to-end processes including data preparation, modeling, and dashboard design.

---

## 🚑 Project 1: Hospital Data Analytics Dashboard

### 🎯 Objective
To design and implement a relational database and create interactive dashboards for hospital staff to monitor patient care, department performance, and financial health.

### 🛠 Tools & Technologies
- Microsoft Excel (for data preparation)
- Azure Blob Storage & Azure SQL Database
- SQL Server Management Studio (SSMS)
- Power BI (DirectQuery mode)

### 📌 Features
- **Three dashboards**, each tailored for a user group:
  - **Patient Care** (Doctors): appointment history, demographics
  - **Operations Metrics** (Administrators): occupancy, staff workload
  - **Financial & Supply Metrics** (Finance/Inventory Teams): billing, medicine supply

### 📈 Key Visual Insights
- Doctor workloads and working hours
- Room occupancy by type (ICU, Private, General)
- Revenue by department and unpaid bill ratios
- Gender and age distribution across departments
- Peak appointment days and seasonal trends

### 📎 Data Strategy
- Synthetic hospital data generated with ChatGPT and Excel
- SQL views created for each business question
- Power BI dashboards connected using DirectQuery

---

## 🌍 Project 2: Global Life Expectancy Analysis and Prediction

### 🎯 Objective
To analyze global and regional life expectancy trends and build a predictive model using socioeconomic indicators.

### 🛠 Tools & Technologies
- Data Sources: World Bank, Our World In Data, IPSOS, StatsCan
- Excel & Power BI for data modeling and visuals
- Python (Scikit-learn) for prediction modeling

### 📌 Features
- Multi-source global health and economic datasets (1960–2022)
- Predictive model using Linear Regression and SVM (2020–2029)
- Categorized and normalized data using DAX and Power Query
- Interactive filters: country, year, region, gender

### 📈 Key Visual Insights
- Historical trends in life expectancy and death rate
- Gender disparities in life expectancy
- Health expenditure and GDP vs life expectancy
- Opioid crisis impact in Canada
- Top global causes of death
- Regional life expectancy imbalance across Canadian provinces

---

## 🧠 Methodology Overview

1. **Data Preparation**: Sourcing, cleaning, reshaping (e.g., unpivoting wide datasets), and type formatting
2. **Modeling**: Creating relationships, DAX measures, and categorical columns
3. **Visualization**: Using diverse visual types — cards, pie charts, heat maps, scatter plots, maps
4. **Prediction (Life Expectancy)**:
   - Feature engineering: death rate, GDP, population, year
   - Models: Linear Regression & SVM
   - Evaluation: R² > 0.9 (Linear), R² > 0.975 (SVM)

---

