#!/usr/bin/env python
import os
from app import create_app
from app import db
from app.models import User


PORT = int(os.environ.get("PORT", 5000))
app = create_app("development")


with app.app_context():
    db.init_app(app)
    db.create_all()
    # populate the database
    if User.query.get(1) is None:
        u = User(username="renemifsud")
        u.set_password("renetest")
        db.session.add(u)
        db.session.commit()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=PORT, threaded=False)
