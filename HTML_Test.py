import pandas as pd
from bs4 import BeautifulSoup
import requests
import numpy as np

is_link = 'https://finance.yahoo.com/quote/PNL.AS/financials?p=PNL.AS'
bs_link = 'https://finance.yahoo.com/quote/AAPL/balance-sheet?p=AAPL'
cf_link = 'https://finance.yahoo.com/quote/AAPL/cash-flow?p=AAPL'


def scraper_to_statement(link):
    headers = []
    temp_list = []
    final = []
    index = 0


    # pull data from link
    page_response = requests.get(link, timeout=1000)
    # structure raw data for parsing
    page_content = BeautifulSoup(page_response.content, features="lxml")
    # filter for items we want
    features = page_content.find_all('div', class_='D(tbr)')

    # create headers
    for item in features[0].find_all('div', class_='D(ib)'):
        headers.append(item.text)

    # statement contents
    while index <= len(features) - 1:
        # filter for each line of the statement
        temp = features[index].find_all('div', class_='D(tbc)')
        for line in temp:
            # each item adding to a temporary list
            temp_list.append(line.text)
        # temp_list added to final list
        final.append(temp_list)
        # clear temp_list
        temp_list = []
        index += 1

    df = pd.DataFrame(final[1:])
    df.columns = headers

    def convert_to_numeric(column):

        first_col = [i.replace(',', '') for i in column]
        second_col = [i.replace('-', '') for i in first_col]
        final_col = pd.to_numeric(second_col, downcast='float', errors='coerce')
        final_col = final_col * 1000

        return final_col

    for column in headers[1:]:
        df[column] = convert_to_numeric(df[column])

    final_df = df
    #final_df.iloc[15:17, 2:6] = final_df.iloc[15:17, 2:6] / 1000 werkt helaas niet verandert per aandeel de rows

    # eigenlijk moet je final_df df_list komt later nog
    final_df.set_index('Breakdown', inplace=True)
    df2_transposed = final_df.T
    df2_transposed = df2_transposed.drop(df2_transposed.index[:1]) # drop 1e rij is TTM
    df2_transposed[['Basic EPS', 'Diluted EPS']] = df2_transposed[['Basic EPS', 'Diluted EPS']] / 1000

    return print(df2_transposed.to_string())


financials = scraper_to_statement(is_link)


