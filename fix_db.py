import sqlite3

conn = sqlite3.connect('tienda.db')
cursor = conn.cursor()

cursor.execute('PRAGMA foreign_keys=off;')
cursor.execute('ALTER TABLE comentarios RENAME TO temp_comentarios;')
cursor.execute('CREATE TABLE comentarios (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER, producto_id INTEGER, calificacion INTEGER CHECK(calificacion >= 1 AND calificacion <= 5), comentario TEXT CHECK(LENGTH(comentario) <= 250), aprobado BOOLEAN DEFAULT 0, fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (usuario_id) REFERENCES usuarios(id), FOREIGN KEY (producto_id) REFERENCES productos(id));')
cursor.execute('INSERT INTO comentarios (id, usuario_id, producto_id, calificacion, comentario, aprobado, fecha) SELECT id, usuario_id, producto_id, calificacion, comentario, aprobado, fecha FROM temp_comentarios;')
cursor.execute('DROP TABLE temp_comentarios;')
cursor.execute('PRAGMA foreign_keys=on;')

conn.commit()
conn.close()

print("Base de datos actualizada. Verifica con PRAGMA table_info(comentarios).")