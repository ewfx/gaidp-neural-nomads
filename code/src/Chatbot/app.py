from typing import Optional
import chainlit as cl
from datetime import datetime, timedelta
import random
import json
import wave
import os
import io
import speech_recognition as sr
import numpy as np
import audioop
import pandas as pd
import requests

@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="Admin",
            markdown_description="This persona provides access to all system features.",
            icon="https://picsum.photos/300",
        ),
        cl.ChatProfile(
            name="Auditor",
            markdown_description="View transactions, analyse and find out anomalies.",
            icon="https://picsum.photos/200",
        ),
    ]
commands = [
    {"id": "Rules", "icon": "bot", "description": "Will show the rules; Usage: /Rules <Rule_indentifier>"},
]

@cl.password_auth_callback
def auth_callback(username: str, password: str):
    if (password == "wf"+username):
        return cl.User(identifier=username, metadata={"role": "user","provider": "credentials"})
    return None

@cl.on_chat_start
async def on_chat_start():
    await cl.context.emitter.set_commands(commands)
    app_user = cl.user_session.get("user")
    await cl.Message(f"Hello {app_user.identifier}").send()
    
    user_chat_profile = cl.user_session.get("chat_profile")
    if user_chat_profile == "Admin":
        await cl.Message(content="👋 Welcome to the Transaction Admin System. How can I help you today?").send()
        
    elif user_chat_profile == "Auditor":
        await cl.Message(content="👋 Welcome Auditor! You can view transactions and audit them for anomalies.").send()


@cl.on_message
async def on_message(message: cl.Message):
    user_chat_profile = cl.user_session.get("chat_profile")
    user_id = cl.user_session.get("user_id")
    content = message.content
    if message.command == "Rules":
        identifier = content
        rules_path = "../Database/rules"
        available_rules = [os.path.splitext(f)[0] for f in os.listdir(rules_path) if f.endswith('.json') and os.path.isfile(os.path.join(rules_path, f))]
        print(available_rules)
        if identifier not in available_rules:
            await cl.Message(content="Invalid identifier. Please type @AvailableRules to see all possible values.").send()
        else:
            # Fetch the rule from the new router
            response_message = f"Displaying rule: {identifier}"
            if user_chat_profile == "Admin":
                rules_table = cl.CustomElement(
                    name="RulesTable",
                    props={"identifier": identifier, "isAdmin": True}
                )
                await cl.Message(content=response_message, elements=[rules_table]).send()
            else:
                rules_table = cl.CustomElement(
                    name="RulesTable",
                    props={"identifier": identifier, "isAdmin": False}
                )
                await cl.Message(content=response_message, elements=[rules_table]).send()


    elif content.lower() =="@availablerules":
        rules_path = "../Database/rules"
        available_rules = [os.path.splitext(f)[0] for f in os.listdir(rules_path) if f.endswith('.json') and os.path.isfile(os.path.join(rules_path, f))]
        await cl.Message(content=f"Available rules: {available_rules}").send()

        
    elif content.lower() == "@createrules":
        res = await cl.AskUserMessage(content="What do you want the new rules set to be called?", timeout=100).send()
        if res:
            await cl.Message(
                content=f"Creating rules: {res['output']}",
            ).send()
        else:
            await cl.Message(content="No response received").send()
            return
        rules_path = f"../Database/rules/{res['output']}.json"
        pdf_res = await cl.AskFileMessage(content="Please upload the PDF for the new rules.", timeout=100, accept=["application/pdf"]).send()
        if pdf_res:
            pdf_file = pdf_res[0]
            print(pdf_file)
            source_path = pdf_file.path
            dest_path = f"../Database/rules/{res['output']}.pdf"
            with open(source_path, "rb") as src, open(dest_path, "wb") as dst:
                dst.write(src.read())
            await cl.Message(content=f"PDF for rules '{res['output']}' uploaded successfully.").send()
            
            # Call the new endpoint to generate rules
            response = requests.post(
                "http://localhost:5000/generate/rules",
                json={"file_path": dest_path, "output_file": rules_path}
            )
            if response.status_code == 200:
                await cl.Message(content="Rules generated successfully.").send()
            else:
                await cl.Message(content=f"Failed to generate rules: {response.json().get('detail')}").send()
        else:
            await cl.Message(content="No PDF uploaded or invalid file type.").send()
            return
        

    elif content.lower() == "@startprofiling":
        files = None
        while files == None:
            files = await cl.AskFileMessage(
                content="Please upload a CSV file to proceed with the audit.",
                accept=["text/csv"],
                max_size_mb=20

                
            ).send()
        
        # Get the uploaded CSV file
        csv_file = files[0]
        
        try:
            await cl.Message(content="Processing the CSV").send()        
            # Parse the CSV with pandas
            df = pd.read_csv(csv_file.path)
            
            # Save the parsed CSV to the data folder
            df.to_csv('../Temp_files/new_tran.csv', index=False)

            delete_response = requests.delete("http://localhost:5000/dbdelete")
            print(delete_response.text)

            response_db = requests.post("http://localhost:5000/uploadTransactionCSV/0")
            print(response_db.text)
            await cl.Message(content="Sending the transactions in Anomaly Identifier Pipeline").send()
            response = requests.get("http://localhost:5000/anamoly_detection_pipeline")
            if response.status_code == 200:

                anomaly_card = cl.CustomElement(
                    name="AnomalyDetectionResultsCard",
                    props={"results": response.text}
                )
                await cl.Message(content="Anomaly Detection completed successfully.", elements=[anomaly_card]).send()
            else:
                await cl.Message(content="Anomaly Detection failed").send()
            
        except Exception as e:
            await cl.Message(content=f"Error processing your CSV file: {str(e)}").send()
            return None, None
        

    elif content.lower() == "@validatedata":
        # Get available rule sets
        rules_path = "../Database/rules"
        available_rules = [os.path.splitext(f)[0] for f in os.listdir(rules_path) if f.endswith('.json') and os.path.isfile(os.path.join(rules_path, f))]
        
        # Create actions for rule selection
        actions = [
            cl.Action(
                name="rule_selection", 
                payload = {"value":rule}, 
                label=rule
            ) for rule in available_rules
        ]
        
        # Send message with rule selection actions
        res = await cl.AskActionMessage(
            content="Select a rule set for data validation:",
            actions=actions
        ).send()
        identifier = res.get("payload").get("value")

        if res:
            await cl.Message(
                content=f"Starting data valiation using rule set: {identifier}",
            ).send()
            response = requests.get(
                f"http://localhost:5000/rules/validate/{identifier}",
            )
            if response.status_code == 200:
                validation_card = cl.CustomElement(
                    name="ValidationResultsCard",
                    props={"results": response.text}
                )
                await cl.Message(content="Validation Completed", elements=[validation_card]).send()
            else:
                await cl.Message(content="Validation failed").send()

    else:
        await cl.Message(content="No response received").send()
        return

