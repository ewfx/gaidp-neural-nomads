# 🚀 Project Name : Gen AI-Powered Data Profiling

## 📌 Table of Contents
- [Introduction](#-introduction)
- [Demo](#-demo)
- [Inspiration](#-inspiration)
- [What It Does](#%EF%B8%8F-what-it-does)
- [Architecture](#-architecture)
- [How We Built It](#%EF%B8%8F-how-we-built-it)
- [Challenges We Faced](#-challenges-we-faced)
- [Future Scope](#-future-scope)
- [How to Run](#-how-to-run)
- [Tech Stack](#%EF%B8%8F-tech-stack)
- [Team](#-team-name--neural-nomads)


---

## 🎯 Introduction
In the banking sector, regulatory reporting involves compiling and analyzing vast amounts of data to ensure compliance with complex regulatory requirements. This process is traditionally manual and time-consuming, often leading to inefficiencies and potential errors.

Our project addresses this challenge by leveraging Generative AI (LLMs) and unsupervised machine learning techniques to automate data profiling. Our goal was to develop a solution that extracts regulatory instructions, generates profiling rules, and flags anomalous transactions along with the reason. By automating these processes, we aim to enhance operational efficiency, reduce compliance risks, and improve reporting accuracy.

## 🎥 Demo 
📹 [Video Demo](https://www.youtube.com/watch?v=3663livYy_g)  

## 💡 Inspiration
The inspiration behind this project stems from the need to streamline regulatory reporting in banking by automating data profiling. Traditional methods involve manual rule definition, which is time-consuming and prone to errors. By leveraging AI and machine learning, we aim to enhance compliance efficiency and accuracy.

## ⚙️ What It Does
1. **Regulatory Instruction Interpretation:** Extracts and interprets regulatory reporting instructions to identify data validation requirements.

2. **Automated Profiling Rule Generation:** Uses Large Language Models (LLM-Gemini) to generate profiling rules based on allowable values and cross-relations between data elements.

3. **Executable Validation Code:** Generates executable SQL queries to assess data conformity against extracted rules.

4. **Anomaly Detection with Reasoning:** Identifies flagged transactions along with their reasons, combining outputs from SQL validation and a unsupervised learning approach(Isolation Forest). The results are further enhanced with natural language reasoning using the Gemini, providing comprehensive and human readable insights into anomalous transactions.

5. **Interactive Custom Conversational Interface (Chainlit UI):** Offers a user-friendly and ADA compliant interface for two primary personas:

     - **Auditor:** Can upload CSV files to receive flagged transactions with detailed explanations, facilitating efficient review and validation.

     - **Admin:** Has the ability to view, update, and refine profiling rules, ensuring that the system remains aligned with evolving regulatory requirements and organizational needs.
       
6. **ADA Compliant Interface:** Includes speech-to-text integration, ensuring accessibility for users with visual or physical impairments, enhancing inclusivity.

7.  **Ethical AI and Fairness:**  
   - Ensured **ethical AI** practices by incorporating fairness and bias checks into the anomaly detection process.  
   - Improved transparency by generating **natural language explanations** for all flagged transactions.  

## 🏗 Architecture
![Gen AI Hackathon (2)](https://github.com/user-attachments/assets/75540c4c-5fb1-4936-a52a-a9b63e43ec8b)



## 🛠️ How We Built It
Our solution was developed using a diverse set of modern technologies and tools to ensure robustness, scalability, and user-friendly interaction:

*   **Chainlit:** Utilized for creating a interactive conversational interface that facilitates smooth interactions between users and the system.

*   **Gemini:** Integrated to generate profiling rules and SQL queries for validation and natural language explanations for flagged transactions, enhancing transparency and understanding.

*   **Scikit-learn:** Employed for implementing machine learning models, specifically the Isolation Forest algorithm for detecting anomalies.

*   **FastAPI:** Used to build a high-performance python based backend API that efficiently handles data processing and requests.

*   **React:** Implemented for developing a responsive and interactive frontend interface.

*   **SQLite:** Served as the database solution for storing and managing profiling rules and transaction data.

## 🚧 Challenges We Faced

1.   **Custom Chainlit Component Development:** Developing a custom Chainlit component that integrates with React allowed us to push the boundaries of conversational interface design. Overcoming compatibility issues and ensuring responsiveness enabled us to create a highly intuitive user experience, enhancing the overall usability of our solution.

2.   **Optimizing Free-Tier Models:** Leveraging free-tier models required us to be creative and resourceful. Despite limitations in accuracy and RPM allowances, we successfully optimized our solution to maximize performance within these constraints. This experience honed our ability to efficiently utilize resources and develop scalable, cost-effective solutions.


## 🔜 Future Scope

✔️ **Chain-of-Thoughts:**  
   - Incorporate real time streaming of chain of thoughts to ensure explainable AI

✔️ **Multi-language support:**  
   - Expand accessibility across regions by incorporating **prompt enhancement** to generate accurate, context-specific profiling rules in multiple languages.  

✔️ **Broader Reporting Coverage:**  
   - Apply the solution to more other regulatory reporting PDFs and schedules using **prompt caching** to reduce model calls and improve efficiency.  

✔️ **Adaptive anomaly models with Human-in-the-loop:**  
   - Enhance anomaly detection accuracy through **human-in-the-loop (HITL)** validation.  
   - Refine machine learning models using **Reinforcement Learning through Human Feedback (RLHF)** to continuously improve accuracy and precision.  

✔️ **Real-time Data Streaming and Analysis:**  
   - Expand the solution to support **real-time data streaming** for continuous monitoring of regulatory compliance.

✔️ **Personalized User Experience:**  
   - Persist user preferences, such as **custom rule filters, display settings, and report preferences**, for a tailored and **personalized experience**.  


## 🏃 How to Run
1. **Clone the repository**  
   ```sh
   git clone https://github.com/ewfx/gaidp-neural-nomads.git
   ```
2. **Create Virtual Environments:** <br>
   
   Create two separate virtual environments for the backend and frontend:
   
    1. **Backend Virtual Environment:** <br>
       
        Navigate to the backend directory.
        ```sh
        cd code/src/Backend server
        ```
        Create virtual environment for backend: 
        ```sh
            python -m venv backend_venv
        ```
       Activate the backend virtual environment:
        ```
            # On Windows
            .\backend_venv\Scripts\activate
            # On Linux/Mac
            source backend_venv/bin/activate
         ```
        
    3. **Frontend Virtual Environment:** <br>
    
       Navigate to the frontend directory.
        ```sh
        cd code/src/Chatbot
        ```
       Similarly create virtual environment for frontend: 
        ```sh
            python -m venv frontend_venv
         ```
       Activate the frontend virtual environment:
       ```
            # On Windows
            .\frontend_venv\Scripts\activate
            # On Linux/Mac
            source frontend_venv/bin/activate
        ```
4. **Install Dependencies and Run Application**

   1.   **Backend Dependencies:**

        Navigate to the backend directory. Install the required dependencies using pip:
        ```sh
        pip install -r requirements.txt
        ```
        Create a .env file under src/Backend server folder and paste your Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)
        ```sh
        GEMINI_API_KEY = <your_api_key>
        ```
        Run the backend server from backend directory:
        ```sh
        python main.py
        ```
   3.   **Frontend Dependencies:**
      
        Navigate to the frontend directory. Install the required dependencies using pip:
        ```sh
        pip install -r requirements.txt
        ```
        Setup chainlit auth secret `CHAINLIT_AUTH_SECRET=<secret_key_obtained>` in .env file under src/Chatbot by running this command
        ```sh
        chainlit create-secret
        ```
        Run the frontend application:
        ```sh
        chainlit run app.py
        ```


## 🏗️ Tech Stack
- 🔹 Frontend: React , Chainlit
- 🔹 Backend: FastAPI , Python
- 🔹 Database: SQLite3
- 🔹 LLM: Gemini

  
![Gen AI Hackathon (1)](https://github.com/user-attachments/assets/dec27744-53c9-4c04-a645-b4ac1dd21f19)
  

## 👥 Team Name : Neural Nomads
- **Neha Anand** - [GitHub](https://github.com/NehaAnand28) | [LinkedIn](https://www.linkedin.com/in/neha-anand-927157200/)
- **Sukriti Bohra** - [GitHub](https://github.com/sukriti136) | [LinkedIn](https://www.linkedin.com/in/sukriti-bohra-b93795218?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app
)
- **Nikhil Giri** - [GitHub](https://github.com/NikhilGiri29) | [LinkedIn](https://www.linkedin.com/in/nikhil-giri-aa7704200/?originalSubdomain=in)
- **Aishwarya Attanti** - [GitHub](https://github.com/attanti123) | [LinkedIn](https://www.linkedin.com/in/attanti123/)
- **Lalitha Ramakrishnan** - [GitHub](https://github.com/lalithapanda) | [LinkedIn](https://www.linkedin.com/in/lalitha-ramakrishnan-0a8b66a/)
