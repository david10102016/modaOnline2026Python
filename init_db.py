from database import get_db_connection, hash_password

def populate_database():
    conn = get_db_connection()
    
    # Verificar si ya hay datos
    existing_categories = conn.execute('SELECT COUNT(*) FROM categorias').fetchone()[0]
    if existing_categories > 0:
        print("Base de datos ya tiene datos iniciales")
        conn.close()
        return
    
    # Insertar categorías
    categorias = [
        # Hombres
        ('Camisas', 'hombres'),
        ('Pantalones', 'hombres'), 
        ('Polos', 'hombres'),
        ('Chaquetas', 'hombres'),
        ('Accesorios', 'hombres'),
        # Mujeres
        ('Blusas', 'mujeres'),
        ('Pantalones', 'mujeres'),
        ('Vestidos', 'mujeres'),
        ('Chaquetas', 'mujeres'),
        ('Accesorios', 'mujeres'),
        # Niños
        ('Ropa Casual', 'ninos'),
        ('Ropa Formal', 'ninos'),
        ('Chaquetas', 'ninos'),
        ('Accesorios', 'ninos'),
        # Ofertas
        ('Ofertas', 'ofertas')
    ]
    
    for nombre, tipo in categorias:
        conn.execute('INSERT INTO categorias (nombre, tipo) VALUES (?, ?)', (nombre, tipo))
    
    # Usuario admin
    admin_password = hash_password('admin123')
    conn.execute('''INSERT INTO usuarios (nombre, correo, contraseña, telefono, rol) 
                    VALUES (?, ?, ?, ?, ?)''', 
                 ('Administrador', 'admin@tienda.com', admin_password, '73138524', 'admin'))
    
    # Productos de muestra (45 productos)
    productos = [
        # Hombres - Camisas (categoria_id = 1)
        ('Camisa Clásica Azul', 'Camisa de vestir azul marino, 100% algodón', 280.00, 1, '/static/images/productos/hombres/camisa1.jpg'),
        ('Camisa Blanca Formal', 'Camisa blanca para ocasiones formales', 320.00, 1, '/static/images/productos/hombres/camisa2.jpg'),
        ('Camisa Casual Gris', 'Camisa gris para uso diario', 250.00, 1, '/static/images/productos/hombres/camisa3.jpg'),
        
        # Hombres - Pantalones (categoria_id = 2)
        ('Pantalón Jean Azul', 'Jean clásico azul, corte regular', 380.00, 2, '/static/images/productos/hombres/pantalon1.jpg'),
        ('Pantalón Formal Negro', 'Pantalón de vestir negro', 420.00, 2, '/static/images/productos/hombres/pantalon2.jpg'),
        ('Pantalón Casual Beige', 'Pantalón cómodo para el día a día', 350.00, 2, '/static/images/productos/hombres/pantalon3.jpg'),
        
        # Hombres - Polos (categoria_id = 3)
        ('Polo Deportivo Rojo', 'Polo rojo para actividades deportivas', 180.00, 3, '/static/images/productos/hombres/polo1.jpg'),
        ('Polo Clásico Azul', 'Polo azul marino básico', 160.00, 3, '/static/images/productos/hombres/polo2.jpg'),
        ('Polo Rayas Verde', 'Polo con rayas verdes y blancas', 190.00, 3, '/static/images/productos/hombres/polo3.jpg'),
        
        # Hombres - Chaquetas (categoria_id = 4)
        ('Chaqueta Cuero Negro', 'Chaqueta de cuero genuino', 890.00, 4, '/static/images/productos/hombres/chaqueta1.jpg'),
        ('Chaqueta Sport Azul', 'Chaqueta deportiva azul', 450.00, 4, '/static/images/productos/hombres/chaqueta2.jpg'),
        ('Chaqueta Formal Gris', 'Chaqueta gris para ocasiones especiales', 650.00, 4, '/static/images/productos/hombres/chaqueta3.jpg'),
        
        # Hombres - Accesorios (categoria_id = 5)
        ('Cinturón Cuero Marrón', 'Cinturón de cuero marrón', 120.00, 5, '/static/images/productos/hombres/accesorio1.jpg'),
        ('Reloj Deportivo', 'Reloj digital para deportes', 220.00, 5, '/static/images/productos/hombres/accesorio2.jpg'),
        ('Gorra Casual Negra', 'Gorra negra ajustable', 85.00, 5, '/static/images/productos/hombres/accesorio3.jpg'),
        
        # Mujeres - Blusas (categoria_id = 6)
        ('Blusa Rosa Elegante', 'Blusa rosa para ocasiones especiales', 240.00, 6, '/static/images/productos/mujeres/blusa1.jpg'),
        ('Blusa Blanca Clásica', 'Blusa blanca versátil', 210.00, 6, '/static/images/productos/mujeres/blusa2.jpg'),
        ('Blusa Floral Azul', 'Blusa con estampado floral', 260.00, 6, '/static/images/productos/mujeres/blusa3.jpg'),
        
        # Mujeres - Pantalones (categoria_id = 7)
        ('Pantalón Jean Negro', 'Jean negro entubado', 360.00, 7, '/static/images/productos/mujeres/pantalon1.jpg'),
        ('Pantalón Formal Gris', 'Pantalón gris de vestir', 390.00, 7, '/static/images/productos/mujeres/pantalon2.jpg'),
        ('Pantalón Casual Blanco', 'Pantalón blanco cómodo', 320.00, 7, '/static/images/productos/mujeres/pantalon3.jpg'),
        
        # Mujeres - Vestidos (categoria_id = 8)
        ('Vestido Rojo Elegante', 'Vestido rojo para fiestas', 480.00, 8, '/static/images/productos/mujeres/vestido1.jpg'),
        ('Vestido Azul Casual', 'Vestido azul para el día', 350.00, 8, '/static/images/productos/mujeres/vestido2.jpg'),
        ('Vestido Floral Primavera', 'Vestido con flores para primavera', 420.00, 8, '/static/images/productos/mujeres/vestido3.jpg'),
        
        # Mujeres - Chaquetas (categoria_id = 9)
        ('Chaqueta Rosa Suave', 'Chaqueta rosa de algodón', 380.00, 9, '/static/images/productos/mujeres/chaqueta1.jpg'),
        ('Chaqueta Negra Formal', 'Chaqueta negra para oficina', 520.00, 9, '/static/images/productos/mujeres/chaqueta2.jpg'),
        ('Chaqueta Blanca Casual', 'Chaqueta blanca ligera', 350.00, 9, '/static/images/productos/mujeres/chaqueta3.jpg'),
        
        # Mujeres - Accesorios (categoria_id = 10)
        ('Collar Perlas Elegante', 'Collar de perlas clásico', 180.00, 10, '/static/images/productos/mujeres/accesorio1.jpg'),
        ('Aretes Dorados', 'Aretes dorados brillantes', 95.00, 10, '/static/images/productos/mujeres/accesorio2.jpg'),
        ('Bolso Cuero Negro', 'Bolso de cuero negro elegante', 420.00, 10, '/static/images/productos/mujeres/accesorio3.jpg'),
        
        # Niños - Ropa Casual (categoria_id = 11)
        ('Polo Niño Azul', 'Polo azul para niño', 120.00, 11, '/static/images/productos/ninos/casual1.jpg'),
        ('Camiseta Niña Rosa', 'Camiseta rosa con estampado', 110.00, 11, '/static/images/productos/ninos/casual2.jpg'),
        ('Short Niño Deportivo', 'Short deportivo cómodo', 95.00, 11, '/static/images/productos/ninos/casual3.jpg'),
        
        # Niños - Ropa Formal (categoria_id = 12)
        ('Camisa Niño Blanca', 'Camisa blanca para eventos', 160.00, 12, '/static/images/productos/ninos/formal1.jpg'),
        ('Pantalón Niño Azul', 'Pantalón azul formal', 180.00, 12, '/static/images/productos/ninos/formal2.jpg'),
        ('Vestido Niña Elegante', 'Vestido elegante para niña', 220.00, 12, '/static/images/productos/ninos/formal3.jpg'),
        
        # Niños - Chaquetas (categoria_id = 13)
        ('Chaqueta Niño Azul', 'Chaqueta abrigada azul', 280.00, 13, '/static/images/productos/ninos/chaqueta1.jpg'),
        ('Chaqueta Niña Rosa', 'Chaqueta rosa con capucha', 260.00, 13, '/static/images/productos/ninos/chaqueta2.jpg'),
        ('Chaqueta Deportiva', 'Chaqueta deportiva unisex', 240.00, 13, '/static/images/productos/ninos/chaqueta3.jpg'),
        
        # Niños - Accesorios (categoria_id = 14)
        ('Gorra Niño Roja', 'Gorra roja ajustable', 65.00, 14, '/static/images/productos/ninos/accesorio1.jpg'),
        ('Mochila Niña Unicornio', 'Mochila con diseño de unicornio', 150.00, 14, '/static/images/productos/ninos/accesorio2.jpg'),
        ('Zapatos Deportivos', 'Zapatos deportivos cómodos', 280.00, 14, '/static/images/productos/ninos/accesorio3.jpg'),
        
        # Ofertas (categoria_id = 15)
        ('Oferta: Camisa + Pantalón', 'Combo camisa y pantalón con descuento', 450.00, 15, '/static/images/productos/ofertas/combo1.jpg'),
        ('Oferta: Vestido Elegante', 'Vestido elegante con 30% descuento', 320.00, 15, '/static/images/productos/ofertas/vestido1.jpg'),
        ('Oferta: Conjunto Niños', 'Conjunto completo para niños', 280.00, 15, '/static/images/productos/ofertas/conjunto1.jpg'),
    ]
    
    for nombre, descripcion, precio, categoria_id, imagen in productos:
        conn.execute('''INSERT INTO productos (nombre, descripcion, precio, categoria_id, imagen) 
                        VALUES (?, ?, ?, ?, ?)''', (nombre, descripcion, precio, categoria_id, imagen))
    
    conn.commit()
    conn.close()
    print("Base de datos poblada exitosamente con 45 productos")

if __name__ == '__main__':
    from database import init_database
    init_database()
    populate_database()