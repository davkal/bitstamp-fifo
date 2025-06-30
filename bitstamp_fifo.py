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
        self.initial_fee = self.fee

    def __repr__(self):
        return '%f %s' % (self.amount, self.symbol)


# Consume holdings in FIFO manner for the given Sell transaction
def consume(holdings, transaction):
    price = transaction.spot_price * transaction.amount
    # Value of first-out holdings
    cost = transaction.fee
    while transaction.amount > ZERO_GUARD:
        holding = holdings[0]
        if transaction.amount >= holding.amount:
            # consume holding fully
            fee = holding.amount / holding.initial_amount * holding.initial_fee
            cost += holding.amount * holding.spot_price + fee
            transaction.amount -= holding.amount
            holdings.popleft()
        else:
            # consume holding partially, adding only partial fee to cost
            fee = transaction.amount / holding.initial_amount * holding.initial_fee
            cost += transaction.amount * holding.spot_price + fee
            holding.amount -= transaction.amount
            holding.fee -= fee
            # holding was bigger than transaction, nothing left to do
            break
    return price - cost


def process_transactions(filename, holdings, requested_year):
    # Gain/loss after sales
    gain = 0
    # Headers for CSV output
    print('Date,Transaction,Symbol,Amount,Rate,Profit')

    # Read all transactions first
    transactions = []
    with open(filename) as csvfile:
        transaction_reader = csv.DictReader(csvfile)
        for row in transaction_reader:
            # Check if this is the new format (CombinedOrders.csv style)
            if 'Order Type' in row and 'Pair' in row:
                # New format: Order Type,Pair,Price,Amount,Value,Closed
                order_type = row['Order Type']
                pair = row['Pair']
                symbol = pair.split('/')[0]  # Extract symbol from pair like "BTC/EUR"
                amount = row['Amount']
                spot_price = row['Price']
                fee = 0  # No fee information in new format
                date_time = row['Closed']
                
                # Extract year from date format "2018-01-04 16:27:42"
                year = date_time.split('-')[0]
                
                transactions.append({
                    'order_type': order_type,
                    'symbol': symbol,
                    'amount': amount,
                    'spot_price': spot_price,
                    'fee': fee,
                    'date_time': date_time,
                    'year': year
                })
                
            elif 'Amount' in row and 'Sub Type' in row:
                # Old format: Type,Datetime,Account,Amount,Value,Rate,Fee,Sub Type
                if row['Type'] != 'Market':
                    continue
                amount_with_symbol = row['Amount']
                if ' ' not in amount_with_symbol:
                    continue
                amount, symbol = amount_with_symbol.split(' ')
                spot_price, _ = row['Rate'].split(' ')
                fee = row['Fee'].split(' ')[0] if row['Fee'] else 0
                order_type = row['Sub Type']
                date_time = row['Datetime']
                
                # Extract year from date format "Jan. 04, 2018, 04:22 PM"
                _, year, _ = date_time.split(', ')
                
                transactions.append({
                    'order_type': order_type,
                    'symbol': symbol,
                    'amount': amount,
                    'spot_price': spot_price,
                    'fee': fee,
                    'date_time': date_time,
                    'year': year
                })
                
            else:
                print('Given file does not look like a supported transactions file.')
                exit(1)
    
    # Sort transactions by date (oldest first)
    def parse_date(date_str):
        if '-' in date_str and len(date_str.split('-')[0]) == 4:
            # New format: "2018-01-04 16:27:42"
            from datetime import datetime
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        else:
            # Old format: "Jan. 04, 2018, 04:22 PM"
            from datetime import datetime
            return datetime.strptime(date_str, '%b. %d, %Y, %I:%M %p')
    
    transactions.sort(key=lambda x: parse_date(x['date_time']))
    
    # Process sorted transactions
    for tx in transactions:
        symbol = tx['symbol']
        if symbol not in holdings:
            holdings[symbol] = deque([])
        holding = holdings[symbol]
        transaction = Transaction(tx['amount'], symbol, tx['spot_price'], tx['fee'])
        
        if tx['order_type'] == 'Buy':
            holding.append(transaction)
        elif tx['order_type'] == 'Sell':
            margin = consume(holding, transaction)
            if (tx['year'] and tx['year'] == requested_year):
                gain += margin
                # CSV output row
                print('"%s",Sell,%s,%s,%s,%f' %
                      (tx['date_time'], symbol, tx['amount'], tx['spot_price'], margin))

    print('Summary gain (negative is loss): %f' % gain)
    return gain


def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else 'Transactions.csv'
    year = sys.argv[2]
    if path.isfile(filename):
        process_transactions(filename, all_holdings, year)
    else:
        print('Could not find transaction file.')
        print('Usage: python bitstamp_fifo.py <Transaction.csv> <year>')
        exit(1)


if __name__ == "__main__":
    main()
