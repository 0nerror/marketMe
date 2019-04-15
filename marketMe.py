#Code designed for use on Windows 10 os, may not function correctly on other operating systems
import smtplib, requests, bs4, random, yaml, calendar, time, os, csv
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def goToMarket(campaign):
    #Set up configuration data
    #Change directories to where the campain data is located
    os.chdir("./Campaigns/" + campaign) 
    config = open("config.cfg.yml", 'r')
    data = yaml.safe_load(config.read())
    with open("template.html", "r") as htmlFile:
        template=htmlFile.read()
    with open("customers.csv", "r") as csvFile:
        recievers = list(csvFile)
    #Change back to the main folder
    os.chdir("../../") 

    #Configure data
    start_date = datetime.strptime(data["start_date"], "%m/%d/%Y")
    end_date = datetime.strptime(data["end_date"], "%m/%d/%Y")
    today = datetime.now()
    calendar_day = calendar.day_name[today.weekday()]
    website = str(data["website"])
    scrape_on = str(data["scrape_on"])

    #Check configuration data and see if campaign is active today
    if(today >= start_date and today <= end_date):
        if(calendar_day in data["send_on"]):
            sender_email = data["sender_email"]
            receiver_emails = recievers
            password = data["password"]
            searchCode = str(data["feature"])
            res = requests.get(website + searchCode)
            showsSoup = bs4.BeautifulSoup(res.text, features="html.parser")
            eventInfo = showsSoup.select("." + scrape_on)
            #Setup SMTP server for SendGrid
            server = smtplib.SMTP("smtp.sendgrid.net", 587)
            server.ehlo()
            server.starttls()
            server.login(sender_email, password)
            #Begin sending emails
            for email in receiver_emails:
                selector = random.randint(0, (len(eventInfo)-1))
                selectedEvent = eventInfo[selector]

                message = MIMEMultipart("alternative")
                message["Subject"] = "Marketing Test"
                message["From"] = data["from"]
                message["To"] = email
                #Text only message for email with html restrictions
                text = "Looking for something to do?" + (' '.join(eventInfo[selector].text))
                #HTML version of email
                html = template + ' '.join(str(e) for e in selectedEvent)

                part1 = MIMEText(text, "plain")
                part2 = MIMEText(html, "html")

                message.attach(part1)
                message.attach(part2)

    
                server.sendmail(sender_email, email, message.as_string())
            #Shutdown SendGrid Server
            server.quit()

#If marketMe is called directly (not imported) begin launching all Campaigns
if __name__ == "__main__":        
    while True:
        for root, dirs, files in os.walk("./Campaigns"):
            for dir in dirs:
                goToMarket(dir)
        #When work is complete close thread and shutdown all services for 24 hours
        time.sleep(86400)