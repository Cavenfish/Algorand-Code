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
        bal = bal * 1e-6
        return bal

    def getAssetBalance(self, ASA):
        bal = self.client.account_asset_info(self.addy, ASA)['asset-holding']['amount']
        tmp = self.client.asset_info(ASA)['params']
        mul = 10 ** (- tmp['decimals'])
        bal = bal * mul
        return bal
    
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

    def transfer(self, to, amount):
        sp   = self.client.suggested_params()
        uTxn = transaction.PaymentTxn(self.addy, sp, to, amount)
        self.executeTxn(uTxn)

    def transferASA(self, to, amount, ASA):
        sp   = self.client.suggested_params()
        uTxn = transaction.AssetTransferTxn(self.addy, sp, to, amount, ASA)
        self.executeTxn(uTxn)

    def closeAccount(self, to):
        sp   = self.client.suggested_params() 
        uTxn = transaction.PaymentTxn(self.addy, sp, to, 0, close_remainder_to=to)
        self.executeTxn(uTxn)

    def optIn(self, ASA):
        sp   = self.client.suggested_params()
        uTxn = transaction.AssetOptInTxn(self.addy, sp, ASA)
        self.executeTxn(uTxn)

    def closeASA(self, to, ASA):
        sp   = self.client.suggested_params()
        uTxn = transaction.AssetCloseOutTxn(self.addy, sp, to, ASA)
        self.executeTxn(uTxn)

