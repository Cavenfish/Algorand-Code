import yaml, sys
import PyBot as pb

acct   = pb.Account(pb.keys[0])
fname  = 'pairs.yaml'
earn   = 'profit.yaml'

def saveYAML(data, saveName):
    with open(saveName, 'w') as stream:
        yaml.dump_all(data, stream, sort_keys=False)

def getBal(tkn):
    if tkn:
        return acct.getAssetBalance(tkn)
    else:
        return acct.getBalance()

def tradeLevels(kind):
    if not pair[kind]: return

    #Get levels for trading
    if kind == 'buyPrices':
        toTrade = [x for x in pair[kind] if x[0] > price]
    else:
        toTrade = [x for x in pair[kind] if x[0] < price]

    if not toTrade: return

    #Store levels to keep and sum trading amount
    keep   = [x for x in pair[kind] if x not in toTrade]
    amount = sum([i[1] for i in toTrade])
    tkn    = pair['tokenA'] if kind == 'buyPrices' else pair['tokenB']
    init   = pair['sellSize'] if kind == 'buyPrices' else pair['buySize']
    b4     = getBal(tkn['id'])

    #Trade
    if kind == 'buyPrices':
        gbot.buy(amount)
        print('Buy Level Order Submitted\n')
    else:
        gbot.sell(amount)
        print('Sell Level Order Submitted\n')

    #Calculate profit
    income = getBal(tkn['id']) - b4 - (init * len(toTrade))

    #Update pairs database
    pair[kind] = keep

    #Update profit database
    profit['total'][tkn['name']]   += income
    profit['current'][tkn['name']] += income

def trade(kind):

    #Get tkn to trade, price multiplier and bal
    p   = pair['profit']
    tkn = tknA if kind == 'buy' else tknB
    mul = 1+p if kind == 'buy' else 1-p
    b4  = getBal(tkn)

    #Trade token
    if kind == 'buy':
        gbot.buy(pair['buySize'])
    else:
        gbot.sell(pair['sellSize'])


    #Get and store level from trade
    size = getBal(tkn) - b4
    levl = price * mul
    key  = 'sell' if kind == 'buy' else 'buy'
    pair[f'{key}Prices'].append([levl, size])

def scale(kind):
    n = len(pair[kind])
    if n >= 15: return 1e5 if kind == 'buyPrices' else 0

    if n <= 10:
        m = 0.075 * (n / 10)
    else:
        m = (0.1 * ((n-10) / 5)) + 0.095

    c = 1.005+m if kind == 'buyPrices' else 0.995-m
    return c

with open(fname, 'r') as stream:
    pairs = list(yaml.safe_load_all(stream))

with open(earn, 'r') as stream:
    profit = yaml.safe_load(stream)

for pair in pairs:
    tknA  = pair['tokenA']['id']
    tknB  = pair['tokenB']['id']
    gPri  = pair['gridPrice']
    gbot  = pb.GridBot(acct, tknA, tknB)
    price = gbot.getPrice()

    if price > gPri * scale('buyPrices'):
        trade('sell')
        print('Sell Order Submitted\n')
    elif price < gPri * scale('sellPrices'):
        trade('buy')
        print('Buy Order Submitted\n')
    else:
        print('Nothing Was Done\n')

    saveYAML(pairs, fname)
    tradeLevels('buyPrices')
    tradeLevels('sellPrices')

    if (price > gPri * 1.2) or (price < gPri * 0.8):
        pair['gridPrice'] = price
        print('Grid Price Updated\n')
    saveYAML(pairs, fname)

    gbot.checkExcess()#Ideally, should make new function
    #then store redeamed amounts in profit.yaml

with open(earn, 'w') as stream:
    yaml.dump(profit, stream, sort_keys=False)
