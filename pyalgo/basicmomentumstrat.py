from pyalgotrade import strategy
from pyalgotrade import plotter
from pyalgotrade.tools import googlefinance
from pyalgotrade.technical import vwap
from pyalgotrade.stratanalyzer import sharpe

import numpy as np

##
##this momentum trategy is very simple, and is run on big tech companies so doesn't mean anything
##Buying when benchmark moves up .5%, and selling when benchmark moves down .5%
##By changing the threshold, we can change and alter the returns that we got.
##
class basicMomentum(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, vwapWindowSize, threshold):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.__instrument = instrument
        self.__vwap = vwap.VWAP(feed[instrument], vwapWindowSize)
        #volume weighted average price
        self.__threshold = threshold
    
    def getVWAP(self):
        return self.__vwap

    def onBars(self, bars):
        vwap = self.__vwap[-1]
        if vwap is None:
            return
        # wait until there is a vwap
        
        shares = self.getBroker().getShares(self.__instrument)
        price = bars[self.__instrument].getClose()
        notional = shares * price
        #notational -> the amount of money we have right now
        if price > vwap * (1 + self.__threshold) and notional < 1000000:
            self.marketOrder(self.__instrument, 100)
            # buy 100 shares when the close price moves up, sell if it moves down
        elif price < vwap * (1 - self.__threshold) and notional > 0:
            self.marketOrder(self.__instrument, -100)
            #sell
    


def main(plot):
    instruments = ["aapl","orcl", "msft", "fb","googl"]
    name = { "aapl": "apple", "orcle": "oracle", "msft": "microsoft", "fb": "facebook", "googl": "google"}
    vwapWindowSize = 5
    threshold = 0.01
    profits = {}
    # Download the bars.
    for instrument in instruments:
        feed = googlefinance.build_feed([instrument], 2016, 2017,".")
        strat = basicMomentum(feed, instrument, vwapWindowSize, threshold)
        sharpeRatioAnalyzer = sharpe.SharpeRatio()
        strat.attachAnalyzer(sharpeRatioAnalyzer)
        
        # tells us the sharpe ratio of the stock during the time

        if plot:
            plt = plotter.StrategyPlotter(strat, True, False, True)
            plt.getInstrumentSubplot(instrument).addDataSeries("vwap", strat.getVWAP())
        strat.run()
        profits[instrument] = (strat.getBroker().getEquity())
        print "Sharpe ratio: %.2f" % sharpeRatioAnalyzer.getSharpeRatio(0.05)

        if plot:
            plt.plot()
            
    profit_array = []
    name_array = []
    for item in profits:
        profits[item] -= 1000000
        profit_array.append(profits[item])
        name_array.append(item)
    print(profits)
    import matplotlib.pyplot as plt
    n = len(instruments)
    profit_std= (9851, 15829, 4111, 20111, 40213)
    index = np.arange(n)
    width= 0.35
    plt.figure()
    plt.bar(index, profit_array, align = 'center', color='b', yerr=profit_std)
    plt.ylabel('Profit')
    plt.title('Profit over 1 year using basic Momentum Trading')
    plt.xlabel('Company')
    plt.xticks(index, name_array)   
    plt.show()
    

if __name__ == "__main__":
    main(False)
