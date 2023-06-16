import requests
import os
from twilio.rest import Client
from dotenv import load_dotenv


load_dotenv()
STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

alpha_avantage_api = os.getenv("APLHA_AVANTAGE_API")
news_api = os.getenv("news_api")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
MY_TWILIO_PHONE_NUMBER = os.getenv("MY_TWILIO_PHONE_NUMBER")
MY_PHONE_NUMBER = os.getenv("MY_PHONE_NUMBER")

# Params for the Stock API
parameters = {
    "function": "TIME_SERIES_DAILY_ADJUSTED",
    "symbol": STOCK_NAME,
    "apikey": alpha_avantage_api,
}


client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

response = requests.get(STOCK_ENDPOINT, params=parameters)
response.raise_for_status()

data = response.json()
#Grabbing the days
latest_day = list(data["Time Series (Daily)"].keys())[0]
latest_day_data = data["Time Series (Daily)"][latest_day]

# Closing Price of yesterday
yesterdays_closing_price = float(latest_day_data["4. close"])

# Closing price of the day before
day_before_yesterday = list(data["Time Series (Daily)"].keys())[1]
latest_day_before_yesterday = data["Time Series (Daily)"][day_before_yesterday]
day_before_yesterday_closing_price = float(latest_day_before_yesterday["4. close"])

# Finding the Positive difference between the 2 days
positive_difference_of_days = abs(yesterdays_closing_price-day_before_yesterday_closing_price)
positive_difference_of_days = round(positive_difference_of_days, 2)
print(f"The Positive difference is: {positive_difference_of_days}")

# Finding if its a decrease or increase
negative_check = yesterdays_closing_price - day_before_yesterday_closing_price
if negative_check <= 0:
    up_down = "⬇"
else:
    up_down = "⬆"

# Finding the Percentage_difference between the 2 days
percentage_difference = abs((day_before_yesterday_closing_price - yesterdays_closing_price))/(abs((day_before_yesterday_closing_price + yesterdays_closing_price))/2)*100
print(f"The Percentage Difference is: {round(percentage_difference, 2)}%")



news_parameters = {
    "q": COMPANY_NAME,
    "apiKey": news_api,
    "from": latest_day_before_yesterday,
    "to": latest_day_data,
    "language": "en",
    "sortBy": "popularity",
    "pageSize": "3"
}
def get_news():
    news_response = requests.get(NEWS_ENDPOINT, params=news_parameters)
    news_response.raise_for_status()

    news_content = news_response.json()
    # Testing the contents here
    # print(news_content["articles"][0]["title"])
    # print(news_content["articles"][0]["description"])

    # Goes through the top 3 Articles and sends them in a text
    for article in range(0, 3):
        news_title = news_content["articles"][article]["title"]
        news_description = news_content["articles"][article]["description"]
        print(f"{STOCK_NAME}: {up_down}{round(percentage_difference, 2)}% \nHeadline: {news_title} \nBrief: {news_description}")
        # message = client.messages \
        #     .create(
        #     body=f"{STOCK_NAME}: {up_down}{round(percentage_difference, 2)}% \nHeadline: {news_title} \nBrief: {news_description}",
        #     from_=MY_TWILIO_PHONE_NUMBER,
        #     to=MY_PHONE_NUMBER
        # )
        # print(message.sid)
        # print(message.status)

# If there is an in crease of more than 5% it will run the next part of the code
if percentage_difference >= 5:
    get_news()
