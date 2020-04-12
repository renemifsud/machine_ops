class ValidateionError(ValueError):
    pass


class User(db.Model):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=False)
    password_hash = db.Column(db.String(100))
    email = db.Column(db.String(30), index=True, unique=True)

    def __init__(self, username, email, password):
        self.username = username
        self.set_password(password)
        self.email = email

    @staticmethod
    def register(username, email, password):
        user = User(username, email, password)
        db.session.add(user)
        db.session.commit()
        return user

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(password)

    def get_url(self):
        return url_for("user", uuid=self.uuid, _external=True)

    def export_data(self):
        return {"self_url": self.get_url(), "username": self.name}

