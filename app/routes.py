from authlib.common.security import generate_token
from flask import render_template, Blueprint, redirect, url_for, flash, session, request
from flask_login import login_user, logout_user, current_user, login_required
from flask import redirect, url_for, request, jsonify
from .recommendation import get_recommendations_with_bert
from .utils import Pagination

from sqlalchemy import func


from . import db, oauth
from .forms import LoginForm, RegisterForm
from .models import Article
from .models import User
from . import mongo

from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    per_page = 12
    category = request.args.get('category')
    user_id = current_user.id if current_user.is_authenticated else None
    
    if category:
        articles = Article.query.filter_by(category=category).order_by(func.random()).paginate(page=page, per_page=per_page)
    else:
        if user_id:
            user_history = list(mongo.db.reading_history.find({
            'user_id': user_id
            }))
            if user_history and len(user_history) >= 5:
                user_history_indices = [history['article_id'] for history in user_history]
                recommended_articles = get_recommendations_with_bert(user_history_indices)
                articles = Pagination(
                    total=len(recommended_articles),
                    page=page,
                    per_page=per_page,
                    items=recommended_articles[(page - 1) * per_page: page * per_page]
                )
            else:
                articles = Article.query.order_by(func.random()).paginate(page=page, per_page=per_page)   
        else:
            articles = Article.query.order_by(func.random()).paginate(page=page, per_page=per_page)    
    
    # Temporary fix
    default_image_url = url_for('static', filename='images/devto_img.png')
    def set_default_image(article_list):
        for article in article_list:
            if article.category == "programming":
                article.image = default_image_url

    if isinstance(articles, list):
        set_default_image(articles)
    else:
        set_default_image(articles.items)


    return render_template('home.html', articles=articles)

@main.route('/search')
def search():
    """
        Instant search
    """
    query = request.args.get('q')
    if query: 
        results = Article.query.filter(Article.title.icontains(query) | Article.author.icontains(query)).all()
    else:
        return redirect(url_for('main.home'))

    # Temporary fix
    default_image_url = url_for('static', filename='images/devto_img.png')
    def set_default_image(article_list):
        for article in article_list:
            if article.category == "programming":
                article.image = default_image_url

    if isinstance(results, list):
        set_default_image(results)
    else:
        set_default_image(results.items)
        
    return render_template('search_results.html', articles = results, query=query)


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
        login_user(user)
        return redirect(url_for('main.home'))
    return render_template('login.html', form=form)


@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None:
            flash('Username already taken')
            return redirect(url_for('main.register'))
        new_user = User(
            username=form.username.data,
            email=form.email.data,
        )
        new_user.set_password(form.password.data)

        db.session.add(new_user)
        db.session.commit()

        flash('Register successfully')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)


@main.route('/login/google')
def google_login():
    redirect_uri = url_for('main.google_authorized', _external=True)
    # nonce for decrypt
    nonce = generate_token(20)
    session['nonce'] = nonce
    return oauth.google.authorize_redirect(redirect_uri, nonce=nonce)


@main.route('/login/google/authorized')
def google_authorized():
    token = oauth.google.authorize_access_token()

    # Nonce from session
    nonce = session.get('nonce')

    # pass nonce to decrypt
    user_info = oauth.google.parse_id_token(token, nonce=nonce)

    email = user_info['email']
    user = User.query.filter_by(email=email).first()

    if user is None:
        user = User(username=email.split('@')[0],
                    email=email,
                    provider='google',
                    provider_user_id=user_info['sub'],
                    access_token=token['access_token']
                    )
        db.session.add(user)
        db.session.commit()
    else:
        user.access_token = token['access_token']
        db.session.commit()

    login_user(user)
    flash("You have successfully logged in with Google!")
    return redirect(url_for("main.home"))


@main.route('/login/github')
def github_login():
    redirect_uri = url_for('main.github_authorized', _external=True)
    return oauth.github.authorize_redirect(redirect_uri)


@main.route('/login/github/authorized')
def github_authorized():
    token = oauth.github.authorize_access_token()
    response = oauth.github.get('https://api.github.com/user')
    user_info = response.json()

    email = user_info['email']
    if email is None:
        # GitHub does not always return the email in the profile, request emails specifically
        response = oauth.github.get('https://api.github.com/user/emails')
        emails = response.json()
        primary_email = next(email['email'] for email in emails if email['primary'])
        email = primary_email

    user = User.query.filter_by(email=email).first()

    if user is None:
        user = User(username=user_info['login'],
                    email=email,
                    provider='github',
                    provider_user_id=user_info['id'],
                    access_token=token['access_token']
                    )
        db.session.add(user)
        db.session.commit()
    else:
        user.access_token = token['access_token']
        db.session.commit()

    login_user(user)
    flash("You have successfully logged in with GitHub!")
    return redirect(url_for("main.home"))


@main.route('/login/facebook')
def facebook_login():
    redirect_uri = url_for('main.facebook_authorized', _external=True)
    return oauth.facebook.authorize_redirect(redirect_uri)


@main.route('/login/facebook/authorized')
def facebook_authorized():
    token = oauth.facebook.authorize_access_token()  # Exchange the code for an access token
    response = oauth.facebook.get('https://graph.facebook.com/me?fields=id,name,email')
    user_info = response.json()  # This contains user details like id, name, email

    # Process the user's data (e.g., create a new user or log them in)
    email = user_info.get('email')
    user = User.query.filter_by(email=email).first()

    if user is None:
        user = User(
            username=user_info['name'],
            email=email,
            provider='facebook',
            provider_user_id=user_info['id'],
            access_token=token['access_token']
        )
        db.session.add(user)
        db.session.commit()
    else:
        user.access_token = token['access_token']
        db.session.commit()

    login_user(user)
    flash("You have successfully logged in with Facebook!")
    return redirect(url_for("main.home"))


@main.route('/logout')
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('main.home'))


@main.route('/article/<int:article_id>', methods=['POST'])
@login_required
def add_reading_history(article_id):
    article = Article.query.get_or_404(article_id)
    if article:
        mongo.db.reading_history.insert_one({
                'user_id': current_user.id,
                'article_id': article_id,
                'timestamp': datetime.utcnow()
            })
        return jsonify({'message': 'Added to reading history'}), 201
    return jsonify({'message': 'Article not found'}), 404

@main.route('/reading-history/', methods=['GET'])
@login_required
def view_reading_history():
    user_id = current_user.id
    
    reading_history = mongo.db.reading_history.find({
        'user_id': user_id
    })
     
    # Store every articles into set
    article_ids = {record.get('article_id') for record in reading_history}
    
    # Filter article for better performance
    articles = Article.query.filter(Article.id.in_(article_ids)).all()
    
    default_image_url = url_for('static', filename='images/devto_img.png')
    
    for article in articles:
        if article.category == "programming":
            article.image = default_image_url
        
    return render_template('reading_history.html', articles=articles)
        
        
    
    
        
        
