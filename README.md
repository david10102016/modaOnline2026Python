# 🛍️ Moda Bolivia – Tienda de Ropa Online

**Descripción**
Moda Bolivia es una tienda de ropa online desarrollada con **Flask (Python)**, **SQLite** y **Bootstrap**. Este proyecto ofrece una solución completa para la venta de ropa en **Santa Cruz de la Sierra, Bolivia**, con funcionalidades clave:

* Catálogo de productos organizado por categorías.
* Carrito de compras con soporte para usuarios registrados y anónimos.
* Sistema de login/registro con validaciones de email, teléfono boliviano y contraseña segura.
* Moderación de comentarios.
* Tour interactivo con **Driver.js**.
* Prueba de usuario (**UAT**) para evaluar la usabilidad.
* Experiencia de compra local simulada con métodos de pago típicos (Tigo Money, QR Simple, WhatsApp).

El sitio está ubicado en **Equipetrol, Santa Cruz**, y simula un flujo de compra real con facturación usando **NIT o CI**.

---

## 🌟 Características Principales

| Funcionalidad                | Descripción                                                                                                                |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| **Catálogo de Productos**    | Productos organizados por categorías: hombres, mujeres, niños, ofertas especiales. Incluye imágenes y descripciones.       |
| **Carrito de Compras**       | Agrega, actualiza y elimina productos; soporta sesiones de usuario y anónimas.                                             |
| **Sistema de Usuarios**      | Registro/Login con validaciones de email, teléfono y contraseña segura.                                                    |
| **Comentarios y Moderación** | Usuarios logueados pueden comentar productos; comentarios con ≤3 estrellas requieren aprobación del admin.                 |
| **Tour Guiado y UAT**        | **Driver.js** para tours interactivos; sistema de prueba de usuario con timer de inactividad de 25 segundos para feedback. |
| **Checkout Boliviano**       | Soporte para métodos de pago locales (Tigo Money, QR Simple, WhatsApp) y facturación (NIT, CI).                            |
| **Panel Administrativo**     | Gestión de productos, órdenes y comentarios pendientes.                                                                    |
| **Responsive Design**        | Diseño adaptable con **Bootstrap** para dispositivos móviles.                                                              |

---

## 🛠️ Instalación

### Requisitos

* **Python 3.13+**
* **SQLite** (incluido en Python)
* Bibliotecas: `Flask`, `bcrypt`, `werkzeug`, `sqlite3`

```bash
pip install flask bcrypt werkzeug
```

### Pasos de Instalación

1. **Clonar el repositorio**

```bash
git clone <URL_DEL_REPOSITORIO>
cd tienda-ropa-online
```

2. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

> Contenido sugerido para `requirements.txt`:

```
flask==2.3.3
bcrypt==4.1.2
werkzeug==2.3.7
```

3. **Configurar la base de datos**

```bash
python database.py  # Inicializa tienda.db
python init_db.py   # Opcional: pobla datos de prueba
```

4. **Ejecutar la aplicación**

```bash
python app.py
```

5. **Abrir en navegador**

```
http://127.0.0.1:5000
```

---

## 👤 Credenciales de Prueba

| Rol     | Email                                                     | Contraseña  |
| ------- | --------------------------------------------------------- | ----------- |
| Admin   | [admin@modabolivia.com](mailto:admin@modabolivia.com)     | 🤡   |
| Usuario | [usuario@modabolivia.com](mailto:usuario@modabolivia.com) | Usuario123! |

---

## 🛒 Uso

### Para Clientes

* **Navegar:** Explora categorías o busca productos.
* **Comprar:** Agrega al carrito, revisa en `/carrito` y completa el checkout.
* **Comentar:** Inicia sesión y califica productos (1-5 estrellas).
* **Tour:** Haz clic en "Tour" para guía interactiva.

### Para Administrador

* **Inicia sesión** con credenciales admin.
* **Panel Admin (`/admin`):** Estadísticas, productos y órdenes.
* **Moderación (`/moderar`):** Aprobar comentarios pendientes.

### UAT (Prueba de Usuario)

* Haz clic en **Tour > Prueba UAT**.
* Selecciona un escenario y navega.
* La notificación de feedback aparece tras **25 segundos de inactividad**.

---

## 📁 Estructura del Proyecto

```
tienda-ropa-online/
├── app.py               # Aplicación Flask principal
├── database.py          # Configuración SQLite y funciones de BD
├── init_db.py           # Poblamiento inicial de datos
├── static/
│   ├── css/
│   │   └── custom.css   # Estilos personalizados
│   ├── js/
│   │   ├── custom.js    # JS principal (tours, UAT, interacciones)
│   │   └── driver-simple.js # Driver.js local para tours
│   └── images/
│       └── productos/   # Imágenes de productos por categoría
├── templates/
│   ├── base.html         # Plantilla base
│   ├── index.html        # Página principal
│   ├── login.html        # Login y registro
│   ├── admin.html        # Panel admin
│   ├── moderar.html      # Moderación de comentarios
│   └── ...               # Otras plantillas
└── requirements.txt      # Dependencias Python
```

---

## 🤝 Contribuciones

Contribuciones son bienvenidas. Por favor, abre un **issue** o **pull request** en GitHub.

---

## ⚖️ Licencia

**MIT License** – Ver `LICENSE` para detalles.

---

## 🧑‍💻 Autor

**Juan David Uscamayta Ramos**
Desarrollador Full Stack
Santa Cruz de la Sierra, Bolivia

* **Email:** [jdav777@outlook.com](mailto:jdav777@outlook.com)
* **YouTube:** [@jdav777](https://www.youtube.com/@jdav777)
* **WhatsApp / Canal de contacto:** JD Server para tutoriales y actualizaciones

---


