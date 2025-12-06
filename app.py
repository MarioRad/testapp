from flask import Flask, render_template

app = Flask(__name__)

# Routes
@app.route('/')
def index():
    print("Hello, world!")
    name = "Alice"
    age = 30
    print(f"My name is {name} and I am {age} years old.")
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)