from flask import Flask, request, render_template, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import requests

client = MongoClient()
db = client.contractor
admin_list = db.admins  # Creating JSON obj
users = db.users
items = db.items


app = Flask(__name__)
@app.route('/')
def home_page():
    """ Display home page """
    return render_template('welcome_page.html')


@app.route('/login_page', methods=['GET', 'POST'])
def login_page():
    """ If user just created a profile it will create it and redirect to login
        page. Otherwise render login_page.html"""
    error = request.args.get('error')
    if request.method == 'GET':
        return render_template('login_page.html', users=users.find(), error=error)
    elif request.method == 'POST':
        new_user = {
            'user': request.form.get('username'),
            'password': request.form.get('password'),
            'status': False,
            'cart': [],
            'admin_status': False

        }
        print("This is the desired new account:", new_user)
        user = users.find_one({'user': new_user['user']})  # Check username
        print("This is the current user we are checking:", user)
        if(user is not None):  # If the user being created exists, give en error
            error = True
            return redirect(url_for('create_account', error=error))
        else:
            #  If the desired username and password don't exist, insert
            users.insert_one(new_user)
            return redirect(url_for('login_page'))


@app.route('/create_user', methods=['GET'])
def create_account():
    """ Check if desired account wasn't created, else render
        create account html"""
    error = request.args.get('error')
    return render_template('create_account.html', error=error)


@app.route('/inventory/show')
def inventory():
    """ Shows all items in inventory """
    return render_template('inventory.html', items=items.find())


@app.route('/inventory/publish', methods=['POST'])
def publish_inventory():
    """ Approve Item and Display it """
    new = request.form.get('new')
    id = request.form.get('_id')
    item = {
        'image': request.form.get('image'),
        'name': request.form.get('name'),
        'price': request.form.get('price'),
        'description': request.form.get('description')
    }
    if new == 'True':  # If admin is making new item
        items.insert_one(item)
        return redirect(url_for('inventory'))
    elif new is None:  # If admin is editing Item
        items.update_one(
        {'_id': ObjectId(id)},
        {'$set': item})
        return redirect(url_for('inventory'))


@app.route('/inventory/form', methods=['GET', 'POST'])
def inventory_form():
    """ Check whethere we are creating a new item or Editing Item"""
    if request.method == 'GET':
        new = 'True'
        return render_template('item_form.html', item=items.find(), new=new)
    elif request.method == 'POST':
        new = 'False'
        cart_id = request.form.get('_id')
        cart = items.find_one({'_id': ObjectId(cart_id)})  # Get CART ID
        return render_template('item_form.html', new=new, item=cart)


@app.route('/delete', methods=['POST'])
def deleting_item():
    """ Deleting desired Item"""
    item_id = request.form.get('_id')
    items.delete_one({'_id': ObjectId(item_id)})
    return redirect(url_for('inventory'))


@app.route('/view/<item_id>', methods=['POST'])
def view_item(item_id):
    current_item = items.find_one({'_id': ObjectId(item_id)})
    user = users.find_one({'_id': ObjectId(request.form.get('user_id'))})
    cart_items = user['cart']
    return render_template('item_view.html', current_item=current_item, cart_items=cart_items)


@app.route('/add_cart', methods=['POST'])
def add_current_item():
    """ TODO: Create collection data for admins.
        This function will render user welcome Page"""

    item = items.find_one({'_id': ObjectId(request.form.get('_id'))})
    user = users.find_one({'_id': ObjectId(request.form.get('user_id'))})
    result = False
    for cart_items in user['cart']:
        if(cart_items['_id'] == item['_id']):
            result = True
    if(result is True):
        admins = ["jeff", "bezos"]
        cart_size = len(user['cart'])  # Figure this out later 10/8/2019 10:58am
        return render_template('user_welcome_page.html', user=user, admins=admins, items=items.find(), cart_size=cart_size)
    elif(result is False):
        user['cart'].append(item)
        user_update = {
            'user': user['user'],
            'password': user['password'],
            'status': user['status'],
            'cart': user['cart'],
            'admin_status': user['admin_status']
            }
        users.update_one({'_id': ObjectId(user['_id'])},
                        {'$set': user_update})
        admins = ["jeff", "bezos"]
        cart_size = len(user['cart'])
        return render_template('user_welcome_page.html', user=user, admins=admins, items=items.find(), cart_size=cart_size)


@app.route('/userpage', methods=['POST'])
def logging_in():
    """ Get input, if password and user match, render Account html.
        Otherwise redirect back with error message"""
    admins = ["jeff", "bezos"]
    user_name_new = request.form.get('username')
    user_password = request.form.get('password')
    for username in users.find():
        print(username)
    user = users.find_one({'user': user_name_new, 'password': user_password})

    if(user is None):
        error = True
        return redirect(url_for('login_page', error=error))

    else:
        cart_size = len(user['cart'])
        return render_template('user_welcome_page.html', user=user, admins=admins, items=items.find(), cart_size=cart_size)


if __name__ == '__main__':
    app.run(debug=True)
