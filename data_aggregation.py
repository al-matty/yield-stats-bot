import os, inspect, sys
import random
import pandas as pd
import urllib.request
from bs4 import BeautifulSoup
from time import time, sleep
from datetime import datetime

from etherscan import Etherscan
from web3.auto.infura import w3

import lookups as lu

logfile = 'statsbot_logging.txt'

#############################################################################
#
#   Initialize connection to Ethereum network
#
#############################################################################


# Initialize Etherscan API
API_KEY = os.environ['ETHERSCAN_API_KEY']
etherscan = Etherscan(API_KEY)

# Connect to ETH Node (Infura)
eth = w3.eth

# Contract addresses
loan_address = '0xbFE28f2d7ade88008af64764eA16053F705CF1f0'
loan_fac_address = '0x49aF18b1ecA40Ef89cE7F605638cF675B70012A7'

# TOKEN_METRICS_TODAY <- gets filled by update_daily_metrics()
TOKEN_METRICS_TODAY = {}


#############################################################################
#
# Helper functions & global variables
#   globals():
#   ABI_LOAN_FAC    Abi for smart contract LoanFactory.sol
#   ABI_LOAN        Abi for smart contract Loan.sol
#   LOAN_FAC        Instantiated & queryable smart contract LoanFactory.sol
#   ALL_LOANS_DATA  dict of dicts: {loan_address_i: {metric_j: val_j, ...}}
#
#############################################################################

# Query Etherscan API to get ABI for of contract address
def get_abi(address):
    abi = etherscan.get_contract_abi(address)
    return abi

def instantiate_contract(address, abi):
    contract = eth.contract(address=address, abi=abi)
    return contract

ABI_LOAN_FAC = get_abi(loan_fac_address)
ABI_LOAN = get_abi(loan_address)


# Appends a row (datetime + log message) to a logfile.
def log(logfile, _str):
    '''
    Appends current date, time, and _str as row to logfile (i.e. logging.txt).
    '''
    # Get current time.
    timestamp = datetime.now()
    parsedTime = timestamp.strftime('%Y %b %d %H:%M')
    row = '\n' + parsedTime + '\t' + _str

    # Avoid skipping the first line if no logfile exists yet
    if not os.path.isfile(logfile):
        row = row[1:]

    # Write to file
    with open(logfile, 'a') as file:
        file.write(row)



# ALL_LOANS <- addresses of all loans ever taken out
LOAN_FAC = instantiate_contract(loan_fac_address, ABI_LOAN_FAC)

try:
    ALL_LOANS = set(LOAN_FAC.caller.getLoans())
except Exception as e:
    message = f"Couldn't query LoanFactory.sol. Aborted data collection. ({e})"
    print(message)
    log(logfile, message)



# Helper function needed by get_loan_data()
def extract_loan_details(loan_dict):
    '''Splits up 'loan_details' into single entries, deletes original.'''

    details = loan_dict['loan_details']

    # Add keys and values to dict
    loan_dict['address_lender'] = details[0]
    loan_dict['address_borrower'] = details[1]
    loan_dict['address_lending_token'] = details[2]
    loan_dict['address_collateral_token'] = details[3]
    loan_dict['principal'] = details[4]
    loan_dict['interest'] = details[5]
    loan_dict['duration'] = details[6]
    loan_dict['collateral'] = details[7]

    # Remove original entry
    del loan_dict['loan_details']
    return loan_dict

# Helper function needed by get_loan_data()
def extract_meta_data(loan_dict):
    '''Splits up 'meta_data' into single entries, deletes original.'''

    meta = loan_dict['meta_data']

    # Add keys and values to dict
    loan_dict['loan_status'] = meta[0]
    loan_dict['ts_start'] = meta[1]
    loan_dict['ts_repaid'] = meta[2]
    loan_dict['liquidatable_t_allowance'] = meta[3]

    # Remove original entry
    del loan_dict['meta_data']
    return loan_dict

# Helper function for get_all_loans(): Get a dict of loan data for a loan_address
def get_loan_data(loan_address):
    '''Takes a loan address and returns a dictionary of loan data.'''
    global ABI_LOAN

    d = {}
    # Instantiate contract to make it callable
    loan = eth.contract(address=loan_address, abi=ABI_LOAN)
    caller = loan.caller()

    # Get data
    d['collateral_balance'] = caller.getCollateralBalance()
    d['loan_details'] = caller.getLoanDetails()
    d['meta_data'] = caller.getLoanMetadata()
    d['ts_due'] = caller.getTimestampDue()
    d['is_defaulted'] = caller.isDefaulted()

    # Extract nested data
    d = extract_loan_details(d)
    d = extract_meta_data(d)

    return d

# Data of all loans ever taken out on yield.credit
ALL_LOANS_DATA = {loan: get_loan_data(loan) for loan in ALL_LOANS}

# Helper functions: Loan filters
def get_all_loans():
    global ALL_LOANS_DATA
    return ALL_LOANS_DATA
def get_active_loans():
    global ALL_LOANS_DATA
    active = {k: v for k, v, in ALL_LOANS_DATA.items() if v['loan_status'] == 0}
    return active
def get_repaid_loans():
    global ALL_LOANS_DATA
    repaid = {k: v for k, v, in ALL_LOANS_DATA.items() if v['loan_status'] == 1}
    return repaid
def get_defaulted_loans():
    global ALL_LOANS_DATA
    defaulted = {k: v for k, v, in ALL_LOANS_DATA.items() if v['loan_status'] == 2}
    return defaulted
def get_non_defaulted_loans():
    global ALL_LOANS_DATA
    non_defaulted = {k: v for k, v, in ALL_LOANS_DATA.items() if v['loan_status'] != 2}
    return non_defaulted
def get_loans_w_bogus_status():
    '''For debugging only'''
    global ALL_LOANS_DATA
    bogus = {k: v for k, v, in ALL_LOANS_DATA.items() if v['loan_status'] == 4}
    return bogus

all_loan_addies = set(get_all_loans().keys())
active_addies = set(get_active_loans().keys())
repaid_addies = set(get_repaid_loans().keys())
defaulted_addies = set(get_defaulted_loans().keys())
bogus_addies = set(get_loans_w_bogus_status().keys())    # only for debugging

n_total = len(all_loan_addies)
n_repaid = len(repaid_addies)
n_active = len(active_addies)
n_defaulted = len(defaulted_addies)



# Helper function for Scrapes and returns price of 1 asset from coingecko
def get_token_price(token_str):
    '''
    Assumes a string matching an existing html child of 'coingecko.com/en/coins/', i.e. 'ethereum'.
    Returns float of current asset price (USD) as given on coingecko.com.
    '''
    url = 'https://www.coingecko.com/en/coins/' + token_str
    userAgent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)' + \
        ' Chrome/41.0.2228.0 Safari/537.36'
    req = urllib.request.Request(url, headers= {'User-Agent' : userAgent})
    html = urllib.request.urlopen(req)
    bs = BeautifulSoup(html.read(), 'html.parser')

    # Scrape price data
    varList = bs.findAll('span', {'class': 'no-wrap'})
    priceStr = varList[0].get_text()
    price_usd = float(priceStr.replace(',','').replace('$',''))

    # Sleep max 2 seconds before function can be called again
    sleep(random.random()*2)

    return price_usd

# Helper function for get_token_metrics. Needed for market cap rank.
def findCell(tableRows, rowKw, cellKw=None, getRawRow=False, stripToInt=True):
    '''
    Assumes tableRows = bs.findAll('tr').
    Cycles through all table rows / cells of a website and returns a match

    If no cellKw set:    Returns 1st matching row.
    If cellKw set:       Returns first matching cell within that row.
    If stripToInt:       Returns int (all numbers within that cell).

    Example:
                >>>findCell(tableRows, 'Price', '$')
                >>>575
    '''
    funcName = inspect.currentframe().f_code.co_name
    result = None

    for row in tableRows:

        # Possibility no cellKw: Return the first row containing rowKw
        if rowKw in row.get_text():
            result = str(row)

            # Possibility getRaw: Return raw bs.Tag object
            if getRawRow and result and not cellKw:
                result = row
                stripToInt = False

    # Possibility cellKw: Return the first cell containing cellKw
    if cellKw and result:
        sCell = [str(cell) for cell in row if cellKw in result][0]
        result = sCell

    # Possibility stripToInt: Extract integers and return int
    if stripToInt and result:
        try:
            n = int(''.join(filter(lambda i: i.isdigit(), result)))
            result = n
        except ValueError:
            print( \
            f'''
            {funcName}():
            There are no digits in the first row containing '{rowKw}' and
            its first cell containing '{cellKw}'.
            ''')

    # Possibility: No rows found matching rowKw
    if not result:
        print(f'{funcName}(): No rows found containing {rowKw}!')
    return result

# Helper function: Removes any '$', '%', and ',' from target string and converts to float
def clean(string):
    # Abort if scraped metric is empty or None
    assert string not in {None, ''}, \
        f"""
        Coingecko seems to have restructured their website.
        One of the metrics couldn't be scraped. Check {funcName}().
        """
    return float(string.replace(',','').replace('$','').replace('%',''))

# Helper function: Looks up token symbol in lookups.py file
def get_token_symbol(token_address, logfile=None):

    try:
        return lu.token_map[token_address]['symbol']

    except KeyError:
        message = f"get_token_symbol(): No entry in token_map in lookups.py for {token_address}."
        print(message)

        if logfile:
            log(logfile, message)

# Helper function: Looks up token coingecko str in lookups.py file
def get_token_str(token_address, logfile=None):

    try:
        return lu.token_map[token_address]['coingecko_str']

    except KeyError:
        message = f"get_token_str(): No entry in token_map in lookups.py for {token_address}."
        print(message)

        if logfile:
            log(logfile, message)

# Helper function: Reverse lookup from token_map
def get_address_by_symbol(symbol):
    address = next(k for k, v in lu.token_map.items() if v['symbol'] == symbol)
    return address

# Helper function: Looks up token decimals value in lookups.py file
def get_token_decimals(token_address, logfile=None):
    try:
        return lu.token_map[token_address]['decimals']
    except KeyError:
        message = f"No entry in token_map in lookups.py for {token_address}."
        print(message)
        if logfile:
            log(logfile, message)

# Decode ERC20 amount based on its number of decimals
def apply_decimals(amount, token_address=None, token_symbol=None, logfile=None):
    '''
    Takes ERC20 address string and looks up / fetches from web3
    decimal information. Returns correct value based on decimals.
    '''

    if token_symbol:
        token_address = get_address_by_symbol(symbol)

    if token_address:
        decimals = get_token_decimals(token_address, logfile=logfile)
        DECIMALS = 10**decimals

        return amount // DECIMALS

    else:
        print('Either a token adress or symbol string has to be specified.')



# Some global variables for data fetching
SCRAPED_PRICES = {}      # temporary storage for asset prices to avoid unnecessary scraping
CONNECTION_ERRORS = 0    # connection error counter (for debugging phase)


# Resets prices stored in memory for sparse scraping.
def reset_scraped_prices(verbose=False):
    '''
    Resets the saved prices used for sparse scraping.
    Needs to be reset whenever new metrics are calculated that
    depend on current prices of cryptos.
    '''
    global SCRAPED_PRICES
    SCRAPED_PRICES = {}
    if verbose:
        print('Cache for previously scraped prices has been cleared.')

# Wrapper to handle connection errors for data fetching functions
def safe_getter(function, delay_seconds=10, max_tries=None, try_nr=0):
    '''
    Repeatedly tries to run a function until there are no connection
    errors. Returns whatever the function returns.
    Example:
            a = safe_getter(some_function) (<- func without parentheses)
    '''
    global CONNECTION_ERRORS

    name = function.__name__
    result = None

    # Try running the function
    try:
        result = function()

    except ConnectionError as e:

        print(f'{name}(): Encountered a connection error.')
        CONNECTION_ERRORS += 1

        sleep(delay_seconds)
        print('Trying again...')

        # Possibility: max_tries is set to some number. Keep count of tries.
        if max_tries:
            try_nr += 1

            # Repeated calling of function until max_tries is reached
            if try_nr < max_tries:
                safe_getter(function, delay_seconds=delay_seconds, max_tries=max_tries, try_nr=try_nr)

            else:
                print(f'{name}(): Maximum connection attempts ({max_tries}) reached. Returned {result}.')

        # Possibility: max_tries not set. Unlimited repetitions.
        else:
            safe_getter(function, delay_seconds=delay_seconds, max_tries=max_tries, try_nr=try_nr)

    return result

# Helper function: Tries to get token price from SCRAPED_PRICES before scraping
def sparse_scrape(token_addy, logfile=None):
    '''
    Returns current USD value of 1 token of given address.
    Scrapes token price from web only if necessary.
    Alway tries to read from SCRAPED_PRICES dict first.
    '''
    # Scrape every token once only
    if token_addy in SCRAPED_PRICES:
        # Read from memory
        token_price = SCRAPED_PRICES[token_addy]

        # For debugging:
        symbol = get_token_symbol(token_addy)
        print(f'Read {symbol} from memory.')

    else:
        # Scrape from web
        token_str = get_token_str(token_addy, logfile)
        token_price = get_token_price(token_str)
        SCRAPED_PRICES[token_addy] = token_price

    return token_price

# Helper function: Returns (principal amount, principal token) for a loan
def get_principal_token_tup(loan_addy):
    '''
    Returns a tuple (decoded amount, token_addy) for borrowed amount of loan
    '''
    loan_data = get_all_loans()[loan_addy]
    raw = loan_data['principal']
    token_addy = loan_data['address_lending_token']
    decoded = apply_decimals(raw, token_addy)

    # For debugging:
    #token_symbol = get_token_symbol(token_addy)

    return decoded, token_addy

# Helper function: Returns (collateral amount, collateral token) for a loan
def get_collateral_token_tup(loan_addy):
    '''
    Returns a tuple (decoded amount, token_addy) for amt collateralized of loan
    '''
    loan_data = get_all_loans()[loan_addy]
    raw = loan_data['collateral']
    token_addy = loan_data['address_collateral_token']
    decoded = apply_decimals(raw, token_addy)

    # For debugging:
    #token_symbol = get_token_symbol(token_addy)

    return decoded, token_addy

# Helper function: Returns USD amount *currently* borrowed
def get_principal_usd_val(loan_addy, logfile=None):
    amt_raw, token = get_principal_token_tup(loan_addy)
    token_price = sparse_scrape(token)
    amt_usd = amt_raw * token_price

    # For degugging:
    #symbol = get_token_symbol(token)
    #print(f'Loan {loan_addy}:')
    #print(f'Borrowed {amt_raw} {symbol} ({amt_usd} USD).')

    return amt_usd

# Helper function: Returns USD amount of collateral *currently* borrowed against
def get_collateral_usd_val(loan_addy, logfile=None):
    amt_raw, token = get_collateral_token_tup(loan_addy)
    token_price = sparse_scrape(token)
    amt_usd = amt_raw * token_price

    # For degugging:
    #symbol = get_token_symbol(token)
    #print(f'Loan {loan_addy}:')
    #print(f'Borrowed {amt_raw} {symbol} ({amt_usd} USD).')

    return amt_usd

# Helper function: Returns decoded interest rate for a loan
def get_interest_rate(loan_addy, logfile=None):
    loan_data = get_all_loans()[loan_addy]
    raw = loan_data['interest']
    decoded = raw / 100

    return decoded

# Helper function: Converts duration in timestamp (seconds) to days
def ts_duration_to_days(ts):

    if isinstance(ts, str):
        ts = int(ts)

    return ts // (24 * 3600)

# Helper function: Returns decoded loan duration (days)
def get_duration_days(loan_addy, logfile=None):
    loan_data = get_all_loans()[loan_addy]

    raw = loan_data['duration']
    decoded = ts_duration_to_days(raw)

    return decoded

# Helper function: Returns the current supply for an ERC20 token (web3 query). Nan if token without totalSupply() function.
def get_supply_for_erc20(symbol=None, address=None):
    '''
    Queries web3 for totalSupply() of token, adjusts value using the
    correct amount of decimals, returns current total supply.
    Accepts a token's symbol (i.e. 'LINK') or its contract address.
    Returns NaN if token doesn't have a totalSupply() function.
    '''
    # contract.totalSupply() does not work for these tokens
    not_possible = {'AMPL', 'AAVE', 'TUSD', 'USDC', 'USDT', 'WBTC', 'CRO'}
    addies_not_possible = {get_address_by_symbol(s) for s in not_possible}

    if symbol:
        if symbol in not_possible:
            return np.nan

        address = get_address_by_symbol(symbol)

    if address:
        if address in addies_not_possible:
            return np.nan

        checksum_address = w3.toChecksumAddress(address)
        abi_token = get_abi(checksum_address)
        contract = instantiate_contract(checksum_address, abi_token)
        raw_supply = contract.caller.totalSupply()
        decoded = apply_decimals(raw_supply, address)

        return decoded

    else:
        print('Either token adress or symbol string has to be specified.')






# Get sum of currently borrowed amounts
def get_currently_borrowed(logfile=None):
    '''
    Returns sum of borrowed amounts currently.
    TVL = sum of all collateral USD values of active loans
    '''
    active_addies = set(get_active_loans().keys())
    principal_loan_tups = [(get_principal_usd_val(loan, logfile=logfile), loan) for loan in active_addies]
    total = sum(tup[0] for tup in principal_loan_tups)

    # For debugging:
    #[print(ele) for ele in principal_loan_tups]

    return total

# Get TVL (sum of current collateral values used in loans)
def get_current_TVL(logfile=None):
    '''
    Returns current TVL.
    TVL = sum of all collateral USD values of active loans
    '''
    active_addies = set(get_active_loans().keys())
    collateral_loan_tups = [(get_collateral_usd_val(loan, logfile=logfile), loan) for loan in active_addies]
    TVL = sum(tup[0] for tup in collateral_loan_tups)

    # For debugging:
    #[print(ele) for ele in collateral_loan_tups]

    return TVL

# Get avg principal USD value of all non_defaulted loans (statusses active and repaid)
def get_avg_loan_val(logfile=None):
    '''
    Returns average loan USD value (= principal) of all loans.
    Defaulted loans with seized collateral are excluded since
    their principal value is always 0.
    '''
    non_def_addies = set(get_non_defaulted_loans().keys())
    principal_loan_tups = [(get_principal_usd_val(loan, logfile=logfile), loan) for loan in non_def_addies]
    mean = sum(tup[0] for tup in principal_loan_tups) / len(principal_loan_tups)

    # For debugging:
    #[print(ele) for ele in principal_loan_tups]

    return mean

# Get avg interest rate of all loans (active, repaid, and defaulted included)
def get_avg_interest_rate(logfile=None):
    '''
    Returns average interest rate of all loans.
    '''
    all_addies = set(get_all_loans().keys())
    interest_loan_tups = [(get_interest_rate(loan, logfile=logfile), loan) for loan in all_addies]
    mean = sum(tup[0] for tup in interest_loan_tups) / len(interest_loan_tups)

    # For debugging:
    #[print(ele) for ele in interest_loan_tups]

    return mean

# Get avg interest rate of all loans (active, repaid, and defaulted included)
def get_avg_loan_duration(logfile=None):
    '''
    Returns average duration of all loans in days.
    '''
    all_addies = set(get_all_loans().keys())
    days_loan_tups = [(get_duration_days(loan, logfile=logfile), loan) for loan in all_addies]
    mean = sum(tup[0] for tup in days_loan_tups) / len(days_loan_tups)

    # For debugging:
    #[print(ele) for ele in days_loan_tups]

    return mean

# Get YLD's current total supply. Calls contract function totalSupply()
def get_YLD_supply():
    return get_supply_for_erc20(symbol='YLD')

# Get # of minted or burned YLD since mainnet. Number positive = minted. Negative = burned.
def get_minted_burned_YLD(current_YLD_supply):
    starting_supply = 624000
    minted_burned = current_YLD_supply - starting_supply
    return minted_burned

# Export specified loan metrics for frontend use or data collection
def export_loan_metrics_dict():
    d = {}

    # Get current UTC time
    timestamp = int(time())
    parsed_ts = datetime.utcfromtimestamp(timestamp).strftime('%d %b %Y - %H:%M UTC')

    # Get data
    d['time'] = parsed_ts
    d['YLD_total_supply'] = get_YLD_supply()
    d['YLD_minted_burned'] = get_minted_burned_YLD(d['YLD_total_supply'])
    d['total_loans'] = len(get_all_loans())
    d['active_loans'] = len(get_active_loans())
    d['repaid_loans'] = len(get_repaid_loans())
    d['defauted_loans'] = len(get_defaulted_loans())
    d['percent_defauted'] = (d['defauted_loans'] / d['total_loans']) * 100
    d['total_collateral_in_use_USD'] = get_current_TVL()
    d['total_borrowed_USD'] = get_currently_borrowed()
    d['avg_loan_val_USD'] = get_avg_loan_val()
    d['avg_interest_rate'] = get_avg_interest_rate()
    d['avg_loan_duration_days'] = get_avg_loan_duration()

    # Round all numerical output to 2 decimals
    d = {k: round(v, 2) if not isinstance(v, str) else v for k, v in d.items()}

    return d




# Query web3 for ERC20 decimals. Not used currently
def get_decimals_from_web3(address, logfile=None):
    '''
    Takes ERC20 address string, gets abi, instantiates contract,
    calls contract.functions.decimals(), returns value.
    '''
    # Exclude AMPL, AAVE, TUSD, USDC, whose abis don't have a decimals() function
    excluded = {
        '0xD46bA6D942050d489DBd938a2C909A5d5039A161',
        '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9',
        '0x0000000000085d4780B73119b644AE5ecd22b376',
        '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'
        }

    if address in excluded:
        print("Can't use decimals() function for this token. Check etherscan.io manually.")

    else:
        # Query web3
        checksum_address = w3.toChecksumAddress(address)
        abi_token = get_abi(checksum_address)
        contract = instantiate_contract(checksum_address, abi_token)
        result = contract.functions.decimals().call()
        print(f'Decimals for {address}:', result)

    return result


# Scrapes coingecko and returns dict of various token metrics for 1 asset (calls findCell() for mc rank)
def get_token_metrics(token_str, logfile=None, waitAfter=3):
    '''
    Assumes a string matching an existing html child of 'coingecko.com/en/coins/', i.e. 'ethereum'.
    Returns a dict of current asset metrics as given on coingecko.com.
    '''

    # Get name of function for error messages (depends on inspect, sys)
    funcName = inspect.currentframe().f_code.co_name
    tokenDict = {}

    # Scrape coingecko content for given token
    url = 'https://www.coingecko.com/en/coins/' + token_str
    userAgent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)' + \
        ' Chrome/41.0.2228.0 Safari/537.36'
    req = urllib.request.Request(url, headers= {'User-Agent' : userAgent})
    html = urllib.request.urlopen(req)
    bs = BeautifulSoup(html.read(), 'html.parser')

    # Load necessary html tag result sets
    noWrapTags = bs.findAll('span', {'class': 'no-wrap'})  # list of html tags
    mt1Tags = bs.findAll('div', {'class': 'mt-1'})
    tableRows = bs.findAll('tr')

    # Extract metrics that need html tag key attribute or other special treatment
    try:
        manuallyScraped = ['priceBTC', 'mcBTC']
        priceBTC = float(noWrapTags[0].get('data-price-btc'))
        mcBTC = float(noWrapTags[1].get('data-price-btc'))
        circSupply = float(mt1Tags[6].get_text().split('/')[0].strip().replace(',',''))
        mcRank = findCell(tableRows, 'Rank', stripToInt=True)

        # If supply is infinite (as in ETH), replace with inf
        try:
            totalSupply = float(mt1Tags[6].get_text().split('/')[1].strip().replace(',',''))
        except ValueError:
            totalSupply = np.inf

    # Possibility: str-to-float conversion failed because it got None as argument
    except TypeError:
        print(f"""
            Coingecko seems to have restructured their website.
            One of these metrics couldn't be scraped:
            {manuallyScraped}
            Check {funcName}().
            """)

    # Extract all other metrics from text and add all to the dict
    tokenDict['priceUSD'] = clean(noWrapTags[0].get_text())
    tokenDict['priceBTC'] = priceBTC
    tokenDict['mcRank'] = mcRank
    tokenDict['mcUSD'] = clean(noWrapTags[1].get_text())
    tokenDict['mcBTC'] = mcBTC
    tokenDict['circSupply'] = circSupply
    tokenDict['totalSupply'] = totalSupply
    tokenDict['24hVol'] = clean(noWrapTags[2].get_text())
    tokenDict['24hLow'] = clean(noWrapTags[3].get_text())
    tokenDict['24hHigh'] = clean(noWrapTags[4].get_text())
    tokenDict['7dLow'] = clean(noWrapTags[10].get_text())
    tokenDict['7dHigh'] = clean(noWrapTags[11].get_text())
    tokenDict['ATH'] = clean(noWrapTags[12].get_text())
    tokenDict['ATL'] = clean(noWrapTags[13].get_text())
    tokenDict['symbol'] = noWrapTags[0].get('data-coin-symbol')

    # Option: Write to logFile if any scraped metric except 'symbol' is not a number
    if logfile:
        allowedTypes = {int, float}
        filtered = {key: value for (key, value) in tokenDict.items() if key != 'symbol'}

        for key, metric in filtered.items():
            if type(metric) not in allowedTypes:
                message = f"Check {funcName}(): Scraped value for \
                    '{tokenStr}': '{key}' is '{metric}', which is not a number."
                log(logfile, message)

    # Wait for max {waitAfter} seconds before function can be called again (= scrape in a nice way)
    sleep(random.random() * waitAfter)

    return tokenDict


# Helper function: Parses UTC time string from timestamp (int / str)
def ts_to_utc_str(ts):

    if isinstance(ts, str):
        ts = int(ts)

    utc = datetime.utcfromtimestamp(ts)
    parsed = utc.strftime('%Y %b %d %H:%M') + ' UTC'

    return parsed
