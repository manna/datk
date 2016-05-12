from flask import Flask, render_template, request, abort, redirect, url_for
from core.algs import *
from core.networks import *
import plotly.plotly as py

app = Flask(__name__)
n = Bidirectional_Ring(6)
a = LCR(n)
b = SynchBFS(n)
L = len(n.snapshots)
currentIndex = 1
py.sign_in('abiswas', 'a6kpv86uv1')
def update_plotly_plot(i):
	py.iplot(n.snapshots[i].draw() ,filename="mathakharap")

update_plotly_plot(currentIndex)

@app.route('/', methods = ['GET','POST'])
def network_page():
	if request.method == 'POST':
		if request.form['submit'] == 'forward':
			if currentIndex < L-1:
				currentIndex += 1
				update_plotly_plot(currentIndex)
				redirect(url_for('/'))

		elif request.form['submit'] == 'backward':
			if currentIndex > 1:
				currentIndex -= 1
				update_plotly_plot(currentIndex)
				redirect(url_for('/'))

		else:
			pass # unknown

	# elif request.method == 'GET':
	return render_template("network_page.html")


if __name__ == '__main__':
	app.run()