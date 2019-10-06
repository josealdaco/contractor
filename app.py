from flask import Flask, request, render_template, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import requests

client = MongoClient()
db = client.contractor
admin_list = db.admins  # Creating JSON obj
users = db.users


app = Flask(__name__)
@app.route('/')
def home_page():
    for x in users.find():
        print(x)
    return render_template('welcome_page.html')


@app.route('/login_page', methods=['GET', 'POST'])
def login_page():
    error = request.args.get('error')
    if request.method == 'GET':
        return render_template('login_page.html', users=users.find(), error=error)
    elif request.method == 'POST':
        user = {
        "user": request.form.get('username'),
        "password": request.form.get('password'),
        "status": False
        }
        print(user)
        users.insert_one(user)
        return redirect(url_for('login_page'))


@app.route('/create_user', methods=['GET'])
def create_account():
    return render_template('create_account.html')




@app.route('/userpage', methods=['POST'])
def logging_in():
    print("Route post working")
    #try:
    #    user = users.find_one({'username': request.form.get('username')},
                            #    {'password':request.form.get('password')})
    #except Exception:
    #    print("Exception")
    username = request.form.get('username')
    password = request.form.get('password')
    user = users.find_one({'user': username, 'password': password})
    if(user is None):
        error = True
        return redirect(url_for('login_page', error=error))

    else:
        return render_template('user_welcome_page.html', user=user)






if __name__ == '__main__':
    app.run(debug=True)
