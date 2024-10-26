from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import telebot
from dotenv import load_dotenv
import string
import random
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime
import requests
import io

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    files = db.relationship('File', backref='owner', lazy=True)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    unique_link = db.Column(db.String(255), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    telegram_file_id = db.Column(db.String(255), nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def generate_unique_link():
    characters = string.ascii_lowercase + string.digits
    while True:
        unique_link = ''.join(random.choice(characters) for _ in range(6))
        if not File.query.filter_by(unique_link=unique_link).first():
            return unique_link

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Это имя пользователя уже занято', 'error')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Аккаунт успешно создан!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    files = File.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', files=files)

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file:
        original_filename = secure_filename(file.filename)
        unique_link = generate_unique_link()
        
        # Отправка файла в Telegram
        with file.stream as file_stream:
            if file.content_type.startswith('video'):
                telegram_message = bot.send_video(chat_id=os.getenv('TELEGRAM_CHAT_ID'), video=file_stream, supports_streaming=True)
                file_id = telegram_message.video.file_id
            else:
                telegram_message = bot.send_document(chat_id=os.getenv('TELEGRAM_CHAT_ID'), document=file_stream)
                file_id = telegram_message.document.file_id
        
        new_file = File(filename=original_filename, original_filename=original_filename, unique_link=unique_link, user_id=current_user.id, telegram_file_id=file_id)
        db.session.add(new_file)
        db.session.commit()
        return jsonify({'success': True, 'unique_link': unique_link, 'original_filename': original_filename})

@app.route('/delete_file/<int:file_id>', methods=['POST'])
@login_required
def delete_file(file_id):
    file = File.query.get_or_404(file_id)
    if file.user_id != current_user.id:
        flash('У вас нет доступа к этому файлу', 'error')
        return redirect(url_for('dashboard'))
    try:
        bot.delete_message(chat_id=os.getenv('TELEGRAM_CHAT_ID'), message_id=file.telegram_file_id)
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Ошибка при удалении файла из Telegram: {e}")
    db.session.delete(file)
    db.session.commit()
    flash('Файл успешно удален', 'success')
    return redirect(url_for('dashboard'))

@app.route('/<string:unique_link>')
def download_file(unique_link):
    file = File.query.filter_by(unique_link=unique_link).first_or_404()
    try:
        file_info = bot.get_file(file.telegram_file_id)
        download_url = f"https://api.telegram.org/file/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/{file_info.file_path}"
        
        response = requests.get(download_url)
        if response.status_code == 200:
            file_content = response.content
            mimetype = 'video/mp4' if file.filename.lower().endswith('.mp4') else 'application/octet-stream'
            return send_file(
                io.BytesIO(file_content),
                mimetype=mimetype,
                as_attachment=True,
                download_name=file.original_filename
            )
        else:
            abort(404)
    except telebot.apihelper.ApiException:
        abort(404)

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        if check_password_hash(current_user.password, old_password):
            current_user.password = generate_password_hash(new_password)
            db.session.commit()
            flash('Пароль успешно изменен', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Неверный текущий пароль', 'error')
    return render_template('change_password.html')

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        if 'username' in request.form:
            new_username = request.form['username']
            current_user.username = new_username
            db.session.commit()
            flash('Имя пользователя успешно изменено', 'success')
        elif 'old_password' in request.form and 'new_password' in request.form:
            old_password = request.form['old_password']
            new_password = request.form['new_password']
            if check_password_hash(current_user.password, old_password):
                current_user.password = generate_password_hash(new_password)
                db.session.commit()
                flash('Пароль успешно изменен', 'success')
            else:
                flash('Неверный текущий пароль', 'error')
    return render_template('settings.html')

with app.app_context():
    db.create_all()

app.run(debug=True)
