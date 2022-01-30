import os
import secrets
import time
from PIL import Image
from sqlalchemy.sql.expression import or_
from flask import render_template, url_for, flash, redirect, request, abort, session
from main import app, db, bcrypt
from main.forms import PostForm, RegistrationForm, LoginForm, UpdateAccountForm, DecryptForm
from main.models import User, Post   
from main.parser import parse
from main.entrophy import calculate_entrophy
from flask_login import login_user, logout_user, current_user, login_required
from main.cipher import encrypt, decrypt, generate_iv
from sqlalchemy import or_, and_
import re
import jinja2

def show_as_encrypted(post):
    post.content = '***content encrypted***' 
    return
    
def find_viewers(text):
    matches = [ t.strip('@;,!?.') for t in text.split() if t.startswith('@') ]
    print(matches)
    return matches

@app.template_filter('tag_parser')
def sanitize(s):
    return parse(s).unescape()

@app.route("/")
@app.route("/index")
def index():
    page = request.args.get('page', 1, type=int)
    if current_user.is_authenticated and not current_user.is_anonymous and current_user.is_active and current_user.username:
        posts = db.session.query(Post).filter(or_(and_(Post.encrypt==False,Post.group_note==True, Post.author==current_user),
            and_(Post.encrypt==False,Post.group_note==True, Post.viewers.any(id=current_user.id)), 
                                                  and_(Post.encrypt==False, Post.group_note==False), 
                                                  and_(Post.author==current_user, Post.encrypt==True)))\
                    .order_by(Post.date_posted.desc())
        for post in posts:
            if post.encrypt:
                post = show_as_encrypted(post)
        posts = posts.paginate(page=page, per_page=5)
    else:
        posts = Post.query.filter(and_(Post.encrypt==False,Post.group_note==False)).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template("index.html", posts=posts)

@app.route("/about")
def about():
    return render_template("about.html", title="about")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}! You can login now', 'success')
        return redirect(url_for('login'))
    return render_template("register.html", title="Register", form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user:
            time.sleep(2**user.attempts)
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            user.attempts = 0
            db.session.commit()
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            if user:
                user.attempts +=1
                db.session.commit()
                flash(f'Login unsuccessful, attempts: {user.attempts}, therefore login will take {2**user.attempts}s', 'danger')
            else:
                flash(f'Login unsuccessful', 'danger')
    return render_template("login.html", title="Login", form=form) 

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    
    output_size = (125, 125)
    img = Image.open(form_picture)
    img.thumbnail(output_size)
    
    img.save(picture_path)
    return picture_fn
    
@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            old_file = current_user.image_file
            old_path = os.path.join(app.root_path, 'static/profile_pics', old_file)
            
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
            if (os.path.exists(old_path) and old_file != 'default.jpg'):
                os.remove(old_path)
            
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    return render_template("account.html", title="Account", image_file = image_file, form=form) 

    
@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        iv = b'a'*16
        content = form.content.data
        if form.encrypt.data:
            if not  form.password.data:
                flash(f'Provide valid password!', 'danger')
                return render_template('full_create_post.html', title="New post",
                           form=form, legend='Add Post', require_pass=False)    
            iv = generate_iv()             
            content = encrypt(form.password.data, content, salt = form.title.data, iv=iv)
            
        post = Post(title=form.title.data, content=content, author=current_user, encrypt=form.encrypt.data, group_note=False, iv=iv)
        
        if not post.encrypt:
            potential_viewers = find_viewers(form.content.data)
            print(potential_viewers)
            for v in potential_viewers:
                viewer = User.query.filter_by(username=v).first()
                if viewer:
                    post.group_note =True
                    post.viewers.append(viewer)
        
        db.session.add(post)
        db.session.commit()
        flash('New post has been added', 'success')
        return redirect(url_for('index'))
    return render_template('full_create_post.html', title="New post",
                           form=form, legend='Add Post', require_pass=False)

@app.route("/post/<int:post_id>", methods=['GET','POST'])
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    form = DecryptForm()
    if form.validate_on_submit():
        if post.author != current_user:
            abort(403)
        entrophy = 8
        content = '***content encrypted***'
        try:
            content = decrypt(password=form.password.data, encrypted=post.content, salt = post.title, iv=post.iv)
            entrophy = calculate_entrophy(bytes(content, 'utf-8'))
        except (IndexError, ValueError):
            flash(f'Incorrect password provided', 'danger')
            return redirect(url_for('post', post_id=post_id)) 
        if not (entrophy < 7 and form.password.data): #bcrypt.check_password_hash(current_user.password, form.password.data)
            flash(f'Incorrect password provided', 'danger')
            return redirect(url_for('post', post_id=post_id))                
        
        post.content = content
        post.encrypt = False
        return render_template('post.html', title=post.title, post=post, form=form) 
    elif request.method == 'GET':
        if post and post.encrypt:
            if (current_user.is_authenticated and not post.author==current_user) or not current_user.is_authenticated:
                flash('You do not have an access to that post', 'danger')
                return redirect(url_for('index'))
            post.content = '***content encrypted***'
        elif post and post.group_note:
            if (current_user.is_authenticated and not ( post.viewers.count(current_user) or post.author == current_user)) or not current_user.is_authenticated:
                flash('You do not have an access to that post', 'danger')
                return redirect(url_for('index'))
        return render_template('post.html', title=post.title, post=post, form=form)

           
@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():        
        
        new_content = form.content.data
        if post.encrypt:
            if not (form.password.data):
                form.encrypt.data = True
                flash(f'Provide password', 'danger')
                return render_template('full_create_post.html', title="Update post",
                           form=form, legend='Update Post', require_pass=True)                
            if(form.content.data == '***content encrypted***'):
                try:
                    form.content.data = decrypt(form.password.data, post.content, salt=post.title, iv=post.iv)
                except ValueError:
                    flash(f'Provided password is incorrect', 'danger')
                    return redirect(url_for('post', post_id=post.id))
                return render_template('full_create_post.html', title="Update post",
                           form=form, legend='Update Post', require_pass=True)
                
            new_content = encrypt(form.password.data, new_content, salt = form.title.data, iv=post.iv)
            
        post.title = form.title.data
        post.content = new_content
        
        if post.group_note:
            potential_viewers = find_viewers(new_content)
            for viewer in post.viewers:
                if not viewer.username in potential_viewers:
                    post.viewers.remove(viewer)
        
        if not post.encrypt:
            potential_viewers = find_viewers(new_content)
            print(potential_viewers)
            for v in potential_viewers:
                viewer = User.query.filter_by(username=v).first()
                if viewer and not post.viewers.count(viewer):
                    post.group_note =True
                    post.viewers.append(viewer)
        
        db.session.commit()
        flash('Post has been updated', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        
        if post.encrypt:
            form.content.data = '***content encrypted***'
            form.encrypt.data=True
            return render_template('full_create_post.html', title="Update post",
                           form=form, legend='Update Post', require_pass=True)
        
    return render_template('create_post.html', title="Update post",
                           form=form, legend='Update Post')
    
@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted', 'success')
    return redirect(url_for('index'))

@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    
    if current_user.is_authenticated and not current_user.is_anonymous and current_user.is_active and current_user.username:
        posts = db.session.query(Post).filter(and_(or_(and_(Post.encrypt==False,Post.group_note==True, Post.author==current_user),
            and_(Post.encrypt==False,Post.group_note==True, Post.viewers.any(id=current_user.id)), 
                                                  and_(Post.encrypt==False, Post.group_note==False), 
                                                  and_(Post.author==current_user, Post.encrypt==True))), Post.author==user)\
                    .order_by(Post.date_posted.desc())
        for post in posts:
            if post.encrypt:
                post = show_as_encrypted(post)
        posts = posts.paginate(page=page, per_page=5)
    else:
        posts = db.session.query(Post).filter(and_(Post.group_note==False, Post.encrypt==False, Post.author==user)).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template("user_post.html", posts=posts, user=user)