import pandas as pd


def covid_data_today(df, df_name):
    df = df.tail(1)
    df = df.set_index('date').transpose().rename_axis('', axis=1)
    df.columns = [df_name]
    df.index = [i[:2] for i in df.index]
    return df


def concat_data_today():
    confirmed = pd.read_csv('data/confirmed.csv')
    death = pd.read_csv('data/death.csv')
    recovered = pd.read_csv('data/recovered.csv')

    confirmed_t = covid_data_today(confirmed, 'confirmed')
    death_t = covid_data_today(death, 'death')
    recovered_t = covid_data_today(recovered, 'recovered')

    covid_today = pd.concat([confirmed_t, death_t, recovered_t], axis=1)
    covid_today = covid_today.rename_axis('country_code').reset_index()

    covid_today['active'] = covid_today['confirmed'] - covid_today['death'] - covid_today['recovered']

    return covid_today


# new_df = concat_data_today()
