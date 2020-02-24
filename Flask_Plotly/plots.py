import pandas
import numpy as np
import plotly.graph_objs as go
from signal import signal
from datetime import datetime
from plotly.offline import plot


DATA = None
LAMBDA = None


def absorbance(amount):
    global DATA, LAMBDA
    # getting last 'amount' measurements
    amount *= -1

    DATA = pandas.read_csv('data.csv')
    LAMBDA = DATA.iloc[:, :1]
    DATA = DATA.iloc[:, amount:]

    plots = []
    plot_name = ''
    for data_header in DATA.columns[amount:]:
        try:
            plot_name = datetime.fromtimestamp(int(data_header))
            plots.append(
                    go.Scatter(
                        x=LAMBDA['lambda'],
                        y=DATA[data_header],
                        name=str(plot_name)
                        )
                    )
        # except lambda value
        # if all the values are in DATA frame
        except ValueError:
            pass

    # for title purpose only
    amount *= -1

    layout = go.Layout(
            title='Absorbance: last ' + message(amount, len(plots)),
            showlegend=True,
            plot_bgcolor='#E6F3FF',
            xaxis=go.layout.XAxis(
                title=go.layout.xaxis.Title(
                    text="Wave length [nm]",
                    font=dict(
                        family="Courier New, monospace",
                        size=18,
                        color="#7f7f7f"
                        )
                    )
                ),
            yaxis=go.layout.YAxis(
                title=go.layout.yaxis.Title(
                    text="Absorbance [AU]",
                    font=dict(
                        family="Courier New, monospace",
                        size=18,
                        color="#7f7f7f"
                        )
                    )
                )
            )

    figure = go.Figure(data=plots, layout=layout)
    config = {'responsive': True}
    plot_div = plot(figure, output_type='div', config=config)
    return plot_div


def dissolvent(amount, values, data):
    global DATA, LAMBDA
    # retrieve index position of 'wave_length'
    # in order to get all 'absorbance' and
    # background values correspondent to 'wave_length'
    data._time = np.array([])

    _index = np.where(LAMBDA.values == float(values['wave_length']))[0][0]
    _b_index = np.where(LAMBDA.values == float(values['b_wave_length']))[0][0]

    data._absorbance = DATA.iloc[[_index]].values[0]
    data._correction = DATA.iloc[[_b_index]].values[0]

    data._concentration = np.multiply(np.subtract(data._absorbance,
                                      data._correction),
                                      float(values['factor']))

    data._dissolved = np.multiply(data._concentration,
                                  float(values['volume']))

    # timeline
    for time in DATA.columns:
        try:
            data._time = np.append(data._time,
                                   datetime.fromtimestamp(int(time)))
        except ValueError:
            pass

    for i in range(1, data._time.size):
        data._time[i] = (data._time[i] - data._time[0]).total_seconds() / 60.0

    data._time[0] = 0

    plot_dissolved = go.Scatter(
            x=data._time,
            y=data._dissolved,
            )

    layout = go.Layout(
            title='Dissolvent: last ' + message(amount, data._time.size),
            showlegend=False,
            plot_bgcolor='#E6F3FF',
            xaxis=go.layout.XAxis(
                title=go.layout.xaxis.Title(
                    text="Time [s]",
                    font=dict(
                        family="Courier New, monospace",
                        size=18,
                        color="#7f7f7f"
                        )
                    )
                ),
            yaxis=go.layout.YAxis(
                title=go.layout.yaxis.Title(
                    text="Drug dissolved [mg]",
                    font=dict(
                        family="Courier New, monospace",
                        size=18,
                        color="#7f7f7f"
                        )
                    )
                )
            )

    figure = go.Figure(data=plot_dissolved, layout=layout)
    config = {'responsive': True}
    data._plot = plot(figure, output_type='div', config=config)
    return True


def message(amount, size):
    if amount > size:
        amount = size

    if amount == 1:
        return str(amount) + ' measurement'
    else:
        return str(amount) + ' measurements'

