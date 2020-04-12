#!/usr/bin/env python
import os
from api import create_app, db

# from api.models import User


app = create_app("config")

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5010))
    app.run(host="127.0.0.1", port=PORT, debug=True)
    
