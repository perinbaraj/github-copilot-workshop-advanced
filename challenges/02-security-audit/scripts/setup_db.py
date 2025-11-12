import psycopg2
from psycopg2 import sql

# Database connection
DB_CONFIG = {
    'host': 'localhost',
    'database': 'postgres',
    'user': 'admin',
    'password': 'admin123'
}

def setup_database():
    # Connect to PostgreSQL
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()
    
    # Create database
    try:
        cur.execute("CREATE DATABASE paysecure")
        print("Database 'paysecure' created successfully")
    except psycopg2.errors.DuplicateDatabase:
        print("Database 'paysecure' already exists")
    
    cur.close()
    conn.close()
    
    # Connect to the new database
    DB_CONFIG['database'] = 'paysecure'
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Create users table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            balance DECIMAL(10, 2) DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create accounts table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            account_number VARCHAR(20) UNIQUE NOT NULL,
            balance DECIMAL(10, 2) DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create payments table (with security issues!)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id SERIAL PRIMARY KEY,
            card_number VARCHAR(16),
            cvv VARCHAR(4),
            expiry VARCHAR(7),
            amount DECIMAL(10, 2),
            status VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create transfers table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS transfers (
            id SERIAL PRIMARY KEY,
            from_account INTEGER REFERENCES accounts(id),
            to_account INTEGER REFERENCES accounts(id),
            amount DECIMAL(10, 2),
            status VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    
    # Insert sample data
    cur.execute('''
        INSERT INTO users (email, password_hash, balance) VALUES
        ('alice@example.com', '5f4dcc3b5aa765d61d8327deb882cf99', 1000.00),
        ('bob@example.com', '5f4dcc3b5aa765d61d8327deb882cf99', 2000.00)
        ON CONFLICT (email) DO NOTHING
    ''')
    
    cur.execute('''
        INSERT INTO accounts (user_id, account_number, balance) VALUES
        (1, '1234567890', 1000.00),
        (2, '0987654321', 2000.00)
        ON CONFLICT (account_number) DO NOTHING
    ''')
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("Database setup complete!")
    print("Sample users created:")
    print("  - alice@example.com / password (MD5 hash: 5f4dcc3b5aa765d61d8327deb882cf99)")
    print("  - bob@example.com / password")

if __name__ == '__main__':
    setup_database()
