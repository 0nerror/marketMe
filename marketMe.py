#Code designed for use on Windows 10 os, may not function correctly on other operating systems
import smtplib, requests, bs4, random, yaml, calendar, time, os, shutil, threading, csv
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def goToMarket(campaign, now):
    #Get configuration data from files
    
    os.chdir("./Campaigns/" + campaign) 
    config = open("config.cfg.yml", 'r')
    data = yaml.safe_load(config.read())
    config.close()
    with open("template.html", "r") as htmlFile:
        template=htmlFile.read()
    with open("customers.csv", "r") as csvFile:
        email_reader = csv.reader(csvFile)
        receivers_emails = list(email_reader)
    os.chdir("../../") 

    #Configure data for use
    start_date = datetime.strptime(data["start_date"], "%m/%d/%Y")
    end_date = datetime.strptime(data["end_date"], "%m/%d/%Y")
    today = now
    calendar_day = calendar.day_name[today.weekday()]
    website = str(data["website"])
    scrape_on = str(data["scrape_on"])
    sender_email = data["sender_email"]
    password = data["password"]

    #Check configuration data and see if campaign is active today
    if(today >= start_date and today <= end_date):
        if(calendar_day in data["send_on"] and today.hour == data["at_hour"] and today.minute == data["at_minute"]):
            
            #Get advertisment from the web
            res = requests.get(website)
            webSoup = bs4.BeautifulSoup(res.text, features="html.parser")
            eventInfo = webSoup.select("." + scrape_on)
            if not len(eventInfo) == 0:

                #Setup SMTP server for SendGrid
                server = smtplib.SMTP("smtp.sendgrid.net", 587)
                server.ehlo()
                server.starttls()
                server.login(sender_email, password)

                #Setup email message
                selector = random.randint(0, (len(eventInfo)-1))
                selectedEvent = eventInfo[selector]
                message = MIMEMultipart("alternative")
                message["Subject"] = "Marketing Test"
                message["From"] = data["from"]

                #Text version of email
                soup = bs4.BeautifulSoup(template, features="html.parser")
                text = soup.get_text() + (' '.join(eventInfo[selector].text))

                #HTML version of email
                html = template + ' '.join(str(e) for e in selectedEvent)

                #Put both parts into email
                part1 = MIMEText(text, "plain")
                part2 = MIMEText(html, "html")
                message.attach(part1)
                message.attach(part2)

                #Begin sending emails
                for email in receivers_emails[0]:
                    message["To"] = data["to"]
                    server.sendmail(sender_email, email, message.as_string())
                    #Create log files
                    log(email, campaign)

                #Shutdown SendGrid Server
                server.quit()

def log(email, campaign):
    now = datetime.now()
    os.chdir("./Logs")
    with open(campaign + ".log", "a+") as log:
        log.write("\nsent email to %s for %s campaign at %s" % (email, campaign, str(now)))
    os.chdir("../")


def cleanUp():
    for root, dirs, files in os.walk("./Campaigns"):
            for dir in dirs:
                os.chdir("./Campaigns/" + dir) 
                config = open("config.cfg.yml", 'r')
                data = yaml.safe_load(config.read())
                config.close()
                end_date = datetime.strptime(data["end_date"], "%m/%d/%Y")
                today = datetime.now()
                #Change back to the main folder
                os.chdir("../../")
                if(end_date < today):
                    shutil.rmtree("./Campaigns/" + dir)

def startCampaign(now):
    for root, dirs, files in os.walk("./Campaigns"):
            for dir in dirs:
                goToMarket(dir,now)

def setup():
    directories = ["Campaigns","Logs"]
    for directory in directories:
        try:
            os.mkdir(directory)
            print("Directory %s created!" % (directory))
        except:
            print("Directory %s already exists!" % (directory))

def main():
    setup()
    while True:
        now = datetime.now()
        midnight = now.hour == 0 and now.minute == 0 and now.second == 0
        onTheMinute = now.second == 0
        if(midnight):
            #Remove any expired campaigns
            cleanUp()
        if(onTheMinute):
            thread = threading.Thread(target = startCampaign(now))
            thread.start()
            thread.join()
        time.sleep(1)

#If marketMe is called directly (not imported) start Campaign processing
if __name__ == "__main__":
    main()