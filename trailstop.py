#!/bin/env python

import sys
import argparse
import csv
import smtplib
if int(sys.version[0]) < 3:
    from urllib2 import Request, urlopen
else:
    from urllib.request import Request, urlopen


def _request(symbol, stat):
    """from https://github.com/cgoldberg/ystockquote/blob/master/ystockquote.py
    l1 = last trade price: closing price if after 4PM
    p = previous close: 2 days old if after 4.
    k = 52 wk high
    j = 52 wk low
    """
    url = 'http://finance.yahoo.com/d/quotes.csv?s=%s&f=%s' % (symbol, stat)
    req = Request(url)
    resp = urlopen(req)
    content = resp.read().decode().strip()
    return content

import re
def request(symbol, stat):
    url = 'http://www.google.com/finance/info?q=%s&' % (symbol)
    req = Request(url)
    resp = urlopen(req)
    content = resp.read().decode().strip().splitlines()
    content = float(re.findall('[\d.]+', content[6])[0])
    return content

def update(l, p):
    stop = l['stop']
    stl = stop.split('%')
    stv = float(stl[0])
    sgn = stv > 0
    stv = abs(stv)
    alert = report = ''
    low = float(l['low'])
    high = float(l['high'])
    sym = l['symbol']
    v = 0
    p = max(.001, p) # prevent div by z
    report = '%6s: %5.1f%%'

    # v value is the sort criteria in percent. 
    # Negatives are good so are listed last.
    # Positives represent losses and deserve the most attention.

    # trail value is used for consistent sorting
    if sgn:
        # stop on price increase - short position
        # Want to cover the short when the price increases from its low.
        # so measure the price against the low.
        v = (p - low)/low*100
        if v < 0:
            report += ' below its low.'
        else:
            report += ' above its low.'
    else:
        # Stop on price decrease - long position.
        # Sell when price drops below its high. 
        v = (high - p)/high*100

        if v < 0:
            report += ' above its high.'
        else:
            report += ' below its high.'

    if len(stl) > 1:
        # This is a percent trailing stop
        if sgn:
            if v >= stv-1:
                alert = '%6s: %s stop gain triggered.' % (sym, stop)
        else:
            if v >= stv:
                alert = '%6s: %s stop loss triggered.' % (sym, stop)
    else:
        # This is a hard-stop
        if sgn:
            # stop in price increase for a short position
            if p >= stv:
                alert = '%6s: has exceeded stop price of %.2f.' % (sym, stv)
        else:
            # stop on price decrease for a long position
            if p <= stv:
                alert = '%6s: has dropped below its stop price of %.2f.' % \
                        (sym, stv)

        report += ' $%.2f from hard stop of $%.2f.' % (p-stv, stv)

    report = report % (sym, v)

    l['high'] = max(high, p)
    l['low'] = min(low, p)
    return alert, report, v

def update_all(folio):
    alerts = ''
    reports = []
    d = {}
    for l in folio:
        p = float(request(l['symbol'], 'l1'))
        alert, report, sortval = update(l, p)
        if alert:
            alerts += alert + '\n'
        d[report] = -sortval
        reports.append(report)
    reports = sorted(reports, key = lambda r : d[r])
    reports = '\n'.join(reports)
    return alerts, reports

def start(f, default_stop):
    """Yahoo puts symbol as first field.  Price as second.
    Rest doesn't matter.
    """
    folio = []
    for l in csv.reader(f):
        p = max(float(l[1]), .001)
        folio.append(dict(symbol = l[0], high = p, low = p, 
                          stop = default_stop))
    return folio

def merge(master, new):
    s = set()
    for l in master:
        s.add(l['symbol'])
    for l in new:
        if l['symbol'] not in s:
            master.append(l)

def write(f, folio):
    w = csv.DictWriter(f, ['symbol', 'high', 'low', 'stop'])
    w.writeheader()
    w.writerows(folio)

def read(f):
    folio = []
    for l in csv.DictReader(f):
        folio.append(l)
    return folio

def send(serv, addr, passw, subj, text):
    server = smtplib.SMTP(serv)
    server.starttls()
    server.login(addr, passw)
    server.sendmail(addr, addr, 'Subject: %s\n\n%s' % (subj, text))
    server.quit()

parser = argparse.ArgumentParser(
        description='Initialize or update stop loss csv files and mail report.',
        )
parser.add_argument('-i', '--start', default = False,
        help = 'Use this to initialize quotes from a yahoo or empty portfolio. '
               'Anything not already in the portfolio is added to it '
               'With a default stop and last price  as high/low');
parser.add_argument('-f', '--folio', default = 'folio.csv',
        help = 'Your portfolio CSV file. Initialize this file or add to it '
               'using --start option.  Edit it by hand to maintain your stop '
               'losses')
parser.add_argument('-s', '--default_stop', default = '-20%',
        help = 'Default stop loss.  Used only with --start when initializing.')
parser.add_argument('-t', '--smtp', default = 'smtp.gmail.com:587',
        help = 'SMTP server to receive the report.')
parser.add_argument('-a', '--addr', default = False,
        help = 'The mail address that receives the report. If not provided '
               'the report goes to stdout in plain text.')
parser.add_argument('-p', '--passw', default = False,
        help = 'SMTP send password.')
args = parser.parse_args()

try:
    f = open(args.folio)
    folio = read(f)
    f.close()
except IOError:
    folio = []
    if args.start == False:
        # when initializing from a yahoo like portfolio folio.csv is not
        # necessary
        sys.stderr.write('Unable to open [%s] for reading.\n' % args.folio)
        sys.exit(1)

if args.start:
    f = open(args.start)
    new = start(f, args.default_stop)
    merge(folio, new)
    f.close()

alerts, reports = update_all(folio)

f = open(args.folio, 'w')
write(f, folio)
f.close()

report = 'ALERTS:\n%s\n\nREPORTS:\n%s\n' % (alerts or 'NONE', reports)

if args.addr and args.passw:
    subj = '%sTrail Stop Portfolio Report' % (alerts and '[ALERTS]' or '')
    send(args.smtp, args.addr, args.passw, subj, report)
else:
    sys.stdout.write(report)

   

