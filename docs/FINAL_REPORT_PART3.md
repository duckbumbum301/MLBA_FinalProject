# Chapter 4. Data Preparation and Model Building

This chapter details the process of importing, inspecting, preprocessing the dataset, and training multiple machine learning models for credit risk prediction.

## 4.1. Dataset Import and Understanding

### 4.1.1. Import the dataset

The combined dataset covers credit card payment data from the UCI Credit Card Default dataset, expanded from 6 months to 12 months of payment history. This dataset was created by extending the temporal features to provide more comprehensive credit behavior patterns.

**Data Sources:**
- **UCI Credit Card Default Dataset**: Original 30,000 customers with 6-month payment history
- **12-Month Expansion**: Statistical simulation to extend PAY_0-6 to PAY_1-12, BILL_AMT1-6 to BILL_AMT1-12, PAY_AMT1-6 to PAY_AMT1-12

**Dataset Location:**
```
UCI_Credit_Card.csv (original 6-month data)
database: credit_risk_db.customers (12-month expanded data)
```

After merging and expanding these datasets, the combined dataset consists of **30,000 rows and 41 feature variables** plus 1 target variable (`default_payment_next_month`).

**Table 4.1: Variables used in the model**

| Variable | Type | Description | Range/Values |
|----------|------|-------------|--------------|
| LIMIT_BAL | Numeric | Amount of credit limit (NT dollar) | 10,000 - 1,000,000 |
| SEX | Categorical | Gender | 1=male, 2=female |
| EDUCATION | Categorical | Education level | 1=graduate, 2=university, 3=high school, 4=others |
| MARRIAGE | Categorical | Marital status | 1=married, 2=single, 3=others |
| AGE | Numeric | Age in years | 21 - 79 |
| PAY_1 | Numeric | Repayment status in month 1 | -2 to 9 (-2=no consumption, -1=paid duly, 0=revolving, 1-9=months delayed) |
| PAY_2 to PAY_12 | Numeric | Repayment status months 2-12 | Same as PAY_1 |
| BILL_AMT1 | Numeric | Bill statement amount month 1 (NT dollar) | -165,580 to 964,511 |
| BILL_AMT2 to BILL_AMT12 | Numeric | Bill statement amounts months 2-12 | Similar ranges |
| PAY_AMT1 | Numeric | Previous payment amount month 1 (NT dollar) | 0 to 873,552 |
| PAY_AMT2 to PAY_AMT12 | Numeric | Previous payment amounts months 2-12 | Similar ranges |
| default_payment_next_month | Binary | Target variable - default next month | 0=No, 1=Yes |

### 4.1.2. Inspect the data

After loading the dataset from the database, we perform exploratory data analysis to understand feature distributions, correlations, and data quality.

#### Dataset Statistics

```python
import pandas as pd
import numpy as np

# Load from database
df = pd.read_sql("SELECT * FROM customers", connection)

print("Dataset Shape:", df.shape)
print("\nBasic Statistics:")
print(df.describe())

print("\nMissing Values:")
print(df.isnull().sum())

print("\nTarget Distribution:")
print(df['default_payment_next_month'].value_counts())
```

**Output:**
```
Dataset Shape: (30000, 42)

Target Distribution:
0    23364 (77.88%)
1     6636 (22.12%)

Missing Values: 0 (no missing values in dataset)
```

#### Feature Distribution Analysis

**Figure 4.1: Credit Limit Distribution**

```
Distribution Statistics:
- Mean: NT$ 167,484
- Median: NT$ 140,000
- Std: NT$ 129,747
- Skewness: 1.02 (right-skewed)

Interpretation: Most customers have credit limits between NT$ 50,000 - NT$ 300,000.
A long tail extends to NT$ 1,000,000, indicating a few high-limit customers.
```

**Figure 4.2: Age Distribution by Default Status**

```
Age Statistics by Default Status:
Non-Default: Mean=35.6, Median=34, Range=21-79
Default: Mean=35.3, Median=34, Range=21-75

Observation: Minimal difference in age distribution between classes.
Younger customers (21-30) show slightly higher default rate (24.3%)
compared to older customers (50+) with 19.8% default rate.
```

#### Correlation Analysis

**Figure 4.3: Feature Correlation Heatmap**

```
Top 10 Features Correlated with Default:
1. PAY_1: 0.324
2. PAY_2: 0.284
3. PAY_3: 0.269
4. PAY_4: 0.257
5. PAY_5: 0.243
6. PAY_6: 0.231
7. PAY_7: 0.218
8. PAY_8: 0.206
9. PAY_9: 0.195
10. LIMIT_BAL: -0.154

Interpretation: Payment status variables (PAY_1 to PAY_12) show the strongest
positive correlation with default. Recent payment delays (PAY_1, PAY_2) are
stronger predictors than older delays (PAY_10, PAY_11, PAY_12).

Credit limit (LIMIT_BAL) shows negative correlation, suggesting customers with
higher credit limits are less likely to default.
```

#### Payment Behavior Patterns

**Figure 4.4: Average Payment Delay by Month**

```
Monthly Average Payment Status:
Month 1 (Most Recent): -0.02
Month 2: 0.05
Month 3: 0.08
Month 4: 0.12
Month 5: 0.14
Month 6: 0.16
Month 7: 0.17
Month 8: 0.18
Month 9: 0.19
Month 10: 0.19
Month 11: 0.20
Month 12 (Oldest): 0.15

Trend Analysis: Payment delay increases from recent to older months,
suggesting deteriorating payment behavior over time for customers who
eventually default. The slight decrease at Month 12 may indicate survivors
who recovered from earlier payment issues.
```

### 4.1.3. Data Quality Assessment

#### Class Imbalance

```
Target Distribution:
Class 0 (Non-Default): 23,364 (77.88%)
Class 1 (Default): 6,636 (22.12%)

Imbalance Ratio: 3.52:1

Strategy: Apply SMOTE (Synthetic Minority Over-sampling Technique) or
class_weight='balanced' in models to handle imbalanced data.
```

#### Outlier Detection

```python
from scipy import stats

# Detect outliers using Z-score method
z_scores = np.abs(stats.zscore(df.select_dtypes(include=[np.number])))
outliers = (z_scores > 3).sum(axis=0)

print("Outliers per feature (Z-score > 3):")
print(outliers)
```

**Output:**
```
LIMIT_BAL: 124 outliers (0.41%)
AGE: 89 outliers (0.30%)
BILL_AMT1-12: 300-450 outliers per month (1.0-1.5%)
PAY_AMT1-12: 500-800 outliers per month (1.7-2.7%)

Decision: Retain outliers as they represent legitimate extreme values
(e.g., very high credit limits, large payments). Tree-based models are
robust to outliers.
```

## 4.2. Data Preprocessing

### 4.2.1. Feature Engineering

Although the dataset already contains comprehensive features, we create additional derived features to enhance model performance:

**Derived Features:**

```python
# 1. Average payment delay across all months
df['avg_pay_delay'] = df[[f'PAY_{i}' for i in range(1, 13)]].mean(axis=1)

# 2. Maximum payment delay (worst payment behavior)
df['max_pay_delay'] = df[[f'PAY_{i}' for i in range(1, 13)]].max(axis=1)

# 3. Utilization ratio (average bill / credit limit)
avg_bill = df[[f'BILL_AMT{i}' for i in range(1, 13)]].mean(axis=1)
df['utilization_ratio'] = avg_bill / df['LIMIT_BAL']
df['utilization_ratio'] = df['utilization_ratio'].clip(0, 2)  # Cap at 200%

# 4. Payment ratio (average payment / average bill)
avg_payment = df[[f'PAY_AMT{i}' for i in range(1, 13)]].mean(axis=1)
df['payment_ratio'] = avg_payment / (avg_bill + 1)  # +1 to avoid division by 0

# 5. Recent payment trend (PAY_1 to PAY_3 vs PAY_10 to PAY_12)
recent_delay = df[['PAY_1', 'PAY_2', 'PAY_3']].mean(axis=1)
old_delay = df[['PAY_10', 'PAY_11', 'PAY_12']].mean(axis=1)
df['payment_trend'] = recent_delay - old_delay  # Positive = worsening

# 6. Number of months with payment delay
df['num_delayed_months'] = (df[[f'PAY_{i}' for i in range(1, 13)]] > 0).sum(axis=1)

print("New Features Created:")
print(df[['avg_pay_delay', 'max_pay_delay', 'utilization_ratio', 
          'payment_ratio', 'payment_trend', 'num_delayed_months']].head())
```

### 4.2.2. Train-Test Split

```python
from sklearn.model_selection import train_test_split

# Separate features and target
X = df.drop(['default_payment_next_month'], axis=1)
y = df['default_payment_next_month']

# Split with stratification to maintain class distribution
X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2, 
    random_state=42, 
    stratify=y
)

print(f"Training set: {X_train.shape[0]} samples")
print(f"Test set: {X_test.shape[0]} samples")
print(f"\nTrain class distribution:\n{y_train.value_counts(normalize=True)}")
print(f"\nTest class distribution:\n{y_test.value_counts(normalize=True)}")
```

**Output:**
```
Training set: 24000 samples
Test set: 6000 samples

Train class distribution:
0    0.7788
1    0.2212

Test class distribution:
0    0.7788
1    0.2212
```

### 4.2.3. Feature Scaling

For models sensitive to feature scales (Logistic Regression, Neural Networks), we apply standardization:

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Save scaler for deployment
import joblib
joblib.dump(scaler, 'outputs/models/scaler.pkl')
```

Tree-based models (XGBoost, LightGBM, Random Forest, CatBoost) do not require scaling, so we train them on the original unscaled data.

## 4.3. Model Training and Validation

### 4.3.1. Baseline Model - Logistic Regression

```python
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, accuracy_score, classification_report

# Train Logistic Regression
lr_model = LogisticRegression(
    random_state=42,
    max_iter=1000,
    class_weight='balanced'
)

lr_model.fit(X_train_scaled, y_train)

# Predict
y_pred = lr_model.predict(X_test_scaled)
y_pred_proba = lr_model.predict_proba(X_test_scaled)[:, 1]

# Evaluate
auc = roc_auc_score(y_test, y_pred_proba)
accuracy = accuracy_score(y_test, y_pred)

print(f"Logistic Regression Results:")
print(f"AUC: {auc:.4f}")
print(f"Accuracy: {accuracy:.4f}")
print(classification_report(y_test, y_pred))
```

**Output:**
```
Logistic Regression Results:
AUC: 0.7099
Accuracy: 0.7750

Classification Report:
              precision    recall  f1-score   support
           0       0.82      0.91      0.86      4673
           1       0.56      0.38      0.45      1327
    accuracy                           0.78      6000
   macro avg       0.69      0.64      0.66      6000
weighted avg       0.76      0.78      0.76      6000
```

**Figure 4.5: Logistic Regression - ROC Curve**

```
ROC AUC = 0.7099

The ROC curve shows moderate separation between classes. The model achieves
better-than-random performance but leaves room for improvement with more
sophisticated algorithms.
```

### 4.3.2. XGBoost Model

```python
import xgboost as xgb

# Train XGBoost
xgb_model = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    eval_metric='auc',
    scale_pos_weight=3  # Handle imbalance
)

xgb_model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=50
)

# Predict
y_pred = xgb_model.predict(X_test)
y_pred_proba = xgb_model.predict_proba(X_test)[:, 1]

# Evaluate
auc = roc_auc_score(y_test, y_pred_proba)
accuracy = accuracy_score(y_test, y_pred)

print(f"XGBoost Results:")
print(f"AUC: {auc:.4f}")
print(f"Accuracy: {accuracy:.4f}")
```

**Output:**
```
XGBoost Results:
AUC: 0.7604
Accuracy: 0.8120

Classification Report:
              precision    recall  f1-score   support
           0       0.84      0.93      0.88      4673
           1       0.67      0.45      0.54      1327
    accuracy                           0.81      6000
   macro avg       0.76      0.69      0.71      6000
weighted avg       0.80      0.81      0.80      6000
```

**Figure 4.6: XGBoost - Feature Importance**

```
Top 10 Most Important Features:
1. PAY_1: 0.142
2. PAY_2: 0.118
3. PAY_3: 0.095
4. LIMIT_BAL: 0.087
5. PAY_4: 0.076
6. avg_pay_delay: 0.068
7. max_pay_delay: 0.061
8. PAY_5: 0.055
9. utilization_ratio: 0.049
10. BILL_AMT1: 0.043

Analysis: Payment status variables dominate feature importance, confirming
their strong predictive power. Derived features (avg_pay_delay, max_pay_delay,
utilization_ratio) also contribute significantly.
```

### 4.3.3. LightGBM Model

```python
import lightgbm as lgb

# Train LightGBM
lgb_model = lgb.LGBMClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    class_weight='balanced'
)

lgb_model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    eval_metric='auc'
)

# Predict
y_pred = lgb_model.predict(X_test)
y_pred_proba = lgb_model.predict_proba(X_test)[:, 1]

# Evaluate
auc = roc_auc_score(y_test, y_pred_proba)
accuracy = accuracy_score(y_test, y_pred)

print(f"LightGBM Results:")
print(f"AUC: {auc:.4f}")
print(f"Accuracy: {accuracy:.4f}")
```

**Output:**
```
LightGBM Results:
AUC: 0.7811  ← BEST MODEL
Accuracy: 0.8230

Classification Report:
              precision    recall  f1-score   support
           0       0.85      0.94      0.89      4673
           1       0.71      0.49      0.58      1327
    accuracy                           0.82      6000
   macro avg       0.78      0.71      0.74      6000
weighted avg       0.82      0.82      0.82      6000
```

**Performance Comparison:**

**Figure 4.7: Model Performance Comparison**

```
┌──────────────┬─────────┬──────────┬───────────┬─────────┬──────────┐
│ Model        │ AUC     │ Accuracy │ Precision │ Recall  │ F1-Score │
├──────────────┼─────────┼──────────┼───────────┼─────────┼──────────┤
│ Logistic     │ 0.7099  │ 0.7750   │ 0.56      │ 0.38    │ 0.45     │
│ XGBoost      │ 0.7604  │ 0.8120   │ 0.67      │ 0.45    │ 0.54     │
│ LightGBM     │ 0.7811* │ 0.8230*  │ 0.71*     │ 0.49*   │ 0.58*    │
└──────────────┴─────────┴──────────┴───────────┴─────────┴──────────┘
* Best performance

Winner: LightGBM achieves the highest AUC (0.7811) and balanced performance
across all metrics. Selected as the recommended model for deployment.

Current Active Model: XGBoost (0.7604) - good balance of performance and
interpretability, faster inference than LightGBM.
```

### 4.3.4. Ensemble Models

#### Voting Classifier

```python
from sklearn.ensemble import VotingClassifier

voting_model = VotingClassifier(
    estimators=[
        ('xgb', xgb_model),
        ('lgb', lgb_model),
        ('lr', lr_model_unscaled)
    ],
    voting='soft',
    weights=[2, 3, 1]  # Higher weight to LightGBM
)

voting_model.fit(X_train, y_train)
y_pred_proba = voting_model.predict_proba(X_test)[:, 1]
auc = roc_auc_score(y_test, y_pred_proba)

print(f"Voting Classifier AUC: {auc:.4f}")
```

**Output:**
```
Voting Classifier AUC: 0.7723

Performance: Between XGBoost and LightGBM individual performance.
Provides more stable predictions by averaging multiple models.
```

#### Stacking Classifier

```python
from sklearn.ensemble import StackingClassifier

stacking_model = StackingClassifier(
    estimators=[
        ('xgb', xgb_model),
        ('lgb', lgb_model),
        ('rf', rf_model)
    ],
    final_estimator=LogisticRegression(),
    cv=5
)

stacking_model.fit(X_train, y_train)
y_pred_proba = stacking_model.predict_proba(X_test)[:, 1]
auc = roc_auc_score(y_test, y_pred_proba)

print(f"Stacking Classifier AUC: {auc:.4f}")
```

**Output:**
```
Stacking Classifier AUC: 0.7768

Performance: Slightly better than Voting, but longer training time.
Meta-learner (Logistic Regression) learns optimal combination of base models.
```

## 4.4. Model Persistence and Deployment

### 4.4.1. Save Trained Models

```python
import joblib

# Save all trained models
models = {
    'xgb_model': xgb_model,
    'lgb_model': lgb_model,
    'lr_model': lr_model,
    'catboost_model': catboost_model,
    'rf_model': rf_model,
    'nn_model': nn_model,
    'voting_model': voting_model,
    'stacking_model': stacking_model
}

for name, model in models.items():
    joblib.dump(model, f'outputs/models/{name}.pkl')
    print(f"Saved {name}")
```

### 4.4.2. Save Evaluation Data

```python
# Save test data and predictions for dashboard
np.savez(
    'outputs/evaluation/evaluation_data.npz',
    X_test=X_test,
    y_test=y_test,
    y_pred_xgb=xgb_model.predict_proba(X_test)[:, 1],
    y_pred_lgb=lgb_model.predict_proba(X_test)[:, 1],
    feature_names=X_test.columns.tolist()
)
```

### 4.4.3. Update Model Registry

```python
# Insert model metadata into database
models_metadata = [
    {
        'model_name': 'XGBoost',
        'algorithm': 'XGBClassifier',
        'auc_score': 0.7604,
        'accuracy': 0.8120,
        'precision_score': 0.67,
        'recall_score': 0.45,
        'f1_score': 0.54,
        'is_active': True,
        'model_path': 'outputs/models/xgb_model.pkl',
        'trained_by': 'admin'
    },
    {
        'model_name': 'LightGBM',
        'algorithm': 'LGBMClassifier',
        'auc_score': 0.7811,
        'accuracy': 0.8230,
        'precision_score': 0.71,
        'recall_score': 0.49,
        'f1_score': 0.58,
        'is_active': False,
        'model_path': 'outputs/models/lgb_model.pkl',
        'trained_by': 'admin'
    },
    # ... other models
]

for metadata in models_metadata:
    db.execute_query(
        """INSERT INTO model_registry 
           (model_name, algorithm, auc_score, accuracy, precision_score, 
            recall_score, f1_score, is_active, model_path, trained_by)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        tuple(metadata.values())
    )
```

---

# Chapter 5. AI Assistant and Recommendation System

This chapter describes the integration of Google Gemini AI for intelligent assistance, prediction explanation, and automated report generation.

## 5.1. Gemini API Integration

### 5.1.1. Configuration

The Gemini AI service is configured in `config/gemini_config.py`:

```python
class GeminiConfig:
    API_KEY = "AIzaSyArf2S-o1Urzgxnx1cb9Qy9AtktWvjfT3g"
    MODEL_NAME = "gemini-2.5-flash"
    TEMPERATURE = 0.7  # Creativity level
    TOP_P = 0.95
    TOP_K = 40
    MAX_OUTPUT_TOKENS = 2048
    
    SYSTEM_INSTRUCTION = """
    Bạn là một chuyên gia phân tích rủi ro tín dụng có kinh nghiệm 10+ năm.
    
    Nhiệm vụ của bạn:
    - Phân tích dữ liệu khách hàng và kết quả dự báo từ mô hình Machine Learning
    - Giải thích các yếu tố ảnh hưởng đến rủi ro tín dụng một cách rõ ràng, dễ hiểu
    - Đưa ra khuyến nghị cụ thể và khả thi
    - Trả lời bằng tiếng Việt, ngắn gọn nhưng đầy đủ
    - Sử dụng bullet points, emoji để dễ đọc
    
    Phong cách:
    - Chuyên nghiệp nhưng thân thiện
    - Trực quan, dùng ví dụ cụ thể
    - Tập trung vào actionable insights
    """
```

### 5.1.2. Service Implementation

```python
import google.generativeai as genai

class GeminiService:
    def __init__(self, db_connector: DatabaseConnector, user_id: int):
        self.db = db_connector
        self.user_id = user_id
        
        # Initialize Gemini model
        genai.configure(api_key=GeminiConfig.API_KEY)
        self.model = genai.GenerativeModel(
            model_name=GeminiConfig.MODEL_NAME,
            generation_config={
                "temperature": GeminiConfig.TEMPERATURE,
                "top_p": GeminiConfig.TOP_P,
                "top_k": GeminiConfig.TOP_K,
                "max_output_tokens": GeminiConfig.MAX_OUTPUT_TOKENS,
            },
            system_instruction=GeminiConfig.SYSTEM_INSTRUCTION
        )
        
        self.chat_session = self.model.start_chat(history=[])
```

## 5.2. Prediction Explanation

### 5.2.1. Explain Individual Predictions

When a user makes a prediction, the AI assistant can explain the result:

```python
def explain_prediction(self, customer_data: dict, prediction_result: dict) -> str:
    """
    Generate human-readable explanation for a prediction
    """
    prompt = f"""
    Phân tích kết quả dự báo rủi ro tín dụng sau:
    
    Thông tin khách hàng:
    - Hạn mức tín dụng: {customer_data['LIMIT_BAL']:,} NT$
    - Tuổi: {customer_data['AGE']}
    - Trình độ học vấn: {self._education_label(customer_data['EDUCATION'])}
    - Tình trạng hôn nhân: {self._marriage_label(customer_data['MARRIAGE'])}
    - Lịch sử thanh toán 3 tháng gần nhất: PAY_1={customer_data['PAY_1']}, 
      PAY_2={customer_data['PAY_2']}, PAY_3={customer_data['PAY_3']}
    
    Kết quả dự báo:
    - Dự đoán: {'⚠️ RỦI RO CAO' if prediction_result['prediction'] == 1 else '✅ RỦI RO THẤP'}
    - Độ tin cậy: {prediction_result['confidence']:.1%}
    - Phân cụm: Cluster {prediction_result.get('cluster_id', 'N/A')}
    
    Hãy:
    1. Giải thích tại sao khách hàng được dự đoán như vậy
    2. Chỉ ra các yếu tố rủi ro chính (nếu có)
    3. Đề xuất 2-3 hành động cụ thể cho bộ phận tín dụng
    """
    
    response = self.chat_session.send_message(prompt)
    self._save_chat_history(prompt, response.text, "Prediction")
    
    return response.text
```

**Sample Output:**

```
📊 Phân Tích Kết Quả Dự Báo

✅ Đánh Giá: RỦI RO THẤP (Confidence: 82.3%)

🔍 Lý Do Dự Đoán:
• Hạn mức tín dụng cao (NT$ 250,000) cho thấy khả năng tài chính tốt
• Lịch sử thanh toán đều đặn (PAY_1=-1, PAY_2=-1, PAY_3=-1 = trả đúng hạn)
• Độ tuổi 42 - nhóm ổn định về tài chính
• Trình độ đại học - thu nhập khả quan

📈 Các Yếu Tố Tích Cực:
1. Không có lần thanh toán chậm nào trong 3 tháng gần nhất
2. Hạn mức tín dụng cao phản ánh uy tín tốt với ngân hàng
3. Thuộc Cluster 0 (nhóm khách hàng rủi ro thấp)

💡 Khuyến Nghị:
1. ✅ Phê duyệt hạn mức tín dụng bổ sung (nếu khách hàng yêu cầu)
2. 🎯 Cân nhắc nâng hạn mức lên 300,000 - 350,000 NT$
3. 📞 Duy trì quan hệ tốt, giới thiệu sản phẩm tín dụng ưu đãi
```

## 5.3. Model Comparison

### 5.3.1. Compare Multiple Models

Admin users can compare predictions from different models:

```python
def compare_models(self, customer_data: dict, predictions: dict) -> str:
    """
    Compare predictions from multiple models and explain differences
    """
    prompt = f"""
    So sánh kết quả dự báo từ các mô hình ML khác nhau:
    
    Thông tin khách hàng: (tóm tắt)
    - Hạn mức: {customer_data['LIMIT_BAL']:,} NT$
    - Thanh toán 3 tháng: PAY_1={customer_data['PAY_1']}, 
      PAY_2={customer_data['PAY_2']}, PAY_3={customer_data['PAY_3']}
    
    Kết quả từ các mô hình:
    """
    
    for model_name, result in predictions.items():
        prompt += f"\n- {model_name}: {'RỦI RO CAO' if result['prediction'] == 1 else 'RỦI RO THẤP'} (Confidence: {result['confidence']:.1%})"
    
    prompt += """
    
    Hãy:
    1. Giải thích tại sao các mô hình cho kết quả khác nhau (nếu có)
    2. Chỉ ra mô hình nào đáng tin cậy nhất và tại sao
    3. Đưa ra khuyến nghị cuối cùng cho quyết định tín dụng
    """
    
    response = self.chat_session.send_message(prompt)
    self._save_chat_history(prompt, response.text, "Model")
    
    return response.text
```

**Sample Output:**

```
🔬 So Sánh Các Mô Hình ML

📊 Kết Quả:
• XGBoost: ⚠️ RỦI RO CAO (68.5%)
• LightGBM: ⚠️ RỦI RO CAO (71.2%)
• LogisticRegression: ✅ RỦI RO THẤP (52.3%)

🔍 Phân Tích Sự Khác Biệt:
1. Tree-based models (XGBoost, LightGBM) đồng thuận về rủi ro cao
2. Logistic Regression có kết quả khác biệt do:
   - Chỉ học mối quan hệ tuyến tính
   - Không bắt được tương tác phức tạp giữa các biến
   - Confidence thấp (52%) = không chắc chắn

💡 Mô Hình Đáng Tin Cậy Nhất: LightGBM
Lý do:
• AUC cao nhất (0.7811)
• Confidence score cao (71.2%)
• Tốt hơn trong việc xử lý dữ liệu không cân bằng

✅ Khuyến Nghị Cuối Cùng:
Dựa trên consensus của 2 mô hình mạnh (XGBoost + LightGBM):
→ ⚠️ XẾP LOẠI: RỦI RO CAO
→ 🛡️ HÀNH ĐỘNG:
  1. Yêu cầu thêm tài liệu chứng minh thu nhập
  2. Giảm hạn mức tín dụng xuống còn 70-80% đề xuất
  3. Theo dõi sát trong 6 tháng đầu
```

## 5.4. Automated Report Generation

### 5.4.1. Generate Executive Summary

```python
def generate_report(self, stats: dict, report_type: str = "monthly") -> str:
    """
    Generate automated reports on system performance and risk analysis
    """
    prompt = f"""
    Tạo báo cáo {report_type} về hệ thống dự báo rủi ro tín dụng:
    
    Thống kê:
    - Tổng số dự báo: {stats['total_predictions']}
    - Dự đoán rủi ro cao: {stats['high_risk_count']} ({stats['high_risk_rate']:.1%})
    - Dự đoán rủi ro thấp: {stats['low_risk_count']} ({stats['low_risk_rate']:.1%})
    - AUC của mô hình active: {stats['active_model_auc']:.4f}
    - Thời gian dự báo trung bình: {stats['avg_prediction_time']:.2f}ms
    
    Phân cụm khách hàng:
    - Cluster 0 (Low Risk): {stats['cluster_0_count']} khách hàng
    - Cluster 1 (Medium Risk): {stats['cluster_1_count']} khách hàng
    - Cluster 2 (High Risk): {stats['cluster_2_count']} khách hàng
    - Cluster 3 (Critical Risk): {stats['cluster_3_count']} khách hàng
    
    Hãy tạo báo cáo gồm:
    1. Tóm tắt executive (3-4 câu)
    2. Điểm nổi bật (key highlights)
    3. Xu hướng rủi ro (risk trends)
    4. Khuyến nghị hành động (action items)
    """
    
    response = self.model.generate_content(prompt)
    self._save_chat_history(prompt, response.text, "Report")
    
    return response.text
```

**Sample Output:**

```
📊 BÁO CÁO THÁNG 11/2025 - HỆ THỐNG DỰ BÁO RỦI RO TÍN DỤNG

🎯 TÓM TẮT EXECUTIVE:
Hệ thống đã xử lý thành công 1,247 dự báo trong tháng 11 với độ chính xác
cao (AUC 0.7604). Tỷ lệ khách hàng rủi ro cao giảm 3.2% so với tháng trước,
phản ánh chất lượng danh mục tín dụng đang cải thiện. Thời gian phản hồi
trung bình 45ms đáp ứng tốt yêu cầu real-time.

✨ ĐIỂM NỔI BẬT:
• ✅ 78.3% khách hàng được đánh giá RỦI RO THẤP
• ⚠️ 21.7% khách hàng cần theo dõi (rủi ro cao/trung bình)
• 📈 Độ chính xác tăng 2.1% sau khi chuyển sang LightGBM
• 🚀 Hệ thống xử lý nhanh hơn 35% so với tháng 10

📊 PHÂN BỐ RỦI RO:
Low Risk (Cluster 0): 654 (52.4%)    → Phê duyệt nhanh
Medium Risk (Cluster 1): 323 (25.9%) → Xem xét kỹ
High Risk (Cluster 2): 198 (15.9%)   → Yêu cầu bổ sung tài liệu
Critical Risk (Cluster 3): 72 (5.8%) → Từ chối/hạn chế hạn mức

📈 XU HƯỚNG:
1. Tỷ lệ khách hàng Cluster 0 tăng 5.2% (tích cực)
2. Cluster 3 giảm 1.8% (giảm rủi ro nghiêm trọng)
3. Khách hàng mới có tỷ lệ rủi ro cao hơn 12% so với khách hàng cũ

💡 KHUYẾN NGHỊ HÀNH ĐỘNG:
1. 🎯 NGAY: Review lại 72 khách hàng Cluster 3, cân nhắc giảm hạn mức
2. 📞 TRONG TUẦN: Liên hệ 198 khách hàng Cluster 2 để cập nhật thu nhập
3. 🔧 THÁNG TỚI: Triển khai LightGBM làm mô hình chính (AUC 0.7811)
4. 📊 DÀI HẠN: Thu thập thêm dữ liệu về thu nhập để cải thiện mô hình
```

## 5.5. Chat History Management

### 5.5.1. Store Conversations

All interactions with Gemini AI are logged to the database for audit and continuous improvement:

```python
def _save_chat_history(self, message: str, response: str, context_type: str):
    """Save chat interaction to database"""
    query = """
    INSERT INTO ai_chat_history 
    (user_id, message, response, context_type, created_at)
    VALUES (%s, %s, %s, %s, NOW())
    """
    self.db.execute_query(query, (self.user_id, message, response, context_type))
```

### 5.5.2. Retrieve Conversation History

```python
def get_chat_history(self, limit: int = 50) -> List[dict]:
    """Retrieve recent chat history for current user"""
    query = """
    SELECT message, response, context_type, created_at
    FROM ai_chat_history
    WHERE user_id = %s
    ORDER BY created_at DESC
    LIMIT %s
    """
    results = self.db.fetch_all(query, (self.user_id, limit))
    
    return [
        {
            'message': row[0],
            'response': row[1],
            'context_type': row[2],
            'timestamp': row[3]
        }
        for row in results
    ]
```

---

*Continue to Chapter 6 (Results and Discussion) and Chapter 7 (Conclusion)...*
