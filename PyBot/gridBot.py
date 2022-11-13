import sys
sys.path.append('./tinyman-py-sdk/')

from tinyman.v1.client import TinymanClient

class GridBot:
    """Algorand GridBot"""

    def __init__(self, acct, tknA, tknB):
        self.acct = acct
        self.tiny = TinymanClient(acct.client, 552635992, acct.addy)
        self.tknA = self.tiny.fetch_asset(tknA)
        self.mulA = 10 ** self.tknA.decimals
        self.tknB = self.tiny.fetch_asset(tknB)
        self.mulB = 10 ** self.tknB.decimals
        self.pool = self.tiny.fetch_pool(self.tknA, self.tknB)
    
    def checkExcess(self):
        excess = self.pool.fetch_excess_amounts()
        return excess

    def viewLastTrade(self):
        return self.last

    def getPrice(self):
        tknIn = self.tknA(self.mulA)
        quote = self.pool.fetch_fixed_input_swap_quote(tknIn, slippage=0.01)
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
        quote = self.pool.fetch_fixed_input_swap_quote(tknIn, slippage=0.01)
        gTxn  = self.pool.prepare_swap_transactions_from_quote(quote)
        self.executeTxn(gTxn)

    def sell(self, amount):
        tknIn = self.tknA(amount * self.mulA)
        quote = self.pool.fetch_fixed_input_swap_quote(tknIn, slippage=0.01)
        gTxn  = self.pool.prepare_swap_transactions_from_quote(quote)
        self.executeTxn(gTxn)

    def collectExcess(self, excess):
        for amount in excess:
            gTxn = self.pool.prepare_redeem_transactions(amount)
            self.executeTxn(gTxn)

