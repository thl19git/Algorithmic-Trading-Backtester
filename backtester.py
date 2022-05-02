import yfinance as yf
import numpy as np
import pandas as pd
import math

class Backtester:
  
  def __init__(self, ticker, startDate):
    self._ticker = ticker
    self._capital = 0
    self._cash = 0
    self._fixedFee = 0
    self._percentFee = 0
    self._tax = False
    self._stocks = 0
    self._movingAverages = []
    self._movingAverageValues = {}
    self._date = startDate
    self._price = 0
    self._data = None

  def setCash(self, cash):
    self._capital += cash - self._cash
    self._cash = cash

  def addCash(self, cash):
    self._capital += cash
    self._cash += cash

  def getCash(self):
    return self._cash

  def setFees(self, fixedFee, percentFee, tax):
    self._fixedFee = fixedFee
    self._percentFee = percentFee / 100
    self._tax = tax

  def price(self):
    return self._price

  def stocks(self):
    return self._stocks

  def buy(self, amount=None):
    if amount == None:
      amount = math.floor((self._cash-self._fixedFee)/(self._price*(1+self._percentFee)))
    self._stocks += amount
    self._cash -= amount * self._price * (1+self._percentFee)
    if self._cash < 0:
      print("Run out of cash!")
      print("Date:", self._date)
      exit(1)

  def sell(self, amount=None):
    if amount == None:
      amount = self._stocks
    if (amount > self._stocks):
      print("Tried to sell",amount,"stocks, but only have",self._stocks)
      exit(1)
    self._stocks -= amount
    self._cash += amount * self._price * (1-self._percentFee) - self._fixedFee

  def setMovingAverages(self, movingAverages):
    self._movingAverages = movingAverages

  def movingAverage(self, days):
    if days not in self._movingAverageValues:
      print("No moving average calculated for",days,"days")
      exit(1)
    return self._movingAverageValues[days]

  def date(self):
    return self._date

  def test(self):
    # Retrieve the data 
    self._data = yf.Ticker(self._ticker).history(start=self._date)
    if len(self._data)== 0:
      exit(1)

    # Calculate moving averages
    for duration in self._movingAverages:
      self._data[str(duration)+"_mavg"] = self._data['Close'].rolling(duration).mean()

    # Cut off data before moving averages
    if len(self._movingAverages) > 0:
      if max(self._movingAverages) > len(self._data):
        print("Can't calculate moving average - use a shorter duration or earlier start date")
        exit(1)
      self._data = self._data[max(self._movingAverages):]

    # Apply the algorithm
    for index, row in self._data.iterrows():
      self._date = index.to_pydatetime().date()
      self._price = row['Close']
      for duration in self._movingAverages:
        self._movingAverageValues[duration] = row[str(duration)+"_mavg"]
      algorithm(self)

    # Calculate final results
    assets = self._cash+self._stocks*self._price
    days = len(self._data)
    cumulativeReturn = assets/self._capital
    # Annualized return assumes all capital was provided at the start
    annualizedReturn = (cumulativeReturn)**(252/days) -1

    # Output results
    print(self._ticker)
    print("Final cash:",self._cash)
    print("Final stocks:",self._stocks)
    print("Final assets:",assets)
    print("Annualized return:",annualizedReturn)
    print("")


#### Define global variables to be used by algorithm here ####



#### Implement the following function with your algorithm ####

# Useful methods:
#   - backtester.price() returns the current stock price
#   - backtester.stocks() returns the number of stocks currently owned
#   - backtester.getCash() returns the current amount of cash
#   - backtester.setCash(cash) sets the cash to the given amount
#   - backtester.addCash(cash) adds the given amount of cash
#   - backtester.buy(amount) buys the provided number of stocks
#     (if no number is provided, the maximum number possible is bought)
#   - backtester.sell(amount) sells the provided number of stocks
#     (if no number is provided, all stocks are sold)
#   - backtester.movingAverage(days) returns the moving average for the
#     given period (must be preset in movingAverages list)
#   - backtester.date() returns the current date

def algorithm(backtester):
  if(backtester.movingAverage(50) >= backtester.movingAverage(200)):
    backtester.buy()
  else:
    backtester.sell()

#### List of tickers you wish to apply the backtester to ####

tickers = ['AAPL','TSLA','VFF']

#### Define the parameters to be used by the backtester ####

startingCash = 10000
startDate = "2019-01-01" # YYYY-MM-DD
fixedTransactionFee = 5 # e.g. 10 = $10
percentTransactionFee = 0.5 # e.g. 0.5 = 0.5%
tax = False # Feature coming soon
movingAverages = [50,200] # List of moving averages (days), e.g [50,200]

# Note - if moving averages are required, the start date of the
# backtesting will be startDate + max(movingAverages)

#### Running the backtester ####

for ticker in tickers: 
  bt = Backtester(ticker, startDate)
  bt.setCash(startingCash)
  bt.setFees(fixedTransactionFee, percentTransactionFee, tax)
  bt.setMovingAverages(movingAverages)
  bt.test()