import yaml
import PyBot as pb

acct   = pb.Account(pb.keys[0])
fname  = 'pairsTEST.yaml'

def saveYAML(data):
    with open(fname, 'w') as stream:
        yaml.dump_all(data, stream, sort_keys=False)

def tradeLevels(kind):
    if not pair[kind]: return
    
    #Get levels for trading
    if kind == 'buyPrices':
        toTrade = [x for x in pair[kind] if x[0] > price]
    else:
        toTrade = [x for x in pair[kind] if x[0] < price]

    #Store levels to keep and sum trading amount
    keep   = [x for x in pair[kind] if x not in toTrade]
    amount = sum([i[1] for i in toTrade])
    
    #Trade
    if kind == 'buyPrices':
        pass
        #gbot.buy(amount)
    else:
        pass
        #gbot.sell(amount)

    #Update pairs database
    pair[kind] = keep

def trade(kind):
    def getBal():
        if tkn:
            return acct.getAssetBalance(tkn)
        else:
            return acct.getBalance()
    
    #Get tkn to trade, price multiplier and bal
    p   = pair['profit']
    tkn = tknA if kind == 'buy' else tknB
    mul = 1+p if kind == 'buy' else 1-p 
    b4  = getBal()

    #Trade token
    if kind == 'buy':
        pass
        #gbot.buy(pair['buySize'])
    else:
        pass
        #gbot.sell(pair['sellSize'])

    #Get and store level from trade
    size = getBal() - b4
    levl = price * mul
    pair[f'{kind}Prices'].append([levl, size])

def scale(kind):
    n = len(pair[kind])
    if n >= 15: return 1
    
    if n <= 10:
        m = 0.075 * (n / 10)
    else:
        m = (0.1 * ((n-10) / 5)) + 0.095
    
    c = 1.005+m if kind == 'buyPrices' else 0.995-m
    return c

with open(fname, 'r') as stream:
    pairs = list(yaml.safe_load_all(stream))

for pair in pairs:
    tknA  = pair['tokenA']['id']
    tknB  = pair['tokenB']['id']
    gPri  = pair['gridPrice']
    gbot  = pb.GridBot(acct, tknA, tknB)
    price = gbot.getPrice()
    
    if price > gPri * scale('buyPrices'):
        trade('sell')
    else if price < gPri * scale('sellPrices'):
        trade('buy')
    else:
        pass

    saveYAML(pairs)
    tradeLevels('buyPrices')
    tradeLevels('sellPrices')
    
    if (price > gPri * 1.2) or (price < gPri * 0.8):
        pair['gridPrice'] = price
    saveYAML(pairs)

