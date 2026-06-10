from database import init_db, add_client
import random

def seed():
    """Function for primary population of the database with test data."""
    # Guaranteed creation of the table structure before data generation begins
    init_db()  
    
    # Lists of allowed values for random distribution by targeting categories
    interests = ["action", "drama", "general"] 
    ages = ["teen", "adult", "senior"]
    
    # Iterative loop to create a fixed array of 100 users
    for i in range(1, 101):
        # Generating a unique email identifier based on the iteration counter
        email = f"user{i}@example.com"
        # Pseudo-random choice of age category using the choice function
        age = random.choice(ages)
        # Pseudo-random choice of the user's primary interest
        interest = random.choice(interests)
        
        # Calling the database abstraction function to directly write the row into the 'clients' table
        add_client(email, age, interest)

    print("Database successfully populated with 100 clients!")

if __name__ == "__main__":
    # Entry point for the standalone execution of the database seeding script
    seed()