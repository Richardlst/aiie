import asyncio
import asyncpg

async def test_connection():
    # Test with port 5433
    print("Testing connection on port 5433...")
    try:
        conn = await asyncpg.connect(
            user='postgres',
            password='postgres',
            host='localhost',
            port=5433,
            database='aiie_db'
        )
        print("✅ Connection successful!")
        version = await conn.fetchval('SELECT version()')
        print(f"PostgreSQL version: {version}")
        await conn.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
