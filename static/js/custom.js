/**
 * TIENDA DE ROPA ONLINE - JAVASCRIPT PERSONALIZADO
 * Tour guiado con Driver.js y funcionalidades interactivas + UAT Básico
 */

// Variables globales
let driver;
let currentPage = '';
let uatMode = false;
let uatData = {
    sessionId: null,
    currentScenario: null,
    startTime: null,
    interactions: [],
    scenarios: [],
    cleanup: null
};

// Inicialización al cargar el DOM
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Inicializar aplicación
 */
function initializeApp() {
    currentPage = getCurrentPage();
    initializeDriver();
    setupEventListeners();
    setupAnimations();
    initializeUAT();
    console.log('🛍️ Tienda de Ropa Online - App inicializada con UAT');
}

/**
 * Detectar página actual
 */
function getCurrentPage() {
    const path = window.location.pathname;
    
    if (path === '/' || path === '/index') return 'home';
    if (path.includes('/producto/')) return 'product';
    if (path.includes('/carrito')) return 'cart';
    if (path.includes('/checkout')) return 'checkout';
    if (path.includes('/login')) return 'login';
    if (path.includes('/admin')) return 'admin';
    if (path.includes('/buscar')) return 'search';
    
    return 'other';
}

/**
 * Inicializar Driver.js para tours guiados
 */
function initializeDriver() {
    if (typeof Driver === 'undefined') {
        console.warn('Driver.js no está disponible');
        return;
    }
    
    driver = new Driver({
        allowClose: true,
        opacity: 0.75,
        padding: 10,
        animate: false,
        showButtons: true,
        scrollIntoViewOptions: {
            behavior: 'smooth',
            block: 'center'
        },
        nextBtnText: 'Siguiente →',
        prevBtnText: '← Anterior',
        closeBtnText: '✕',
        doneBtnText: '¡Listo!'
    });
}

/**
 * Configurar event listeners
 */
function setupEventListeners() {
    const tourBtn = document.getElementById('tour-btn');
    if (tourBtn) {
        tourBtn.addEventListener('click', handleTourButtonClick);
    }
    
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) target.scrollIntoView({ behavior: 'smooth', block: 'center' });
        });
    });
    
    setupProductCardEffects();
    setupLazyLoading();
    setupUATTracking();
}

/**
 * Manejar click del botón Tour/UAT
 */
function handleTourButtonClick() {
    Swal.fire({
        title: '¿Qué deseas hacer?',
        html: `
            <div style="text-align: left; margin: 20px 0;">
                <p><strong>Tour Guiado:</strong> Te mostraré cómo usar la tienda paso a paso</p>
                <p><strong>Prueba de Usuario:</strong> Navega libremente mientras evaluamos la usabilidad</p>
            </div>
        `,
        showDenyButton: true,
        showCancelButton: true,
        confirmButtonText: '📚 Tour Guiado',
        denyButtonText: '🔍 Prueba UAT',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#007bff',
        denyButtonColor: '#28a745'
    }).then((result) => {
        if (result.isConfirmed) {
            startAppropiateTour();
        } else if (result.isDenied) {
            startUATSession();
        }
    });
}

// ===============================
// SISTEMA UAT BÁSICO
// ===============================

/**
 * Inicializar sistema UAT
 */
function initializeUAT() {
    // Crear ID de sesión único
    uatData.sessionId = 'uat_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    
    // Cargar datos previos si existen
    const savedData = localStorage.getItem('uat_sessions');
    if (!savedData) {
        localStorage.setItem('uat_sessions', JSON.stringify([]));
    }
}

/**
 * Iniciar sesión UAT
 */
function startUATSession() {
    uatMode = true;
    uatData.startTime = Date.now();
    uatData.interactions = [];
    
    showUATScenarioSelection();
}

/**
 * Mostrar selección de escenarios UAT
 */
function showUATScenarioSelection() {
    const scenarios = [
        {
            id: 'registro',
            title: 'Crear cuenta nueva',
            description: 'Regístrate como nuevo usuario en la tienda',
            estimatedTime: '3 minutos'
        },
        {
            id: 'busqueda',
            title: 'Buscar y ver producto',
            description: 'Encuentra un producto específico usando el buscador',
            estimatedTime: '2 minutos'
        },
        {
            id: 'compra',
            title: 'Simular compra completa',
            description: 'Agrega productos al carrito y ve hasta checkout',
            estimatedTime: '5 minutos'
        },
        {
            id: 'navegacion',
            title: 'Explorar categorías',
            description: 'Navega por diferentes categorías de productos',
            estimatedTime: '3 minutos'
        }
    ];
    
    const scenarioButtons = scenarios.map((s, index) => 
        `<button class="uat-scenario-btn" data-scenario="${s.id}" style="display: block; width: 100%; margin: 8px 0; padding: 12px; border: 2px solid #007bff; background: #f8f9fa; border-radius: 8px; cursor: pointer; text-align: left;">
            <strong>${s.title}</strong><br>
            <small style="color: #666;">${s.description} (${s.estimatedTime})</small>
        </button>`
    ).join('');
    
    Swal.fire({
        title: '🔍 Prueba de Usuario (UAT)',
        html: `
            <div style="text-align: left;">
                <p style="margin-bottom: 20px; color: #666;">Selecciona una tarea para realizar. Navegarás libremente mientras registramos tu experiencia:</p>
                ${scenarioButtons}
            </div>
        `,
        showConfirmButton: false,
        showCancelButton: true,
        cancelButtonText: 'Cancelar',
        allowOutsideClick: false,
        width: '500px',
        didOpen: () => {
            document.querySelectorAll('.uat-scenario-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    const scenario = this.getAttribute('data-scenario');
                    Swal.close();
                    selectUATScenario(scenario);
                });
            });
        }
    });
}

/**
 * Seleccionar escenario UAT
 */
function selectUATScenario(scenarioId) {
    uatData.currentScenario = scenarioId;
    Swal.close();
    
    const scenarioInfo = {
        'registro': 'Intenta registrarte como nuevo usuario. Al final te preguntaré qué tal fue la experiencia.',
        'busqueda': 'Busca un producto que te interese usando el buscador o categorías.',
        'compra': 'Agrega productos al carrito y ve hasta el proceso de compra (sin finalizar).',
        'navegacion': 'Explora diferentes secciones y categorías de la tienda.'
    };
    
    Swal.fire({
        title: 'Tarea Iniciada',
        text: scenarioInfo[scenarioId],
        icon: 'info',
        confirmButtonText: 'Comenzar',
        timer: 4000
    }).then(() => {
        startUATTracking(scenarioId);
    });
}

/**
 * Iniciar tracking UAT con timer de inactividad
 */
function startUATTracking(scenarioId) {
    console.log(`UAT iniciado: ${scenarioId}`);
    uatData.scenarioStartTime = Date.now();
    
    // Variables de control del timer
    let uatInactivityTimer = null;
    const INACTIVITY_TIMEOUT = 25000; // 25 segundos
    
    // Función para reiniciar el temporizador
    const resetInactivityTimer = () => {
        if (!uatMode) return;
        
        if (uatInactivityTimer) {
            clearTimeout(uatInactivityTimer);
        }
        
        console.log('Timer reseteado - 25 segundos de inactividad para feedback');
        uatInactivityTimer = setTimeout(() => {
            if (uatMode) {
                console.log('Inactividad de 25s detectada - mostrando feedback');
                showUATFeedback();
            }
        }, INACTIVITY_TIMEOUT);
    };
    
    // Iniciar el temporizador inmediatamente
    resetInactivityTimer();
    
    // Handler de actividad del usuario
    const onUserActivity = () => {
        if (!uatMode) return;
        console.log('Actividad detectada:', event.type);
        resetInactivityTimer();
    };
    
    // Configurar listeners
    const activityEvents = ['click', 'scroll', 'keypress', 'mousemove', 'touchstart'];
    activityEvents.forEach(eventType => {
        document.addEventListener(eventType, onUserActivity, { passive: true });
    });
    
    // Función de limpieza
    const cleanupUATSystem = () => {
        console.log('Limpiando sistema UAT completo');
        if (uatInactivityTimer) {
            clearTimeout(uatInactivityTimer);
            uatInactivityTimer = null;
        }
        activityEvents.forEach(eventType => {
            document.removeEventListener(eventType, onUserActivity);
        });
    };
    
    // Guardar limpieza
    uatData.cleanup = cleanupUATSystem;
    
    console.log('UAT configurado - timer activo desde el inicio');
    
    // Mostrar indicador
    setTimeout(() => {
        showUATIndicator();
    }, 100);
}

/**
 * Mostrar indicador UAT discreto
 */
function showUATIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'uat-indicator';
    indicator.innerHTML = '🔍 UAT Activo';
    indicator.style.cssText = `
        position: fixed; 
        top: 20px; 
        right: 20px; 
        background: #28a745; 
        color: white; 
        padding: 8px 12px; 
        border-radius: 20px; 
        font-size: 12px; 
        z-index: 1000;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    `;
    document.body.appendChild(indicator);
    
    // Auto-remover después de 3 segundos
    setTimeout(() => {
        if (indicator && indicator.parentNode) {
            indicator.parentNode.removeChild(indicator);
        }
    }, 3000);
}

/**
 * Configurar tracking de eventos UAT
 */
function setupUATTracking() {
    // Tracking de clicks globales
    document.addEventListener('click', function(e) {
        if (uatMode) {
            trackUATInteraction('click', {
                element: e.target.tagName,
                className: e.target.className,
                id: e.target.id,
                text: e.target.innerText?.substring(0, 50)
            });
        }
    });
    
    // Tracking de formularios
    document.addEventListener('submit', function(e) {
        if (uatMode) {
            trackUATInteraction('form_submit', {
                form: e.target.id || 'unknown',
                action: e.target.action
            });
        }
    });
    
    // Tracking de inputs abandonados
    document.addEventListener('focusout', function(e) {
        if (uatMode && (e.target.type === 'text' || e.target.type === 'email')) {
            if (e.target.value.trim() === '') {
                trackUATInteraction('input_abandoned', {
                    field: e.target.name || e.target.id,
                    placeholder: e.target.placeholder
                });
            }
        }
    });
}

/**
 * Registrar interacción UAT
 */
function trackUATInteraction(type, data) {
    uatData.interactions.push({
        type: type,
        data: data,
        timestamp: Date.now() - uatData.scenarioStartTime,
        page: currentPage,
        url: window.location.pathname
    });
}

/**
 * Mostrar feedback UAT
 */
function showUATFeedback() {
    if (!uatMode) return;
    
    const timeSpent = Math.round((Date.now() - uatData.scenarioStartTime) / 1000);
    console.log('Mostrando feedback UAT - tiempo:', timeSpent);
    
    Swal.fire({
        title: 'Feedback de Prueba UAT',
        html: `
            <div style="text-align: left;">
                <p><strong>Tiempo transcurrido:</strong> ${timeSpent} segundos</p>
                <p><strong>¿Lograste completar la tarea?</strong></p>
                <div style="margin: 15px 0;">
                    <label style="display: block; margin: 8px 0;">
                        <input type="radio" name="uat-success" value="si" style="margin-right: 8px;"> Sí, completé la tarea
                    </label>
                    <label style="display: block; margin: 8px 0;">
                        <input type="radio" name="uat-success" value="parcial" style="margin-right: 8px;"> Parcialmente
                    </label>
                    <label style="display: block; margin: 8px 0;">
                        <input type="radio" name="uat-success" value="no" style="margin-right: 8px;"> No pude completarla
                    </label>
                </div>
                <p><strong>¿Qué dificultades encontraste?</strong></p>
                <textarea id="uat-difficulties" class="form-control" rows="3" style="width: 100%; margin: 10px 0; padding: 8px;" placeholder="Describe cualquier problema, confusión o dificultad..."></textarea>
                <p><strong>Califica la experiencia (1-5):</strong></p>
                <div style="margin: 10px 0;">
                    <input type="range" id="uat-rating" min="1" max="5" value="3" style="width: 100%;">
                    <div style="display: flex; justify-content: space-between; font-size: 12px; color: #666;">
                        <span>Muy difícil</span>
                        <span>Muy fácil</span>
                    </div>
                </div>
            </div>
        `,
        confirmButtonText: 'Enviar Feedback',
        cancelButtonText: 'Continuar sin feedback',
        showCancelButton: true,
        allowOutsideClick: false,
        preConfirm: () => {
            const success = document.querySelector('input[name="uat-success"]:checked')?.value;
            const difficulties = document.getElementById('uat-difficulties').value;
            const rating = document.getElementById('uat-rating').value;
            
            if (!success) {
                Swal.showValidationMessage('Por favor indica si completaste la tarea');
                return false;
            }
            
            return { success, difficulties, rating };
        }
    }).then((result) => {
        if (result.isConfirmed) {
            saveUATResults(result.value, timeSpent);
        }
        endUATSession();
    });
}

/**
 * Guardar resultados UAT
 */
function saveUATResults(feedback, timeSpent) {
    const uatResult = {
        sessionId: uatData.sessionId,
        scenario: uatData.currentScenario,
        page: currentPage,
        timeSpent: timeSpent,
        interactions: uatData.interactions.length,
        success: feedback.success,
        difficulties: feedback.difficulties,
        rating: parseInt(feedback.rating),
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent
    };
    
    fetch('/api/uat/save', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(uatResult)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('UAT Result enviado al servidor:', uatResult);
            Swal.fire({
                title: '¡Gracias por tu feedback!',
                text: 'Tu experiencia ha sido registrada y nos ayudará a mejorar la tienda.',
                icon: 'success',
                timer: 3000
            });
        } else {
            console.error('Error guardando UAT:', data.error);
            saveUATToLocalStorage(uatResult);
        }
    })
    .catch(error => {
        console.error('Error enviando UAT:', error);
        saveUATToLocalStorage(uatResult);
    });
}

/**
 * Fallback: guardar en localStorage si el servidor falla
 */
function saveUATToLocalStorage(uatResult) {
    const sessions = JSON.parse(localStorage.getItem('uat_sessions') || '[]');
    sessions.push(uatResult);
    localStorage.setItem('uat_sessions', JSON.stringify(sessions));
    
    Swal.fire({
        title: '¡Gracias por tu feedback!',
        text: 'Tu experiencia ha sido registrada localmente.',
        icon: 'success',
        timer: 3000
    });
}

/**
 * Finalizar sesión UAT
 */
function endUATSession() {
    console.log('Terminando sesión UAT');
    uatMode = false;
    uatData.currentScenario = null;
    uatData.interactions = [];
    
    if (uatData.cleanup) {
        uatData.cleanup();
        uatData.cleanup = null;
    }
    
    const indicator = document.getElementById('uat-indicator');
    if (indicator) indicator.remove();
    
    console.log('UAT session ended');
}

/**
 * Obtener timeout del escenario
 */
function getScenarioTimeout(scenarioId) {
    const timeouts = {
        'registro': 180000, // 3 minutos
        'busqueda': 120000, // 2 minutos  
        'compra': 300000,   // 5 minutos
        'navegacion': 180000 // 3 minutos
    };
    return timeouts[scenarioId] || 180000;
}

// ===============================
// FUNCIONES TOUR ORIGINAL
// ===============================

/**
 * Iniciar tour apropiado según la página
 */
function startAppropiateTour() {
    if (!driver) {
        Swal.fire({
            icon: 'info',
            title: 'Tour no disponible',
            text: 'El sistema de tours está cargando...'
        });
        return;
    }
    
    switch (currentPage) {
        case 'home': startHomeTour(); break;
        case 'product': startProductTour(); break;
        case 'cart': startCartTour(); break;
        case 'checkout': startCheckoutTour(); break;
        case 'admin': startAdminTour(); break;
        case 'login': startLoginTour(); break;
        default: startGeneralTour();
    }
}

/**
 * Tour de la página principal
 */
function startHomeTour() {
    const steps = [
        { element: '#logo-tienda', popover: { title: '🏠 Logo de la Tienda', description: 'Este es el logo principal. Te lleva al inicio.', position: 'bottom' } },
        { element: '#form-buscar', popover: { title: '🔍 Buscar Productos', description: 'Usa este buscador para encontrar productos específicos.', position: 'bottom' } },
        { element: '#nav-categorias', popover: { title: '📂 Categorías', description: 'Aquí puedes explorar por categorías: Hombres, Mujeres, Niños.', position: 'bottom' } },
        { element: '#nav-carrito', popover: { title: '🛒 Tu Carrito', description: 'Aquí verás los productos que agregues al carrito.', position: 'left' } }
    ];
    driver.defineSteps(steps);
    driver.start();
}

/**
 * Tour de página de producto
 */
function startProductTour() {
    const steps = [
        { element: '#detalle-producto', popover: { title: '👕 Detalle', description: 'Ver detalles.', position: 'top' } },
        { element: '#imagen-principal', popover: { title: '📸 Imagen', description: 'Haz clic para zoom.', position: 'right', interaction: { type: 'click' } } },
        { element: '#cantidad', popover: { title: '🔢 Cantidad', description: 'Ingresa 1-10.', position: 'left', interaction: { type: 'input', condition: (v) => v >= 1 && v <= 10 } } },
        { element: '#form-agregar-carrito', popover: { title: '🛒 Agregar', description: 'Haz clic para agregar.', position: 'left', interaction: { type: 'submit' } } }
    ];
    driver.defineSteps(steps);
    driver.start();
}

/**
 * Tour del carrito de compras
 */
function startCartTour() {
    const steps = [
        { element: '#items-carrito', popover: { title: '🛒 Productos', description: 'Ajusta cantidad.', position: 'right', interaction: { type: 'input', condition: (v) => v >= 1 } } },
        { element: '.btn-outline-danger', popover: { title: '🗑️ Eliminar', description: 'Elimina un item.', position: 'left', interaction: { type: 'click' } } }
    ];
    driver.defineSteps(steps);
    driver.start();
}

/**
 * Tour del checkout boliviano
 */
function startCheckoutTour() {
    const steps = [
        { element: '#nombre', popover: { title: '👤 Nombre', description: 'Ingresa tu nombre.', position: 'right', interaction: { type: 'input', condition: (v) => v.trim().length > 0 } } },
        { element: '#telefono', popover: { title: '📞 Teléfono', description: 'Ingresa un número.', position: 'right', interaction: { type: 'input', condition: (v) => /^[678]\d{7}$/.test(v) } } },
        { element: '#btn-finalizar-compra', popover: { title: '🎉 Finalizar', description: 'Confirma compra.', position: 'top', interaction: { type: 'click' } } }
    ];
    driver.defineSteps(steps);
    driver.start();
}

/**
 * Tour del panel administrativo
 */
function startAdminTour() {
    const steps = [
        { element: '#estadisticas-admin', popover: { title: '📊 Estadísticas', description: 'Ver estadísticas.', position: 'bottom', interaction: { type: 'click' } } },
        { element: '#acciones-rapidas', popover: { title: '⚡ Acciones', description: 'Accede aquí.', position: 'bottom', interaction: { type: 'click' } } }
    ];
    driver.defineSteps(steps);
    driver.start();
}

/**
 * Tour de login/registro
 */
function startLoginTour() {
    const steps = [
        { element: '#correo-login', popover: { title: '📧 Correo', description: 'Ingresa tu email.', position: 'right', interaction: { type: 'input', condition: (v) => v.includes('@') } } },
        { element: '#password-login', popover: { title: '🔐 Contraseña', description: 'Ingresa contraseña.', position: 'right', interaction: { type: 'input', condition: (v) => v.length >= 1 } } },
        { element: '#form-login', popover: { title: '🚀 Iniciar', description: 'Haz clic para login.', position: 'left', interaction: { type: 'submit' } } }
    ];
    driver.defineSteps(steps);
    driver.start();
}

/**
 * Tour general para otras páginas
 */
function startGeneralTour() {
    const steps = [
        { element: '#navbar-principal', popover: { title: '🧭 Navegación', description: 'Navega aquí.', position: 'bottom', interaction: { type: 'click' } } },
        { element: '#nav-carrito', popover: { title: '🛒 Carrito', description: 'Ve tu carrito.', position: 'left', interaction: { type: 'click' } } }
    ];
    driver.defineSteps(steps);
    driver.start();
}

/**
 * Configurar efectos para cards de productos
 */
function setupProductCardEffects() {
    document.querySelectorAll('.producto-card').forEach(card => {
        card.addEventListener('mouseenter', () => card.style.transform = 'translateY(-10px) scale(1.02)');
        card.addEventListener('mouseleave', () => card.style.transform = 'translateY(0) scale(1)');
        const img = card.querySelector('.producto-imagen');
        if (img && !img.complete) img.addEventListener('load', () => { img.style.opacity = '1'; });
    });
}

/**
 * Configurar lazy loading para imágenes
 */
function setupLazyLoading() {
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src || img.src;
                    img.classList.remove('lazy');
                    observer.unobserve(img);
                }
            });
        });
        document.querySelectorAll('img[data-src]').forEach(img => observer.observe(img));
    }
}

/**
 * Configurar animaciones al scroll
 */
function setupAnimations() {
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) entry.target.classList.add('animate-fade-in-up');
            });
        }, { threshold: 0.1, rootMargin: '0px 0px -100px 0px' });
        document.querySelectorAll('.card, .producto-card, .categoria-card').forEach(el => observer.observe(el));
    }
}

/**
 * Actualizar contador del carrito
 */
function actualizarContadorCarrito() {
    fetch('/api/carrito/count')
        .then(res => res.json())
        .then(data => {
            const contador = document.getElementById('carrito-count');
            if (contador) {
                contador.textContent = data.count || 0;
                contador.style.display = data.count > 0 ? 'block' : 'none';
            }
        })
        .catch(err => console.log('Error actualizando carrito:', err));
}

/**
 * Agregar al carrito
 */
function agregarAlCarritoGlobal(productoId, cantidad = 1) {
    const formData = new FormData();
    formData.append('producto_id', productoId);
    formData.append('cantidad', cantidad);
    
    Swal.fire({ title: 'Agregando...', didOpen: () => Swal.showLoading(), timer: 1000, showConfirmButton: false });
    
    fetch('/agregar_carrito', { method: 'POST', body: formData })
        .then(res => res.json())
        .then(data => {
            Swal.close();
            if (data.success) {
                Swal.fire({ icon: 'success', title: '¡Agregado!', text: data.message, timer: 2000, showConfirmButton: false, toast: true, position: 'top-end', backdrop: false });
                actualizarContadorCarrito();
            } else {
                Swal.fire({ icon: 'error', title: 'Error', text: data.message || 'No se pudo agregar' });
            }
        })
        .catch(err => {
            console.error('Error:', err);
            Swal.close();
            Swal.fire({ icon: 'error', title: 'Error de conexión', text: 'No se pudo agregar' });
        });
}

// Función global para ver resultados UAT (para admin)
function viewUATResults() {
    const sessions = JSON.parse(localStorage.getItem('uat_sessions') || '[]');
    
    if (sessions.length === 0) {
        Swal.fire({
            title: 'Sin datos UAT',
            text: 'No hay sesiones de prueba registradas aún.',
            icon: 'info'
        });
        return;
    }
    
    const results = sessions.map(s => 
        `<div style="border: 1px solid #ddd; margin: 10px 0; padding: 10px; border-radius: 5px;">
            <strong>${s.scenario}</strong> - ${s.success} (${s.timeSpent}s) - Rating: ${s.rating}/5<br>
            <small>${s.timestamp}</small>
            ${s.difficulties ? `<br><em>"${s.difficulties}"</em>` : ''}
        </div>`
    ).join('');
    
    Swal.fire({
        title: `Resultados UAT (${sessions.length} sesiones)`,
        html: `<div style="max-height: 400px; overflow-y: auto;">${results}</div>`,
        width: '600px'
    });
}

window.TiendaBolivia = {
    startTour: startAppropiateTour,
    agregarCarrito: agregarAlCarritoGlobal,
    actualizarContador: actualizarContadorCarrito,
    getCurrentPage: getCurrentPage,
    startUAT: startUATSession,
    viewUATResults: viewUATResults
};

window.addEventListener('error', (e) => console.error('Error global capturado:', e.error));

console.log(`
🛍️ TIENDA DE ROPA ONLINE - SANTA CRUZ, BOLIVIA
===================================================
✅ JavaScript personalizado cargado con UAT CORREGIDO
📍 Ubicación: Equipetrol, Santa Cruz
📱 WhatsApp: +591 73138524
🌐 Proyecto DataCraft SQLite y Render
🔍 UAT System: Timer inactividad solo con actividad real
===================================================
`);

document.addEventListener('DOMContentLoaded', () => setTimeout(actualizarContadorCarrito, 1000));