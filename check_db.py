from src.database import db

def check_tables():
    # Check ventas table structure
    print("\n=== ventas table structure ===")
    ventas_columns = db.execute_query("PRAGMA table_info(ventas)")
    for col in ventas_columns:
        print(f"{col['name']}: {col['type']} {'PRIMARY KEY' if col['pk'] else ''}")
    
    # Check venta_items table structure
    print("\n=== venta_items table structure ===")
    venta_items_columns = db.execute_query("PRAGMA table_info(venta_items)")
    for col in venta_items_columns:
        print(f"{col['name']}: {col['type']} {'PRIMARY KEY' if col['pk'] else ''}")
    
    # Check if we have any ventas
    print("\n=== ventas count ===")
    ventas_count = db.execute_query("SELECT COUNT(*) as count FROM ventas")[0]['count']
    print(f"Total ventas: {ventas_count}")
    
    # Show first few ventas if any exist
    if ventas_count > 0:
        print("\n=== Sample ventas ===")
        sample_ventas = db.execute_query("SELECT id, codigo_venta, fecha_venta, total, estado FROM ventas ORDER BY fecha_venta DESC LIMIT 5")
        for venta in sample_ventas:
            print(f"{venta['id']}: {venta['codigo_venta']} - {venta['fecha_venta']} - ${venta['total']} - {venta['estado']}")
    else:
        print("No hay ventas en la base de datos.")

if __name__ == "__main__":
    check_tables()
