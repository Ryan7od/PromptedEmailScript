A script to have an LLM generate a non-determinant response to a prompt, then send it to a list of recipients.

.env:
EMAIL_LIST= {Comma list of emails to send to}


SMTP_USERNAME= {Sender email}
SMTP_PASSWORD= {Sender SMTP password}

AFFIRMATION_PROMPT1="Use the random seed "
AFFRIMATION_PROMPT2=" to {rest of prompt}"

HUGGINGFACE_APIKEY= {Huggingface API Key}
