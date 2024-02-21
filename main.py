# CS 348 Project
from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import errorcode

from datetime import datetime

app = Flask(__name__)
username = "admin"
password = "password123"
alc_categories = ["wine", "tequila", "vodka", "whiskey", "gin", "beer", "liqueur"]
cid = -1


@app.route("/")
def homepage():
    return render_template("begin.html", title="Liquore", error="<None>")


def get_cid():
    global cid
    return cid


def select_all_ps(table_name):
    try:
        cnx = mysql.connector.connect(
            user='root', password='Betty123!', host='localhost', port='33061', database='village_bottle_shoppe')
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

    cursor = cnx.cursor()
    query = "SELECT * FROM %s;" % table_name
    cursor.execute(query)
    data = cursor.fetchall()

    cursor.close()
    cnx.close()

    return data


def products_by_category(category):
    try:
        cnx = mysql.connector.connect(
            user='root', password='Betty123!', host='localhost', port='33061', database='village_bottle_shoppe')
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

    cursor = cnx.cursor(prepared=True)
    query = "SELECT * FROM Product WHERE category = %s;"
    cursor.execute(query, (category, ))
    data = cursor.fetchall()

    cursor.close()
    cnx.close()
    return data

@app.route("/viewbycategory")
def view_by_category():
    return 0

def get_categories():
    try:
        cnx = mysql.connector.connect(
            user='root', password='Betty123!', host='localhost', port='33061', database='village_bottle_shoppe')
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

    cursor = cnx.cursor()
    query = "SELECT category, COUNT(productId) FROM Product GROUP BY category ORDER BY COUNT(productId) DESC;"
    cursor.execute(query)
    data = cursor.fetchall()

    cursor.close()
    cnx.close()
    return data

@app.route("/viewproducts")
def view_products():
    data = select_all_ps("Product")
    return render_template("viewproducts.html", title="Products | Liquore", data=data)


@app.route("/viewinventory")
def view_inventory():
    data = select_all_ps("Product")
    return render_template("inventory.html", title="Inventory | Liquore", data=data)


def customer_order_history():
    try:
        cnx = mysql.connector.connect(
            user='root', password='Betty123!', host='localhost', port='33061', database='village_bottle_shoppe')
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

    cursor = cnx.cursor(prepared=True)
    cart_id = get_cart_id()
    # Finding OrderIds that are not cart
    query = "SELECT orderId, transactionAmount, customerId FROM Orders WHERE orderId <> %s;" % cart_id
    cursor.execute(query)
    data = cursor.fetchall()

    cursor.close()
    cnx.close()
    return data

# Reports

@app.route("/salesbycustomer")
def sales_by_customer():
    try:
        cnx = mysql.connector.connect(
            user='root', password='Betty123!', host='localhost', port='33061', database='village_bottle_shoppe')
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

    cursor = cnx.cursor()
    # Finding OrderIds by customer
    query = "SELECT Orders.customerId, Customer.firstName, Customer.lastName, COUNT(orderId), SUM(transactionAmount), AVG(transactionAmount) FROM Orders INNER JOIN Customer ON Orders.customerId = Customer.customerId WHERE orderId IS NOT NULL GROUP BY Orders.customerId;"
    cursor.execute(query)
    data = cursor.fetchall()

    cursor.close()
    cnx.close()
    return render_template("salesbycustomer.html", title="Sales Report | Liquore", data=data)


def view_top_sellers():
    try:
        cnx = mysql.connector.connect(
            user='root', password='Betty123!', host='localhost', port='33061', database='village_bottle_shoppe')
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

    cursor = cnx.cursor()
    query = "SELECT DISTINCT p.productId, p.name, p.category, p.description, p.price, SUM(o.quantity), p.inventoryQuantity FROM Product p, OrderItem o WHERE o.productId = p.productId AND o.orderId IN (SELECT orderId FROM Orders WHERE completedDate IS NOT NULL) GROUP BY o.productId, p.name, p.category, p.description, p.price, p.inventoryQuantity ORDER BY SUM(o.quantity) DESC LIMIT 5;"
    cursor.execute(query)
    data = cursor.fetchall()

    cursor.close()
    cnx.close()
    return data


def monthly_sales_report(month):
    try:
        cnx = mysql.connector.connect(user='root', password='Betty123!', host='localhost', port='33061', database='village_bottle_shoppe')

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
 
    cursor = cnx.cursor()
    query = "SELECT firstName, lastName, transactionAmount, round((transactionAmount * .07),2) AS SALES_TAX, round((transactionAmount * .93),2) AS REVENUE from Customer C inner join Orders O on C.customerid = O.customerid where MONTH(completedDate) = %s;" % month
    cursor.execute(query)
    data = cursor.fetchall()
 
    cursor.close()
    cnx.close()
    return render_template("monthlysales.html", title="Monthly Sales Report | Liquore", data=data)


@app.route("/monthlysalesreport")
def currentmonthreport():
    return monthly_sales_report(int(datetime.today().month))

def completed_orders_ps():
    try:
        cnx = mysql.connector.connect(
            user='root', password='Betty123!', host='localhost', port='33061', database='village_bottle_shoppe')
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

    cursor = cnx.cursor()
    query = "SELECT orderId FROM Orders WHERE completedDate IS NOT NULL;"
    cursor.execute(query)
    data = cursor.fetchall()

    cursor.close()
    cnx.close()
    return data


def get_cart_id():
    try:
        cnx = mysql.connector.connect(
            user='root', password='Betty123!', host='localhost', port='33061', database='village_bottle_shoppe')
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

    cursor = cnx.cursor(prepared=True)
    print(get_cid())
    # query = "SELECT orderId FROM Orders WHERE customerId = %s AND completedDate IS NULL"  # Finding CartID
    cursor.execute("SELECT orderId FROM Orders WHERE customerId = %s AND completedDate IS NULL;" % (get_cid(), ))
    data = cursor.fetchall()
    print(data[0])
    print("data[0][0]", data[0][0])

    cursor.close()
    cnx.close()
    return data[0][0]


def add_to_cart(qty, product_id):
    try:
        cnx = mysql.connector.connect(
            user='root', password='Betty123!', host='localhost', port='33061', database='village_bottle_shoppe')
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

    cursor = cnx.cursor()
    order_id = get_cart_id()
    print("Back from get cart")
    print(product_id)
    print(order_id)
    print(qty)
    cursor.execute("SELECT name, category, price FROM Product WHERE productId = %s;" % product_id)
    data1 = cursor.fetchall()
    cursor.execute("SELECT quantity FROM OrderItem WHERE orderId = %s AND productId = %s;" % (order_id, product_id))
    data = cursor.fetchall()
    num = cursor.rowcount
    if (num == 0):
        print("Item doesn't exist in cart yet")
        query = "INSERT INTO OrderItem VALUES(%s, %s, %s);" % (
            order_id, product_id, qty)
        cursor.execute(query)
        cnx.commit()
    else:
        print("Item already exists in cart")
        cursor.execute("UPDATE OrderItem SET quantity = %s WHERE orderId = %s AND productId = %s;" % (
            qty, order_id, product_id))
        cnx.commit()

    cursor.close()
    cnx.close()
    return data1


def check_inventory(qty, product_id):
    try:
        cnx = mysql.connector.connect(
            user='root', password='Betty123!', host='localhost', port='33061', database='village_bottle_shoppe')
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

    cursor = cnx.cursor()
    checkQty = "SELECT inventoryQuantity FROM Product WHERE productId = %s;" % product_id
    cursor.execute(checkQty)
    data = cursor.fetchone()
    if (data[0] - int(qty) < 0):
        cursor.close()
        cnx.close()
        return False
    else:
        cursor.close()
        cnx.close()
        return True

@app.route("/getcart")
def getcartitems():
    try:
        cnx = mysql.connector.connect(
            user='root', password='Betty123!', host='localhost', port='33061', database='village_bottle_shoppe')
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

    cursor = cnx.cursor()
    order_id = get_cart_id()
    query = "SELECT o.productId, p.name, p.category, o.quantity, (p.price * o.quantity) as TotalPrice FROM OrderItem o INNER JOIN Product p ON o.productId = p.productId WHERE o.orderId = %s;" % order_id
    cursor.execute(query)
    data = cursor.fetchall()

    cursor.close()
    cnx.close()

    return render_template("cart.html", title="Cart | Liquore", data=data)


@app.route('/addquantity', methods=['POST', 'GET'])
def addquantity():
    if request.method == 'POST':
        result = request.form
        qty = result.get('quantity')
        product_id = result.get('productId')
        print(product_id)
        print(qty)
        bool_add = check_inventory(qty, product_id)

        if (bool_add):
            print(product_id)
            print(qty)
            add_to_cart(qty, product_id)
            return getcartitems()

    #   Update qty for particular item
        # return render_template("cart.html", title="Cart | Liquore", productId=product_id, qty=qty, data=data)


@app.route("/getuserinput", methods=['GET', 'POST'])
def getUserInput():
    return render_template('registeruser.html', title="Register User | Liquore")


@app.route("/registeruser", methods=['GET', 'POST'])
def registeruser():
    first_name = request.form['fname']
    last_name = request.form['lname']
    age = request.form.get('age')
    acc_num = request.form.get('accNum')
    routing_num = request.form.get('routeNum')
    if (int(age) < 21):
        return render_template("begin.html", title="Liquore", error="Underage")

    try:
        cnx = mysql.connector.connect(user='root', password='Betty123!', host='localhost', port='33061', database='village_bottle_shoppe', autocommit=False)

        cursor = cnx.cursor()
        cnx.start_transaction(isolation_level='SERIALIZABLE')
        cursor.execute("INSERT INTO BankingInfo(accountNum, routingNum) VALUES(%s, %s);" % (acc_num, routing_num))
        cursor.execute("SELECT MAX(bankId) FROM BankingInfo;")
        bank_id = cursor.fetchone()
        cursor.execute("INSERT INTO Customer(firstName, lastName, age, bankId) VALUES(%s, %s, %s, %s);", (first_name, last_name, age, bank_id[0]))
        cursor.execute("SELECT MAX(customerId) FROM Customer;")
        user_id = cursor.fetchone()
        cursor.execute("INSERT INTO Orders(completedDate, transactionAmount, customerId) VALUES(NULL, NULL, %s);" % (user_id[0]))
        cnx.commit()

        cursor.close()
        cnx.close()
        return render_template("accountcreated.html", title="Account Created | Liquore", userId=user_id[0], userName=first_name)

    except mysql.connector.Error as err:
        cnx.rollback()  # rollback changes
        print("Rolling back ...")
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

    finally:
        cursor.close()
        cnx.close()


@app.route("/trylogin", methods=['GET', 'POST'])
def trylogin():
    return render_template('login.html', title="Login | Liquore")


@app.route("/loginuser", methods=['GET', 'POST'])
def loginuser():
    global cid
    user_id = request.form['userId']

    try:
        cnx = mysql.connector.connect(user='root', password='Betty123!', host='localhost', port='33061', database='village_bottle_shoppe')

        cursor = cnx.cursor()
        cursor.execute("SELECT customerId FROM Customer WHERE customerId = %s;" % user_id)
        customerId = cursor.fetchall()
        if cursor.rowcount == 1:
            # Login successful
            cursor.close()
            cnx.close()
            bestsellers = view_top_sellers()
            categories = get_categories()
            cid = customerId[0][0]
            print("cid = ", cid)
            return render_template("customerhome.html", title="Home Page | Liquore", userId=customerId[0], bestsellers=bestsellers, categories=categories)
        else:
            return render_template("begin.html", title="Liquore", error="Unsuccessful_login")

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        
        cursor.close()
        cnx.close()
        return render_template("begin.html", title="Liquore", error="Database_issues")

@app.route("/homep", methods=['GET', 'POST'])
def homep():
    global cid
    bestsellers = view_top_sellers()
    categories = get_categories()
    return render_template("customerhome.html", title="Home Page | Liquore", userId=cid, bestsellers=bestsellers, categories=categories)


@app.route("/tryloginseller", methods=['GET', 'POST'])
def tryloginseller():
    return render_template('sellerlogin.html', title="Seller Login | Liquore")


@app.route("/loginseller", methods=['GET', 'POST'])
def loginseller():
    username = request.form['username']
    password = request.form['password']

    if (username == "admin" and password == "password123"):
        return render_template("sellerhome.html", title="Seller Home | Liquore")
    else:
        return render_template("begin.html", title="Liquore", error="Unsuccessful_seller_login")


@app.route("/deleteitem", methods=['GET', 'POST'])
def deleteitem():
    global cid
    print("POST request sent")
    product_id = request.form['productId']
    print("DELETE = %d", product_id)

    try:
        cnx = mysql.connector.connect(user='root', password='Betty123!', host='localhost', port='33061', database='village_bottle_shoppe')

        cursor = cnx.cursor()
        cart_id = get_cart_id()
        print(product_id)
        print(cart_id)
        cursor.execute("DELETE FROM OrderItem WHERE productId = %s AND orderId = %s" % (product_id, cart_id))
        cnx.commit()

        cursor.close()
        cnx.close()
        return getcartitems()

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        
        cursor.close()
        cnx.close()
        return render_template("begin.html", title="Liquore", error="Database_issues")


if __name__ == "__main__":
    app.run(debug=True)
    render_template("begin.html", title="Liquore", error="<None>")

# @app.route("/")
# def homepage():
#     return render_template("index.html", title="HOME PAGE")

# @app.route("/docs")
# def docs():
#     return render_template("index.html", title="docs page")

# @app.route("/about")
# def about():
#     return render_template("index.html", title="about page")

# if __name__ == "__main__":
#     app.run(debug=True)