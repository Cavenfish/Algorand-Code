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
        gbot.buy(amount)
    else:
        gbot.sell(amount)

    #Update pairs database
    pair[kind] = keep

def trade(kind):
    def getBal():
        if tkn:
            return acct.getAssetBalance(tkn)
        else:
            return acct.getBalance()
    
    p   = pair['profit']
    tkn = tknA if kind == 'buy' else tknB
    mul = 1+p if kind == 'buy' else 1-p 
    print(tkn)
    print(mul)

    b4 = getBal()

    if kind == 'buy':
        pass
        #gbot.buy(pair['buySize'])
    else:
        pass
        #gbot.sell(pair['sellSize'])

    size = getBal() - b4
    levl = price * mul
    pair[f'{kind}Prices'].append([levl, size])

with open(fname, 'r') as stream:
    pairs = list(yaml.safe_load_all(stream))

for pair in pairs:
    tknA  = pair['tokenA']['id']
    tknB  = pair['tokenB']['id']
    gbot = pb.GridBot(acct, tknA, tknB)
    price = gbot.getPrice()
    trade('buy')
    trade('sell')
    #saveYAML(pairs)

