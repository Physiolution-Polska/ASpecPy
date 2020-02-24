import time
import views
from flask import Flask, jsonify
from flask import render_template, request, redirect, url_for
from flask_paginate import get_page_parameter

app = Flask(__name__)


# defaut value for measurements plots
AMOUNT = 5


def amount_check(value):
    """
    Function checks whether the value
    provided in 'POST' or 'GET'
    request is valid
    """
    global AMOUNT
    if not value:
        return AMOUNT
    else:
        value = int(value)
        if value == 0:
            value = 5
            AMOUNT = value
            return value
        elif value < 0:
            value *= -1
            AMOUNT = value
            return value
        AMOUNT = value
        return value


@app.route("/")
def index():
    return render_template('index.html', title='Plotly preview',
                           data_plot='/plot')


@app.route("/plot", methods=['GET', 'POST'])
def absorbance():
    if request.method == 'POST':
        page_amount = amount_check(request.form.get('amount'))
        return redirect(url_for('absorbance', amount=str(page_amount)))

    page_amount = amount_check(request.args.get('amount'))
    return views.absorbance(page_amount)


@app.route("/dissolvent", methods=['GET', 'POST'])
def dissolvent():
    values = {}
    """
    Page 'POST' -> 'GET' values
    that are used for plotting
    dissolvent plot
    """
    form = ['wave_length', 'b_wave_length', 'volume', 'factor']

    if request.method == 'POST':
        for key in form:
            values[key] = float(request.form.get(key))

        return redirect(url_for('dissolvent',
                                wave_length=values['wave_length'],
                                b_wave_length=values['b_wave_length'],
                                volume=values['volume'],
                                factor=values['factor']))

    for key in form:
        values[key] = request.args.get(key)

    return views.dissolvent(AMOUNT, values)


@app.route("/table")
def table():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    return views.table(page)


if __name__ == "__main__":
    app.run()
