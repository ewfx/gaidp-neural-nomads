import re
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
import google.generativeai as genai
from google.generativeai import GenerativeModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Validate API key
if not API_KEY:
    raise ValueError(
        " Missing Gemini API key. Make sure it's set in the .env file.")

# Configure Gemini API
genai.configure(api_key=API_KEY)

# File paths
MODEL_PATH = "./models/anomoly_detection_model.pkl"
gemini_model = genai.GenerativeModel("gemini-1.5-pro")

def train_model(file_path):
    start_time = datetime.now()
    
    df = pd.read_csv(file_path, index_col="Transaction ID")  
    df.fillna("Unknown", inplace=True)

    # Encode categorical features
    label_encoders = {}
    categorical_cols = df.select_dtypes(include=['object']).columns

    for col in categorical_cols:
        df[col] = df[col].astype(str)
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le

    # Normalize numerical features
    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df)

    # Train Isolation Forest
    iso_forest = IsolationForest(n_estimators=100, contamination=0.02, random_state=42)
    iso_forest.fit(df_scaled)  # Training step

    end_time = datetime.now()

    # Save trained model, scaler, and encoders
    model_metadata = {
        "model": iso_forest, 
        "scaler": scaler, 
        "encoders": label_encoders, 
        "df_original": df,
        "training_metadata": {
            "timestamp": start_time.isoformat(),
            "total_transactions": len(df),
            "categorical_columns": list(categorical_cols),
            "training_time": (end_time - start_time).total_seconds(),
            "model_params": {
                "n_estimators": 100,
                "contamination": 0.02,
                "random_state": 42
            }
        }
    }
    
    joblib.dump(model_metadata, MODEL_PATH)
    
    return {
        "status": "success",
        "message": f" Model trained and saved to {MODEL_PATH}",
        "model_details": model_metadata["training_metadata"]
    }

def detect_anomalies(file_path):
    start_time = datetime.now()
    
    if not os.path.exists(MODEL_PATH):
        return {
            "error": "Model not found! Please train the model first.",
            "status": "failed"
        }

    saved_data = joblib.load(MODEL_PATH)
    iso_forest = saved_data["model"]
    scaler = saved_data["scaler"]
    label_encoders = saved_data["encoders"]
    
    df_new = pd.read_csv(file_path, index_col="Transaction ID")
    total_transactions = len(df_new)
    
    df_new.fillna("Unknown", inplace=True)
    
    categorical_cols = df_new.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        df_new[col] = df_new[col].astype(str)
        if col in label_encoders:
            le = label_encoders[col]
            df_new[col] = df_new[col].apply(lambda x: le.transform([x])[0] if x in le.classes_ else -1)
        else:
            df_new[col] = -1  
    
    df_scaled_new = scaler.transform(df_new)
    df_new["Anomaly"] = iso_forest.predict(df_scaled_new)

    anomalous_transactions = df_new[df_new["Anomaly"] == -1].index.tolist()
    
    end_time = datetime.now()
    
    return {
        "timestamp": start_time.isoformat(),
        "total_transactions": total_transactions,
        "anomalous_transactions": len(anomalous_transactions),
        "anomaly_rate": round(len(anomalous_transactions) / total_transactions * 100, 2),
        "anomaly_ids": anomalous_transactions,
        "execution_time": (end_time - start_time).total_seconds(),
        "model_details": {
            "model_type": "Isolation Forest",
            "contamination_rate": 0.02,
            "n_estimators": 100
        },
        "output_file": "../Temp_files/analysed_transaction.xlsx",
        "status": "success"
    }

def analyze_anomalies(transaction_ids, new_data_path):
    start_time = datetime.now()
    saved_data = joblib.load(MODEL_PATH)
    df_original = saved_data["df_original"]
    df_new = pd.read_csv(new_data_path, index_col="Transaction ID")

    # Extract only the anomalous transactions using the provided list of IDs
    anomalous_df = df_new.loc[transaction_ids]

    # Merge original dataset with detected anomalies and mark anomaly flag
    df_full = pd.concat([df_original, anomalous_df])  
    df_full["Anomaly"] = df_full.index.isin(anomalous_df.index).astype(int)

    # Get only normal transactions for comparison
    normal_transactions = df_full[df_full["Anomaly"] == 0].drop(columns=["Anomaly"], errors="ignore")

    # Prepare human-readable analysis document
    anomaly_report = []
    anomalies_data = {}

    for txn_id, row in anomalous_df.iterrows():
        differences = {}
        explanation = f"🔹 *Transaction ID: {txn_id}*\n"

        for col in df_original.columns:
            if col in normal_transactions:
                normal_mean = normal_transactions[col].mean()
                normal_std = normal_transactions[col].std()

                if col in saved_data["encoders"]:  # Categorical column
                    normal_mode = normal_transactions[col].mode().values
                    if row[col] not in normal_mode:
                        differences[col] = f"Unusual category: {row[col]}"
                        explanation += f"   - *{col}*: {row[col]} is not a common category.\n"
                else:  # Numerical column
                    if abs(row[col] - normal_mean) > 2 * normal_std:
                        differences[col] = f"Outlier value: {row[col]} (Normal: Mean {normal_mean:.2f}, Std {normal_std:.2f})"
                        explanation += f"   - *{col}*: {row[col]} is far from the usual range (Mean: {normal_mean:.2f}, Std: {normal_std:.2f}).\n"

        anomaly_report.append(explanation)
        anomalies_data[str(txn_id)] = differences

    # Combine everything into a human-readable document
    report_text = "\n".join(anomaly_report)

    # Convert to JSON and send to Gemini
    anomalies_json = json.dumps(anomalies_data, indent=2)
    prompt = f"""
    Below is a human-readable report of financial transactions flagged as anomalous:

    {report_text}

    Additionally, here is a JSON containing structured anomaly details:

    {anomalies_json}

    Please analyze these transactions and return a JSON output explaining why each transaction might be suspicious.
    
    The JSON should look like:
    
        "transaction Id1": "Explanation for anomaly 1",
        "transaction Id2": "Explanation for anomaly 2"
    
    """

    ai_response = gemini_model.generate_content(prompt).text
    cleaned_text = re.sub(r'```json\n|\n```', '', ai_response)
    print(cleaned_text)
    update_csv_with_reasons(new_data_path, transaction_ids, json.loads(cleaned_text))
    
    end_time = datetime.now()
    
    return {
        "timestamp": start_time.isoformat(),
        "total_anomalies": len(transaction_ids),
        "ai_analysis_time": (end_time - start_time).total_seconds(),
        "output_file": "../Temp_files/analysed_transaction.xlsx",
        "status": "success",
        "raw_analysis": cleaned_text
    }

def update_csv_with_reasons(file_path, anomaly_ids, explanations):
    df_new = pd.read_csv(file_path, index_col="Transaction ID")

    # Ensure all anomaly IDs are strings for consistency with the dictionary
    explanations = {str(k): v for k, v in explanations.items()}

    # Add a new "Reason" column, defaulting to "Normal transaction"
    df_new["Reason"] = df_new.index.map(lambda txn: explanations.get(str(txn), ""))
    
    df_new.to_csv("../Temp_files/analysed_transaction.csv", index=True)
    
    # Function to highlight anomalies in yellow
    def highlight_anomalies(row):
        return ["background-color: yellow" if str(row.name) in anomaly_ids else "" for _ in row]

    # Apply highlighting
    styled_df = df_new.style.apply(highlight_anomalies, axis=1)

    # Save to Excel with formatting
    styled_df.to_excel("../Temp_files/analysed_transaction.xlsx", index=True, engine="openpyxl")  

    print(f" Updated CSV saved as 'analysed_transaction.xlsx' with anomaly reasons.")