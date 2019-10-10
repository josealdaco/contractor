from flask import Flask, request, render_template, redirect, url_for, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/contractor')
client = MongoClient(host=f'{host}?retryWrites=false')
db = client.get_default_database()
admin_list = db.admins  # Creating JSON obj
users = db.users
items = db.items
seller_items = db.seller_items
"""
    BLOCKER: CANNOT CHANGE URL BECAUSE THE RENDER IS DONE WITH POST,
    REDIRECT_URL CAN ONLY REDIRECT TO HTML THAT WAS RENDERED WITH 'GET'
"""

app = Flask(__name__)
@app.route('/')
def home_page():
    """ Display home page """
    return render_template('welcome_page.html')


def ip_adress():
    return jsonify({'ip': request.remote_addr}), 200


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
            'status': False,  # decides if user is offline
            'cart': [],
            'personal_item': [],
            'admin_status': False,
            'ip_address': ip_adress()

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
    new_approval = request.form.get('approval')
    seller = users.find_one({'_id': ObjectId(request.form.get('seller'))})
    id = request.form.get('_id')
    if seller is None:
        item = {
            'seller': 'Amazonia',
            'image': request.form.get('image'),
            'name': request.form.get('name'),
            'price': request.form.get('price'),
            'description': request.form.get('description')
        }
    else:
        item = {
            'seller': seller['user'],
            'image': request.form.get('image'),
            'name': request.form.get('name'),
            'price': request.form.get('price'),
            'description': request.form.get('description'),
            'seller_ip': seller['ip_address']
            }
    if new == 'True' or new_approval == 'True':  # If admin is making new item
        items.insert_one(item)
        return redirect(url_for('inventory'))
    elif new is None:  # If admin is editing Item
        items.update_one(
        {'_id': ObjectId(id)},
        {'$set': item})
        return redirect(url_for('inventory'))


@app.route('/show/cart', methods=['POST'])
def show_cart():
    """ SHOWS ALL THE ITEMS IN THE CART
        We will also display non duplicate and
        amound present"""
    # Variables
    user = users.find_one({'_id': ObjectId(request.form.get('user_id'))})
    print("This is the user that wants to view cart:", user)
    cart = user['cart']
    duplicate_list = []
    cart_clone = cart
    index_for_duplicate = 0
    first = False
    total_amount = 0
    for items in cart:
        for item_2 in cart_clone:
            if items['_id'] == item_2['_id']:
                if first is True:
                    print("FIRST HAS BECOME TRUE")
                    if items['_id'] != duplicate_list[index_for_duplicate]['_id']:
                        duplicate_list.append(items)
                        index_for_duplicate += 1
                elif index_for_duplicate == 0 and first is False:
                    duplicate_list.append(items)
                    first = True
    duplicate_amount = []
    for x in duplicate_list:
        duplicate_amount.append(0)
    index_for_total = 0
    max = 0
    second = False
    print("Length of cart:", len(duplicate_list))
    print("This is the ids of clones:", duplicate_list)
    if len(duplicate_list) != 0:
        for duplicate in duplicate_list:
            print("The ones we are checking:", duplicate)
            for item in cart:
                if duplicate['_id'] == item['_id']:
                    total_amount += 1
                max += 1
                print(max)
            if max == len(cart):
                print("This is the total amount:", total_amount)
                if second is True:
                    index_for_total += 1
                print("This is the index:", index_for_total)
                duplicate_amount[index_for_total] = {
                    'item': duplicate,
                    'amount': total_amount
                }
                total_amount = 0
                max = 0
                second = True
    print("This is the list of amount per clone:", duplicate_amount)
    # Finding total cost for all items
    total_price = 0
    for item in duplicate_amount:
        total_price += float(item['item']['price'])
        total_price *= float(item['amount'])

    return render_template('show_cart.html', user=user, cart=duplicate_amount, total_price=round(total_price))


@app.route('/show_users', methods=['GET'])
def show_users():
    """ SHOW ALL USERS IN DATABASE"""
    return render_template('show_users.html', users=users.find())


@app.route('/delete_all', methods=['POST'])
def delete_all():
    db.users.drop()  # Delete all users
    error = request.args.get('error')
    return render_template('login_page.html', users=users.find(), error=error)


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
    checker = False
    for check in user['cart']:
        if ObjectId(check['_id']) == ObjectId(current_item['_id']):
            checker = True
    result = request.form.get('result')
    if(result is None):
        result = False
    print("This is the status of checker:", checker)
    return render_template('item_view.html', current_item=current_item, user=user, result=result, checker=checker)


@app.route('/adding_items', methods=['POST'])
def add_item_number():
    user = users.find_one({'_id': ObjectId(request.form.get('user_id'))})
    item_id = request.form.get('item_id')
    item = items.find_one({'_id': ObjectId(item_id)})
    amount = int(request.form.get('quantity'))
    cart = user['cart']
    print("This is cart before the update")
    for x in cart:
        print(x)
    find_index = 0
    for carts in cart:
        if(carts['_id'] == ObjectId(item_id)):
            break
        find_index += 1

    for index in range(amount):
        cart.append(item)
    # This is where we update our cart_size
    user_update = {
        'user': user['user'],
        'password': user['password'],
        'status': user['status'],
        'cart': cart,
        'admin_status': user['admin_status']
        }
    users.update_one({'_id': ObjectId(user['_id'])},
                    {'$set': user_update})

    # redifining cart
    #cart = user['cart']
    duplicate_list = []
    cart = user['cart']
    cart_clone = cart
    print("This is the cart len:", len(cart_clone), len(cart))
    index_for_duplicate = 0
    first = False
    total_amount = 0
    index_two = 0
    for x in cart_clone:
        print("This is cart  clone :", x, '\n', '\n')

    for y in cart:
        print("This is cart :", y, '\n', '\n')

    for current_item in cart:
        print("number:", 1)
        for item2 in cart_clone:
            print("This is the item_2 item:", item2)
            if current_item['_id'] == item2['_id']:
                if first is True:
                    print("FIRST HAS BECOME TRUE")
                    check = False
                    for x in duplicate_list:
                        if ObjectId(current_item['_id']) != ObjectId(x['_id']):
                            check = False
                        else:
                            check = True
                    if (check is False):
                        print("Comparing IDS:", current_item['_id'], ":", duplicate_list[index_for_duplicate]['_id'])
                        #dict_clone = {
                        #    '_id': current_item['_id'],
                        #    'image': current_item['image'],
                        #    'name': current_item['_id'],
                        #    'price': current_item['price'],
                        #    'description': current_item['description']
                        #}
                        #duplicate_list.insert(index_two, dict_clone)
                        duplicate_list.append(current_item)
                        #index_for_duplicate += 1
                elif index_for_duplicate == 0 and first is False:
                    duplicate_list.append(current_item)
                    first = True
                    index_two += 1
    # Filter once more
    res_list = []
    append_index = 0  # This is so we don't insert to last by default
    for i in range(len(duplicate_list)):
        if duplicate_list[i] not in duplicate_list[i + 1:]:
            res_list.insert(append_index, duplicate_list[i])
            append_index
    print("This should only include non duplicate", res_list)
    duplicate_amount = []
    for x in res_list:
        duplicate_amount.append(0)
    index_for_total = 0
    max = 0
    second = False
    print("Length of cart:", len(res_list))
    print("This is the ids of clones:", res_list)
    if len(res_list) != 0:
        for duplicate in res_list:
            print("The ones we are checking:", duplicate)
            for current_item_2 in cart:
                if duplicate['_id'] == current_item_2['_id']:
                    total_amount += 1
                max += 1
                print(max)
            if max == len(cart):
                print("This is the total amount:", total_amount)
                if second is True:
                    index_for_total += 1
                print("This is the index:", index_for_total)
                duplicate_amount[index_for_total] = {
                        'item': duplicate,
                        'amount': total_amount
                        }
                total_amount = 0
                max = 0
                second = True
    print("This is the list of amount per clone:", duplicate_amount)
    # Finding total cost for all items
    total_price = 0
    for item in duplicate_amount:
        total_price += float(item['item']['price'])
        total_price *= float(item['amount'])
    print("This is the final product:", duplicate_amount)

    return render_template('show_cart.html', user=user, cart=duplicate_amount, total_price=round(total_price))


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


@app.route('/seller/items', methods=['POST'])
def verify():
    """Will verify items desired to be listed """
    if request.method == 'POST':
        user = users.find_one({'_id': ObjectId(request.form.get('user_id'))})
        item_name = request.form.get('name')
        item_image = request.form.get('image')
        item_price = request.form.get('price')
        item_description = request.form.get('description')
        sell_item = {
            'seller': user['_id'],  # Get Seller ID
            'image': item_image,
            'name': item_name,
            'price': item_price,
            'description': item_description
        }
        seller_items.insert_one(sell_item)
        pending = True  # Pending for approval
        return render_template('user_seller_items.html', pending=pending, user=user, user_item=user['personal_item'])

@app.route('/create/seller/item', methods=['POST', 'GET'])
def create_item():
    user = users.find_one({'_id': ObjectId(request.form.get('user_id'))})
    return render_template('new_seller_item.html', user=user)


@app.route('/update/personal_item', methods=['POST'])
def update_personalitem():
    user = users.find_one({'_id': ObjectId(request.form.get('user_id'))})
    item_name = request.form.get('name')
    item_image = request.form.get('image')
    item_price = request.form.get('price')
    item_description = request.form.get('description')
    personal_cart = user['personal_item']
    sell_item = {
        'seller': user['_id'],  # Get Seller ID
        'image': item_image,
        'name': item_name,
        'price': item_price,
        'description': item_description
    }

    personal_cart.append(sell_item)

    user_update = {
        'user': user['user'],
        'password': user['password'],
        'status': user['status'],  # decides if user is offline
        'cart': user['cart'],
        'personal_item': personal_cart,
        'admin_status': user['admin_status']
        }
    users.update_one({'_id': ObjectId(user['_id'])},
                    {'$set': user_update})

    return render_template('user_seller_items.html', user_item=user['personal_item'], user=user)


@app.route('/render/user_items', methods=['POST'])
def user_items():
    user = users.find_one({'_id': ObjectId(request.form.get('user_id'))})
    print("This is the user who wants to sell!!", user)
    items = user['personal_item']
    return render_template('user_seller_items.html', user_item=items, user=user)


@app.route('/seller/stuff', methods=['GET'])
def seller_stuff():
    return render_template('seller_items.html', seller_items=seller_items.find())


@app.route('/remove/cart/item', methods=['POST'])
def remove_amount():
    amount = request.form.get('quantity_delete')
    item = items.find_one({'_id': ObjectId(request.form.get('item_id'))})
    user = users.find_one({'_id': ObjectId(request.form.get('user_id'))})
    cart = user['cart']
    cart_index = 0
    # Check for edge casing LATER
    for recall in range(int(amount)):
        for index in cart:
            if ObjectId(index['_id']) == ObjectId(item['_id']):
                cart.pop(cart_index)
                break
            cart_index += 1
        cart_index = 0
    user_update = {
        'user': user['user'],
        'password': user['password'],
        'status': user['status'],
        'cart': cart,
        'admin_status': user['admin_status']
        }
    users.update_one({'_id': ObjectId(user['_id'])},
                    {'$set': user_update})

    duplicate_list = []
    cart = user['cart']
    cart_clone = cart
    index_for_duplicate = 0
    first = False
    total_amount = 0
    index_two = 0

    for current_item in cart:
        for item2 in cart_clone:
            if current_item['_id'] == item2['_id']:
                if first is True:
                    check = False
                    for x in duplicate_list:
                        if ObjectId(current_item['_id']) != ObjectId(x['_id']):
                            check = False
                        else:
                            check = True
                    if (check is False):
                        #dict_clone = {
                        #    '_id': current_item['_id'],
                        #    'image': current_item['image'],
                        #    'name': current_item['_id'],
                        #    'price': current_item['price'],
                        #    'description': current_item['description']
                        #}
                        #duplicate_list.insert(index_two, dict_clone)
                        duplicate_list.append(current_item)
                        #index_for_duplicate += 1
                elif index_for_duplicate == 0 and first is False:
                    duplicate_list.append(current_item)
                    first = True
                    index_two += 1
    # Filter once more
    res_list = []
    append_index = 0  # This is so we don't insert to last by default
    for i in range(len(duplicate_list)):
        if duplicate_list[i] not in duplicate_list[i + 1:]:
            res_list.insert(append_index, duplicate_list[i])
            append_index
    print("This should only include non duplicate", res_list)
    duplicate_amount = []
    for x in res_list:
        duplicate_amount.append(0)
    index_for_total = 0
    max = 0
    second = False
    print("Length of cart:", len(res_list))
    print("This is the ids of clones:", res_list)
    if len(res_list) != 0:
        for duplicate in res_list:
            for current_item_2 in cart:
                if duplicate['_id'] == current_item_2['_id']:
                    total_amount += 1
                max += 1
                print(max)
            if max == len(cart):
                if second is True:
                    index_for_total += 1
                duplicate_amount[index_for_total] = {
                        'item': duplicate,
                        'amount': total_amount
                        }
                total_amount = 0
                max = 0
                second = True
    print("This is the list of amount per clone:", duplicate_amount)
    # Finding total cost for all items
    total_price = 0
    for item in duplicate_amount:
        total_price += float(item['item']['price'])
        total_price *= float(item['amount'])
    print("This is the final product:", duplicate_amount)

    return render_template('show_cart.html', user=user, cart=duplicate_amount, total_price=round(total_price))


    # This is where it ends


@app.route('/userpage', methods=['POST'])
def logging_in():
    """ Get input, if password and user match, render Account html.
        Otherwise redirect back with error message"""
    admins = ["jeff", "bezos"]
    user_name_new = request.form.get('username')
    user_password = request.form.get('password')
    for username in users.find():
        print("Users in database:", username)
    user = users.find_one({'user': user_name_new, 'password': user_password})

    if(user is None):
        error = True
        return redirect(url_for('login_page', error=error))

    else:
        cart_size = len(user['cart'])
        return render_template('user_welcome_page.html', user=user, admins=admins, items=items.find(), cart_size=cart_size)


if __name__ == '__main__':
      app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))
