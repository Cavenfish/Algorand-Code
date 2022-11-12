from algosdk import account, mnemonic
from algosdk.v2client import algod

class Account:
    """Algorand wallet account"""

    def __init__(self, privateKey):
        api         = 'https://node.algoexplorerapi.io'
        self.client = algod.AlgodClient('', api)
        
        if privateKey:
            self.pk   = privateKey
            self.addy = account.address_from_private_key(privateKey)
        else:
            self.pk, self.addy = account.generate_account()

    def getBalance(self):
        bal = self.client.account_info(self.addy)['amount']
        print(f'Algo Balance: {bal*1e-6}')
