# Guion de presentación — GameDeals TFG

Duración objetivo: 20 minutos
Estructura: 7 secciones

---

## Sección 1 — Presentación personal (1 min)

"Buenos días. Me llamo Bernardo González y este es mi Trabajo de Fin de Grado del ciclo de Desarrollo de Aplicaciones Multiplataforma.

El proyecto se llama GameDeals: un comparador de ofertas de videojuegos que agrega precios de varias tiendas digitales en tiempo real, muestra el historial de precios de cada título y permite configurar alertas para recibir un email automático cuando un juego baja del precio que estás dispuesto a pagar."

---

## Sección 2 — Problema y motivación (2 min)

"La idea surge de un problema cotidiano. Si quieres comprar un videojuego al mejor precio posible, tienes que revisar manualmente Steam, GOG, Fanatical, Humble Bundle, Epic Games Store... cada una con sus propias rebajas y sin ninguna forma de compararlas fácilmente.

Servicios como IsThereAnyDeal o AllKeyShop existen en inglés, pero no hay nada similar en español ni tan orientado al usuario casual. Además, estos servicios no siempre muestran el historial de precios de forma visual ni permiten gestionar una wishlist personal con alertas personalizadas.

GameDeals resuelve exactamente eso: centraliza la información, guarda cómo ha evolucionado el precio a lo largo del tiempo y te avisa cuando puedes comprar ese juego que llevas meses esperando."

---

## Sección 3 — Arquitectura y tecnologías (3 min)

"Antes de entrar en la demo, quiero explicar brevemente cómo está construida la aplicación.

Backend: FastAPI con Python 3.11. Elegí FastAPI porque genera documentación automática con Swagger, tiene validación de datos integrada con Pydantic y tiene un rendimiento excelente gracias a su naturaleza asíncrona.

La base de datos es SQLite gestionada con SQLAlchemy 2.0. Para un TFG con un volumen de datos moderado, SQLite es más que suficiente y elimina la necesidad de instalar un servidor de base de datos.

La autenticación usa JWT. El token se firma en el servidor y el cliente lo almacena en localStorage. Las rutas protegidas comprueban el token en cada petición.

Para mantener los precios actualizados uso APScheduler: jobs programados que llaman a la API de CheapShark cada hora, a la API de Steam cada dos horas y a los scrapers de Fanatical y Humble Bundle cada seis horas. Las alertas se comprueban cada treinta minutos.

Tengo dos tipos de scrapers: uno con BeautifulSoup4 para Fanatical, cuyo HTML es estático, y uno con Playwright para Humble Bundle, que renderiza la página con JavaScript.

Frontend: React 19 con Vite y Tailwind CSS. La arquitectura es SPA con React Router. La autenticación se gestiona a través de un AuthContext que expone el usuario y el estado de sesión a toda la aplicación. Hay un WishlistContext similar para el contador de la wishlist en la navbar.

Para los datos externos de los juegos uso la API gratuita de RAWG, que proporciona descripciones, géneros y la nota de Metacritic."

---

## Sección 4 — Demo en vivo (8 min)

[Abrir el navegador en http://localhost:5173]

4.1 — Home (1 min)
"Esta es la página de inicio. Muestra las mejores ofertas del momento, las novedades recientes y los juegos gratis de la semana. Los datos se actualizan automáticamente gracias a los jobs del scheduler."

4.2 — Búsqueda (1 min)
"Si busco, por ejemplo, 'cyberpunk', el buscador tiene debounce de 300 ms para no lanzar peticiones en cada tecla. Vemos los resultados en tiempo real."

4.3 — Ficha de juego (2 min)
"Entro en un juego. Aquí veo la descripción, los géneros y la nota de Metacritic obtenida de RAWG. Más abajo está la tabla comparativa con el precio en cada tienda donde el juego está disponible. También aparece la gráfica de historial de precios con Recharts, que muestra cómo ha variado el precio y marca el mínimo histórico."

4.4 — Wishlist (1 min)
"Me registro... y añado este juego a la wishlist con el botón de corazón. La wishlist es persistente: se guarda en base de datos y el contador de la navbar se actualiza al instante."

4.5 — Alertas (2 min)
"Voy a /alerts. Aquí creo una alerta: busco el juego con debounce y pongo un precio objetivo. La alerta queda activa. Cada treinta minutos el scheduler comprueba si algún precio ha bajado del objetivo. Si lo ha hecho, el estado cambia a 'disparada' y se envía un email al usuario. Las alertas se agrupan por estado: activas, pausadas y disparadas."

4.6 — Deals y filtros (1 min)
"En /deals tengo el catálogo completo con filtros: por tienda, precio máximo, descuento mínimo y plataforma. El panel de filtros es colapsable. La paginación es infinita con 'Cargar más'."

---

## Sección 5 — Decisiones técnicas destacadas (3 min)

"Quiero destacar tres decisiones técnicas que considero especialmente relevantes.

Primera: scrapers duales. Fanatical y Humble Bundle no tienen APIs públicas. Para Fanatical usé BeautifulSoup4 porque su HTML es estático y se puede parsear directamente. Para Humble Bundle tuve que usar Playwright porque la página carga el contenido con JavaScript: el scraper abre un navegador sin cabeza, espera a que se renderice el DOM y extrae los datos.

Segunda: gestión del historial de precios. Cada vez que el scheduler detecta que un precio ha cambiado, guarda un registro en la tabla PriceHistory. Esto permite construir la gráfica de evolución temporal sin necesidad de APIs externas.

Tercera: alertas con doble consulta. El job de alertas primero obtiene los IDs de las alertas activas no disparadas, y luego hace una segunda consulta con joinedload para cargar el juego y el usuario asociado. Esto evita el problema N+1 de consultas y hace que el proceso de comprobación sea eficiente incluso con cientos de alertas."

---

## Sección 6 — Conclusiones y aprendizajes (2 min)

"Este proyecto me ha permitido trabajar por primera vez con una arquitectura cliente-servidor desacoplada de forma completa, desde el diseño de la base de datos hasta la interfaz de usuario.

Los principales aprendizajes han sido: el uso de ORMs con SQLAlchemy y cómo optimizar las queries con joinedload y contains_eager para evitar el problema N+1; la autenticación stateless con JWT y cómo proteger rutas tanto en el backend como en el frontend; el scraping con dos técnicas distintas según el tipo de página; y la gestión de estado global en React con Context API.

Como mejoras futuras consideraría: añadir más tiendas (GOG, Green Man Gaming), implementar notificaciones push además del email, añadir un panel de administración para gestionar el catálogo y migrar la base de datos a PostgreSQL para soportar más usuarios concurrentes."

---

## Sección 7 — Cierre (1 min)

"Para terminar, el código está organizado para que sea fácil añadir nuevas fuentes de precios: basta con implementar el servicio correspondiente y registrar el job en el scheduler.

Muchas gracias por su atención. Quedo a su disposición para cualquier pregunta."

---

Fin del guion — duración estimada: 20 minutos
