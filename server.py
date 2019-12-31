from flask import Flask, render_template, request, redirect, session, flash
from flask_bcrypt import Bcrypt
from datetime import datetime
import re
from mysqlconnection import connectToMySQL

app = Flask(__name__)
app.secret_key = "Greetings Earthlings!"
bcrpyt = Bcrypt(app)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_user', methods=['POST'])
def create_user():
    is_valid = True
    SpecialSym = ['$','@', '#', '%']
    
    if len(request.form['fname']) < 1:
        is_valid = False
        flash("Please enter a first name")
    
    if len(request.form['lname']) < 1:
        is_valid = False
        flash("Please enter a last name")
    
    if not EMAIL_REGEX.match(request.form['email']):
        is_valid = False
        flash("Invalid email address!")
    
    if len(request.form['pass']) < 5:
        is_valid = False
        flash("Password Must Be At Least 5 Characters")
    
    if request.form['cpass'] != request.form ['pass']:
        is_valid = False
        flash("Incorrect Password")
    
    if not request.form['fname'].isalpha():
        is_valid = False
        flash("First name can only contain alphabetic characters")
    
    if not request.form['lname'].isalpha():
        is_valid = False
        flash("Last name can only contain alphabetic characters")
    
    if not any(char.isdigit() for char in request.form['pass']): 
        is_valid = False
        flash('Password should have at least one numeral') 
    
    if not any(char.isupper() for char in request.form['pass']): 
        is_valid = False
        flash('Password should have at least one uppercase letter') 
    
    if not any(char.islower() for char in request.form['pass']): 
        is_valid = False
        flash('Password should have at least one lowercase letter') 
    
    if not any(char in SpecialSym for char in request.form['pass']): 
        is_valid = False
        flash('Password should have at least one of the symbols $@#')
    
    mysql = connectToMySQL("quote_dash")
    validate_email_query = 'SELECT id_users FROM users WHERE email=%(email)s;'
    form_data = {
        'email': request.form['email']
    }
    existing_users = mysql.query_db(validate_email_query, form_data)

    if existing_users:
        is_valid = False
        flash("Email already in use")
    
    if not is_valid:
        return redirect("/")

    if is_valid:
        mysql = connectToMySQL("quote_dash")
        pw_hash = bcrpyt.generate_password_hash(request.form['pass'])
        query = "INSERT into users(first_name, last_name, email, password, created_at, updated_at) VALUES (%(fname)s, %(lname)s, %(email)s, %(password_hash)s, NOW(), NOW());"

        data = {
            "fname": request.form['fname'],
            "lname": request.form['lname'],
            "email": request.form['email'],
            "password_hash": pw_hash
        }
        result_id = mysql.query_db(query, data)
        flash("Successfully added:{}".format(result_id))
        return redirect("/success")
    return redirect("/")

@app.route('/login', methods=['POST'])
def login():
    mysql = connectToMySQL("quote_dash")
    query = "SELECT * FROM users WHERE email = %(email)s;"
    data = { "email": request.form['email'] }
    result = mysql.query_db(query,data)
    if result: 
        if bcrpyt.check_password_hash(result[0]['password'], request.form['pass']):
            session['user_id'] = result[0]['id_users']
            return redirect("/success")
    flash("You could not be logged in")
    return redirect("/")

@app.route('/success')
def success():
    if 'user_id' not in session: 
        return redirect("/")

    mysql = connectToMySQL("quote_dash")
    query = "SELECT users.first_name, users.last_name FROM users WHERE id_users = %(uid)s"
    data = {
        'uid': session['user_id']
    }
    result = mysql.query_db(query,data)

    mysql = connectToMySQL("quote_dash")
    query = "SELECT quotes.author, quotes.id_quotes, quotes.content, quotes.author_name, quotes.created_at, users.first_name, users.last_name FROM quotes JOIN users on quotes.author = users.id_users ORDER BY created_at DESC;"
    all_quotes = mysql.query_db(query)

    mysql = connectToMySQL("quote_dash")
    query = "SELECT quotes_id_quotes FROM liked_quotes WHERE users_id_users = %(user_id)s"
    data = {
        'user_id': session['user_id']
    }
    results = mysql.query_db(query,data)
    liked_quote_ids = [result['quotes_id_quotes'] for result in results]

    mysql = connectToMySQL("quote_dash")
    query = "SELECT quotes_id_quotes, COUNT(quotes_id_quotes) AS like_count FROM liked_quotes GROUP BY quotes_id_quotes;"
    like_count = mysql.query_db(query)

    for quote in all_quotes:
        for like in like_count:
            if like['quotes_id_quotes']  == quote['id_quotes']:
                quote['like_count'] = like['like_count']
        
        if 'like_count' not in quote:
            quote['like_count'] = 0 
    if result:
        return render_template("dashboard.html", user_fn = result[0], all_quotes = all_quotes, liked_quote_ids = liked_quote_ids)
    else:
        return render_template("dashboard.html") 

@app.route('/quotes/create', methods=["POST"])
def create_quote():
    is_valid = True
    if len(request.form['author']) < 3:
        is_valid = False
        flash("Author must be greater than 3 characters")
    if len(request.form['quote']) < 10:
        is_valid = False
        flash("Quote must be between 10-255 characters")
    if len(request.form['quote']) > 255:
        is_valid = False
        flash("Quote must be between 10-255 characters")

    if is_valid:
        mysql = connectToMySQL("quote_dash")
        query = "INSERT into quotes(content, author, author_name, created_at, updated_at) VALUES (%(qc)s, %(aid)s, %(a_name)s, NOW(), NOW());"

        data = {
            "qc": request.form['quote'],
            "aid": session['user_id'],
            "a_name": request.form['author']
        }
        mysql.query_db(query, data)
        
    return redirect("/success")


@app.route('/like_quote/<quote_id>')
def like_quote(quote_id):
    mysql = connectToMySQL("quote_dash")
    query = "INSERT INTO liked_quotes (users_id_users, quotes_id_quotes) VALUES (%(user_id)s, %(quote_id)s);"
    data = {
        'user_id': session['user_id'],
        'quote_id': quote_id
    }
    mysql.query_db(query,data)
    return redirect("/success")

@app.route('/unlike_quote/<quote_id>')
def unlike_quote(quote_id):
    mysql = connectToMySQL("quote_dash")
    query = "DELETE FROM liked_quotes WHERE users_id_users = %(user_id)s AND quotes_id_quotes = %(quote_id)s;"
    data = {
        'user_id': session['user_id'],
        'quote_id': quote_id
    }
    mysql.query_db(query, data)
    return redirect("/success")

@app.route('/myaccount/<account_id>')
def edit_account(account_id):
    mysql = connectToMySQL("quote_dash")
    query = "SELECT * FROM users WHERE id_users = %(u_id)s;"
    data = { 
        'u_id': session['user_id']
    }
    user_data = mysql.query_db(query,data)
    return render_template("edit.html", user_data = user_data[0])

@app.route('/update_account/<account_id>', methods=["POST"])
def update_quote(account_id):
    is_valid = True
    
    if len(request.form['f_name']) < 3:
        is_valid = False
        flash("Please enter a valid first name")
    
    if len(request.form['l_name']) < 3:
        is_valid = False
        flash("Please enter a valid last name")
    
    if not EMAIL_REGEX.match(request.form['email']):
        is_valid = False
        flash("Invalid email address")

    mysql = connectToMySQL("quote_dash")
    validate_email_query = 'SELECT id_users FROM users WHERE email=%(email)s;'
    form_data = {
        'email': request.form['email']
    }
    existing_users = mysql.query_db(validate_email_query, form_data)

    if existing_users:
        is_valid = False
        flash("Email already in use")
    
    if is_valid:
        mysql = connectToMySQL("quote_dash")
        query = "UPDATE users SET first_name = %(first_name)s, last_name = %(last_name)s, email = %(email)s WHERE users.id_users = %(u_id)s;"
        data = {
            'first_name': request.form['f_name'],
            'last_name': request.form['l_name'],
            'email': request.form['email'],
            'u_id': account_id
        }
        mysql.query_db(query,data)
        return redirect('/success')
    return redirect(f"/myaccount/{account_id}")

@app.route('/delete_quote/<quote_id>')
def delete_quote(quote_id):
    mysql = connectToMySQL("quote_dash")
    query = "DELETE FROM quotes WHERE id_quotes = %(q_id)s AND author = %(u_id)s;"
    data = { 
        'q_id': quote_id,
        'u_id': session['user_id']
    }
    mysql.query_db(query,data)
    return redirect('/success')

@app.route('/user/<user_id>')
def user_quotes(user_id):
    mysql = connectToMySQL("quote_dash")
    query = "SELECT users.first_name, users.last_name FROM users WHERE id_users = %(uid)s"
    data = {
        'uid': user_id
    }
    result = mysql.query_db(query,data)
    
    mysql = connectToMySQL("quote_dash")
    query = "SELECT quotes.author, quotes.author_name, quotes.id_quotes, quotes.content, quotes.created_at, users.first_name, users.last_name FROM quotes JOIN users on quotes.author = users.id_users WHERE quotes.author = %(u_id)s;"
    data = {
        'u_id': user_id
    }
    user_quotes = mysql.query_db(query,data)

    return render_template ("/user_quotes.html", user_fn = result[0], user_quotes = user_quotes)

@app.route('/logout')
def logout():
    session.clear()
    flash("You have successfully logged yourself out")
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)