import requests
import schedule
import time
import os
import smtplib
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()


url = "https://www.bbc.co.uk/sport"
username = "bbcnewssender@gmail.com"
password = os.getenv('GMAIL_APP_PASSWORD')

titles_and_urls = []

def sportScrape():
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        soup = BeautifulSoup(response.content, 'html.parser')
        promo_divs = soup.find_all("div", {"data-testid": "promo"})

        titles_and_urls.clear()  # clear old data

        for promo in promo_divs:
            a_tag = promo.find("a", class_="ssrcss-mnw9yn-PromoLink")
            p_tag = promo.find("p", class_="ssrcss-1b1mki6-PromoHeadline")
            if a_tag and p_tag and p_tag.span:
                href = a_tag.get("href")
                full_url = "https://www.bbc.co.uk" + href if href.startswith("/") else href
                headline = p_tag.span.text.strip()
                titles_and_urls.append((headline, full_url))
        
        print(f"Scraped {len(titles_and_urls)} articles")
        
    except requests.exceptions.RequestException as e:
        print(f"Error scraping website: {e}")
    except Exception as e:
        print(f"Unexpected error during scraping: {e}")

def sendEmail():
    try:
        if not titles_and_urls:
            print("No articles to send")
            return
            
        # Create email content
        email_body = "\n\n".join(f"{title}\n{url}" for title, url in titles_and_urls)
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = 'harrydbritton@gmail.com'
        msg['Subject'] = 'Daily Sports News'
        
        # Add body to email
        msg.attach(MIMEText(email_body, 'plain'))

        # Gmail SMTP configuration
        smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.ehlo()
        smtpObj.login(username, password)
        
        # Send email
        text = msg.as_string()
        smtpObj.sendmail(username, 'harrydbritton@gmail.com', text)
        print("Email sent successfully")
        smtpObj.quit()
        
    except smtplib.SMTPException as e:
        print(f"SMTP error occurred: {e}")
    except Exception as e:
        print(f"Error sending email: {e}")

def job():
    print(f"Running job at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    sportScrape()
    sendEmail()

# Schedule the job to run daily at 8:00 AM
schedule.every().day.at("08:00").do(job)

# For testing - run once immediately
job()

# Main loop
if __name__ == "__main__":
    print("Sports scraper started. Press Ctrl+C to stop.")
    print("Scheduled to run daily at 08:00")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute