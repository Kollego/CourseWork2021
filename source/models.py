from source import db, bcrypt


class Highlight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    offset = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Highlight of {self.video_id}>'


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    # Create table
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    highlights = db.relationship('Highlight', backref='video', lazy=True)
    processed = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return '<Video %r>' % self.name


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    videos = db.relationship('Video', backref='author', lazy=True)

    def __repr__(self):
        return '<Author %r>' % self.name


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    videos = db.relationship('Video', backref='game', lazy=True)

    def __repr__(self):
        return '<Game %r>' % self.name


users_videos = db.Table('users_videos',
                        db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                        db.Column('video_id', db.Integer, db.ForeignKey('video.id'), primary_key=True)
                        )


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    videos = db.relationship('Video', secondary=users_videos, lazy='subquery',
                             backref=db.backref('users', lazy=True))

    def __init__(self, username, password):
        self.username = username
        self.password = User.hashed_password(password)

    @staticmethod
    def hashed_password(password):
        return bcrypt.generate_password_hash(password).decode("utf-8")

    @staticmethod
    def get_user_with_username_and_password(username, password):
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.Password, password):
            return user
        else:
            return None

    def __repr__(self):
        return f"<User '{self.id}','{self.username}','{self.password}'>"

    @property
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
        }

