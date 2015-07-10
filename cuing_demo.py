import random
from uuid import uuid4
from flask import (
  Flask,
  session,
  request,
  redirect,
  url_for,
  render_template,
  render_template_string
)
app = Flask(__name__)

app.config.update(dict(
  DEBUG=True,
  SECRET_KEY='3.14159', # shhhhh
))

from planout.experiment import SimpleExperiment
from planout.ops.random import *

class CuingExperiment(SimpleExperiment):
  def setup(self):
    self.set_log_file('cuing_webapp.log')

  def assign(self, params, userid):
    params.use_round_number = BernoulliTrial(p=0.5, unit=userid)
    if params.use_round_number:
      params.v1_count = RandomInteger(min=1, max=4, unit=userid)
      params.v2_count = RandomInteger(min=2, max=5, unit=userid)
      params.v3_count = RandomInteger(min=4, max=8, unit=userid)
    else:
      params.v1_count = 0
      params.v2_count = 0
      params.v3_count = 0

def count_format(number):
  return 10**number

@app.route('/')
def main():
    # if no userid is defined make one up
    if 'userid' not in session:
        session['userid'] = str(uuid4())

    cuing_exp = CuingExperiment(userid=session['userid'])
    v1 = cuing_exp.get('v1_count')
    v2 = cuing_exp.get('v2_count')
    v3 = cuing_exp.get('v3_count')

    return render_template("index.html", v1_count = count_format(v1), v2_count = count_format(v2), v3_count = count_format(v3))

@app.route('/reset')
def reset():
  session.clear()
  return redirect(url_for('main'))

@app.route('/submit')
def vote():
  v1_choice = request.args.get('video1')
  v2_choice = request.args.get('video2')
  v3_choice = request.args.get('video3')
  try:

    cuing_exp = CuingExperiment(userid=session['userid'])
    cuing_exp.log_event('vote', {'v1_choice': v1_choice, 'v2_choice': v2_choice, 'v3_choice': v3_choice})

    return render_template_string("""
      <html>
        <head>
          <title>Thank you</title>
        </head>
        <body>
          <p>Thank you for your selection</p>
          <p><a href="/">Back</a></p>
        </body>
      </html>
      """)
  except ValueError:
    return render_template_string("""
      <html>
        <head>
          <title>Oops!</title>
        </head>
        <body>
          <p>Something went wrong</p>
          <p><a href="/">Back</a></p>
        </body>
      </html>
      """)


if __name__ == '__main__':
    app.run()
