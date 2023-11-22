import os
import requests
import urllib.request
import json
from flask import Flask, render_template, request, flash, redirect, session, g, abort, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from forms import UserAddForm, UserEditForm, LoginForm
from models import connect_db, db, User, Bookshelf

app = Flask(__name__)

CURR_USER_KEY = "curr_user"

app.config['SECRET_KEY'] = "KariLovesRobSooooooooMuch"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True

# THIS IS FOR HEROKU
# uri = os.environ.get('DATABASE_URL', 'postgresql:///book')
# if uri.startswith('postgres://'):
# 	uri = uri.replace('postgres://', 'postgresql://', 1)


# THIS IS FOR RENDER
DATABASE = 'postgresql:///vdjvsrng:9pCjNU-s_FRmX5elmOAwcY0IA8E4vwQp@suleiman.db.elephantsql.com/vdjvsrng'
uri = os.environ.get('DATABASE_URL',f'{DATABASE}')
app.config['SQLALCHEMY_DATABASE_URI'] = uri


connect_db(app)
db.create_all()

api_key = "AIzaSyCUg3r9gfvDYIa_y33XCA5wobD3S4do8g8"

url = "https://www.googleapis.com/books/v1/volumes"

# req = urllib.request.urlopen

payload = {
    'q': 'title',
    'key': api_key
}

#######################################################
    #GOOGLE BOOKS ROUTES
#######################################################

@app.route("/search")
def search():
    book = request.args.get('q')
    payload["q"] = book
    pg = 1
    return redirect(f'/books/{pg}')

@app.route('/books/<int:pg>')
def books(pg):
    booklist = []
    payload['startIndex'] = str((pg-1)*40)
    payload['maxResults'] = '40'
    res = requests.get(url, params = payload)
    data = res.json()
    x = 0
    y = 40
    for b in range (x, y):
        booklist.append(data['items'][b])
    return render_template ('books.html', books = booklist, pg = pg)






@app.route('/book/<id>')
def search_book(id):
    res = requests.get(url +'/'+id)
    data = res.json()
    return render_template('book.html', book = data)

@app.route('/book/<id>/favorite', methods= ["GET","POST"])
def add_fav_book(id):
    if not g.user:
        flash("Have to be logged in to add a favorite", "danger")
        return redirect("/login")
    res = requests.get(url +'/'+id)
    book = res.json()
    book_title = book['volumeInfo']['title']
    Bookshelf.add(
        user_id = g.user.id,
        book_id = id,
        book_title = book_title
    )
    db.session.commit()
    user_id = g.user.id
    return redirect (f"/users/{user_id}")
    
@app.route('/book/<book_id>/favorite/delete', methods= ["GET","POST"])
def delete_favorite(book_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    book = Bookshelf.query.filter(Bookshelf.book_id==book_id).first()
    db.session.delete(book)
    db.session.commit()

    return redirect(f"/users/{g.user.id}")



#######################################################
    #Login / register / logout
#######################################################

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/')
def homepage():
    return render_template ("home.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""
    do_logout()
    flash("You have been logged out!")
    return redirect("/login")


@app.route('/signup', methods=["GET", "POST"])
def signup():
    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data
                )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    return render_template("/users/signup.html", form=form)

    #######################################################
    # User Information and profile

    #######################################################

@app.route('/users/<int:user_id>', methods=["GET", "POST"])
def users_show(user_id):
    """Show user profile."""
    user = User.query.get_or_404(user_id)
    bookshelf = Bookshelf.query.filter(Bookshelf.user_id==user_id).all()
    return render_template('users/detail.html', user=user, bookshelf=bookshelf)

@app.route('/users/profile', methods=["GET", "POST"])
def edit_profile():
    """Update profile for current user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = g.user
    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):
            user.username = form.username.data
            user.email = form.email.data

            db.session.commit()
            return redirect(f"/users/{user.id}")

        flash("Wrong password, please try again.", 'danger')

    return render_template('users/edit.html', form=form, user_id=user.id)

@app.route('/users/delete')
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")
   
    #######################################################
    # error handling
    #######################################################

@app.errorhandler(500)
def page_not_found(e):
    """when the search fails it returns 500, so redirect for that"""

    return render_template('badsearch.html'), 500