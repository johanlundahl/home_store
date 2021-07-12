from home_store.app import app, mydb


def get_sensors():
    with app.app_context():
        return mydb.sensors()


def create():
    mydb.create_all()


def drop():
    mydb.drop_all()
