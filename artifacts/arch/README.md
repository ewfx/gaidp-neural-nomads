# 🚀 Gen AI Hackathon – Data Profiling and Anomaly Detection

## 🛠️ **Architecture Overview**
This project is designed to perform **data profiling and anomaly detection** on financial transaction data. It uses **LLM-powered rule generation and SQL execution** to identify anomalous transactions. The architecture consists of the following layers:

---

## 📚 **1. Application Layer**

### **User Interface:**
- Allows users to upload **rules and regulations** (CSV/PDF) and transaction datasets.
- Provides **persona-based access control** with authentication features.
- Displays profiling results and detected anomalies using a visual dashboard.
- **Tools:** 
  - CSV/PDF import functionality.
  - Interactive data visualization.

---

## ⚙️ **2. Middleware Layer**

The middleware handles the core processing logic and interacts with the LLM API. It comprises:

### **FastAPI Middleware and LLM Wrapper**
- Handles communication between the frontend, database, and LLM.
- **Components:**
  - **Rule Engine:** Generates SQL rules by interpreting the uploaded CSV/PDF content.
  - **Anomaly Detector:** Identifies outliers by executing generated SQL rules on the transaction database.
  - **SQL Executor:** Executes SQL commands against the on-premises database.
- **Technologies:** 
  - **FastAPI:** For API interactions.
  - **SQL:** For executing the profiling rules on the database.
  - **LangChain/LLM Wrapper:** To send inference requests to Gemini API.

---

## 🔥 **3. LLM Integration (Gemini API)**

- The architecture uses **Google Gemini** for:
  - **Chat completion** and LLM inference.
  - Generating **SQL rules** from extracted fields.
  - Executing SQL queries to detect anomalous transactions.
- **Outputs:** Executable SQL commands returned to the middleware.

---

## 💾 **4. On-Premises Database**

- Stores **rules and transactions** for profiling.
- The middleware executes SQL queries on this database and retrieves the result set.
- **Databases:**
  - **Rules DB**: Stores the generated profiling rules.
  - **Transaction DB**: Contains financial transaction records.

---

## 🔁 **5. RLHF (Reinforcement Learning with Human Feedback)**

- Feedback from the application interface is sent to the **RLHF module**.
- RLHF refines the rules and anomaly detection accuracy based on user input.
- Enhances **rule learning** iteratively.

---

## 🚦 **Tech Stack**
- **Frontend:** React (Application Interface)
- **Backend:** FastAPI (Middleware)
- **Database:** SQL (On-Premises)
- **LLM:** Gemini API for rule generation and anomaly detection
- **Machine Learning:** RLHF for continuous improvement
- **Deployment:** Docker (optional for scalability)

---

## 🔥 **Flow Summary**
1. User uploads transaction data and rules (CSV/PDF) via the application interface.
2. The middleware processes the files and sends them to the **Gemini LLM** for rule generation.
3. The LLM returns SQL rules, which are executed on the on-premises database.
4. SQL results are sent back to the application and displayed visually.
5. Users can provide feedback, which is used by the **RLHF module** to improve accuracy over time.

---

✅ **This architecture ensures efficient data profiling, anomaly detection, and continuous improvement using reinforcement learning.**