# test_supabase.py
import os
import psycopg2
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

print("🔧 Testando conexões...")
print(f"Host: {os.getenv('SUPABASE_DB_HOST')}")
print(f"User: {os.getenv('SUPABASE_DB_USER')}")
print(f"DB Name: {os.getenv('SUPABASE_DB_NAME')}")
print()

# Teste 1: Conexão PostgreSQL direta
try:
    conn = psycopg2.connect(
        dbname=os.getenv('SUPABASE_DB_NAME'),
        user=os.getenv('SUPABASE_DB_USER'),
        password=os.getenv('SUPABASE_DB_PASSWORD'),
        host=os.getenv('SUPABASE_DB_HOST'),
        port=os.getenv('SUPABASE_DB_PORT'),
        sslmode='require'
    )
    print("✅ Conexão com PostgreSQL (Supabase DB) funcionando!")
    conn.close()
except Exception as e:
    print(f"❌ Erro no PostgreSQL: {e}")

# Teste 2: Conexão com cliente Supabase
try:
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_KEY')
    )
    print("✅ Cliente Supabase inicializado!")
except Exception as e:
    print(f"❌ Erro no cliente Supabase: {e}")

print("\n✅ Testes concluídos!")