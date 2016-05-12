from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    # return 'Hello World!'
    return render_template("hello_world.html")

if __name__ == '__main__':
    app.run()