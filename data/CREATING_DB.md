# Creating PostgreSQL Database for MidasEngine

Before running `python -m data.db_initialize`, you need to create a PostgreSQL database instance. Here are three options:

## **Option 1: Using PostgreSQL Command Line**

1. **Connect to PostgreSQL as superuser:**
```bash
psql -U postgres
```

2. **Create database and user:**
```sql
-- Create the database
CREATE DATABASE midas_engine;

-- Create a user (optional, you can use postgres user)
CREATE USER midas_user WITH PASSWORD 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE midas_engine TO midas_user;

-- Exit psql
\q
```

## **Option 2: Using pgAdmin (GUI)**

1. Open pgAdmin
2. Right-click on "Databases" → "Create" → "Database"
3. Name: `midas_engine`
4. Click "Save"

## **Option 3: Using Docker (if you have Docker)**

```bash
# Run PostgreSQL in Docker
docker run --name midas-postgres \
  -e POSTGRES_DB=midas_engine \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  -d postgres:15
```

## **Update Your Environment Variables**

Create a `.env` file in your project root:

```bash
# .env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=midas_engine
DB_USER=postgres
DB_PASSWORD=your_password
```

## **Then Run the Initialization:**

```bash
python -m data.db_initialize
```

The script will automatically:
- Connect to your database
- Create 300 tables (20 symbols × 15 intervals)
- Ingest and aggregate all your CSV data
- Show progress and statistics

## **Verification**

After initialization, you can verify the setup:

```bash
# Check database statistics
python -m data.db_utils
```

This will show you:
- Total number of tables created
- Records per symbol and interval
- Date ranges of your data
