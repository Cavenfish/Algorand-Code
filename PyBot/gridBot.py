import sys
from .config import *
sys.path.append(cfg.tinyPath)

from tinyman.v1.client import TinymanClient

class GridBot:
    """Algorand GridBot"""

    def __init__(self, acct, tknA, tknB):
        self.acct = acct
        self.tiny = TinymanClient(acct.client, cfg.tinyID, acct.addy)
        self.tknA = self.tiny.fetch_asset(tknA)
        self.mulA = 10 ** self.tknA.decimals
        self.tknB = self.tiny.fetch_asset(tknB)
        self.mulB = 10 ** self.tknB.decimals
        self.pool = self.tiny.fetch_pool(self.tknA, self.tknB)

    def viewExcess(self):
        excess = self.pool.fetch_excess_amounts()
        return excess

    def checkExcess(self):
        ex   = self.pool.fetch_excess_amounts()

        if not ex:
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
        tknIn = self.tknB(amount * self.mulB)
        quote = self.pool.fetch_fixed_input_swap_quote(tknIn, slippage=0.001)
        gTxn  = self.pool.prepare_swap_transactions_from_quote(quote)
        self.executeTxn(gTxn)

    def sell(self, amount):
        tknIn = self.tknA(amount * self.mulA)
        quote = self.pool.fetch_fixed_input_swap_quote(tknIn, slippage=0.001)
        gTxn  = self.pool.prepare_swap_transactions_from_quote(quote)
        self.executeTxn(gTxn)

    def collectExcess(self, excess):
        for i in excess:
            amt  = excess[i]
            gTxn = self.pool.prepare_redeem_transactions(amt)
            self.executeTxn(gTxn)
