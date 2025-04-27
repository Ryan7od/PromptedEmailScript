import os
import random
import time
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def send_email(subject, body, recipients):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")

    msg = MIMEMultipart()
    msg["From"] = smtp_username
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)

        for recipient in recipients:
            msg["To"] = recipient
            server.sendmail(smtp_username, recipient, msg.as_string())
            del msg["To"]
            print(f"Email sent to {recipient}")

    except Exception as e:
        print("Error sending email:", str(e))


def get_affirmation():
    HF_API_TOKEN = os.getenv("HUGGINGFACE_APIKEY")
    #model = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    #model = "google/gemma-3-1b-it"
    model = "google/gemma-2-2b-it"
    API_URL = f"https://api-inference.huggingface.co/models/{model}"

    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    prompt = os.getenv("PROMPT1") + str(random.randint(1,10000)) + os.getenv("PROMPT2")
    print(prompt)

    max_retries = 5
    result = None
    for attempt in range(max_retries):
        for backoff in [2, 4, 8, 16]:
            result = requests.post(API_URL, headers=headers, json={"inputs": prompt})
            if result.status_code == 503:
                print(f"503—retrying in {backoff}s…")
                time.sleep(backoff)
                continue
            result.raise_for_status()
            result = result.json()
            break
        else:
            raise RuntimeError("Model still unavailable after retries")
        if "error" in result and "loading" in result["error"].lower():
            print (result)
            wait_time = result["estimated_time"]
            print(f"Attempt {attempt + 1}: Model is loading. Waiting {wait_time} seconds...")
            time.sleep(wait_time)
        elif "error" in result:
            print(result)
            print("Unknown error, trying again one more time")
        else:
            break

    if isinstance(result, list) and "generated_text" in result[0]:
        affirmation = result[0]["generated_text"]
        print(affirmation)
        if affirmation.startswith(prompt):
            return affirmation[len(prompt):].strip()
        return affirmation

    print(result)
    return "Affirmation generation failed, my bad"

def lambda_handler(event, context):
    execute()
    print("Lambda triggered!")
    return {
        'statusCode': 200,
        'body': 'Daily affirmation email sent successfully!'
    }

def execute():
    recipients = os.getenv("EMAIL_LIST").split(',')
    print(recipients)
    body = get_affirmation()
    print(body)
    send_email("Your Daily Affirmation", body, recipients)

if __name__ == "__main__":
    execute()

