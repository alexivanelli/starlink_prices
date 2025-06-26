import requests
import pandas as pd
import json
import datetime

class StarlinkDataHandler:

    @staticmethod
    def get_starlink_data():
        url = "https://api.starlink.com/public-files/landing-prices.json"
        response = requests.get(url)
        data = response.json()
        return data

    @staticmethod
    def find_roam_data(data):
        roam_data = None

        # find roam data
        for d in data:
            if d['invitationType'] == '8':
                roam_data = d
                break

        result = []
        for d in roam_data['countries']:
            d_result = {
                'region_code': d['regionCode'],
                'currency': d['currencyCode'],
            }

            for s in d['subscriptions']:
                d_result[s['description']] = s['price']

            result.append(d_result)

        return result

    @staticmethod
    def get_currency_rates():
        url = "https://v6.exchangerate-api.com/v6/afc88a9bd5c0a3964887c600/latest/USD"
        response = requests.get(url)
        data = response.json()
        return data['conversion_rates']

    @staticmethod
    def run():
        # get starlink data
        data = StarlinkDataHandler.get_starlink_data()
        data = StarlinkDataHandler.find_roam_data(data)
        df = pd.DataFrame(data)

        df = df.rename(columns={'Roam - Unlimited': 'roam_unlimited'})
        df = df[['region_code', 'currency', 'roam_unlimited']]
        df = df.dropna(subset=['roam_unlimited'])

        # get currency data
        data_currencies = StarlinkDataHandler.get_currency_rates()
        df_currencies = pd.DataFrame([data_currencies.keys(), data_currencies.values()]).T
        df_currencies.columns = ['currency', 'rate']

        df = pd.merge(df, df_currencies, on='currency', how='left')

        # get country names
        df_region = pd.read_json('all.json')
        df_region = df_region[['name', 'alpha-2', 'region']]
        df_region.columns = ['country', 'region_code', 'region']
        df = pd.merge(df, df_region, on='region_code', how='left')
        df['roam_unlimited_usd'] = df['roam_unlimited'] / df['rate']
        df = df[['country', 'region', 'currency', 'roam_unlimited', 'roam_unlimited_usd']]

        # Create the output structure
        output = {
            "date": datetime.datetime.now().strftime('%Y%m%d'),
            "data": json.loads(df.to_json())
        }
        
        # Save to JSON file
        with open("prices.json", "w") as f:
            json.dump(output, f, indent=2)


if __name__ == '__main__':
    data = StarlinkDataHandler.run()
