from home_store.app import mydb


def create():
    mydb.create_all()

def drop():
    mydb.drop_all()