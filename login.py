from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB setup
client = MongoClient('localhost', 27017)  # Assuming MongoDB is running locally on default port
db = client['NewSummary']
collection = db['LoginData']

@app.route('/')
def index():
    return render_template('loginpage.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username exists in the database
        user = collection.find_one({'username': username})
        if user:
            # If the username exists, check if the password matches
            if user['password'] == password:
                # Password matches, redirect to success page
                return redirect(url_for('success'))
        
        # If username or password is incorrect, redirect back to login page with error message
        error_message = "Invalid username or password. Please try again."
        return render_template('loginpage.html', error_message=error_message)

@app.route('/success')
def success():
    return "Login successful!"

if __name__ == '__main__':
    app.run(debug=True)
