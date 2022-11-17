from home_store.app import app, mydb


def get_sensors():
    with app.app_context():
        return mydb.sensors()


def create():
    with app.app_context():
        mydb.create_all()


def drop():
    with app.app_context():
        mydb.drop_all()
