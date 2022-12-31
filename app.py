from flask import render_template
from flask import Flask,request
import requests
import smtplib
from selenium import webdriver
from selenium.webdriver.common.by import By
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

app = Flask(__name__, template_folder='templates')
scheduler = BackgroundScheduler()


@app.route('/')
def home():
    return render_template('home.html')



@app.route('/submit', methods=['POST'])
def submit():
    ticker = request.form['ticker']
    threshold = request.form['threshold']
    notification_type = request.form['notification_type']
    frequency=request.form['frequency']
    email_address=request.form['email']
    if frequency=='hourly':
        time_notf=1
    elif frequency=='daily':
        time_notf=24*7
    else:
        time_notf=0
    

    scheduler.add_job(
    func=check_price,
    trigger=IntervalTrigger(minutes=time_notf),
    args=[ticker, threshold, notification_type,email_address],
    id='price_check_job'
    )
    scheduler.start()
    return 'Form submitted successfully!'

def check_price(ticker, threshold, notification_type,email_address):    
    if compare_price(ticker, threshold):
        notification(ticker, threshold, notification_type,email_address)

def compare_price(ticker, threshold):
    price = get_stock_price(ticker)
    if price is not None and price >= threshold:
        return True
    return False

def get_stock_price(ticker):
    try:
        driver = webdriver.Firefox() 
        
        driver.get(f'https://finance.yahoo.com/quote/{ticker}/history?p={ticker}')
        # if check_exists_by_xpath(driver,'/html/body/div[1]/div/div/div[1]/div/div[4]/div/div/div[1]/div/div/div/div/div/section/button[1]/svg/path'):
        #     cross=driver.find_element('/html/body/div[1]/div/div/div[1]/div/div[4]/div/div/div[1]/div/div/div/div/div/section/button[1]/svg/path')
        #     cross.click()
        stock_price = driver.find_element(by = By.XPATH, value = '/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[6]/div/div/div/div[3]/div[1]/div[1]/fin-streamer[1]')
        price = stock_price.text
        print(price)
        driver.close()
        return price
    except (KeyError, requests.RequestException):
        return None


def notification(ticker, threshold, notification_type,email_address):
    
    if notification_type == 'email':
        send_email_notification(ticker, threshold,email_address)

def send_email_notification(ticker, threshold,email_address):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('aaryanshrestha313@gmail.com', 'a.rnsesta@gmail.com')
    subject = f'Stock price alert: {ticker}'
    body = f'The price of {ticker} has reached or exceeded the threshold of {threshold}.'
    message = f'Subject: {subject}\n\n{body}'
    server.sendmail('aaryanshrestha313@gmail.com', f'{email_address}', message)
    server.quit()
