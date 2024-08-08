import datetime
import os
import datetime as dt
import requests
from twilio.rest import Client

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
STOCK_API_KEY = os.environ.get("STOCK_API_KEY")

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

account_sid = os.environ.get("ACCOUNT_SID")
auth_token = os.environ.get("AUTH_TOKEN")


# ----- Time Date ----
time = dt.datetime.today()
today = time.isoformat().split("T")[0]
yesterday = (time - datetime.timedelta(days=1)).isoformat().split("T")[0]
before_yesterday = (time - datetime.timedelta(days=2)).isoformat().split("T")[0]


news_params = {
    "q": COMPANY_NAME,
    "from": yesterday,
    "sortBy": "popularity",
    "apiKey": NEWS_API_KEY
}

stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": "TSLA",
    "interval": "5min",
    'extended_hours': False,
    "apikey": STOCK_API_KEY
}
news_response = requests.get(NEWS_ENDPOINT, params=news_params)
news_response.raise_for_status()
news_data = news_response.json()

x = slice(3)
articles = news_data['articles'][:3]
article_titles = [article["title"] for article in articles]
article_brief = [article["description"] for article in articles]


stock_response = requests.get(STOCK_ENDPOINT, params=stock_params)
stock_response.raise_for_status()
stock_data = stock_response.json()

stock_close_yesterday = float(stock_data['Time Series (Daily)'][yesterday]['4. close'])
stock_close_before_yesterday = float(stock_data['Time Series (Daily)'][before_yesterday]['4. close'])

stock_change = stock_close_yesterday - stock_close_before_yesterday
stock_increase = round(stock_change / stock_close_yesterday) * 100

up_down = None
if stock_change > 0:
    up_down = "🔺"
else:
    up_down = "🔻"

formatted_message = [f"Headline: {article['title']}.\nBrief: {article['description']}" for article in articles]

if abs(stock_increase) >= 0:
    client = Client(account_sid, auth_token)
    for article in formatted_message:
        message = client.messages.create(
            body=f"{STOCK}: {up_down} {stock_increase}% \n{article}",
            from_="+18448956019",
            to=os.environ.get("PHONE_NUMBER")
        )
        print(f"{message.status}")
else:
    print("Stock did not move by 5%")
