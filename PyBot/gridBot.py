import sys
sys.path.append('./tinyman-py-sdk/')

from tinyman.v1.client import TinymanClient

class GridBot:
    """Algorand GridBot"""

    def __init__(self, acct):
        self.acct = acct
        self.tiny = TinymanClient(acct.client, 552635992, acct.addy)
        self.tknA = self.tiny.fetch_asset(0)        #Algo
        self.tknB = self.tiny.fetch_asset(31566704) #USDC
        self.pool = self.tiny.fetch_pool(self.tknA, self.tknB)
    
    def executeTxn(self, gTxn):
        gTxn.sign_with_private_key(self.acct.addy, self.acct.pk)
        result = self.tiny.submit(gTxn, wait=True)

    def optInTiny(self):
        gTxn = self.tiny.prepare_app_optin_transactions()
        self.executeTxn(gTxn)

    def buy(self, amount):
        tknIn = self.tknB(amount)
        quote = self.pool.fetch_fixed_input_swap_quote(tknIn, slippage=0.01)
        gTxn  = self.pool.prepare_swap_transactions_from_quote(quote)
        self.executeTxn(gTxn)

    def sell(self, amount):
        tknIn = self.tknA(amount)
        quote = self.pool.fetch_fixed_input_swap_quote(tknIn, slippage=0.01)
        gTxn  = self.pool.prepare_swap_transactions_from_quote(quote)
        self.executeTxn(gTxn)
