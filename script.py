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
    model = "google/gemma-2-2b-it"
    API_URL = f"https://api-inference.huggingface.co/models/{model}"

    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    prompt = os.getenv("AFFIRMATION_PROMPT") + str(random.randint(1,10000))
    print(prompt)

    max_retries = 5
    result = None
    for attempt in range(max_retries):
        result = requests.post(API_URL, headers=headers, json={"inputs": prompt}).json()
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
            prompt2 = "Please take the following input and format it so that it is only the inspirational message: \"" + affirmation + "\". Do not provide anything else, only the formatted message. Do not repeat the instruction."
            middle = requests.post(API_URL, headers=headers, json={"inputs": prompt2}).json()[0]["generated_text"]
            generated_text = middle[len(prompt2):].strip()
        else:
            generated_text = affirmation.strip()
        return generated_text

    print(result)
    return "Affirmation generation failed, my bad"

if __name__ == "__main__":
    recipients = os.getenv("EMAIL_LIST").split(',')
    print(recipients)
    body = get_affirmation()
    print(body)
    send_email("Your Daily Affirmation", body, recipients)

