#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to update a csv file and loans.png with current metrics.
Assumed to be scheduled to run multiple times a day.
"""

print('\n' + '='*60)
print('\nScript started. Reading loan data from the Ethereum blockchain...')

import os
import pandas
from data_aggregation import (
    reset_scraped_prices,
    export_loan_metrics_dict,
    safe_getter,
    append_to_csv
    )
from image_manipulation import update_loan_stats

# Define csv file to append data to
metrics_csv = 'yield_stats_v1.csv'

# Clear price memory to get current token prices
print('Resetting price data stored in memory...')
reset_scraped_prices(verbose=True)



# Read token data from Ethereum blockchain, scrape price data from web
print('Scraping price data to get aggregated loan statistics...')
metrics = safe_getter(export_loan_metrics_dict)

# Helper function for table-style plotting
def prettyprint(dict_):
    print('\n{:^35} | {:^6}'.format('metric', 'value'))
    print('-'*65)
    for k,v in dict_.items():
        print("{:35} | {:<20}".format(k,v))

# Print sample
print('\nLoan metrics updated. Data from export_loan_metrics_dict():')
prettyprint(metrics)

# Save to csv file. Only add header if no csv file exists yet.
print(f'\nAppending data to {metrics_csv}...')
append_to_csv(metrics_csv, metrics, verbose=False)
print(f'{metrics_csv} has been updated successfully.')

# Update loans.png
update_loan_stats(metrics, verbose=True)
