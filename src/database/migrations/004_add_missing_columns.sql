-- Add missing created_at and updated_at columns to ventas table if they don't exist
-- For SQLite, we need to check if the columns exist first

-- For ventas.created_at
PRAGMA foreign_keys=off;
BEGIN TRANSACTION;

-- Check if ventas.created_at exists
SELECT 1 FROM pragma_table_info('ventas') WHERE name = 'created_at';
-- If the above returns 0 rows, then add the column

ALTER TABLE ventas ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP;

-- Check if ventas.updated_at exists
SELECT 1 FROM pragma_table_info('ventas') WHERE name = 'updated_at';
-- If the above returns 0 rows, then add the column

ALTER TABLE ventas ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP;

-- For venta_items.created_at
SELECT 1 FROM pragma_table_info('venta_items') WHERE name = 'created_at';
-- If the above returns 0 rows, then add the column

ALTER TABLE venta_items ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP;

COMMIT;
PRAGMA foreign_keys=on;
