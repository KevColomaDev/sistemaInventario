from src.database import db

def check_products():
    # Check productos table structure
    print("\n=== productos table structure ===")
    try:
        productos_columns = db.execute_query("PRAGMA table_info(productos)")
        for col in productos_columns:
            print(f"{col['name']}: {col['type']} {'PRIMARY KEY' if col['pk'] else ''}")
        
        # Check if we have any products
        print("\n=== productos count ===")
        productos_count = db.execute_query("SELECT COUNT(*) as count FROM productos")[0]['count']
        print(f"Total productos: {productos_count}")
        
        # Show first few products if any exist
        if productos_count > 0:
            print("\n=== Sample productos ===")
            sample_products = db.execute_query("SELECT id, codigo, nombre, precio, cantidad FROM productos ORDER BY nombre LIMIT 5")
            for prod in sample_products:
                print(f"{prod['id']}: {prod['codigo']} - {prod['nombre']} - ${prod['precio']} - Stock: {prod['cantidad']}")
        else:
            print("No hay productos en la base de datos.")
            
    except Exception as e:
        print(f"Error al verificar productos: {str(e)}")

if __name__ == "__main__":
    check_products()
