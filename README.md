# Installation
To use Simple Coin you should install Tendermint core, Redis and some Python libraries. All the instructions were tested on the Ubuntu 16.04, not sure about other OS.

## Tendermint & abci-cli (optional, need for testing)
```bash
$ mkdir tendermint
$ cd tendermint
$ sudo docker run --rm -v /your/tendermint/folder:/tendermint tendermint/tendermint:0.24.0 init
[10-18|17:05:28.863] Generated private validator   module=main path=/tendermint/config/priv_validator.json
[10-18|17:05:28.863] Generated node key            module=main path=/tendermint/config/node_key.json
[10-18|17:05:28.863] Generated genesis file        module=main path=/tendermint/config/genesis.json
```

## Redis
```bash
$ sudo apt update
$ sudo apt install redis-server
$ sudo service redis-server restart
$ redis-cli  # Check is everything ok
127.0.0.1:6379> ping
PONG  # Press CTRL+C
```

## Repo
```bash
$ sudo apt-get install python3-dev virtualenv git
$ git clone https://github.com/SoftblocksCo/Simple_coin
$ cd Simple_coin
$ virtualenv --python python3.6 --no-site-packages venv
$ source venv/bin/activate  # Activate your virtual environment every time you use Simple Coin
$ pip install -r requirements.txt
```

# Run Simple Coin
```bash
$ cd Simple_coin
$ source venv/bin/activate
$ python application.py
$ # In another terminal
$ cd tendermint # directory we created earlier
$ sudo docker run --rm --network "host" -v /your/tendermint/folder:/tendermint tendermint/tendermint:0.24.0 node
```

# Wallet
In order to achive the great UI/UX, I've developed the new generation wallet. So anyone can work with Simple Coin without any troubles and don't touch code at all. Ed25519 cryptography was used - [here's](https://ed25519.cr.yp.to/) the docs.
```bash
$ python wallet.py --help
usage: Simple wallet for SimpleCoin [-h] [-n] [-w WALLET] [-t] [-b BROADCAST]
                                    [-g GET_BALANCE] [-s] [-c CHECK_SIGN]
                                    [-m MESSAGE] [-p PUB_KEY] [-a AMOUNT]
                                    [-r RECEIVER] [-d DATA]

optional arguments:
  -h, --help            show this help message and exit
  -n, --new             Create new keypair
  -w WALLET, --wallet WALLET
                        Path to the .sc wallet
  -t, --transaction     Create & sign a txn
  -b BROADCAST, --broadcast BROADCAST
                        Broadcast txn to the network
  -g GET_BALANCE, --get_balance GET_BALANCE
                        Get balance for some address
  -s, --sign            Sign a message
  -c CHECK_SIGN, --check_sign CHECK_SIGN
                        Specify the signature
  -m MESSAGE, --message MESSAGE
                        Message to sign or to check
  -p PUB_KEY, --pub_key PUB_KEY
                        Public key, corresponding to the signature
  -a AMOUNT, --amount AMOUNT
                        Amount of coins to send in txn
  -r RECEIVER, --receiver RECEIVER
                        Transaction receiver
  -d DATA, --data DATA  Small piece of data to store in txn
```

## Generate new wallet
This method creates new wallet file and saves it in the `--wallet` path. Inside this file there will be two rows: first one is a private key, second one is a public key. And this is all you need to use Simple Coin blockchain!

```bash
$ python wallet.py --new --wallet Alice.sc
New keypair saved into the Alice.sc
$ cat Alice.sc
OaEbR7z0UhqOeL0StWUZpe45H97H2NkwFhvZ0Ghrk3Y
jqRN5C3kS4t7kr7vFtdjouz1pw7eKhn+YoK1LvBcvEU
```

## Generate transaction
This method generates new transaction and signs it. Each transaction is a simple JSON, here's an example:
```json
{
  "sender" : "jqRN5C3kS4t7kr7vFtdjouz1pw7eKhn+YoK1LvBcvEU",
  "receiver" : "WTLAL/dJWptYX2zE9XvFVcbGQvLRE7zsKYoI5bbnDcg",
  "amount" : 123,
  "data" : "big espresso",
  "timestamp" : 1517395993,
  "signature" : "<SIGNATURE>"
}
```
Transaction should be signed with a private key, according to the `sender` public key, otherwise it won't be valid (pretty obvious, isn't it?).
```bash
python wallet.py --transaction --wallet wallets/Bob.sc --receiver 'jqRN5C3kS4t7kr7vFtdjouz1pw7eKhn+YoK1LvBcvEU' --data 'hi, Alice!' --amount 10
Your txn is printed bellow. Copy as it is and send with the ABCI query or using `--broadcast` flag

0x7b2273656e646572223a202235393332633032666637343935613962353835663663633466353762633535356336633634326632643131336263656332393861303865356236653730646338222c20227265636569766572223a20226a71524e3543336b533474376b7237764674646a6f757a31707737654b686e2b596f4b314c764263764555222c202274696d657374616d70223a20313531373339363635372c202264617461223a202268692c20416c69636521222c20227369676e6174757265223a2022334b5750435434496d4b542f593535762b634866754270766f6c4e58747058516f306474516f7467624141564d5870424d48633734716850664f5376393569686d7369536e346f6f5039677557747158486b79334341222c2022616d6f756e74223a2031307d
```


## Send transaction
This methods broadcasts signed transaction to the Tendermint nodes. Also, you can do it manually: after launching `tendermint node` and Application, open the [http://localhost:46657/](http://localhost:46657/). It's something like a build-in Tendermint API, which includes method `broadcast_tx_async` for txn broadcasting (just copy-paste your txn into the `tx` GET argument).
```bash
$ python wallet.py --broadcast '0x7b2273656e646572223a202235393332633032666637343935613962353835663663633466353762633535356336633634326632643131336263656332393861303865356236653730646338222c20227265636569766572223a20226a71524e3543336b533474376b7237764674646a6f757a31707737654b686e2b596f4b314c764263764555222c202274696d657374616d70223a20313531373339363635372c202264617461223a202268692c20416c69636521222c20227369676e6174757265223a2022334b5750435434496d4b542f593535762b634866754270766f6c4e58747058516f306474516f7467624141564d5870424d48633734716850664f5376393569686d7369536e346f6f5039677557747158486b79334341222c2022616d6f756e74223a2031307d'
Your txn have been broadcasted to the network!
```

## Get balance
This method returns your current balance. As well as `Send transaction` method, it uses Tendermint API to make a query to the Application. You should specify public key after `--get_balance` flag.
```bash
$ python wallet.py --get_balance fRsyOcYoFJOg9nXk6iugOMApvRXEghAbSpFIHxRWdNA
There are 1000 SimpleCoins on the fRsyOcYoFJOg9nXk6iugOMApvRXEghAbSpFIHxRWdNA
```

## Sign message
This method allows you to sign any message with your private key.
```bash
$ cat Alice.sc
0GqohWtjnIjmsm46Cq+o53+iqoHu/OIOmKV8C44Lz9I
fRsyOcYoFJOg9nXk6iugOMApvRXEghAbSpFIHxRWdNA
$ python wallet.py --sign --message 'I need to be sure' --wallet Alice.sc
The signature is:	 Ulh1in480frZoVzW+wEcbMYxu1w0YKXyipUPP1fSPyIUbYnHWe3OvHqJ5lyiIAKf/ltyQ3WB+KBpaPAAFMJcCQ
```

## Check message signature
This method allows you to check, that the signature satisfies the public key and a message.
```bash
$ cat Alice.sc
0GqohWtjnIjmsm46Cq+o53+iqoHu/OIOmKV8C44Lz9I
fRsyOcYoFJOg9nXk6iugOMApvRXEghAbSpFIHxRWdNA
$ python wallet.py --check 'Ulh1in480frZoVzW+wEcbMYxu1w0YKXyipUPP1fSPyIUbYnHWe3OvHqJ5lyiIAKf/ltyQ3WB+KBpaPAAFMJcCQ' --pub_key 'fRsyOcYoFJOg9nXk6iugOMApvRXEghAbSpFIHxRWdNA' --message 'I need to be sure' -w Alice.sc
Valid signature!
$ python wallet.py --check 'Ulh1in480frZoVzW+wEcbMYxu1w0YKXyipUPP1fSPyIUbYnHWe3OvHqJ5lyiIAKf/ltyQ3WB+KBpaPAAFMJcCQ' --pub_key 'fRsyOcYoFJOg9nXk6iugOMApvRXEghAbSpFIHxRWdNA' --message 'I dont need to be sure' -w Alice.sc
Invalid signature!
```
