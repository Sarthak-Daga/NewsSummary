from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB setup
client = MongoClient('localhost', 27017)  # Assuming MongoDB is running locally on default port
db = client['NewSummary']
collection = db['LoginData']

@app.route('/')
def index():
    return render_template('signuppage.html')

@app.route('/pageofinterests')
def pageofinterests():
    return render_template('POI.html')


@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Check if the passwords match
        if password != confirm_password:
            error_message = "Passwords do not match. Please try again."
            return render_template('signuppage.html', error_message=error_message)
        
        # Check if the username already exists
        if collection.find_one({'username': username}):
            warning_message = f"Username '{username}' already exists. Please choose a different username."
            return render_template('signuppage.html', warning_message=warning_message)
        
        # Inserting data into MongoDB
        user_data = {
            'username': username,
            'password': password
        }
        collection.insert_one(user_data)
        
        # Redirect to the page of interest after successful signup
        return redirect(url_for('pageofinterests'))


@app.route('/success')
def success():
    return "You have successfully signed up!"

if __name__ == '__main__':
    app.run(debug=True)
