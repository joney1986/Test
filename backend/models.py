from .app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    resumes = db.relationship('Resume', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Storing resume data as a JSON string
    data = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Resume {self.id} for User {self.user_id}>'
