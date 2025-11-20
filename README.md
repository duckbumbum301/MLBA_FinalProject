# Credit Risk Scoring System

A comprehensive credit risk analysis and scoring platform built with Python 3.12 and PyQt6. This system enables financial institutions to assess customer default risk using advanced machine learning models, a user-friendly interface, and robust data management.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Usage Guide](#usage-guide)
- [Team Members](#team-members)
- [Contributing](#contributing)
- [License](#license)

## Overview

The Credit Risk Scoring System is a full-stack application designed to automate and enhance the process of credit risk assessment. It provides:
- A modern desktop interface for data entry, prediction, and reporting.
- Machine learning models (XGBoost, LightGBM, Logistic Regression) for risk scoring.
- Admin and user roles with tailored access and management features.
- Data visualization and model comparison tools.

## Features

- Customer data management and search
- Credit risk prediction using multiple ML models
- Model comparison and performance metrics (ROC-AUC, PR-AUC, Accuracy, etc.)
- Admin dashboard for model management and user administration
- Multi-currency support (VND/NT$)
- Audit logs and prediction history
- AI Assistant (Gemini integration, optional)

## Technology Stack

- **Python 3.12** (recommended)
- **PyQt6** for GUI
- **scikit-learn**, **xgboost**, **lightgbm** for ML
- **MySQL** for database
- **pandas**, **numpy**, **matplotlib** for data processing and visualization

## Project Structure

```
MLBA_FinalProject/
├── main.py                  # Main entry point
├── ui/                      # UI components (PyQt6)
├── services/                # Business logic and database services
├── ml/                      # Machine learning scripts and models
├── models/                  # Data models
├── outputs/                 # Model files, evaluation results, charts
├── database/credit_risk_db/ # SQL schema files (import here!)
├── config/                  # Configuration files
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Prerequisites

- **Python 3.12** (strongly recommended)
- **MySQL** server (tested with MySQL 8+)
- **pip** (Python package manager)

## Installation

1. **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/MLBA_FinalProject.git
    cd MLBA_FinalProject
    ```
2. **Create and Activate a Virtual Environment (Recommended)**
    ```bash
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```
3. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

## Database Setup

1. **Start MySQL Server** and create a database (e.g., `credit_risk_db`).
2. **Import Data Schema**
    - Open your MySQL client (Workbench, DBeaver, or command line).
    - Import all `.sql` files from the folder:
      ```
      database/credit_risk_db/
      ```
    - This will create all necessary tables: users, customers, predictions_log, model_registry, etc.
3. **(Optional) Update database credentials**
    - Edit `config/database_config.py` if your MySQL username/password is different.

## Running the Application

1. **Train Machine Learning Models** (first time only)
    ```bash
    python ml/train_models.py
    ```
    This will generate model files and evaluation data in `outputs/models/` and `outputs/evaluation/`.

2. **Start the Application**
    ```bash
    python main.py
    # or
    py -3.12 main.py
    ```

## Usage Guide

- On launch, the login screen will appear. Use the following demo accounts:

    **Admin:**
    - Username: `ilovetranduythanh2`
    - Password: `10diem10diem`

    **User:**
    - Username: `ilovetranduythanh1`
    - Password: `10diem10diem`

- **Admin** can manage users, train models, view all predictions, and access system settings.
- **User** can input customer data, make predictions, and view their own prediction history.
- Use the "Model Management" tab (Admin) to train or activate new models.
- All data is stored in the MySQL database.

## Team Members

This project is developed by **Group 3** for the final project.
| No  | Name                   | Student ID | Email                        | Role   |
| :-- | :--------------------- | :--------- | :--------------------------- | :----- |
| 1   | Nguyen Chi Duc         | K234111429 | ducnc234112e@st.uel.edu.vn   | Leader |
| 2   | Nguyen Hoang Khanh Nhu       | K234111412 | nhunhk234111e@st.uel.edu.vn   | Member |
| 3   | Huynh Ngoc Nhu Y  | K234111462 | yhnn234112e@st.uel.edu.vn   | Member |
| 4   | Nguyen Thi Bao Tran | K234111455 | tranntb234112e@st.uel.edu.vn | Member |
| 5   | Nguyen Quoc Thinh    | K234111452 | thinhnq234112e@st.uel.edu.vn   | Member |


## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m 'Add YourFeature'`).
4. Push to your branch (`git push origin feature/YourFeature`).
5. Open a Pull Request.

## License

This project is for educational purposes only. All rights reserved by the development team.
