#!/usr/bin/env python
import os
from api import create_app, db

# from api.models import User


app = create_app("config")

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=PORT, debug=True)
    db = SQLAlchemy(app)
    db.create_all()
