from pymongo import MongoClient, ASCENDING

def create_users_indexes(db):
    db.users.create_index([("document_id", ASCENDING)], unique=True)
    db.users.create_index([("phone", ASCENDING)], unique=True)
    db.users.create_index([("email", ASCENDING)], unique=True)


def create_accounts_indexes(db):
    db.accounts.create_index([("account_id", ASCENDING)], unique=True)
    

def create_transactions_history_indexes(db):
    db.transactions_history.create_index([("account_id", ASCENDING)], unique=True)
