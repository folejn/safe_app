from main import db, login_manager, migrate
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

junction_table = db.Table('junction', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    attempts = db.Column(db.Integer, default=0, nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    encrypt = db.Column(db.Boolean, default=False, nullable=False)
    #password = db.Column(db.String(60), nullable=False)
    group_note = db.Column(db.Boolean, nullable=False, default=False)
    viewers = db.relationship("User",
                    secondary=junction_table, backref='visible') 
    
    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

