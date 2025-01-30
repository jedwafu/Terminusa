from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import bcrypt
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///terminusa.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models
class Player(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    level = db.Column(db.Integer, default=1)
    tac_balance = db.Column(db.Integer, default=100)
    health = db.Column(db.Integer, default=100)

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    item_name = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Marketplace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    item_name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Achievements(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=False)

class PlayerAchievements(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)

# Initialize Database
with app.app_context():
    db.create_all()

# Flask-Login User Loader
@login_manager.user_loader
def load_user(user_id):
    return Player.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if Player.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))

        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        new_player = Player(username=username, password_hash=password_hash)
        db.session.add(new_player)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        player = Player.query.filter_by(username=username).first()
        if player and bcrypt.checkpw(password.encode(), player.password_hash.encode()):
            login_user(player)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', player=current_user)

@app.route('/explore')
@login_required
def explore():
    reward = random.randint(10, 50)
    current_player = Player.query.get(current_user.id)
    current_player.tac_balance += reward
    db.session.commit()

    flash(f'Decrypted {reward} Quantum Cores from quantum matrix!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/marketplace')
@login_required
def marketplace():
    listings = Marketplace.query.filter(Marketplace.seller_id != current_user.id).all()
    return render_template('marketplace.html', listings=listings)

@app.route('/achievements')
@login_required
def achievements():
    player_achievements = PlayerAchievements.query.filter_by(player_id=current_user.id).all()
    return render_template('achievements.html', achievements=player_achievements)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)