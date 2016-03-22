
from pytz import timezone


#################################################
# # Strategy Outline
# ####TODO   dan gei ni zuo la XD

##################################################
# # Initialize constants and the bootstrap function
# #  if you want to change and improve the strategy,
# # only change the constants
# # please document the periods of your backtests (start time and end time)
# # the constants used, and some general comments (end gain/loss, fluctuation compared to SPY, risk, and etc)
# # # # GENERAL
CHOSEN_SECURITIES = [sid(37945), sid(37515), sid(17455), sid(37514),sid(37083), sid(41575), sid(37049), sid(37048), sid(8554)]
BALANCE_FREQUENCY = 1    # in days    (subject to change)
STOP_LOSS_FREQUENCY = 300    # in mins  (lets just keep it at 30 mins)



Top_Stock_Chosen= 4 # dan's constant for number of stock, required at the trade function
                 # try to pick even number of stocks

# apparently mavg() must be inputed a size as a direct constant 
#SMA_SHORT_PERIOD = 30
#SMA_LONG_PERIOD = 120
# # # # COND1
COND1_USED = True
SMA_RATIO_LOWER_BOUND = 1.0
# # # # COND2
COND2_USED = True
# the long term sma is said to be ticking up if
# it has been rising(not strictly) for (SMA_LONG_TICK_UP_PERIOD) days
SMA_LONG_TICK_UP_PERIOD = 1   
# if SMA last day > SMA today, it is rising for 1 extra day
# elif SMA last day > SMA today * SMA_LONG_TICK_UP_CONSTANT, it is keeping even
# else it is falling
SMA_LONG_TICK_UP_CONSTANT = .999

###TO DO
###Jake's constants for stop loss and etc
STOP_LOSS_USED = True
#Jake constant for underperforming percentage, the number there is = olderprice/newprice currently 5%
underperforming_PCT = .99




def initialize(context):
    log.info("hi")
    context.dayCount = -4;
    context.stocks = CHOSEN_SECURITIES  
    for stock in context.stocks:
        context.smaShort = dict.fromkeys(context.stocks, 0.0)  #contain floats
        context.smaLong = dict.fromkeys(context.stocks, 0.0)   #contain floats
        context.ratio = dict.fromkeys(context.stocks, 0.0)	  #contain floats
        context.cond = dict.fromkeys(context.stocks, True)      #contain boolean
        context.stopList = dict.fromkeys(context.stocks, 0.0)
        context.sorder = dict.fromkeys(context.stocks, 0.0) #Dan Contain floats
        #tipup contains a int that ranges [-(SMA_LONG_TICK_UP_PERIOD) , 0]
        # if tipup is 0, it is the long term sma is ticking up
        context.tipup = dict.fromkeys(context.stocks, 0)     #contain int
    #no transaction cost for now
    set_commission(commission.PerTrade(cost=6.0))
    set_slippage(slippage.FixedSlippage(spread=0.00))


###########################################
# #jake functions of trade executions
# jake part stop loss
# will be called every 30 mins from handle_data
# current strategy: (to be filled)
# will sell securities that are underperforming(-5%)
# and call rerank and trade to rebalance the portfolio
def stop_loss(context, data):
    for stock in context.stocks:
    	if stock in data:
            price = data[stock].price
            if context.stopList[stock] == 0.0:
                context.stopList[stock] = price
            difference = price/context.stopList[stock]
            if difference <= underperforming_PCT:            
                #log.info(stock)
                #log.info("prev " + str(context.stopList[stock]))
                #log.info ("stoploss")
                #log.info("now " + str(price))
                currentValue = context.portfolio.positions[stock].amount
                context.stopList[stock] = price
                order(stock, -currentValue)
            context.stopList[stock] = price
    pass


# Dan's part trade
# will be called every month from handle_data
# rebalance the portfolio based on rank
# both the sorted array and the number of valid securities are inside context
def trade(context,data):
    x = 0
    #log.info("hi trade")
    y = 0
    for stock in context.stocks:
        if stock == sid(8554):
            y = y + 1
            log.info("rank " + str(y))
    for stock in context.stocks: # sell stocks here
        x = x + 1
        #log.info("selling stock")
        if context.cond[stock] == False or x > Top_Stock_Chosen:
            currentValue = context.portfolio.positions[stock].amount
            #log.info("sold stock" + str(stock))
            #log.info(currentValue)
            order(stock, -currentValue)
    #        context.portfolio.cash = context.portfolio.cash + currentValue
    x = 0
    currentValue = 0
    orderAmount = 0
    numberChosen = 0;
    for stock in context.stocks:
        x = x + 1
        upperBound = Top_Stock_Chosen + 1
        if x < upperBound:
            if context.cond[stock] == True:
                numberChosen = numberChosen + 1
                #log.info(numberChosen)
    
    

    x = 0
    for stock in context.stocks: # buy stocks here
        x = x + 1
        #log.info("b s")
        upperBound = Top_Stock_Chosen + 1
        if x < upperBound or x < y + 1:
            currentValue = context.portfolio.positions[stock].amount
            if stock in data:
                orderAmount = (context.portfolio.portfolio_value/numberChosen) / data[stock].price
            else:
                orderAmount = 0
            #log.info(context.portfolio.cash)
            #log.info(context.cond[stock])
            if context.cond[stock] == True:
                order(stock, orderAmount-currentValue)
                #log.info(orderAmount)
                #log.info(currentValue)
                #log.info("b s" + str(stock) + str(context.portfolio.positions[stock].amount))
                #context.portfolio.cash = context.portfolio.cash - cashUsed
                
    pass

###########################################
# # Helper functions
# return an updated context with a sorted array and the number of stocks
# called by stop_loss and handle_data
def rerank(context, data):
    context = cond_calc(context)
    newlist = []
    for stock in context.stocks:
        newlist.append((context.cond[stock], context.ratio[stock], stock))
    context.stocks = [x for (z, y, x) in sorted(newlist, reverse = True)]
    return context

# calculate if the long term sma is trending up and store the results in
# called DAILY by handle_data
# DAN DONT CALL
def long_trend_calc(context, data):
    for stock in context.stocks:
    	#current_sma = data[stock].mavg(SMA_LONG_PERIOD)
    	if stock in data:
            current_sma = data[stock].mavg(2)
        else:
            current_sma = 0
        if current_sma > context.smaLong[stock]:
            context.tipup[stock] += 1
        elif current_sma > (context.smaLong[stock] * SMA_LONG_TICK_UP_CONSTANT):
            continue;
        else:
            context.tipup[stock] = 0
    return context

# calculate if the conditions for each stocks and store them in context.cond
# called by rerank ONLY
# DAN DONT CALL
def cond_calc(context):
    for stock in context.stocks:
        cond1 = (context.ratio[stock] > 1.0)
        cond2 = (context.tipup[stock] >= SMA_LONG_TICK_UP_PERIOD)
        if COND1_USED:
            context.cond[stock] = cond1
        else:
            context.cond[stock] = True
        if COND2_USED:
            #stored under conditon 2
            context.cond[stock] = (context.cond[stock] and cond2)
        #else:
            #uses the result from the if else of cond1
    return context

# ranking comparator
# return  ints, -1 => stock1 is before stock2
# 0 => stock1 is the same rank as stock2
# 1 => stock1 is after stock2
# used ONLY by rerank
"""def cmp_routine(stock1, stock2):
   #conditions check for stock1 and stock2
    if (context.cond[stock1] and (not context.cond[stock2])):
        return -1
    elif (context.cond[stock2] and (not context.cond[stock1])):
        return 1
    if (context.ratio[stock1] > context.ratio[stock2]):
        return -1
    elif (context.ratio[stock1] == context.ratio[stock2]):
        return 0
    else:
        return 1"""
##############################################
# # Event handler for trading events in the market
# Tian's part handler
# 1.grab neccessary data
# 2.rank according to ratios of (the periods are tentative) MA(30), MA(120) and the conditions
# 3.keep track of time and call dan's functions
def handle_data(context, data):
    #log.info("handle_data")
    local_time = get_datetime().astimezone(timezone('US/Eastern'))
    log.info("local_time.hour" + str(local_time.hour))
    log.info("local_time.minute" + str(local_time.minute))
    if local_time.hour == 10 and local_time.minute == 0:
        #log.info("in hour cond")
        context.dayCount += 1
        context =  long_trend_calc(context, data)
        for stock in context.stocks:
            if stock in data:
                #context.smaShort[stock] = data[stock].mavg(SMA_SHORT_PERIOD)
                #context.smaLong[stock] = data[stock].mavg(SMA_LONG_PERIOD)
                context.smaShort[stock] = data[stock].mavg(1)
                #log.info("!smashort" + str(context.smaShort[stock]))
                context.smaLong[stock] = data[stock].mavg(2)
                #log.info("!smalong" + str(context.smaLong[stock]))
            if context.smaLong[stock] == 0:
                    context.ratio[stock] = 0.0
                    continue;
            context.ratio[stock] = context.smaShort[stock] / context.smaLong[stock]
            #log.info("smashort" + str(context.smaShort[stock]))
            #log.info("smalong" + str(context.smaLong[stock]))
    if local_time.hour == 10 and STOP_LOSS_USED and context.dayCount%BALANCE_FREQUENCY != 0 :
        stop_loss(context,data)
    
    context = rerank(context, data)
    #log.info("local hour" + str(local_time.hour))
    if local_time.hour == 10 and local_time.minute == 0 and context.dayCount%BALANCE_FREQUENCY == 0:
        #log.info("trade")
        trade(context, data)
    
        for stock in context.stocks:
            log.info(str(stock) + " " + str(context.portfolio.positions[stock].amount))
    """if context.dayCount % BALANCE_FREQUENCY == 0 and local_time.hour == 10 and local_time.minute == 1:
        
            #log.info("ratio" + str(context.ratio[stock]))"""
