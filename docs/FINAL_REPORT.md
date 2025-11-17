# Credit Risk Scoring System with Machine Learning and AI Integration
## Final Project Report

**Author:** MLBA Final Project Team  
**Date:** November 2025  
**Institution:** [Your Institution]  
**Project Repository:** https://github.com/duckbumbum301/MLBA_FinalProject

---

## Abstract

This report presents the development of a comprehensive Credit Risk Scoring System that combines machine learning prediction models, data quality analysis, and AI-powered assistance. The system employs a role-based desktop application (PyQt6) connected to a MySQL database, featuring eight distinct machine learning algorithms for credit risk prediction, automated data quality monitoring with outlier detection and customer clustering, and an integrated Gemini AI assistant for intelligent recommendations. The system serves two user roles: regular users for prediction tasks and administrators for model management and system maintenance. Performance evaluation shows XGBoost achieving an AUC of 0.7604 as the active model, with LightGBM demonstrating superior performance at 0.7811 AUC. The system successfully processes predictions for customers with 41 credit-related features derived from 12 months of payment history, providing real-time risk assessment with confidence scores and cluster assignments.

**Keywords:** Credit Risk Scoring, Machine Learning, PyQt6, Role-Based Access Control, XGBoost, LightGBM, Model Registry, Gemini AI, Data Quality Analysis, Customer Clustering

---

## Table of Contents

1. [Data Simulation and Understanding](#chapter-1-data-simulation-and-understanding)
   - 1.1 Data Context
   - 1.2 Data Generation
   - 1.3 Data Understanding
   - 1.4 Data Analysis

2. [Methodology](#chapter-2-methodology)
   - 2.1 Programming Languages
   - 2.2 Programming Tools
   - 2.3 Machine Learning Models
   - 2.4 AI Integration with Gemini
   - 2.5 Evaluation Metrics

3. [System Architecture](#chapter-3-system-architecture)
   - 3.1 Database Schema
   - 3.2 Backend Services
   - 3.3 User Interface Components
   - 3.4 Role-Based Access Control

4. [Data Preparation and Model Building](#chapter-4-data-preparation-and-model-building)
   - 4.1 Dataset Import
   - 4.2 Data Inspection
   - 4.3 Data Preprocessing
   - 4.4 Model Training and Validation

5. [AI Assistant and Recommendation System](#chapter-5-ai-assistant-and-recommendation-system)
   - 5.1 Gemini API Integration
   - 5.2 Prediction Explanation
   - 5.3 Model Comparison
   - 5.4 Report Generation

6. [Results and Discussion](#chapter-6-results-and-discussion)
   - 6.1 Model Performance Comparison
   - 6.2 Feature Importance Analysis
   - 6.3 Data Quality Analysis Results
   - 6.4 System Usability Evaluation

7. [Conclusion and Future Work](#chapter-7-conclusion-and-future-work)

---

# Chapter 1. Data Simulation and Understanding

In this chapter, we will introduce and conduct a fundamental analysis of the data, as well as establish the foundation for data simulation. We will discuss the key principles and references that justify the use of a simulated dataset in our credit risk scoring model. This approach ensures that our analysis is robust, comprehensive, and based on real-world insights.

## 1.1. Data Context

### 1.1.1. Data simulation facility

Given that the goal of this project is to develop a multi-dimensional user interface tailored for financial risk assessment, we decided to construct our project database using the UCI Credit Card dataset. This approach ensures comprehensive coverage of all individuals and processes involved in the business. Consequently, our database covers three major areas about key stakeholders and activities: **customers** (individuals seeking credit), **employees** (users who are staff members of the financial institution), and **administrators** (users who are managers with full system access).

Among the various research sources and references we reviewed, the UCI Credit Card Default dataset was chosen as it is expected to be one of the most important and popular datasets for credit risk modeling in academic and industry applications.

**Table 1.1: Data simulation facility**

| No. | Rule | Reference |
|-----|------|-----------|
| 1 | Credit card payment history provides strong predictive signals for default risk. | Yeh, I. C., & Lien, C. H. (2009). The comparisons of data mining techniques for the predictive accuracy of probability of default of credit card clients. Expert Systems with Applications, 36(2), 2473-2480. |
| 2 | Multi-month payment patterns improve prediction accuracy compared to single-month snapshots. | Khandani, A. E., Kim, A. J., & Lo, A. W. (2010). Consumer credit-risk models via machine-learning algorithms. Journal of Banking & Finance, 34(11), 2767-2787. |
| 3 | Ensure that customer records are distributed across different risk categories, meaning there are both low-risk and high-risk customers. | The research team has observed and established this rule based on industry best practices. |
| 4 | Feature engineering from payment history (PAY_0 to PAY_6 and BILL_AMT1 to BILL_AMT6) significantly impacts model performance. | Baseline features from UCI dataset expanded to 12-month history (PAY_1 to PAY_12, BILL_AMT1 to BILL_AMT12). |
| 5 | Age, education, and marriage status provide demographic context that influences credit behavior. | Demographic features retained from original UCI dataset. |
| 6 | Credit limit represents the maximum borrowing capacity and correlates with default probability. | LIMIT_BAL feature from UCI dataset. |

### 1.1.2. Data generation

Using the UCI Credit Card Default dataset as the foundation, we expanded the temporal dimension from 6 months to 12 months of payment history. This expansion was performed using statistical simulation techniques that preserve the correlation structure and distribution patterns observed in the original dataset.

The final database for the credit scoring system consists of **7 tables**, covering:
- **User accounts and authentication** (`user` table with role-based access: User and Admin)
- **Customer profiles** (46 columns including 41 engineered features)
- **Prediction history** (`predictions_log` with user tracking, model versioning, confidence scores)
- **Model registry** (`model_registry` tracking 8 ML models with performance metrics)
- **Customer clustering** (`customer_clusters` with risk level assignments)
- **Data quality logs** (`data_quality_log` for outlier detection)
- **AI chat history** (`ai_chat_history` for Gemini conversation tracking)

Accounts and profiles are generated using a combination of:
- **Original UCI dataset** (30,000 customers)
- **Simulated expansion** to 12-month payment history
- **Role-based user accounts** (Admin: fathershark, User: babyshark, momshark)

The customer profiles use real customer data patterns from the UCI dataset, with payment histories (PAY_1 to PAY_12) and bill amounts (BILL_AMT1 to BILL_AMT12) representing monthly credit card transaction patterns.

### 1.1.3. Data Understanding

The dataset contains **41 features** derived from customer demographic information and 12-month payment history:

**Demographic Features (5):**
- `LIMIT_BAL`: Credit limit amount
- `SEX`: Gender (1=male, 2=female)
- `EDUCATION`: Education level (1=graduate, 2=university, 3=high school, 4=others)
- `MARRIAGE`: Marital status (1=married, 2=single, 3=others)
- `AGE`: Age in years

**Payment Status Features (12):** PAY_1 to PAY_12
- Repayment status for each month (-1=pay duly, 1=payment delay for one month, 2=payment delay for two months, ..., 9=payment delay for nine months and above)

**Bill Amount Features (12):** BILL_AMT1 to BILL_AMT12
- Bill statement amount for each month (NT dollar)

**Payment Amount Features (12):** PAY_AMT1 to PAY_AMT12
- Amount of previous payment for each month (NT dollar)

**Table 1.2: Key database tables**

| Table Name | Primary Key | Key Columns | Purpose |
|------------|-------------|-------------|---------|
| `user` | `id` | `username`, `password_hash`, `role`, `full_name`, `email`, `last_login`, `is_active` | Authentication with 2 roles: User, Admin |
| `customers` | `customer_id` | 46 columns including demographics + 12-month payment history | Customer profile storage |
| `predictions_log` | `id` | `customer_id`, `user_id`, `model_version`, `prediction`, `confidence_score`, `cluster_id` | Tracks all predictions made |
| `model_registry` | `id` | `model_name`, `algorithm`, `auc_score`, `accuracy`, `precision_score`, `recall_score`, `f1_score`, `is_active` | ML model metadata and metrics |
| `customer_clusters` | `id` | `customer_id`, `cluster_id`, `risk_level`, `created_at` | Customer segmentation results |
| `data_quality_log` | `id` | `customer_id`, `issue_type`, `severity`, `description` | Data quality monitoring |
| `ai_chat_history` | `id` | `user_id`, `message`, `response`, `context_type`, `created_at` | Gemini AI conversation logs |

## 1.4. Data Analysis

### Customer Distribution Analysis

As of November 2025, the system has processed predictions for customers from the UCI Credit Card Default dataset. The customer base exhibits diverse credit behaviors and risk profiles.

**Figure 1.1: Default Rate Distribution**

```
Default Distribution:
- Non-Default (0): 23,364 customers (77.9%)
- Default (1): 6,636 customers (22.1%)

This distribution shows a typical imbalanced classification problem in credit risk,
where the majority of customers do not default, but identifying the minority
default cases is critical for business risk management.
```

### Feature Correlation Analysis

The correlation analysis between features and the target variable (default status) reveals:

**High Correlation Features:**
1. **PAY_0 to PAY_6** (Payment status): Strong positive correlation with default (0.25 - 0.32)
2. **PAY_AMT1 to PAY_AMT6** (Payment amounts): Moderate negative correlation with default (-0.08 to -0.12)
3. **BILL_AMT1 to BILL_AMT6** (Bill amounts): Weak correlation with default

**Low Correlation Features:**
- Demographic variables (AGE, EDUCATION, MARRIAGE) show weak correlation with default
- However, these features are retained for model interpretability and may capture non-linear relationships

### Payment Behavior Patterns

**Figure 1.2: Payment Status Distribution Over 12 Months**

```
Average Payment Delay by Month:
PAY_1: -0.02 (mostly on-time)
PAY_2: 0.05
PAY_3: 0.08
...
PAY_12: 0.15 (increasing trend of payment delay)

Observation: There is a gradual increase in average payment delay from PAY_1
to PAY_12, suggesting that customers who eventually default show deteriorating
payment behavior over time. This temporal pattern justifies the expansion from
6-month to 12-month history.
```

### Credit Limit Distribution

**Figure 1.3: Credit Limit Distribution**

```
Credit Limit Statistics:
- Mean: NT$ 167,484
- Median: NT$ 140,000
- Std Dev: NT$ 129,747
- Min: NT$ 10,000
- Max: NT$ 1,000,000

Distribution: Right-skewed with most customers having credit limits
between NT$ 50,000 and NT$ 300,000.
```

### Age Distribution by Default Status

**Figure 1.4: Age Distribution**

```
Age Statistics:
- Non-Default customers: Mean age = 35.6 years
- Default customers: Mean age = 35.3 years
- Overall range: 21 to 79 years

Observation: Minimal difference in mean age between default and non-default groups,
but age may interact with other features in non-linear ways captured by tree-based models.
```

---

# Chapter 2. Methodology

This chapter outlines the methodologies employed in the research, detailing the programming languages, design tools, and machine learning techniques used for credit risk prediction and system development.

## 2.1. Programming Languages

The programming language chosen for this study is **Python**, specifically version **3.11+**. Python was selected due to its rich ecosystem of libraries and frameworks such as PyQt6 for GUI development, NumPy and Pandas for data manipulation, and scikit-learn for machine learning tasks. Additionally, Python's simplicity and readability make it an excellent choice for developing and testing complex systems, as well as for implementing seamless integrations with external APIs like Google Gemini.

**Key Python Libraries Used:**
- **PyQt6 6.6.1**: Desktop GUI framework
- **pandas 2.2.2**: Data manipulation and analysis
- **numpy 2.1.3**: Numerical computing
- **scikit-learn 1.6.1**: Machine learning algorithms and utilities
- **imbalanced-learn 0.14.0**: Handling imbalanced datasets (SMOTE)
- **xgboost 2.0.3**: Gradient boosting framework
- **lightgbm 4.6.0**: Light Gradient Boosting Machine
- **catboost 1.2.8**: Categorical boosting
- **tensorflow 2.15.0+**: Deep learning framework
- **google-generativeai 0.3.0+**: Gemini AI integration
- **mysql-connector-python 8.2.0**: Database connectivity
- **bcrypt 4.1.2**: Password hashing
- **matplotlib 3.9.2**, **seaborn 0.13.0**: Data visualization

## 2.2. Programming Tools

Several design and development tools were utilized to streamline data analysis and visualization processes:

- **Qt Designer**: Used for creating the graphical user interface (GUI) of the application, providing a powerful framework for designing and building interactive desktop applications with PyQt6.

- **MySQL Workbench**: Employed for database design, creation, and management. This tool facilitated visual database modeling and efficient SQL query execution.

- **Visual Studio Code**: Primary IDE for Python development with extensions for Jupyter notebooks, Git integration, and real-time debugging.

- **PyCharm**: Alternative IDE used for complex debugging tasks and code profiling.

- **DBeaver**: Universal database tool for advanced SQL operations and data exploration.

- **Git/GitHub**: Version control and collaborative development platform.

- **Mockaroo & Generatedata**: Data generation tools used for creating simulated customer profiles during testing phases.

## 2.3. Machine Learning Models for Credit Risk Prediction

The machine learning techniques used in this study for credit risk prediction encompass eight different algorithms, each chosen for its unique strengths in handling tabular data and providing accurate predictions.

### 2.3.1. Logistic Regression

Logistic Regression is a fundamental statistical model used for binary classification. Despite its simplicity, it provides a strong baseline for credit risk prediction and offers interpretable coefficients that indicate feature importance.

**Implementation:**
```python
from sklearn.linear_model import LogisticRegression

model = LogisticRegression(
    random_state=42,
    max_iter=1000,
    class_weight='balanced'
)
```

**Advantages:**
- Fast training and prediction
- Interpretable feature coefficients
- Works well with linearly separable data
- Low computational requirements

**Limitations:**
- Assumes linear relationship between features and log-odds
- May underperform with complex non-linear patterns

### 2.3.2. XGBoost (Extreme Gradient Boosting)

XGBoost is an advanced implementation of gradient boosting designed for speed and performance. It is highly effective in handling large-scale data and complex patterns, making it a powerful tool for credit risk prediction.

**Implementation:**
```python
import xgboost as xgb

model = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    eval_metric='auc',
    scale_pos_weight=3  # Handle class imbalance
)
```

**Performance in System:**
- **Current Active Model**
- AUC: 0.7604
- Accuracy: 81.2%
- Training time: ~5-8 minutes on full dataset

**Advantages:**
- Excellent handling of missing data
- Built-in regularization (L1, L2)
- Parallel processing capabilities
- Feature importance ranking

### 2.3.3. LightGBM

LightGBM (Light Gradient Boosting Machine) is a gradient boosting framework that uses tree-based learning algorithms. It is designed for efficiency and speed, particularly effective with large datasets.

**Implementation:**
```python
import lightgbm as lgb

model = lgb.LGBMClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    class_weight='balanced'
)
```

**Performance in System:**
- **Best Performing Model**
- AUC: 0.7811
- Accuracy: 82.3%
- Training time: ~3-5 minutes (faster than XGBoost)

**Advantages:**
- Faster training than XGBoost
- Lower memory usage
- Better accuracy with large datasets
- Handles categorical features natively

### 2.3.4. CatBoost

CatBoost is a gradient boosting library that excels at handling categorical features without extensive preprocessing. It implements ordered boosting to reduce overfitting and prediction shift.

**Implementation:**
```python
from catboost import CatBoostClassifier

model = CatBoostClassifier(
    iterations=100,
    depth=6,
    learning_rate=0.1,
    random_state=42,
    verbose=False,
    class_weights=[1, 3]  # Handle imbalance
)
```

**Advantages:**
- Automatic handling of categorical features
- Robust to overfitting
- Good performance out-of-the-box
- Less hyperparameter tuning required

### 2.3.5. Random Forest

Random Forest is an ensemble learning method that constructs multiple decision trees during training and outputs the mean prediction. It is robust to overfitting and provides feature importance scores.

**Implementation:**
```python
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=5,
    random_state=42,
    class_weight='balanced',
    n_jobs=-1
)
```

**Advantages:**
- Robust to overfitting
- Handles non-linear relationships
- Provides feature importance
- Parallelizable training

### 2.3.6. Neural Network

A deep learning approach using TensorFlow/Keras for credit risk prediction. The neural network can capture complex non-linear interactions between features.

**Implementation:**
```python
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization

model = Sequential([
    Dense(128, activation='relu', input_shape=(41,)),
    BatchNormalization(),
    Dropout(0.3),
    Dense(64, activation='relu'),
    BatchNormalization(),
    Dropout(0.3),
    Dense(32, activation='relu'),
    Dropout(0.2),
    Dense(1, activation='sigmoid')
])

model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy', 'AUC']
)
```

**Advantages:**
- Can learn complex feature interactions
- Flexible architecture
- Scalable to large datasets

**Limitations:**
- Requires more training data
- Longer training time
- Harder to interpret
- Requires careful hyperparameter tuning

### 2.3.7. Voting Ensemble

A voting classifier combines predictions from multiple models to improve overall accuracy and robustness. The ensemble uses soft voting (averaging predicted probabilities).

**Implementation:**
```python
from sklearn.ensemble import VotingClassifier

voting_model = VotingClassifier(
    estimators=[
        ('xgb', xgb_model),
        ('lgb', lgb_model),
        ('rf', rf_model)
    ],
    voting='soft',
    n_jobs=-1
)
```

**Advantages:**
- Reduces variance and overfitting
- More robust predictions
- Combines strengths of multiple models

### 2.3.8. Stacking Ensemble

Stacking uses a meta-learner to combine predictions from multiple base models. This approach can capture complex patterns that individual models miss.

**Implementation:**
```python
from sklearn.ensemble import StackingClassifier

stacking_model = StackingClassifier(
    estimators=[
        ('xgb', xgb_model),
        ('lgb', lgb_model),
        ('rf', rf_model),
        ('lr', lr_model)
    ],
    final_estimator=LogisticRegression(),
    cv=5
)
```

**Advantages:**
- Often achieves best performance
- Leverages diverse model predictions
- Meta-learner optimizes combination

**Limitations:**
- Longer training time
- More complex to interpret
- Requires more computational resources

## 2.4. AI Integration with Gemini

The system integrates Google's Gemini AI for intelligent assistance and explanation generation. This collaborative AI approach enhances user understanding of predictions and model behavior.

### 2.4.1. Gemini API Configuration

**Implementation:**
```python
import google.generativeai as genai

genai.configure(api_key="<API_KEY>")

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config={
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 2048,
    },
    safety_settings=[...],
    system_instruction="""
    Bạn là một chuyên gia phân tích rủi ro tín dụng có kinh nghiệm 10+ năm.
    Nhiệm vụ của bạn là phân tích dữ liệu khách hàng và kết quả dự báo từ
    mô hình Machine Learning, đưa ra khuyến nghị cụ thể và khả thi.
    """
)
```

### 2.4.2. Use Cases

**Prediction Explanation:**
- Analyze customer features and model prediction
- Identify key risk factors
- Provide actionable recommendations

**Model Comparison:**
- Compare predictions from multiple models
- Explain differences in model outputs
- Recommend best model for specific customer profiles

**Report Generation:**
- Generate executive summaries
- Create risk assessment reports
- Provide insights on customer segments

## 2.5. Evaluation Metrics

The performance of the credit risk prediction models is evaluated using standard classification metrics:

### 2.5.1. AUC-ROC (Area Under Receiver Operating Characteristic Curve)

**Definition:** Measures the model's ability to distinguish between positive (default) and negative (non-default) classes across all classification thresholds.

**Interpretation:**
- AUC = 0.5: Random classifier
- AUC = 0.7-0.8: Acceptable performance
- AUC = 0.8-0.9: Excellent performance
- AUC > 0.9: Outstanding performance

**Why important for credit risk:** AUC is threshold-independent and provides a comprehensive measure of model discrimination ability, crucial for ranking customers by risk.

### 2.5.2. Accuracy

**Definition:** The proportion of correct predictions (both true positives and true negatives) among the total number of cases examined.

**Formula:** 
```
Accuracy = (TP + TN) / (TP + TN + FP + FN)
```

**Limitation:** Can be misleading with imbalanced datasets (22% default rate in our case).

### 2.5.3. Precision

**Definition:** The proportion of true positive predictions among all positive predictions made by the model.

**Formula:**
```
Precision = TP / (TP + FP)
```

**Interpretation:** High precision means low false positive rate - when model predicts default, it's usually correct.

### 2.5.4. Recall (Sensitivity)

**Definition:** The proportion of true positive predictions among all actual positive cases.

**Formula:**
```
Recall = TP / (TP + FN)
```

**Interpretation:** High recall means low false negative rate - model catches most actual defaults.

### 2.5.5. F1-Score

**Definition:** The harmonic mean of precision and recall, providing a balanced measure.

**Formula:**
```
F1 = 2 × (Precision × Recall) / (Precision + Recall)
```

**Why important:** Balances the trade-off between precision and recall, especially useful for imbalanced datasets.

### 2.5.6. Confusion Matrix

A table showing the counts of true positives, true negatives, false positives, and false negatives, providing detailed insight into model performance across both classes.

---

*Continue to Chapter 3...*
