from datetime import datetime
from random import randint

class AccountIdGenerator:    
    @staticmethod
    def generate(db) -> str:
        for i in range(5):
            current_time = datetime.now()
            new_id = f"{current_time.day:02d}{current_time.month:02d}{current_time.year}{randint(0, 999):03d}{randint(0, 999):03d}"

            if db.accounts.find_one({"account_id": new_id}) is None:
                break
            else:
                new_id = None

        
        if new_id is None:
            raise Exception("Failed to generate unique account id. Please try again.")

        return new_id
            
