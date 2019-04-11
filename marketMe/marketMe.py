import smtplib, requests, bs4, random, sys, yaml, calendar
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

path = '/users/chrisgrant/marketMe/config.yml'
config = open(path, 'r')
data = yaml.safe_load(config.read())
with open("template.html", "r") as htmlFile:
    template=htmlFile.read()
start_date = datetime.strptime(data["start_date"], "%m/%d/%Y")
end_date = datetime.strptime(data["end_date"], "%m/%d/%Y")
today = datetime.now()
calendar_day = calendar.day_name[today.weekday()]

if(today >= start_date and today <= end_date):
    if(calendar_day in data["send_on"]):
        sender_email = data["sender_email"]
        receiver_emails = data["recipient_list"]
        password = data["password"]
        searchCode = ''.join(sys.argv[1:])
        res = requests.get('https://www.ticketsmeters.com/search?q='+ searchCode)
        showsSoup = bs4.BeautifulSoup(res.text, features="html.parser")
        eventInfo = showsSoup.select('.event-info')

        server = smtplib.SMTP("smtp.sendgrid.net", 587)
        server.ehlo()
        server.starttls()
        server.login(sender_email, password)

        for email in receiver_emails:
            selector = random.randint(0, (len(eventInfo)-1))
            selectedEvent = eventInfo[selector]

            message = MIMEMultipart("alternative")
            message["Subject"] = "Marketing Test"
            message["From"] = data["from"]
            message["To"] = email

            text = "Looking for something to do?" + (' '.join(eventInfo[selector].text))

            html = template + ' '.join(str(e) for e in selectedEvent)

            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")

            message.attach(part1)
            message.attach(part2)

    
            server.sendmail(sender_email, email, message.as_string())
        server.quit()