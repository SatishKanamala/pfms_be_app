from fastapi_mail import FastMail,MessageSchema,ConnectionConfig
from starlette.config import Config


async def send_email(subject: str, recipient: list[str], password:str, username:str):
    #message = f"{message} Your password is: {password}"
    html_content = f"""
    <!DOCTYPE html>
    <html>
        <body>
            <h3>Hi {username}, Welcome to PFMS</h3><br/>
            <p>Your Automated generated password  is: {password} </p>
            <p>Use this password when you login to PFMS with your mail. This is automate generated mail please do not reply</p>
            <br />

            <p>Thank you,</p>
            <p>Team PFMS.</p>

        </body>
    </html>
    """
    message = MessageSchema(
        subject=subject,
        recipients=recipient,
        body=html_content,
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)
 
config = Config('.env')
 
mail_port_str = config("MAIL_PORT")
mail_port = int(mail_port_str.split()[0])
 
conf = ConnectionConfig(
MAIL_USERNAME = config("MAIL_USERNAME"),
MAIL_PASSWORD = config("MAIL_PASSWORD"),
MAIL_FROM = config("MAIL_FROM"),
MAIL_PORT =  mail_port,
MAIL_SERVER = config("MAIL_SERVER"),
 
USE_CREDENTIALS = config("USE_CREDENTIALS"),
MAIL_STARTTLS= config("MAIL_STARTTLS"),
MAIL_SSL_TLS = config("MAIL_SSL_TLS"),
MAIL_DEBUG =config("MAIL_DEBUG"),
 
SUPPRESS_SEND = config("SUPPRESS_SEND"),
VALIDATE_CERTS= config("VALIDATE_CERTS"),
 
)
 
import random
import string
 
def generate_password():
    """Generates a random numeric password of specified length."""
    digits = string.ascii_letters
    password = ''.join(random.choice(digits) for _ in range(6))
    password += '!A1'
    return password