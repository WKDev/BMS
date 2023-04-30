from flask_sqlalchemy import SQLAlchemy
import datetime
db = SQLAlchemy()

class Table(db.Model):
    __tablename__= "sleep"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, default=datetime.datetime.now)
    sleeptime=db.Column(db.Time, default=datetime.time(hour=0,minute=0,second=0))
