import plots
from flask import render_template
from flask_paginate import Pagination
from dissolvent_page_data import Page_data

DATA = None

def absorbance(amount):
    return render_template('plot.html', index='/',
                           plot=plots.absorbance(amount))


def dissolvent(amount, values):
    global DATA
    DATA = Page_data()
    plots.dissolvent(amount, values, DATA)
    DATA.round()
    return render_template('dissolvent.html', index='/',
                           plot=DATA._plot, data=DATA)

def table(page):
    global DATA
    paginator = Pagination(page=page, total=DATA._time.size,
                           per_page=2, css_framework='bootstrap3')

    startIndex = page - 1
    stopIndex = startIndex + paginator.per_page
    if stopIndex > DATA._time.size:
        stopIndex = DATA._time.size
    
    return render_template('table.html', data=DATA,
                           pagination=paginator, start=startIndex,
                           stop=stopIndex)
