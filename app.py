from flask import Flask, request, render_template, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

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


@app.route('/login_page', methods=['GET'])
def login_page():
    return render_template('login_page.html', users=users.find())


@app.route('/userpage', methods=['POST'])
def logging_in():
    print("Route post working")
    #try:
    #    user = users.find_one({'username': request.form.get('username')},
                            #    {'password':request.form.get('password')})
    #except Exception:
    #    print("Exception")
    #user = users.find()
    return redirect(url_for('user_page'))


if __name__ == '__main__':
    app.run(debug=True)
