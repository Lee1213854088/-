from extensions import db


class test_deal_info(db.Model):
    id = db.Column(db.String(60), primary_key=True)
    salesman = db.Column(db.String(60), nullable=False)
    buyer = db.Column(db.String(60), nullable=False)
    number = db.Column(db.String(60), nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, value in data.items():
            setattr(self, key, value)


class users(db.Model):
    id = db.Column(db.String(60), primary_key=True)
    username = db.Column(db.String(60), nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, value in data.items():
            setattr(self, key, value)


class admins(db.Model):
    id = db.Column(db.String(60), primary_key=True)
    username = db.Column(db.String(60), nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, value in data.items():
            setattr(self, key, value)


class accounts(db.Model):
    id = db.Column(db.String(60), primary_key=True)
    username = db.Column(db.String(60), nullable=False)
    money = db.Column(db.String(60), nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, value in data.items():
            setattr(self, key, value)


class some_advice(db.Model):
    username = db.Column(db.String(60), primary_key=True)
    advice = db.Column(db.String(300), nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, value in data.items():
            setattr(self, key, value)

