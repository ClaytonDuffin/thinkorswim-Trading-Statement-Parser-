# thinkorswim-Trading-Statement-Parser-
Python script to be used for brief analysis and charting of a trading statement generated through the thinkorswim® desktop application.

This script was designed to be used for observing the performance of a sequence of single-leg options on futures trades. These trades are to have been executed through thinkorswim® paperMoney®. It is likely that this script would work with a real money statement, though it is not developed to the point where I would encourage doing so. In order to use the script for paper tradinng different products, say outright futures, or equity ETFs, some minor adjustments would need to be made. In order to get the script to the point where you would want to to use it for live trading (using real money), larger adjustments would need to be made, for example, basing P/L off specific contract specs, and having the script interpret multiple different products being traded at once. The initial parsing of the statement and the outline for how I've gone about things thus far is here, so in setting it up for your own specific use case, have fun!

I used this to track paper-trading performance when I first became interested in trading options on futures. One major limitation to this use case that I've since realized, is that in live trading (using real money), the slippage factor is astronomically high when compared with the thinkorswim® paperMoney® platform, at least for options on futures, and index options (SPX). Slippage is more realistic for outright futures contract positions but still do be cautious of this when using this script. 

Also do be warned, that even for the intended use case, options on futures, this script is not currently configured for trades where you might scale both in-to and out-of, your position(s) (example: buy 1, buy 1, buy 1, sell 1, sell 2). You can add size, but you must close out all your size at once for the script to function properly (example: buy 1, buy 2, sell 3). The script does compute fine for trades where direction was immediately changed (example: buy 1, sell 2: long -> short). 

Attached in this repository is exampleStatement.csv, an example statement which was generated through the thinkorswim® desktop application after a day of paper trading in April of 2022. 75 paper trades in total were executed on that day, and the chart attached in the repository, outputChart1.png, shows what the script outputs when ran. In addition to the chart, the script also prints some general trading metrics (cumulative performance, number of trades, median holding period, win-loss ratio, puts/calls, average gain, average loss, bernardo and ledoit ratio).
