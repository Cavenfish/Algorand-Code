import json
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.future import transaction

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
    
    def viewLastTxn(self):
        tmp = json.dumps(self.last, indent=2)
        print(tmp)

    def executeTxn(self, uTxn):
        sTxn = uTxn.sign(self.pk)
        txid = self.client.send_transaction(sTxn)
        try:
            self.last = transaction.wait_for_confirmation(self.client, txid, 4)
        except Exception as err:
            print(err)

    def transfer(self, amount, to):
        sp   = self.client.suggested_params()
        uTxn = transaction.PaymentTxn(self.addy, sp, to, amount)
        self.executeTxn(uTxn)

    def closeAccount(self, to):
        sp   = self.client.suggested_params() 
        uTxn = transaction.PaymentTxn(self.addy, sp, to, 0, close_remainder_to=to)
        self.executeTxn(uTxn)

    def optIn(self, ASA):
        sp   = self.client.suggested_params()
        uTxn = transaction.AssetOptInTxn(self.addy, sp, ASA)
        self.executeTxn(uTxn)

