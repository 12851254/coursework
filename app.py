# import Flask from flask
from flask import Flask
# import 'request' to request data from html
from flask import request
# import SQLAlchemy for database operations
from flask_sqlalchemy import SQLAlchemy
# import UserMixin, RoleMixin
from flask_security import UserMixin, RoleMixin
# import required librearies from flask_login and flask_security
from flask_login import LoginManager, login_manager, login_user
from flask_security import Security, SQLAlchemySessionUserDatastore
from flask import render_template, redirect, url_for
from flask_security import roles_accepted



# pass current module (__name__) as argument
# this will initialize the instance
 
app = Flask(__name__)
# path to sqlite database
# this will create the db file in instance
# if database not present already
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///g4g.sqlite3"
# needed for session cookies
app.config['SECRET_KEY'] = 'MY_SECRET'
# hashes the password and then stores in the databse
app.config['SECURITY_PASSWORD_SALT'] = "MY_SECRET"
# allows new registrations to application
app.config['SECURITY_REGISTERABLE'] = True
# to send automatic registration email to user
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False

# and store the instance in 'db'
db = SQLAlchemy()
db.init_app(app)
 
# runs the app instance
app.app_context().push()

# create table in database for assigning roles
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))   
 
# create table in database for storing users
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    active = db.Column(db.Boolean())
    # backreferences the user_id from roles_users table
    roles = db.relationship('Role', secondary=roles_users, backref='roled')
 
# create table in database for storing roles
class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
     
# creates all database tables
@app.before_first_request
def create_tables():
    db.create_all()


 
# signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    msg=""
    # if the form is submitted
    if request.method == 'POST':
    # check if user already exists
        user = User.query.filter_by(email=request.form['email']).first()
        msg=""
        # if user already exists render the msg
        if user:
            msg="User already exist"
            # render signup.html if user exists
            return render_template('signup.html', msg=msg)
         
        # if user doesn't exist
         
        # store the user to database
        user = User(email=request.form['email'], active=1, password=request.form['password'])
        # store the role
        role = Role.query.filter_by(id=request.form['options']).first()
        user.roles.append(role)
         
        # commit the changes to database
        db.session.add(user)
        db.session.commit()
         
        # login the user to the app
        # this user is current user
        login_user(user)
        # redirect to index page
        return redirect(url_for('index'))
         
    # case other than submitting form, like loading the page itself
    else:
        return render_template("signup.html", msg=msg)


# ======================================================================================
# ‘/’ URL is bound with index() function.
@app.route('/')
# defining function index which returns the rendered html code
# for our home page
def index():
    return render_template("index.html")
#===================================================================================== 
# signin page
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    msg=""
    if request.method == 'POST':
        # search user in database
        user = User.query.filter_by(email=request.form['email']).first()
        # if exist check password
        if user:
            if  user.password == request.form['password']:
                # if password matches, login the user
                login_user(user)
                return redirect(url_for('index'))
            # if password doesn't match
            else:
                msg="Wrong username or password"
         
        # if user does not exist
        else:
            msg="wrong username or password"
        return render_template('signin.html', msg=msg)
         
    else:
        return render_template("signin.html", msg=msg)



#for running the app
if __name__ == "__main__": 
    app.run(debug = True)