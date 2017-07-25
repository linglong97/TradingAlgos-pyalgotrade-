from pyalgotrade import strategy
from pyalgotrade.barfeed import googlefeed
from pyalgotrade.technical import ma # allows us to compute moving averages
from pyalgotrade.technical import rsi # allows us to compute relative strength index

class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, smaPeriod):
        strategy.BacktestingStrategy.__init__(self, feed, 1000)
        self.__position = None
        self.__instrument = instrument
        self.__rsi = rsi.RSI(feed[instrument].getCloseDataSeries(), smaPeriod)
        self.__sma = ma.SMA(self.__rsi,15)
##        self.setUseAdjustedValues(True)
        #gets the sma from the data set, show rsi after
        
    def onEnterOk(self, position):
        execInfo= position.getEntryOrder().getExecutionInfo()
        self.info("BUY at $%.2f" %(execInfo.getPrice()))
        #set our current position and
        
    def onEnterCanceled(self, position):
        #if no enter, then just reset it
        self.__position = None

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        self.info("SELL at $%.2f" % (execInfo.getPrice()))
        self.__position = None

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.__position.exitMarket()

    def onBars(self, bars):
        # Wait for enough bars to be available to calculate a SMA.
        if self.__sma[-1] is None:
            return

        bar = bars[self.__instrument]
        # If a position was not opened, check if we should enter a long position.
        if self.__position is None:
            if bar.getPrice() > self.__sma[-1]:
                # Enter a buy market order for 10 shares. The order is good till canceled.
                self.__position = self.enterLong(self.__instrument, 10, True)
        # Check if we have to exit the position.
        elif bar.getPrice() < self.__sma[-1]:
            self.__position.exitMarket()      

    def onBars(self, bars):
        bar = bars[self.__instrument]
        self.info("%s %s %s" % (bar.getClose(), self.__rsi[-1], self.__sma[-1]))
        
def run_strategy(smaPeriod):
    # Load the yahoo feed from the CSV file
    feed = googlefeed.Feed()
    feed.addBarsFromCSV("aapl", "aapl-2011.csv")

    # Evaluate the strategy with the feed's bars.
    myStrategy = MyStrategy(feed, "aapl", smaPeriod)
    myStrategy.run()
    print "Final portfolio value: $%.2f" % myStrategy.getBroker().getEquity()

run_strategy(30)
