# 'status' flag for loans:              0 = active, 1 = repaid, 2 = defaulted
# 'status' flag for offers/requests:    0 = pending, 1 = accepted, 2 = canceled

# TODO: Store ABIs here

# Map keys to data types for converion by convert_values_to_human_readable()
type_map = {
    'collateral_balance': 'uint256',
    'ts_due': 'ts',
    'is_defaulted': 'bool',
    'address_lender': 'address',
    'address_borrower': 'address',
    'address_lending_token': 'address',
    'address_collateral_token': 'address',
    'principal': 'uint256',
    'interest': 'uint256',
    'duration': 'ts',
    'collateral': 'uint256',
    'loan_status': 'int',
    'ts_start': 'ts',
    'ts_repaid': 'ts',
    'liquidatable_t_allowance': 'ts'
    }

# Map linking each supported token to some data needed frequently

token_map = {
    '0xADE00C28244d5CE17D72E40330B1c318cD12B7c3':
        {'symbol': 'ADX', 'coingecko_str': 'adex', 'decimals': 18},
    '0xfF20817765cB7f73d4bde2e66e067E58D11095C2':
        {'symbol': 'AMP', 'coingecko_str': 'amp', 'decimals': 18},
    '0xDcB01cc464238396E213a6fDd933E36796eAfF9f':
        {'symbol': 'YLD', 'coingecko_str': 'yield', 'decimals': 18},
    '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2':
        {'symbol': 'WETH', 'coingecko_str': 'weth', 'decimals': 18},
    '0x6B175474E89094C44Da98b954EedeAC495271d0F':
        {'symbol': 'DAI', 'coingecko_str': 'dai', 'decimals': 18},
    '0x111111111117dC0aa78b770fA6A738034120C302':
        {'symbol': '1INCH', 'coingecko_str': '1inch', 'decimals': 18},
    '0xD46bA6D942050d489DBd938a2C909A5d5039A161':
        {'symbol': 'AMPL','coingecko_str': 'ampleforth', 'decimals': 9},
    '0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C':
        {'symbol': 'BNT', 'coingecko_str': 'bancor-network', 'decimals': 18},
    '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9':
        {'symbol': 'AAVE', 'coingecko_str': 'aave', 'decimals': 18},
    '0xa117000000f279D81A1D3cc75430fAA017FA5A2e':
        {'symbol': 'ANT', 'coingecko_str': 'aragon', 'decimals': 18},
    '0xba100000625a3754423978a60c9317c58a424e3D':
        {'symbol': 'BAL', 'coingecko_str': 'balancer', 'decimals': 18},
    '0xBA11D00c5f74255f56a5E366F4F77f5A186d7f55':
        {'symbol': 'BAND', 'coingecko_str': 'band-protocol', 'decimals': 18},
    '0x0D8775F648430679A709E98d2b0Cb6250d2887EF':
        {'symbol': 'BAT', 'coingecko_str': 'basic-attention-token', 'decimals': 18},
    '0xc00e94Cb662C3520282E6f5717214004A7f26888':
        {'symbol': 'COMP', 'coingecko_str': 'compound', 'decimals': 18},
    '0x2ba592F78dB6436527729929AAf6c908497cB200':
        {'symbol': 'CREAM', 'coingecko_str': 'cream', 'decimals': 18},
    '0xA0b73E1Ff0B80914AB6fe0444E65848C4C34450b':
        {'symbol': 'CRO', 'coingecko_str': 'crypto-com-coin', 'decimals': 8},
    '0xD533a949740bb3306d119CC777fa900bA034cd52':
        {'symbol': 'CRV', 'coingecko_str': 'curve-dao-token', 'decimals': 18},
    '0xF629cBd94d3791C9250152BD8dfBDF380E2a3B9c':
        {'symbol': 'ENJ', 'coingecko_str': 'enjin-coin', 'decimals': 18},
    '0xc944E90C64B2c07662A292be6244BDf05Cda44a7':
        {'symbol': 'GRT', 'coingecko_str': 'the-graph', 'decimals': 18},
    '0xdd974D5C2e2928deA5F71b9825b8b646686BD200':
        {'symbol': 'KNC', 'coingecko_str': 'kyber-network', 'decimals': 18},
    '0x1cEB5cB57C4D4E2b2433641b95Dd330A33185A44':
        {'symbol': 'KP3R', 'coingecko_str': 'keep3rv1', 'decimals': 18},
    '0x514910771AF9Ca656af840dff83E8264EcF986CA':
        {'symbol': 'LINK', 'coingecko_str': 'chainlink', 'decimals': 18},
    '0xBBbbCA6A901c926F240b89EacB641d8Aec7AEafD':
        {'symbol': 'LRC', 'coingecko_str': 'loopring', 'decimals': 18},
    '0x0F5D2fB29fb7d3CFeE444a200298f468908cC942':
        {'symbol': 'MANA', 'coingecko_str': 'decentraland', 'decimals': 18},
    '0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2':
        {'symbol': 'MKR', 'coingecko_str': 'maker', 'decimals': 18},
    '0x408e41876cCCDC0F92210600ef50372656052a38':
        {'symbol': 'REN', 'coingecko_str': 'republic-protocol', 'decimals': 18},
    '0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F':
        {'symbol': 'SNX', 'coingecko_str': 'synthetix-network-token', 'decimals': 18},
    '0x57Ab1ec28D129707052df4dF418D58a2D46d5f51':
        {'symbol': 'SUSD', 'coingecko_str': 'susd', 'decimals': 18},
    '0x6B3595068778DD592e39A122f4f5a5cF09C90fE2':
        {'symbol': 'SUSHI', 'coingecko_str': 'sushi', 'decimals': 18},
    '0x0000000000085d4780B73119b644AE5ecd22b376':
        {'symbol': 'TUSD', 'coingecko_str': 'true-usd', 'decimals': 18},
    '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984':
        {'symbol': 'UNI', 'coingecko_str': 'uniswap', 'decimals': 18},
    '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48':
        {'symbol': 'USDC', 'coingecko_str': 'usd-coin', 'decimals': 6},
    '0xdAC17F958D2ee523a2206206994597C13D831ec7':
        {'symbol': 'USDT', 'coingecko_str': 'tether', 'decimals': 6},
    '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599':
        {'symbol': 'WBTC', 'coingecko_str': 'wrapped-bitcoin', 'decimals': 8},
    '0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e':
        {'symbol': 'YFI', 'coingecko_str': 'yearn-finance', 'decimals': 18},
    '0xE41d2489571d322189246DaFA5ebDe1F4699F498':
        {'symbol': 'ZRX', 'coingecko_str': '0x', 'decimals': 18}}
