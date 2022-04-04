from datetime import datetime, date
import dash
import dash_bootstrap_components as dbc
from dash import html, dash_table, dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import api
from helpers import human_format

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server


def header(name):
    title = html.H2(name, style={"margin-top": 5})

    return dbc.Row([dbc.Col(title, md=9)])


# Card components
total_cards = [
    dbc.Card(
        [
            html.H2(className="card-title", id='total-credit'),
            html.P("Total Credit Amount", className="card-text"),
        ],
        body=True,
        color="green",
        inverse=True,
    ),
    dbc.Card(
        [
            html.H2(className="card-title", id='average-credit'),
            html.P("Average Monthly Credit", className="card-text"),
        ],
        body=True,
        color="green",
        inverse=True,
    ),
    dbc.Card(
        [
            html.H2(className="card-title", id="total-debit"),
            html.P("Total Debit Amount", className="card-text"),
        ],
        body=True,
        color="brown",
        inverse=True,
    ),
    dbc.Card(
        [
            html.H2(className="card-title", id="average-debit"),
            html.P("Average Monthly Debit", className="card-text"),
        ],
        body=True,
        color="brown",
        inverse=True,
    ),
    dbc.Card(
        [
            html.H2(className='card-title', id='total-debit-credit-no'),
            html.P("Credit No / Debit No", className="card-text"),
        ],
        body=True,
        color="primary",
        inverse=True,
    ),
]


app.layout = dbc.Container(
    [
        header("Bank statement analyser - (MICANS Hospital Ltd)"),
        html.Hr(),
        html.Br(),
        html.H4(id='filter-details'),
        html.Br(),
        html.Div([
            dcc.DatePickerRange(
                id='my-date-picker-range',
                min_date_allowed=date(1995, 8, 5),
                max_date_allowed=datetime.date(datetime.now()),
                initial_visible_month=datetime.date(datetime.now()),
                end_date=datetime.date(datetime.now())
            )
        ]),
        html.Div(id='start-date'),
        html.Div(id='end-date'),
        html.Br(),
        dbc.Row([dbc.Col(card) for card in total_cards]),
        html.Br(),
        dcc.Graph(id='bar-plot'),
        html.H4("Credit/Debit M-o-M "),
        html.Hr(),
        html.Div(id='i-expense-table'),
        html.Br(),
        html.H4("Suspected Transactions"),
        html.Hr(),
        html.Div(id='outlier-table'),
        html.Br(),
        html.H4("Overdraft periods"),
        html.Hr(),
        html.Div(id='overdraft-table'),
        html.Br(),
        html.H4("All Bank Transactions"),
        html.Hr(),
        html.Div(id='transactions-table'),
    ],
    fluid=False,
)


def plot_month_debit_credit(expense_df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[str(date_) for date_ in expense_df['month_year'].to_list()],
                             y=expense_df['credit'], line=dict(width=6), name='Monthly credit'))

    fig.add_trace(go.Scatter(x=[str(date_) for date_ in expense_df['month_year'].to_list()],
                             y=expense_df['debit'], line=dict(color='firebrick', width=4),
                             name='Monthly debit'))

    fig.update_layout(title='Credit/Debit M-o-M',
                      xaxis_title='Dates',
                      yaxis_title='Amount')

    return fig


def display_table_data(df, column_list):
    style_cell = {'border': '1px solid grey', 'textAlign': 'left'}
    style_header = {'border': '1px solid black', 'textAlign': 'left',
                    'color': 'black', 'fontWeight': 'bold', 'backgroundColor': 'rgb(210, 210, 210)'}

    return dash_table.DataTable(df.to_dict('records'),
                                [{"name": i, "id": i} for i in df[column_list].columns],
                                filter_action="native",
                                sort_action="native",
                                sort_mode="multi",
                                column_selectable="single",
                                style_cell=style_cell,
                                style_header=style_header,
                                style_table={'height': '300px', 'overflowX': 'scroll', 'overflowY': 'auto'})


@app.callback(
    Output('filter-details', 'children'),
    Output('total-credit', 'children'),
    Output('average-credit', 'children'),
    Output('total-debit', 'children'),
    Output('average-debit', 'children'),
    Output('total-debit-credit-no', 'children'),
    Output('bar-plot', 'figure'),
    Output('i-expense-table', 'children'),
    Output('outlier-table', 'children'),
    Output('overdraft-table', 'children'),
    Output('transactions-table', 'children'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'))
def update_output(start_date, end_date):
    i_expense_columns = ['month_year', 'total_credit', 'total_debit']
    d_trans_columns = ['trans_date', 'value_date', 'narration', 'Credit', 'Debit', 'Balance']
    start_date_string = ''
    end_date_string = ''
    start_date_object = None
    end_date_object = None

    if start_date is not None:
        start_date_object = date.fromisoformat(start_date)
        start_date_string = start_date_object.strftime('%B %d, %Y')

    if end_date is not None:
        end_date_object = date.fromisoformat(end_date)
        end_date_string = end_date_object.strftime('%B %d, %Y')

    df, i_expense_df, overdraft_df, outlier_df = api.get_transactions(start_date_object, end_date_object)
    debit_credit_str = f"{df[df['credit'] != 0].shape[0]}/{df[df['debit'] != 0].shape[0]}"
    average_monthly_credit = human_format(i_expense_df['credit'].mean()) if not i_expense_df[
        'credit'].empty else '₦0.00'
    average_monthly_debit = human_format(i_expense_df['debit'].mean()) if not i_expense_df[
        'debit'].empty else '₦0.00'

    month_debit_credit_fig = plot_month_debit_credit(i_expense_df)

    i_expense_table = display_table_data(i_expense_df, i_expense_columns)
    outlier_table = display_table_data(outlier_df, outlier_df.columns)
    overdraft_table = display_table_data(overdraft_df, overdraft_df.columns)
    transactions_table = display_table_data(df, df[d_trans_columns].columns)

    filter_str = f"{start_date_string} - {end_date_string}"

    return (
        filter_str,
        human_format(df['credit'].sum()),
        average_monthly_credit,
        human_format(df['debit'].sum()),
        average_monthly_debit,
        debit_credit_str,
        month_debit_credit_fig,
        i_expense_table,
        outlier_table,
        overdraft_table,
        transactions_table,
    )


if __name__ == '__main__':
    app.run_server(debug=True)
