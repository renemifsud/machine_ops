#!/usr/bin/env python
import os 
from api import create_app, db
from api.models import User

app = create_app(os.environ.get('FLASK_CONFIG', 'development'))
PORT = int(os.environ.get("PORT", 5000))
with app.app_context():
    db.create_all()
    # create a development user
    if User.query.get(1) is None:
        u = User(username='renemifsud')
        u.set_password('renetest')
        db.session.add(u)
        db.session.commit()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=PORT, debug=True)
