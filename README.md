# Bitstamp FIFO Gain/Loss calculator

FIFO-based accounting for [Bitstamp](https://bitstamp.net) transaction files to calculate year gain/loss for tax purposes.
Does not support tax-free year-long holdings.

## Setup

Requires python 2.7

1. Clone repo
2. Download `Transactions.csv` into cloned repo.
3. Run `python bitstamp_fifo.py`

## Notes

- Distinguishes between different cryto currencies
- Assumes all transactions are done in same fiat currency (e.g., EUR)
- No detection of year-long holdings
- Only works for transactions started in the first year.

## TODO

- [ ] Support for arbitrary date ranges
