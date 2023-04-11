from flask import Flask, render_template, redirect, url_for, session, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, EqualTo, InputRequired, Length
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/telsoft/Desktop/ijiolao/qwedatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# and store the instance in 'db'
db = SQLAlchemy()
db.init_app(app)
 
# runs the app instance
# app.app_context().push()



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)


class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    license_plate = db.Column(db.String(50), nullable=False)
    security_team_id = db.Column(db.Integer, db.ForeignKey('security_team.id'))
    security_team = db.relationship('SecurityTeam', backref='vehicles')


class DeliveryRoute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)


class SecurityTeam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)

# creates all database tables
with app.app_context():
    db.create_all()


class UserForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=20), EqualTo('confirm_password')])
    confirm_password = PasswordField('Confirm Password')
    role = SelectField('Role', choices=[('admin', 'Admin'), ('security', 'Security'), ('dispatcher', 'Dispatcher'), ('rider', 'Rider')], validators=[InputRequired()])
    submit = SubmitField('Register')


class VehicleForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    model = StringField('Model', validators=[DataRequired()])
    license_plate = StringField('License Plate', validators=[DataRequired()])
    submit = SubmitField('Add Vehicle')


class DeliveryRouteForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Add Delivery Route')


class SecurityTeamForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Add Security Team')


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', message='Invalid username or password')
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        role = form.role.data
        user = User(username=username, password=password, role=role)
        db.session.add(user)
        try:
            db.session.commit()
            flash('User created successfully', 'success')
            return redirect(url_for('dashboard'))
        except:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
    return render_template('register.html', form=form)


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    role = session['role']
    if role == 'admin':
        users = User.query.all()
        vehicles = Vehicle.query.all()
        routes = DeliveryRoute.query.all()
        teams = SecurityTeam.query.all()
        return render_template('admin_dashboard.html', users=users, vehicles=vehicles, routes=routes, teams=teams)
    elif role == 'security':
        teams = SecurityTeam.query.all()
        return render_template('security_dashboard.html', teams=teams)
    else:
        return render_template('dashboard.html')


@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return redirect(url_for('dashboard'))
    if session['role'] != 'admin':
        return redirect(url_for('dashboard'))
    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.password = form.password.data
        user.role = form.role.data
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('edit_user.html', form=form)


@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return redirect(url_for('dashboard'))
    if session['role'] != 'admin':
        return redirect(url_for('dashboard'))
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/add_vehicle', methods=['GET', 'POST'])
def add_vehicle():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session['role'] != 'admin':
        return redirect(url_for('dashboard'))
    form = VehicleForm()
    if form.validate_on_submit():
        name = form.name.data
        model = form.model.data
        license_plate = form.license_plate.data
        vehicle = Vehicle(name=name, model=model, license_plate=license_plate)
        db.session.add(vehicle)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('add_vehicle.html', form=form)


@app.route('/edit_vehicle/<int:vehicle_id>', methods=['GET', 'POST'])
def edit_vehicle(vehicle_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    vehicle = Vehicle.query.filter_by(id=vehicle_id).first()
    if not vehicle:
        return redirect(url_for('dashboard'))
    if session['role'] != 'admin':
        return redirect(url_for('dashboard'))
    form = VehicleForm(obj=vehicle)
    if form.validate_on_submit():
        vehicle.name = form.name.data
        vehicle.model = form.model.data
        vehicle.license_plate = form.license_plate.data
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('edit_vehicle.html', form=form)

@app.route('/delete_vehicle/<int:vehicle_id>')
def delete_vehicle(vehicle_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    vehicle = Vehicle.query.filter_by(id=vehicle_id).first()
    if not vehicle:
        return redirect(url_for('dashboard'))
    if session['role'] != 'admin':
        return redirect(url_for('dashboard'))
    db.session.delete(vehicle)
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/add_route', methods=['GET', 'POST'])
def add_route():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session['role'] != 'admin':
        return redirect(url_for('dashboard'))
    form = DeliveryRouteForm()
    if form.validate_on_submit():
        start_location = form.start_location.data
        end_location = form.end_location.data
        distance = form.distance.data
        route = DeliveryRoute(start_location=start_location, end_location=end_location, distance=distance)
        db.session.add(route)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('add_route.html', form=form)


@app.route('/edit_route/<int:route_id>', methods=['GET', 'POST'])
def edit_route(route_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    route = DeliveryRoute.query.filter_by(id=route_id).first()
    if not route:
        return redirect(url_for('dashboard'))
    if session['role'] != 'admin':
        return redirect(url_for('dashboard'))
    form = DeliveryRouteForm(obj=route)
    if form.validate_on_submit():
        route.start_location = form.start_location.data
        route.end_location = form.end_location.data
        route.distance = form.distance.data
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('edit_route.html', form=form)


@app.route('/delete_route/<int:route_id>')
def delete_route(route_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    route = DeliveryRoute.query.filter_by(id=route_id).first()
    if not route:
        return redirect(url_for('dashboard'))
    if session['role'] != 'admin':
        return redirect(url_for('dashboard'))
    db.session.delete(route)
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/add_team', methods=['GET', 'POST'])
def add_team():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session['role'] != 'security':
        return redirect(url_for('dashboard'))
    form = SecurityTeamForm()
    if form.validate_on_submit():
        name = form.name.data
        team = SecurityTeam(name=name)
        db.session.add(team)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('add_team.html', form=form)


@app.route('/edit_team/<int:team_id>', methods=['GET', 'POST'])
def edit_team(team_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    team = SecurityTeam.query.filter_by(id=team_id).first()
    if not team:
        return redirect(url_for('dashboard'))
    if session['role'] != 'security':
        return redirect(url_for('dashboard'))
    form = SecurityTeamForm(obj=team)
    if form.validate_on_submit():
        team.name = form.name.data
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('edit_team.html', form=form)

@app.route('/delete_team/<int:team_id>')
def delete_team(team_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    team = SecurityTeam.query.filter_by(id=team_id).first()
    if not team:
        return redirect(url_for('dashboard'))
    if session['role'] != 'security':
        return redirect(url_for('dashboard'))
    db.session.delete(team)
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/assign_team/<int:team_id>/<int:vehicle_id>')
def assign_team(team_id, vehicle_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    team = SecurityTeam.query.filter_by(id=team_id).first()
    vehicle = Vehicle.query.filter_by(id=vehicle_id).first()
    if not team or not vehicle:
        return redirect(url_for('dashboard'))
    if session['role'] != 'security':
        return redirect(url_for('dashboard'))
    vehicle.security_team = team
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/dismiss_team/<int:vehicle_id>')
def dismiss_team(vehicle_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    vehicle = Vehicle.query.filter_by(id=vehicle_id).first()
    if not vehicle:
        return redirect(url_for('dashboard'))
    if session['role'] != 'security':
        return redirect(url_for('dashboard'))
    vehicle.security_team = None
    db.session.commit()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
     with app.app_context():
        db.create_all()
        app.run(debug=True)