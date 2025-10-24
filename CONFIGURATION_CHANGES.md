# Cambios en la Configuración del Proyecto

## Resumen

Se actualizó el sistema de configuración del proyecto para usar archivos JSON en lugar de variables de entorno (`.env`), siguiendo el patrón del proyecto CTA.

## Archivos Modificados

### 1. `bets_project/settings.py`

**Cambios principales:**

- **Sistema de configuración JSON**: Ahora lee de `bets_project/bets.config.json` (desarrollo) o `/etc/bets.config.json` (producción)
- **DEBUG automático**: Se determina automáticamente según la ubicación del archivo de configuración
- **Logging mejorado**:
  - Desarrollo: Logs a consola con formato verbose
  - Producción: Logs a archivos + notificaciones por email para errores 500
- **Seguridad mejorada**: Configuración HSTS, SSL, cookies seguras en producción
- **Nuevas apps**: Añadidas `django.contrib.humanize`, `sendgrid`, `sendgrid_backend`
- **MESSAGE_TAGS**: Configurados para Bootstrap 5
- **FILE_UPLOAD**: Configuración de permisos y límites de tamaño
- **SESSION_COOKIE_AGE**: Cambiado de 10000 a 3600 segundos (1 hora)

### 2. `bets_project/bets.config.json` (nuevo)

Archivo de configuración con las credenciales reales:
```json
{
  "SECRET_KEY": "...",
  "SENDGRID_API_KEY": "...",
  "DB_HOST": "localhost",
  "DB_NAME": "elguaire_lapolla",
  "DB_USER": "web-user-tennis",
  "DB_PASS": "...",
  "DB_PORT": "3306",
  "FROM_EMAIL": "noreply@elguaire.com",
  "SITE_URL": "https://bets.elguaire.com",
  "SITE_NAME": "La Polla - ElGuaire"
}
```

**IMPORTANTE**: Este archivo está en `.gitignore` y NO se sube al repositorio.

### 3. `bets_project/bets.config.json.example` (nuevo)

Plantilla de ejemplo para configuración (sin credenciales reales).

### 4. `.gitignore`

Añadidas líneas para ignorar archivos de configuración:
```
# Configuration files (JSON)
bets_project/bets.config.json
/etc/bets.config.json
```

### 5. `logs/.gitkeep` (nuevo)

Directorio creado para almacenar logs de producción:
- `django_errors.log` - Todos los errores de Django
- `bets_errors.log` - Errores HTTP 500 específicamente

### 6. `CLAUDE.md`

Actualizado con instrucciones sobre el nuevo sistema de configuración JSON.

## Cómo Usar

### Desarrollo

1. Copia el archivo de ejemplo:
```bash
cp bets_project/bets.config.json.example bets_project/bets.config.json
```

2. Edita `bets_project/bets.config.json` con tus credenciales reales

3. El sistema detectará automáticamente que estás en desarrollo (DEBUG=True)

### Producción

1. Crea el archivo en `/etc/bets.config.json` con las credenciales de producción

2. El sistema detectará automáticamente que estás en producción (DEBUG=False)

3. Asegúrate de que el directorio `../logs/` existe y tiene permisos de escritura

## Ventajas del Nuevo Sistema

1. **Más seguro**: El archivo de configuración nunca se sube a git
2. **Más limpio**: Un solo archivo JSON en lugar de múltiples variables de entorno
3. **Más flexible**: Fácil añadir nuevas configuraciones
4. **Mejor logging**: Sistema de logs diferenciado para desarrollo y producción
5. **Notificaciones**: Emails automáticos cuando hay errores 500 en producción
6. **Consistente**: Mismo patrón que el proyecto CTA

## Compatibilidad

- El archivo `.env` anterior **YA NO SE USA**
- Todas las variables se leen del archivo JSON
- No hay dependencia de `python-dotenv` (aunque sigue en requirements.txt para compatibilidad)

## Migración desde .env

Si tenías un archivo `.env`, migra los valores a `bets_project/bets.config.json`:

| Variable .env | Campo JSON |
|---------------|------------|
| SECRET_KEY | SECRET_KEY |
| DEBUG | (automático según ubicación del archivo) |
| DB_NAME | DB_NAME |
| DB_USER | DB_USER |
| DB_PASSWORD | DB_PASS |
| DB_HOST | DB_HOST |
| DB_PORT | DB_PORT |
| SENDGRID_API_KEY | SENDGRID_API_KEY |
| FROM_EMAIL | FROM_EMAIL |
| SITE_URL | SITE_URL |
| SITE_NAME | SITE_NAME |

## Notas Importantes

1. **Nunca subas `bets.config.json` a git** - Está en .gitignore
2. **Genera un nuevo SECRET_KEY** - No uses el de ejemplo
3. **En producción, usa `/etc/bets.config.json`** - Ubicación estándar del sistema
4. **El directorio logs debe existir en producción** - Creado en `/shared/projects/elguaired/logs/`
5. **Configura ADMINS en settings.py** - Para recibir notificaciones de errores

## Testing

Para probar que todo funciona:

```bash
# Activar entorno virtual
source venv_elg/bin/activate

# Verificar que la configuración se carga
python manage.py check

# Probar el servidor
python manage.py runserver
```

Si hay errores, revisa:
1. Que existe `bets_project/bets.config.json`
2. Que el JSON es válido (sin comas extras, etc.)
3. Que todas las claves requeridas están presentes
