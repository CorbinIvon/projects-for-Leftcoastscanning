# This script will have a function accessible from other scripts that will send a message to whomever needs the message.
# Source - https://realpython.com/python-send-email/#getting-started
# Before use, make sure the google account you are trying to use has Developer mode enabled.
import smtplib, ssl
def send_email(reciever, message_header, message_body):
    try:
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = ""  # Enter your address
        if reciever == "":
            reciever = sender_email
        password = ""
        receiver_email = reciever  # Enter receiver address

        message = ("Subject: " + message_header + "\n\n" + message_body)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
        print ("An Error has occured and has been sent.")
    except:
        print("There seems to be an issue sending the message.")
