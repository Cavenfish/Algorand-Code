import sys
from .config import *
sys.path.append(cfg.tinyPath)
from tinyman.assets import AssetAmount

from tinyman.v1.client import TinymanClient
from tinyman.v2.client import TinymanV2Client

class GridBot:
    """Algorand GridBot"""

    def __init__(self, acct, tknA, tknB):
        self.acct = acct
        self.tiny = TinymanClient(acct.client, cfg.tinyIDv1, acct.addy)
        self.tknA = self.tiny.fetch_asset(tknA)
        self.mulA = 10 ** self.tknA.decimals
        self.tknB = self.tiny.fetch_asset(tknB)
        self.mulB = 10 ** self.tknB.decimals
        self.pickPool()

    def pickPool(self):
        tinyV1 = TinymanClient(self.acct.client, cfg.tinyIDv1, self.acct.addy)
        tinyV2 = TinymanV2Client(self.acct.client, cfg.tinyIDv2, self.acct.addy)
        v1Pool = tinyV1.fetch_pool(self.tknA, self.tknB)
        v2Pool = tinyV2.fetch_pool(self.tknA, self.tknB)
        v1TVL  = v1Pool.info()['asset1_reserves']
        v2TVL  = v2Pool.info()['asset_1_reserves']

        if v1TVL > v2TVL:
            self.tiny = tinyV1
            self.pool = v1Pool
        else:
            self.tiny = tinyV2
            self.pool = v2Pool

    def viewExcess(self):
        excess = self.pool.fetch_excess_amounts()
        return excess

    def checkExcess(self):
        ex   = self.pool.fetch_excess_amounts()

        if not ex:
            return

        if len(ex) < 2:
            return

        if (ex[self.tknA] > 1e6) and (ex[self.tknB] >  0.25e6):
            self.collectExcess(ex)
            print('\nAssets Redeamed\n')
            amt = [ex[i].amount*1e-6 for i in ex]
            return amt

    def viewLastTrade(self):
        return self.last

    def getPrice(self):
        tknIn = self.tknA(self.mulA)
        quote = self.pool.fetch_fixed_input_swap_quote(tknIn, slippage=0.001)
        price = quote.amount_out.amount / self.mulB
        return price

    def executeTxn(self, gTxn):
        gTxn.sign_with_private_key(self.acct.addy, self.acct.pk)
        self.last = self.tiny.submit(gTxn, wait=True)

    def optInTiny(self):
        gTxn = self.tiny.prepare_app_optin_transactions()
        self.executeTxn(gTxn)

    def buy(self, amount):
        if self.tiny.version == 'v2':
            tknIn = AssetAmount(self.tknB, int(amount * self.mulB))
        else:
            tknIn = self.tknB(amount * self.mulB)
        quote = self.pool.fetch_fixed_input_swap_quote(tknIn, slippage=0.005)
        gTxn  = self.pool.prepare_swap_transactions_from_quote(quote=quote)
        self.executeTxn(gTxn)

    def sell(self, amount):
        if self.tiny.version == 'v2':
            tknIn = AssetAmount(self.tknA, int(amount * self.mulA))
        else:
            tknIn = self.tknA(amount * self.mulA)
        quote = self.pool.fetch_fixed_input_swap_quote(tknIn, slippage=0.005)
        gTxn  = self.pool.prepare_swap_transactions_from_quote(quote)
        self.executeTxn(gTxn)

    def collectExcess(self, excess):
        for i in excess:
            amt  = excess[i]
            gTxn = self.pool.prepare_redeem_transactions(amt)
            self.executeTxn(gTxn)
