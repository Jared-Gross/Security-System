import smtplib, os, json
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def email_picture(name, text):
    settings_file = os.path.dirname(os.path.realpath(__file__)) + '/settings.json'
    email_address = []
    ip = []
    image_folder = 'Pics'
    with open(settings_file) as file:
        settings_json = json.load(file)
        for info in settings_json:
            for email in info['email address']: email_address.append(email)
            for ipaddress in info['host address']: ip.append(ipaddress)
    EMAIL = 'jaredgrozz@gmail.com'
    EMAIL_TO = email_address[0].split(', ')
    EMAIL_PASSWORD = 'ffvprugomuuywemq'#<-
    '''                                   \
                                        \
    DO NOT USE YOUR ACTUAL GMAIL PASSWORD!! \
    go here sign into your google account    \
    https://myaccount.google.com/security     \
        go to app passwords                    |
    create a password and put that password there.
    
    Also showcased here: https://www.interviewqs.com/blog/py_email
    '''
    for i, k in enumerate(EMAIL_TO):
        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = 'Carpentar Shop ALERT!'
        msgRoot['From'] = EMAIL
        msgRoot['To'] = k
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)
        msgText = MIMEText(f'{text}\n\n{datetime.now()}\n<br><img src="cid:image1"><img src="cid:image2"><br> <a href=\"http://{ip}:5000\">Watch Live</a>', 'html')
        msgAlternative.attach(msgText)
        for i, j in enumerate(name):
            try:
                with open(f'Pics/{name[i]}', 'rb') as fp:
                    msgImage = MIMEImage(fp.read())
                    msgImage.add_header('Content-ID', f'<image>{i}')
                    msgRoot.attach(msgImage)
            except FileNotFoundError:
                with open(f'Pics/{name[0]}', 'rb') as fp:
                    msgImage = MIMEImage(fp.read())
                    msgImage.add_header('Content-ID', f'<image>{i}')
                    msgRoot.attach(msgImage)
        smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp.login(EMAIL, EMAIL_PASSWORD)
        smtp.sendmail(EMAIL, k, msgRoot.as_string())
        smtp.quit()
        print('Email sent!')
    for the_file in os.listdir(image_folder):
        file_path = os.path.join(image_folder, the_file)
        try:
            if os.path.isfile(file_path): os.unlink(file_path)
        except Exception as e:
            print(e)
    print('Images deleted')
