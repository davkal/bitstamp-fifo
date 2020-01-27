import csv
from collections import deque
from os import path
import sys

# Protect loops from rounding issues
ZERO_GUARD = 1.0e-8

# symbol -> []
all_holdings = {}


class Transaction:
    def __init__(self, amount, symbol, spot_price, fee):
        # self.amount will be mutated when consuming holdings
        self.amount = round(float(amount), 8)
        self.initial_amount = self.amount
        self.symbol = symbol
        self.spot_price = round(float(spot_price), 8)
        self.fee = float(fee)

    def __repr__(self):
        return '%f %s' % (self.amount, self.symbol)


# Consume holdings in FIFO manner for the given Sell transaction
def consume(holdings, transaction):
    price = transaction.spot_price * transaction.amount
    # Value of first-out holdings
    cost = transaction.fee
    while transaction.amount > ZERO_GUARD:
        holding = holdings[0]
        if transaction.amount > holding.amount:
            # consume holding fully
            cost += holding.amount * holding.spot_price + holding.fee
            transaction.amount -= holding.amount
            holdings.popleft()
        else:
            # consume holding partially, adding only partial fee to cost
            fee = holding.amount / holding.initial_amount * holding.fee
            cost += transaction.amount * holding.spot_price + fee
            holding.amount -= transaction.amount
            # holding was bigger than transaction, nothing left to do
            break
    return price - cost


def process_transactions(filename):
    # Gain/loss after sales
    gain = 0

    with open(filename) as csvfile:
        transaction_reader = csv.DictReader(csvfile)
        for row in transaction_reader:
            if 'Amount' not in row:
                print('Given file does not look like a Bitstamp transactions file.')
                exit(1)
            amount, symbol = row['Amount'].split(' ')
            if symbol not in all_holdings:
                all_holdings[symbol] = deque([])
            # assuming same currency on all transactions
            spot_price, _ = row['Rate'].split(' ')
            fee = row['Fee'].split(' ')[0] if row['Fee'] else 0
            transaction = Transaction(amount, symbol, spot_price, fee)
            if row['Sub Type'] == 'Buy':
                all_holdings[symbol].append(transaction)
            elif row['Sub Type'] == 'Sell':
                margin = consume(all_holdings[symbol], transaction)
                gain += margin
                print('Sold %s with %f gain' % (symbol, margin))
    print('Summary gain (negative is loss): %f' % gain)


def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else 'Transactions.csv'
    if path.isfile(filename):
        process_transactions(filename)
    else:
        print('Could not find transaction file.')
        print('Usage: python bitstamp_fifo.py <Transaction.csv>')
        exit(1)


if __name__ == "__main__":
    main()
