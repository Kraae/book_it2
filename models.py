from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)
    with app.app_context():
        db.create_all()

class Bookshelf(db.Model):
    __tablename__='favorites'

    id = db.Column(
        db.Integer,
        primary_key=True
    )   

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"), nullable = False)
    
    book_id = db.Column(
        db.String,
        unique=True,
        nullable = False
    )
    book_title = db.Column(
        db.String,
        nullable = False

    )

    @classmethod
    def add(cls, user_id, book_id,book_title):
        """ADDS A FAVORITE BOOK TO THE LIST"""

        favorite = Bookshelf(
            user_id = user_id,
            book_id = book_id,
            book_title = book_title
        )
        
        db.session.add(favorite)
        return favorite
    @classmethod
    def byUser(cls, user_id):
        return Bookshelf.query.filter_by(user_id = user_id)

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.Text, nullable=False,  unique=True)

    email = db.Column(db.Text, nullable = False, unique = True)

    password = db.Column(db.Text, nullable=False)

    favorites = db.relationship('Bookshelf')

    @classmethod
    def signup(cls, username, email, password):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

