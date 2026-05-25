# GameDeals — Contexto del proyecto

## Qué es este proyecto
Aplicación web de detección y comparación de ofertas de videojuegos, similar a AllKeyShop/IsThereAnyDeal. Agrega precios de múltiples tiendas mediante APIs públicas y scrapers propios.

## Stack tecnológico
- **Backend:** Python + FastAPI + SQLAlchemy + SQLite + APScheduler
- **Frontend:** React + Vite + Tailwind CSS
- **Scraping:** BeautifulSoup4 (páginas estáticas) + Playwright (páginas con JS)
- **Auth:** JWT con bcrypt

## APIs integradas
- CheapShark (precios multi-tienda PC)
- RAWG (metadatos de juegos)
- Steam API (precios en euros)
- Epic Games endpoint público (juegos gratis semanales)
- GamerPower (DLCs y juegos gratuitos)

## Scrapers propios
- Fanatical → BeautifulSoup4
- Humble Bundle → Playwright

## Estructura de carpetas
gamedeals/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routers/
│   │   └── services/
├── frontend/
│   └── (React + Vite)
├── diario_de_desarrollo.docx
├── guia_uso_diario.docx
├── clavetodo.docx
├── CLAUDE.md

## Contexto del desarrollador
- Estudiante de 2.º DAM (Desarrollo de Aplicaciones Multiplataforma)
- Entrega del TFG: 2 de junio de 2026
- Inicio del desarrollo: 5 de mayo de 2026
- Tiempo disponible: ~28 días, 2 horas diarias
- Se usa Claude Code para todo el desarrollo (el desarrollador dirige, Claude programa)
- También hay selectividad (PAU desde FP) en las mismas fechas → prioridad al estudio sobre el TFG

## Plan de desarrollo (resumen)
- **Semana 1 (5–11 may):** Setup, base de datos, APIs principales
- **Semana 2 (12–18 may):** Frontend base, autenticación, scraper Fanatical
- **Semana 3 (19–25 may):** Scraper Humble, historial de precios, wishlist, alertas
- **Semana 4 (26 may–2 jun):** Pulido, documentación, presentación

## Archivos importantes del proyecto
- `diario_de_desarrollo.docx` → registro de sesiones de trabajo (formato Word)
- `guia_uso_diario.docx` → instrucciones actualizadas para arrancar y usar el proyecto (formato Word)
- `clavetodo.docx` → documento de justificación del tech stack + esquema de BD (formato Word)

## Instrucciones para Claude Code — LEER SIEMPRE

Al terminar cada sesión de trabajo, actualiza AUTOMÁTICAMENTE estos archivos usando python-docx:

### 1. diario_de_desarrollo.docx
Añade una nueva entrada al final del documento con este formato:

**Entrada #[N]**
Fecha: [FECHA]

**Prompts recibidos del usuario:**
- Prompt 1: [texto íntegro o resumen fiel del primer prompt recibido]
- Prompt 2: [texto íntegro o resumen fiel del segundo prompt, si lo hay]
- (etc.)

**Resumen de tareas realizadas:**
- [lista de lo que se hizo realmente]

**Estado del proyecto:** [porcentaje estimado de completitud]
**Próxima sesión:** [qué toca hacer según el plan]
**Incidencias:** [problemas encontrados y cómo se resolvieron, o "Ninguna"]

### 2. guia_uso_diario.docx
Actualiza este archivo siempre que cambie algo que afecte a cómo se arranca o usa el proyecto:
- Comandos para arrancar backend y frontend
- Variables de entorno necesarias
- Dependencias nuevas instaladas
- Rutas o endpoints nuevos disponibles
- Cualquier cambio que el desarrollador necesite saber para la siguiente sesión

### 3. clavetodo.docx
Claude Code DEBE actualizar automáticamente este documento (usando python-docx) después de cada sesión si se han añadido tecnologías, librerías, decisiones de arquitectura o cambios en el esquema de la base de datos. Añadir la información en la sección correspondiente del documento (estructura del proyecto, esquema de BD, etc.).

**IMPORTANTE:** La actualización de clavetodo.docx es responsabilidad de Claude Code, NO del desarrollador. Claude Code debe hacerlo automáticamente al final de cada sesión sin necesidad de que se lo pidan.
