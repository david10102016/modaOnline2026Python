@app.route('/api/carrito/count')
def get_carrito_count():
    conn = get_db_connection()
    usuario_id = session.get('user_id')
    session_id = get_session_id()
    
    if usuario_id:
        count = conn.execute('''
            SELECT SUM(cantidad) FROM carrito WHERE usuario_id = ?
        ''', (usuario_id,)).fetchone()[0]
    else:
        count = conn.execute('''
            SELECT SUM(cantidad) FROM carrito WHERE session_id = ?
        ''', (session_id,)).fetchone()[0]
    
    conn.close()
    return jsonify({'count': count or 0})