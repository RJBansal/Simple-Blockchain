from flask import Flask, jsonify, request
from uuid import uuid4
import hashlib
import time as t
import json


class BlockChain:

    global reward
    reward = 100

    def __init__(self):
        self.chain = []
        self.transactions = []

        self.new_block(proof=1, previous_hash='23r89hwkjs')

    def new_transaction(self, sender, recipient, amount):
        """

        :param sender: <str> Sender Address
        :param recipient: <str> Recipient Address
        :param amount: <int> Amount of tokens sent
        :return: <int> last block index
        """

        t = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        }
        self.transactions.append(t)

        return self.last_block()['index'] + 1

    def new_block(self, proof, previous_hash):

        """

        :param proof:  <int> proof number
        :param previous_hash: <str> previous hash, only Genesis has no previous
        :return: block
        or self.hash(self.chain[-1])
        """

        block_new = {
            'index': len(self.chain) + 1,
            'timestamp': t.time(),
            'transactions': self.transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        self.transactions = []
        self.chain.append(block_new)
        return "New Block Created"

    def last_block(self):
        return self.chain[-1]

    def hash(self, block):

        block_string = str(block).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):

        curr_proof = 0;
        while self.valid_proof(last_proof, curr_proof) is False:
            curr_proof += 1

        return curr_proof

    def valid_proof(self, last_proof, proof):

        attempt = hashlib.sha256((f'{last_proof}{proof}').encode()).hexdigest()
        if attempt[:4] == "0000":
            return True
        else:
            return False

    def is_chain_valid(self):
        for x in range(1, self.chain.count()):
            curr = self.chain[x]
            prev = self.chain[x-1]

            if curr.hash != self.hash(curr):
                return False
            elif curr.previous_hash != prev.hash:
                return False
            else:
                return True

    def get_balance(self, node):
        balance = 0;
        for block in self.chain:
            for t in block['transactions']:
                if t['sender'] == node:
                    balance -= t['amount']
                elif t['recipient'] == node:
                    balance += t['amount']

        return balance


class Server:

    app = Flask(__name__)

    global node
    #nodes = []
    node = str(uuid4()).replace('-', "")

    global blockchain
    blockchain = BlockChain()


    @app.route('/')
    def hello_world():
        return 'Blockchain'

    @app.route('/transaction/new', methods=['POST'])
    def transactions():

        values = request.get_json()
        required = ['sender', 'recipient', 'amount']
        if not all(k in values for k in required):
            return 'Missing values', 401

        index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

        response = {'message': f'Transaction will be added to Block {index}'}
        return jsonify(response)

    @app.route('/chain', methods=['GET'])
    def view_chain():
        response = {
            'chain': blockchain.chain,
            'length': len(blockchain.chain),
        }

        return jsonify(response)

    @app.route('/mine', methods=['GET'])
    def mine_block():
        last_block = blockchain.last_block()
        last_proof = last_block['proof']
        mine = blockchain.proof_of_work(last_proof)

        blockchain.new_transaction(sender=node, recipient='user', amount=100)
        prev_hash = blockchain.hash(last_block)
        block_to_add = blockchain.new_block(mine, prev_hash)

        return jsonify(block_to_add)

    @app.route('/balance', methods=['GET'])
    def get_balance():

        return jsonify(blockchain.get_balance('user'))

    if __name__ == '__main__':
        #app.run()
        app.run(host='0.0.0.0', port=5001)


