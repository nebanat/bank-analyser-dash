from datetime import datetime, timedelta
import json
import pandas as pd


def get_income_expense(trans_df):
    trans_df['month_year'] = trans_df['trans_date'].dt.to_period('M')

    income_expense_df = trans_df.groupby(['month_year']).sum().reset_index('month_year')

    income_expense_df = income_expense_df.drop(columns=['balance'])

    income_expense_df['credit'] = pd.to_numeric(income_expense_df['credit'], errors='coerce')
    income_expense_df['total_credit'] = income_expense_df['credit'].apply(lambda x: "₦{:,.2f}".format((x)))
    income_expense_df['debit'] = pd.to_numeric(income_expense_df['debit'], errors='coerce')
    income_expense_df['total_debit'] = income_expense_df['debit'].apply(lambda x: "₦{:,.2f}".format(x))

    return income_expense_df


def get_transactions(start_date, end_date):
    with open('response_2.json', 'r') as f:
        resp = json.load(f)

    df = pd.DataFrame(resp.get('transactions'))

    df['value_date'] = pd.to_datetime(df['value_date'], errors='coerce')
    df['trans_date'] = pd.to_datetime(df['trans_date'], errors='coerce')
    df['value_date'] = df['value_date'].dt.date
    df['trans_date'] = df['trans_date'].dt.date

    start = start_date or (datetime.date(datetime.now()) - timedelta(days=2*365))
    end = end_date or datetime.date(datetime.now())

    df = df[(df['trans_date'] >= start) & (df['trans_date'] <= end)]
    start_str = start.strftime('%Y-%m')
    end_str = end.strftime('%Y-%m')

    overdraft_df = df[df['balance'] < 0]
    overdraft_df = overdraft_df.drop(columns=['month_year'])

    i_expense_df = pd.DataFrame(resp.get('income_expense'))
    i_expense_df = i_expense_df.drop(columns=['balance'])
    i_expense_df = i_expense_df[(i_expense_df['month_year'] >= start_str) & (i_expense_df['month_year'] <= end_str)]

    i_expense_df['credit'] = pd.to_numeric(i_expense_df['credit'], errors='coerce')
    i_expense_df['total_credit'] = i_expense_df['credit'].apply(lambda x: "₦{:,.2f}".format((x)))
    i_expense_df['debit'] = pd.to_numeric(i_expense_df['debit'], errors='coerce')
    i_expense_df['total_debit'] = i_expense_df['debit'].apply(lambda x: "₦{:,.2f}".format(x))

    outlier_df = pd.DataFrame(resp.get('outlier_transactions'))
    outlier_df = outlier_df.drop(columns=['month_year'])
    outlier_df['value_date'] = pd.to_datetime(outlier_df['value_date'], errors='coerce')
    outlier_df['trans_date'] = pd.to_datetime(outlier_df['trans_date'], errors='coerce')
    outlier_df['value_date'] = outlier_df['value_date'].dt.date
    outlier_df['trans_date'] = outlier_df['trans_date'].dt.date
    outlier_df = outlier_df[(outlier_df['trans_date'] >= start) & (outlier_df['trans_date'] <= end)]

    outlier_df['credit'] = pd.to_numeric(outlier_df['credit'], errors='coerce')
    outlier_df['balance'] = pd.to_numeric(outlier_df['balance'], errors='coerce')
    outlier_df['credit'] = outlier_df['credit'].apply(lambda x: "₦{:,.2f}".format(x))
    outlier_df['balance'] = outlier_df['balance'].apply(lambda x: "₦{:,.2f}".format(x))

    df = df.drop(columns=['month_year'])

    df['credit'] = pd.to_numeric(df['credit'], errors='coerce')
    df['debit'] = pd.to_numeric(df['debit'], errors='coerce')
    df['balance'] = pd.to_numeric(df['balance'], errors='coerce')

    df['Credit'] = df['credit'].apply(lambda x: "₦{:,.2f}".format(x))
    df['Debit'] = df['debit'].apply(lambda x: "₦{:,.2f}".format(x))
    df['Balance'] = df['balance'].apply(lambda x: "₦{:,.2f}".format(x))

    return (df.sort_values(by=['trans_date'], ascending=True),
            i_expense_df.sort_values(by=['month_year'], ascending=True),
            overdraft_df.sort_values(by=['trans_date'], ascending=True),
            outlier_df.sort_values(by=['trans_date'], ascending=True))

