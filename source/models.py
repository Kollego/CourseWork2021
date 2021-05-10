from source import db


class Highlight(db.Model):
    #__tablename__ = 'Highlights'
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    offset = db.Column(db.Integer, nullable=False)

    # def __init__(self, id, video_id, offset):
    #     self.id = id
    #     self.video_id = video_id
    #     self.offset = offset

    def __repr__(self):
        return '<Highlight %r>' % self.id


class Video(db.Model):
    #__tablename__ = 'Videos'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    # Create table
    author = db.Column(db.String(200), nullable=False)
    author_image_url = db.Column(db.String(200), nullable=False)
    # Create table
    game = db.Column(db.String(200), nullable=False)
    highlights = db.relationship('Highlight', backref='video', lazy=True)

    # def __init__(self, id, name, image_url, author, author_image_url, game):
    #     self.id = id
    #     self.name = name
    #     self.image_url = image_url
    #     self.author = author
    #     self.author_image_url = author_image_url
    #     self.game = game

    def __repr__(self):
        return '<Video %r>' % self.id
