import csv
from itertools import chain
import pandas as pd
from dateutil.parser import parse
import random
import matplotlib.pyplot as plt

cashBalance = []
futuresStatement = []
forexStatements = []
accountOrderHistory = []
totalCash = []
accountTradeHistory = []
profitsandLosses = []
forexAccountSummary = []
accountSummary = []

with open('exampleStatement.csv') as statement:
    
    statement = csv.reader(statement, delimiter = '\n')
    count, breakCount, secondBreakCount, thirdBreakCount  = 0, 0, 0, 0
    
    for line in statement:
        count+= 1
        
        if count < 5:
            continue
        if (len(line) == 0):
            breakCount += 1
        if breakCount < 1:
            cashBalance.append(line)
        if (breakCount == 1 and (len(line) != 0) and breakCount < 2):
            futuresStatement.append(line)
        if (breakCount == 2 and (len(line) != 0) and breakCount < 3):
            forexStatements.append(line)
        if breakCount == 3 and (len(line) != 0) and breakCount < 4:
            totalCash.append(line)
        if (breakCount == 5 and (len(line) != 0) and breakCount < 6):
            accountOrderHistory.append(line)
        if (breakCount == 6 and (len(line) != 0) and breakCount < 7):
            accountTradeHistory.append(line) 
        if (str(line) == "['Profits and Losses']"):
            secondBreakCount += breakCount
        if ((breakCount != 0) and (breakCount == secondBreakCount) and (len(line) != 0) and (breakCount < secondBreakCount+1)):
            profitsandLosses.append(line) 
        if ((breakCount != 0) and (breakCount == secondBreakCount + 1) and (len(line) != 0)):
            forexAccountSummary.append(line)
        if (str(line) == "['Account Summary']"):
            thirdBreakCount += breakCount
        if (thirdBreakCount == breakCount) and (thirdBreakCount > secondBreakCount):
            accountSummary.append(line)
            
            
'Converts the initial list of lists to a pandas dataframe.'
def orderSplitter(subsection: list) -> pd.DataFrame:
    subsection.pop(0)
    for i, j in enumerate(subsection):
        j[0] = j[0].split(',')
    
    subsectionDataFrame = pd.DataFrame(list(chain.from_iterable(subsection[1:])), columns = list(chain.from_iterable(subsection[0]))).iloc[: , 1:].iloc[::-1].reset_index().drop(["index"], axis=1)
    
    return subsectionDataFrame

orders = orderSplitter(accountTradeHistory)


'''Sorts through dataframe to pull out desired product (options, futures, ETFs, etc.)'''
indexList = []
for i,j in enumerate(orders['Spread']):
    if j == 'SINGLE': # Would change to FUTURE or whatever other product it is you're looking to track. Just be mindful that this script is designed to track single legged option trades
        indexList.append(i)

futuresTrades = orders.loc[orders.index[indexList]]
symbolsTraded = list(set(futuresTrades['Symbol']))


'''Bunches trades by symbols being traded, so handles cases where you might be trading
    numerous tickers, whether trading those concurrently or sequentially.'''
ordersBySymbol = {}
for z in symbolsTraded:
    indexList = []
    for i,j in enumerate(futuresTrades['Symbol']):
        if j == z:
            indexList.append(i)
    ordersBySymbol[z] = futuresTrades.loc[futuresTrades.index[indexList]]


'''Used for looping through trades and determining if a trade is to be closed, and then if it is, 
    computing some general information for the trade; profit, loss, holding period, etc.'''
def closeTrade(tradeOpen: list,
               closingOrder: list) -> list:
    
    totalQuantity = 0
    weight = 0
    direction = ''
    contractType = tradeOpen[0][8]
    symbol = tradeOpen[0][5]
    expirationDate = tradeOpen[0][6]
    timePositionWasOpened = tradeOpen[0][0]
    timePositionWasClosed = closingOrder[0]
    costBasis = 0 
    exitPrice = closingOrder[9]
    profitLoss = 0
    holdingPeriod = round(((parse(timePositionWasClosed) - parse(timePositionWasOpened)).total_seconds() / 60.0), 3)
    tradingExpenses = 0
    
    for i in tradeOpen:
        if i[3][0] == '-':
            i[3]= i[3].replace('-','')
            direction = 'Short'
            weight += int(i[3]) * float(i[9])
            totalQuantity += int(i[3])
    try:
        costBasis = (weight / totalQuantity)
    except:
        pass
    
    for i in tradeOpen:

        if i[3][0] == '+':
            i[3]= i[3].replace('+','')
            direction = 'Long'
            weight += int(i[3]) * float(i[9])
            totalQuantity += int(i[3])
    try:
        costBasis = (weight / totalQuantity)
    except:
        pass
    
    if direction == 'Short':
        if ((float(exitPrice) - float(costBasis)) / float(costBasis)) < 0:
            profitLoss = abs((float(exitPrice) - float(costBasis)) / float(costBasis))
        else:
            profitLoss = -(float(exitPrice) - float(costBasis)) / float(costBasis)
    
    if direction == 'Long':
        profitLoss = (float(exitPrice) - float(costBasis)) / float(costBasis)
    
    #for some reason interprets flat trades as negative values, so to keep win-loss ratio "even" for flat trades, I do this.
    if profitLoss == -0.0:
        profitLoss = random.choice((-0.0, 0.0))
    
    positionStats = [symbol, contractType, expirationDate, direction, timePositionWasOpened, timePositionWasClosed, float(holdingPeriod), float(totalQuantity), float(costBasis), float(exitPrice), float(profitLoss), float(tradingExpenses)]

    return positionStats


'''Loops through orders for symbols traded and creates a list of lists storing individual trades.'''
trades = []
for key, positionStats in ordersBySymbol.items():
    if isinstance(key, str) : # replace this with something like: if (key == '/MYM'): to filter by individual tickers, if you want.
        for i in range(len(positionStats)):
            for z in range(len(positionStats)):
                if (positionStats['Pos Effect'].iloc[z]) != 'TO OPEN':
                    positionStats.drop(positionStats.index[z], inplace = True)
                    break
                else:
                    break
                
        openTrades = []
        for z in range(len(positionStats)):
            if (positionStats['Pos Effect'].iloc[z]) == 'TO OPEN':
                openTrades.append(list(positionStats.iloc[z]))
            else:
                try:
                    for i in openTrades:
                        if (i[7] == positionStats['Strike'].iloc[z]) and (positionStats['Pos Effect'].iloc[z] == 'TO CLOSE'):
                            trades.append(closeTrade(openTrades, positionStats.iloc[z]))
                            break
                    openTrades = []
                except:
                    #no trade currently opened to be closed
                    pass


#sorts by the time a trade was initially opened
sortedTrades = sorted(trades[1:], key = lambda x: parse(x[4]))

profitLoss, holdingPeriods = [], []
for i in sortedTrades:
    profitLoss.append(i[10])
    holdingPeriods.append(i[6])

#adding leading placeholder 0's to make charting easier to interpret visually later on
profitLoss.insert(0,0)
holdingPeriods.insert(0,0)
     
profitLossAndHoldingPeriods = pd.DataFrame({'profitLoss': profitLoss, 'holdingPeriods': holdingPeriods})


'''To be used for counting how many puts vs. calls were bought.'''
puts = []
calls = []
for i in sortedTrades:
    if (i[1]) == "PUT":
        puts.append(i[1])
    else:
        calls.append(i[1])


'''Prints out some general information computed from the return series.'''
print("\nCumulative Performance: " + format(((profitLossAndHoldingPeriods.profitLoss.sum()) * 100), ".4f") + "%")
print("\nTotal Number of Trades: " + str(len(profitLossAndHoldingPeriods) - 1))
print("\nMedian Holding Period: " + format((profitLossAndHoldingPeriods.holdingPeriods.median()), ".3f") + " [minutes]")
print("\nWin Loss Ratio: " + format(((1 - ((profitLossAndHoldingPeriods.profitLoss[profitLossAndHoldingPeriods.profitLoss < 0 ].count()) / (len(profitLossAndHoldingPeriods) - 1))) * 100), ".4f") + "%, " + str((profitLossAndHoldingPeriods.profitLoss[profitLossAndHoldingPeriods.profitLoss > 0 ].count())) + ":" + str((profitLossAndHoldingPeriods.profitLoss[profitLossAndHoldingPeriods.profitLoss < 0 ].count())))
print("\nPuts to Calls: " + format(((len(puts) / (len(profitLossAndHoldingPeriods) - 1)) * 100), ".4f") + str("%, ") + str(len(puts)) + ":" + str(len(calls)))
print("\nAverage Gain: " + format(((profitLossAndHoldingPeriods.profitLoss[profitLossAndHoldingPeriods.profitLoss > 0 ].mean()) * 100), ".4f") + "%")
print("\nAverage Loss: " + format(((profitLossAndHoldingPeriods.profitLoss[profitLossAndHoldingPeriods.profitLoss < 0 ].mean()) * 100), ".4f") + "%")
print("\nBernardo and Ledoit Ratio: " + format(((profitLossAndHoldingPeriods.profitLoss[profitLossAndHoldingPeriods.profitLoss > 0 ].sum()) / (abs(profitLossAndHoldingPeriods.profitLoss[profitLossAndHoldingPeriods.profitLoss < 0 ].sum()))), ".4f"))


'''Method to be used for plotting equity curve.'''
def paperTradePlot(data: pd.DataFrame) -> None:
    
    ax1 = data.profitLoss.cumsum().plot(color = 'black', figsize = [14.275, 9.525])
    ax1.axhline(0, linewidth = 1, color = 'firebrick')
    ax1.set_title('Cumulative Positionwise Equity Curve', fontsize = 18)
    ax1.set_xlabel('Number of Trades', size = 16)
    values = ax1.get_yticks()
    ax1.set_yticklabels(['{:,.0%}'.format(x) for x in values])
    ax1.set_xlim(0, (len(data)-1))
    ax1.grid(which = 'both', linestyle = '-', linewidth = '0.9', color = 'dimgrey')
    ax1.grid(which = 'minor', linestyle = ':', linewidth = '0.9', color = 'grey')
    plt.tick_params(labelsize = 16, labelright = True)
    plt.minorticks_on()
    plt.pause(0.01)

paperTradePlot(profitLossAndHoldingPeriods)
