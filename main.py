import os
import requests
from datetime import datetime, timedelta
from twilio.rest import Client

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
stock_api_key = os.environ.get("STOCK_API_KEY")
news_api_key = os.environ.get("NEWS_API_KEY")

account_sid = os.environ.get("ACCOUNT_SID")
twilio_auth_token = os.environ.get("TWILIO_AUTH_TOKEN")

STOCK_PARAMETERS = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": stock_api_key,
}


response = requests.get(STOCK_ENDPOINT, params=STOCK_PARAMETERS)
response.raise_for_status()
data = response.json()["Time Series (Daily)"]
data_list = [value for (key, value) in data.items()]

#Get yesterday's closing stock price.
yesterday_data = data_list[0]
yesterday_closing_price = yesterday_data["4. close"]
print(yesterday_closing_price)

#Get the day before yesterday's closing stock price
day_before_yesterday_data = data_list[1]
day_before_yesterday_closing_price = day_before_yesterday_data["4. close"]
print(day_before_yesterday_closing_price)

#Find the positive difference between 1 and 2. e.g. 40 - 20 = -20, but the positive difference is 20.
difference = float(yesterday_closing_price) - float(day_before_yesterday_closing_price)
up_down = None
if difference > 0:
    up_down = "🔺"
else:
    up_down = "🔻"

#Work out the percentage difference in price between closing price yesterday and closing price the day before yesterday.
diff_percent = round((difference / float(day_before_yesterday_closing_price)) * 100)    

#remember to set it to 5
#Instead of printing ("Get News"), use the News API to get articles related to the COMPANY_NAME.
if abs(diff_percent) > 3:
    news_params = {
        "apiKey": news_api_key,
        "qInTitle": COMPANY_NAME,
        "language": "en",
    }

    news_response = requests.get(NEWS_ENDPOINT, params=news_params)
    news_response.raise_for_status()
    articles = news_response.json()["articles"]

    # Use Python slice operator to create a list that contains the first 3 articles. Hint: https://stackoverflow.com/questions/509211/understanding-slice-notation
    three_articles  = articles [:3]

    #Create a new list of the first 3 article's headline and description using list comprehension.
    formatted_articles = [f"{STOCK_NAME}: {up_down}{diff_percent}%\nHeadline: {article['title']}. \nBrief: {article['description']}" for article in three_articles]
    
    #Send each article as a separate message via Twilio. 
    client = Client(account_sid, twilio_auth_token)

    for article in formatted_articles:
        message = client.messages.create(
            body= article,
            from_="+12567******",
            to="+234913******",
        )
        print(message.status)

