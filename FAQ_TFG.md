# Preguntas frecuentes del tribunal — GameDeals TFG

Duración estimada del turno de preguntas: 5 minutos
Formato: Pregunta y respuesta que yo daría

---

## Categoría 1 — Arquitectura y tecnologías

P1. ¿Por qué elegiste FastAPI en lugar de Django o Flask?

"FastAPI tiene tres ventajas clave para este proyecto. Primero, genera documentación interactiva con Swagger automáticamente, lo que facilita mucho el desarrollo y las pruebas. Segundo, la validación de datos con Pydantic está integrada: si un campo llega con el tipo incorrecto, FastAPI devuelve un error claro sin que yo tenga que escribir código de validación manual. Tercero, es asíncrono por naturaleza, lo que le da mejor rendimiento bajo carga concurrente. Django hubiera sido excesivo para este proyecto y Flask requiere más configuración manual."

P2. ¿Por qué SQLite y no PostgreSQL o MySQL?

"Para el alcance de un TFG con un número limitado de usuarios y datos, SQLite es suficiente. No requiere instalar ni configurar un servidor de base de datos, lo que simplifica el despliegue y las pruebas locales. Si el proyecto escalara a producción con muchos usuarios concurrentes, migraría a PostgreSQL: SQLAlchemy hace que ese cambio sea mínimo, solo hay que cambiar la cadena de conexión."

P3. ¿Cómo funciona la autenticación JWT?

"Cuando el usuario inicia sesión, el backend verifica las credenciales contra la base de datos usando bcrypt para comparar el hash de la contraseña. Si son correctas, genera un token JWT firmado con una clave secreta que incluye el ID del usuario y una fecha de expiración. El frontend guarda ese token en localStorage y lo incluye en la cabecera Authorization de cada petición a rutas protegidas. El backend verifica la firma del token en cada request sin necesidad de consultar la base de datos."

P4. ¿Qué es APScheduler y cómo lo usas?

"APScheduler es una biblioteca de Python para programar tareas que se ejecutan en segundo plano a intervalos regulares, como un cron pero embebido en la aplicación. En mi caso tengo cuatro jobs: CheapShark cada hora, Steam cada dos horas, Fanatical y Humble cada seis horas, y la comprobación de alertas de precio cada treinta minutos. El scheduler arranca con la aplicación y se detiene cuando la aplicación se apaga."

---

## Categoría 2 — Scrapers y datos

P5. ¿Qué diferencia hay entre el scraper de Fanatical y el de Humble Bundle?

"Fanatical sirve el HTML con los datos de las ofertas ya en el HTML inicial, así que BeautifulSoup4 puede parsear directamente la respuesta HTTP. Humble Bundle, en cambio, carga el contenido con JavaScript después de que el navegador ejecuta el JS de la página. Por eso necesité Playwright, que abre un navegador Chromium sin cabeza, espera a que el DOM esté listo y luego extrae los datos. Es más lento, pero es la única forma de acceder a contenido renderizado en cliente."

P6. ¿Qué pasa si un scraper falla o la tienda cambia su estructura HTML?

"Los scrapers están envueltos en bloques try-except. Si uno falla, el job de ese scraper registra el error en los logs y continúa, sin afectar al resto de la aplicación ni a los otros scrapers. Si la estructura HTML cambia, el scraper dejará de extraer datos correctamente y tendré que actualizarlo. Es la limitación inherente del scraping: es frágil ante cambios en el frontend de los sitios objetivo."

P7. ¿Cómo evitas hacer demasiadas peticiones a las APIs externas?

"Los jobs están configurados con intervalos razonables: CheapShark cada hora porque su API es pública y tiene rate limits generosos; Steam cada dos horas; los scrapers cada seis horas porque son más pesados. Si quisiera ser más estricto, podría añadir un sleep entre peticiones dentro del job o implementar un sistema de caché con Redis."

P8. ¿Cómo construyes el historial de precios?

"Cada vez que el scheduler ejecuta un job y obtiene un precio nuevo para un juego en una tienda, comprueba si el precio ha cambiado respecto al último registrado. Si ha cambiado, inserta un nuevo registro en la tabla PriceHistory con el precio y la fecha. La gráfica del frontend simplemente consulta ese historial ordenado por fecha y lo renderiza con Recharts."

---

## Categoría 3 — Frontend y React

P9. ¿Qué es un Context en React y cómo lo usas?

"React Context es un mecanismo para compartir estado entre componentes sin tener que pasarlo como props por cada nivel del árbol de componentes, lo que se llama prop drilling. Tengo dos contextos: AuthContext, que expone el usuario autenticado, si está cargando y la función de logout a toda la aplicación; y WishlistContext, que expone los items de la wishlist y el contador para el badge de la navbar. Cualquier componente puede acceder a estos datos con el hook useContext."

P10. ¿Qué es el debounce y por qué lo usas en el buscador?

"El debounce es una técnica que retrasa la ejecución de una función hasta que han pasado N milisegundos desde la última vez que se llamó. En el buscador, sin debounce, se lanzaría una petición al backend en cada tecla que el usuario pulsa. Con debounce de 300 ms, solo se lanza una petición cuando el usuario deja de escribir durante 300 ms. Esto reduce significativamente el número de peticiones y mejora la experiencia de usuario."

P11. ¿Por qué usas Tailwind CSS y no CSS normal o un framework como Bootstrap?

"Tailwind es utility-first: en lugar de escribir clases CSS semánticas, combinas clases utilitarias directamente en el JSX. Esto tiene dos ventajas principales: no hay que cambiar de archivo entre JSX y CSS, lo que acelera el desarrollo; y el CSS final solo contiene las clases que realmente usas, lo que hace el bundle más pequeño. Bootstrap tiene componentes predefinidos que aceleran el prototipado pero limitan la personalización."

P12. ¿Qué es Vite y por qué lo elegiste sobre Create React App?

"Vite es un bundler moderno que usa ES modules nativos del navegador durante el desarrollo, lo que hace que el servidor de desarrollo arranque casi instantáneamente y los cambios se reflejen en menos de 100 ms. Create React App usa Webpack, que es más lento en proyectos grandes. Vite es actualmente el estándar recomendado para proyectos React nuevos."

---

## Categoría 4 — Base de datos y seguridad

P13. ¿Cómo están relacionadas las tablas de tu base de datos?

"Las tablas principales son: Game (información del juego), Store (tiendas), Deal (oferta actual de un juego en una tienda, con precio y descuento), PriceHistory (historial de precios), User (usuarios registrados), WishlistItem (relación many-to-many entre usuarios y juegos) y Alert (alertas de precio de un usuario para un juego con un precio objetivo). Las relaciones son: un Game tiene muchos Deals, un Deal pertenece a un Game y una Store, PriceHistory se asocia a un Game y una Store, WishlistItem une User con Game, y Alert une User con Game."

P14. ¿Qué es el problema N+1 y cómo lo resuelves?

"El problema N+1 ocurre cuando cargas una lista de N objetos y luego haces una consulta adicional por cada objeto para cargar sus relaciones, resultando en N+1 consultas en total. Por ejemplo, si cargo 100 ofertas y luego accedo a deal.game para cada una, se hacen 101 consultas. Lo resuelvo con joinedload o contains_eager de SQLAlchemy, que carga las relaciones en una sola consulta usando JOINs de SQL."

P15. ¿Cómo almacenas las contraseñas?

"Nunca se almacena la contraseña en texto plano. Uso bcrypt para generar un hash salado de la contraseña en el momento del registro. Cuando el usuario inicia sesión, bcrypt compara la contraseña introducida con el hash almacenado. Aunque alguien accediera a la base de datos, no podría obtener las contraseñas originales."

P16. ¿Qué es CORS y por qué lo configuras?

"CORS (Cross-Origin Resource Sharing) es una política de seguridad del navegador que bloquea las peticiones HTTP desde un origen (dominio + puerto) a otro diferente, a menos que el servidor lo permita explícitamente. Como el frontend está en localhost:5173 y el backend en localhost:8000, son orígenes distintos. En FastAPI configuro el middleware CORSMiddleware para permitir peticiones desde el origen del frontend."

P17. ¿El token JWT expira? ¿Qué pasa cuando expira?

"Sí, los tokens tienen una fecha de expiración configurable. Cuando el token expira, el backend devuelve un error 401 Unauthorized. En el frontend, el AuthContext detecta ese error en las respuestas de la API y ejecuta automáticamente el logout, limpiando el token de localStorage y redirigiendo al usuario a la página de login."

P18. ¿Qué haría diferente si tuviera más tiempo?

"Añadiría tests automatizados tanto en el backend con pytest como en el frontend con Vitest y Testing Library. Implementaría notificaciones push además del email para las alertas. Añadiría más fuentes de precios: GOG tiene una API pública, Green Man Gaming también. Y migraría a PostgreSQL con Docker para facilitar el despliegue en un servidor real. También me gustaría añadir un sistema de reseñas de usuarios para que la comunidad pueda valorar las tiendas."
