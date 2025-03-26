from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import json
from services.anamoly_service import train_model, detect_anomalies, analyze_anomalies

router = APIRouter()

@router.get('/initiate')
def initiate():
    return train_model("../Temp_files/transaction.csv")

@router.get("/anamoly_detection_and_analysis")
def anamoly_detection_and_analysis():
    anomalies = detect_anomalies("../Temp_files/new_tran.csv")
    return analyze_anomalies(anomalies, "../Temp_files/new_tran.csv")

@router.get("/anamoly_detection_pipeline")
def anamoly_detection_and_analysis():
    training_result = train_model("../Temp_files/new_tran.csv")
    print("======================================")
    print(training_result)
    anomalies = detect_anomalies("../Temp_files/new_tran.csv")
    print("======================================")
    print(anomalies)
    print("======================================")
    return analyze_anomalies(anomalies['anomaly_ids'], "../Temp_files/new_tran.csv")