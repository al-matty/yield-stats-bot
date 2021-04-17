#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to update loans.png with current metrics.
Assumed to be scheduled to run multiple times a day.
"""
import os
import pandas
from data_aggregation import reset_scraped_prices, export_loan_metrics_dict
from image_manipulation import update_loan_stats

# connection error counter (for debugging only)
connection_errors = 0

# Clear price memory to get current token prices
reset_scraped_prices()

# Wrapper to handle connection errors
def safe_update():
    '''
    Tries to fetch loan metrics until there's no connection error.
    Returns a loan statistics dict.
    '''
    try:

        metrics = export_loan_metrics_dict()

    except ConnectionError:

        print('Encountered a connection error. Trying again...')
        connection_errors += 1

        sleep(20)
        safe_update()

    return metrics


# Read token data from Ethereum blockchain, scrape price data from web
metrics = safe_update()

# Helper function for table-style plotting
def prettyprint(dict_):
    print('\n{:^35} | {:^6}'.format('metric', 'value'))
    print('-'*65)
    for k,v in dict_.items():
        print("{:35} | {:<20}".format(k,v))

# Print sample
print(f'\nLoan metrics updated. Encountered {connection_errors} connection errors.')
print('Data from export_loan_metrics_dict():')
prettyprint(metrics)

# Save to csv file. Only add header if no csv file exists yet.

# Convert dict to pandas df
#outfile =
#df.to_csv(output_path, mode='a', header=not os.path.exists(outfile))

update_loan_stats(metrics)
