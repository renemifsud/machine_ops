#!/usr/bin/env python
import os
from app import create_app
from app.models import User


PORT = int(os.environ.get("PORT", 5000))
CONFIG = os.environ.get("APP_CONFIG", "development")
app = create_app(CONFIG)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=PORT)
