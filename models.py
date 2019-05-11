from hello import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=False, nullable=False)
    question_number = db.Column(db.SmallInteger, default=0)
    demostrative = db.Column(db.SmallInteger, default=0)
    rigid = db.Column(db.SmallInteger, default=0)
    pedantic = db.Column(db.SmallInteger, default=0)
    excitable = db.Column(db.SmallInteger, default=0)
    hyperten = db.Column(db.SmallInteger, default=0)
    dysthymic = db.Column(db.SmallInteger, default=0)
    alarming = db.Column(db.SmallInteger, default=0)
    cyclosilicate = db.Column(db.SmallInteger, default=0)
    exalted = db.Column(db.SmallInteger, default=0)
    emotive = db.Column(db.SmallInteger, default=0)

    def __repr__(self):
        return '<User %r>' % self.username
