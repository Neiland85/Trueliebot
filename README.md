# TruelieBot

**TruelieBot** es un bot para analizar conversaciones de WhatsApp y detectar comportamientos sospechosos o manipuladores. Utiliza Flask y machine learning para interactuar con una base de datos y procesar texto.

---

## Clonar el repositorio

Clona el repositorio con el siguiente comando:

```bash
git clone https://github.com/Neiland85/TruelieBot.git
O accede directamente al repositorio en GitHub aquí.

Instalación
1. Crea y activa un entorno virtual:
Para aislar las dependencias del proyecto, crea un entorno virtual:

bash
Copiar código
python3 -m venv .venv
source .venv/bin/activate
2. Instala las dependencias:
Ejecuta el siguiente comando para instalar todas las dependencias necesarias:

bash
Copiar código
pip install -r requirements.txt
3. Crea el archivo .env con tu configuración:
Crea un archivo llamado .env en la raíz del proyecto y agrega tu clave de API de OpenAI:

plaintext
Copiar código
OPENAI_API_KEY=tu_clave_api
Uso
1. Ejecuta la aplicación Flask:
Ejecuta el archivo principal del proyecto para iniciar la aplicación:

bash
Copiar código
python app.py
La aplicación estará disponible en http://127.0.0.1:5000/ (o el puerto que hayas configurado en app.py).

2. Ejecuta las pruebas unitarias:
Para asegurarte de que todo funciona correctamente, ejecuta las pruebas unitarias con:

bash
Copiar código
pytest
Estructura del proyecto
app.py: Archivo principal para ejecutar la aplicación Flask.
initialize_db.py: Script para inicializar la base de datos.
test_app.py: Pruebas unitarias para validar el funcionamiento del proyecto.
requirements.txt: Lista de dependencias necesarias para el proyecto.
.env: Archivo con configuraciones sensibles como claves API (excluido del repositorio).
.flake8: Configuración para el linter Flake8.
README.md: Documentación básica del proyecto.
Contribuciones
¡Las contribuciones son bienvenidas! Si encuentras algo que mejorar o agregar, abre un issue o pull request en el repositorio. Por favor, sigue estas pautas de colaboración:

Crea una rama para tus cambios:

bash
Copiar código
git checkout -b feature/nombre-de-tu-cambio
Asegúrate de que el código pase las pruebas antes de enviar tu pull request:

bash
Copiar código
pytest
Describe claramente qué problema resuelve tu contribución en el pull request.

Verificaciones recomendadas
1. Bases de datos locales:
Si conversations.db es una base de datos temporal, ya está excluida del repositorio a través del .gitignore.
Si necesitas generarla, utiliza el script initialize_db.py y documenta su uso en este README.
2. Dependencias adicionales:
Si utilizas funciones avanzadas de paquetes como numpy o pandas, verifica que estén incluidas en requirements.txt.
3. Cobertura de pruebas:
Asegúrate de que test_app.py cubra las funciones principales del proyecto. Si es necesario, añade casos adicionales.
Licencia
Este proyecto está bajo la licencia MIT. Siéntete libre de usarlo, modificarlo y distribuirlo.

yaml
Copiar código

---

### **Puntos destacados del archivo `README.md`**

1. **Clonación del repositorio**:
   Instrucciones claras para clonar el proyecto y acceder al repositorio.

2. **Instalación**:
   Pasos detallados para configurar el entorno virtual, instalar dependencias y crear el archivo `.env`.

3. **Uso**:
   Explicación sobre cómo ejecutar la aplicación y las pruebas.

4. **Estructura del proyecto**:
   Una descripción clara de los archivos principales para que otros desarrolladores comprendan su propósito.

5. **Contribuciones**:
   Guía para colaborar con el proyecto siguiendo las mejores prácticas.

6. **Verificaciones recomendadas**:
   Información para asegurarse de que todo funcione correctamente.

7. **Licencia**:
   Indica cómo se puede usar el proyecto.

---

## Despliegue rápido en Heroku/Render

### Heroku
1. Instala Heroku CLI y haz login.
2. Ejecuta:
   ```bash
   heroku create nombre-de-tu-app
   heroku config:set OPENAI_API_KEY=tu_clave_openai
   git push heroku main
   heroku open
   ```
## Autenticación de endpoints

Los endpoints sensibles (/api/feedback, /api/patrones, /api/estadisticas) ahora están protegidos con autenticación JWT.

### Obtener un token de autenticación

Para obtener un token, utiliza el nuevo endpoint `/api/auth/login`:

```sh
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"usuario_id": 1, "password": "trueliebot-admin-demo", "role": "admin"}'
```
### Render
1. Ve a https://dashboard.render.com y crea un nuevo Web Service.
2. Elige tu repo y configura:
   - Start command: `python app.py`
   - Environment: Python 3.11
   - Añade la variable OPENAI_API_KEY

### Docker (opcional)
Si quieres usar Docker, crea un archivo `Dockerfile` así:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --upgrade pip && pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "app.py"]
```

Luego ejecuta:
```bash
docker build -t trueliebot .
docker run -p 5000:5000 trueliebot
```

### Pruebas Endpoint de integración con OpenAI

### `/api/openai` (POST)

Permite enviar un prompt y obtener una respuesta generada por OpenAI GPT-3.5-turbo.

**Request:**
```json
{
  "prompt": "¿Cuál es la capital de Francia?"
}
```

**Response (producción):**
```json
{
  "response": "París"
}
```

**Modo Mock para pruebas locales**

Si defines la variable de entorno `MOCK_OPENAI=1`, el endpoint responderá siempre con `"París"` sin consumir tu cuota de OpenAI. Esto permite testear y desarrollar sin depender de la API real.

**Ejemplo de uso en local:**

```sh
export MOCK_OPENAI=1
python app.py
```

**Test automatizado:**

El endpoint está cubierto por tests automáticos. Si usas `MOCK_OPENAI=1`, los tests no requieren acceso real a la API de OpenAI.

## Integración de cita científica y consejos en `/api/openai`

Ahora el endpoint `/api/openai` no solo responde con la respuesta generada por OpenAI, sino que también analiza el prompt recibido. Si detecta palabras clave relacionadas con manipulación, mentira o técnicas de detección, la respuesta incluirá automáticamente:
- `study_citation`: cita científica relevante.
- `study_summary`: resumen del estudio científico.
- `advice`: lista de consejos para afrontar situaciones de manipulación o engaño.

### Ejemplo de uso

**Request:**
```json
{
  "prompt": "¿Cómo detectar una microexpresión en una conversación?"
}
```

**Response:**
```json
{
  "response": "Las microexpresiones son expresiones faciales involuntarias...",  
  "study_citation": "Ekman, P., & Friesen, W. V. (1975). Unmasking the face.",
  "study_summary": "Identificación de microexpresiones faciales involuntarias que delatan emociones ocultas.",
  "advice": [
    "Mantén la calma: No respondas con ira ni impulsividad, respira profundo antes de actuar.",
    "No te culpes: Recuerda que la responsabilidad de la mentira o manipulación es del depredador, no tuya.",
    "Documenta los hechos: Lleva un registro de las situaciones, mensajes o comportamientos sospechosos.",
    "Evita la confrontación directa: Si es posible, busca el diálogo en un entorno seguro y sin acusaciones.",
    "Haz preguntas abiertas: Permite que la otra persona explique, en vez de acusar directamente.",
    "Busca apoyo: Habla con amigos, familiares o un profesional sobre lo que estás viviendo.",
    "Pon límites claros: Expresa de manera asertiva lo que no toleras y cuáles son tus valores.",
    "No te aísles: Mantén tu red de apoyo y actividades que te hagan sentir bien.",
    "Infórmate: Aprende sobre técnicas de manipulación y cómo protegerte emocionalmente.",
    "Si la situación es grave, busca ayuda profesional o legal: Tu bienestar y seguridad son lo más importante."
  ]
}
```

Si el prompt no contiene ninguna palabra clave relevante, la respuesta será únicamente el campo `response` con la respuesta generada por OpenAI.

## Citas científicas automáticas en las conversaciones

Cuando envías un mensaje a `/api/conversations` que contiene palabras clave relacionadas con estudios científicos sobre detección de mentiras (por ejemplo: "microexpresion", "cognitivo", "resonancia", "paraverbal", "scan", "inteligencia artificial", "emocional"), el bot responde automáticamente con la cita y el resumen relevante del estudio correspondiente.

### Ejemplo de uso

**Request:**
```json
{
  "profile": "test",
  "message": "El análisis de microexpresion es clave para detectar mentiras."
}
```

**Response:**
```json
{
  "message": "Conversation created",
  "study_citation": "Ekman, P., & Friesen, W. V. (1975). Unmasking the face.",
  "study_summary": "Identificación de microexpresiones faciales involuntarias que delatan emociones ocultas."
}
```

## Ejemplo de respuesta automática con cita y consejos

Si envías un mensaje a `/api/conversations` que contenga una palabra clave relacionada con manipulación o engaño, la respuesta incluirá:
- Mensaje de éxito
- Cita y resumen científico relevante
- Guion de consejos para afrontar la situación

**Request:**
```json
{
  "profile": "test",
  "message": "El análisis de microexpresion es clave para detectar mentiras."
}
```

**Response:**
```json
{
  "message": "Conversation created",
  "study_citation": "Ekman, P., & Friesen, W. V. (1975). Unmasking the face.",
  "study_summary": "Identificación de microexpresiones faciales involuntarias que delatan emociones ocultas.",
  "advice": [
    "Mantén la calma: No respondas con ira ni impulsividad, respira profundo antes de actuar.",
    "No te culpes: Recuerda que la responsabilidad de la mentira o manipulación es del depredador, no tuya.",
    "Documenta los hechos: Lleva un registro de las situaciones, mensajes o comportamientos sospechosos.",
    "Evita la confrontación directa: Si es posible, busca el diálogo en un entorno seguro y sin acusaciones.",
    "Haz preguntas abiertas: Permite que la otra persona explique, en vez de acusar directamente.",
    "Busca apoyo: Habla con amigos, familiares o un profesional sobre lo que estás viviendo.",
    "Pon límites claros: Expresa de manera asertiva lo que no toleras y cuáles son tus valores.",
    "No te aísles: Mantén tu red de apoyo y actividades que te hagan sentir bien.",
    "Infórmate: Aprende sobre técnicas de manipulación y cómo protegerte emocionalmente.",
    "Si la situación es grave, busca ayuda profesional o legal: Tu bienestar y seguridad son lo más importante."
  ]
}
```

## Endpoints de Feedback y Aprendizaje Continuo

### Feedback sobre análisis
- `POST /api/feedback`
  - Registra feedback de usuario sobre un análisis.
  - JSON: `{ "analisis_id": int, "usuario_id": int, "tipo": "positivo|negativo|sugerencia", "comentario": str }`
- `GET /api/feedback/<analisis_id>`
  - Consulta feedback asociado a un análisis.

### Patrones de manipulación
- `POST /api/patrones`
  - Registra un nuevo patrón (expresión regular, descripción, validado, creado_por).
- `GET /api/patrones`
  - Lista todos los patrones registrados.

### Estadísticas de aprendizaje
- `GET /api/estadisticas`
  - Devuelve estadísticas básicas de uso, feedback y patrones validados.

### Ejemplo de flujo
1. El usuario o sistema registra un análisis de conversación.
2. Se puede registrar feedback sobre ese análisis (positivo, negativo, sugerencia).
3. Se pueden registrar y consultar patrones de manipulación detectados.
4. El bot puede consultar estadísticas para ajustar su comportamiento o mostrar resultados a administradores.

Estos endpoints permiten realimentar y mejorar el bot de forma continua, facilitando el aprendizaje y la adaptación a nuevos patrones de manipulación o feedback de usuarios.

## Tabla resumen de endpoints REST

| Endpoint                | Método | Descripción                                                      |
|------------------------|--------|------------------------------------------------------------------|
| /api/feedback          | POST   | Registrar feedback de usuario sobre un análisis                  |
| /api/feedback/<id>     | GET    | Consultar feedback asociado a un análisis                        |
| /api/patrones          | POST   | Registrar un nuevo patrón de manipulación                        |
| /api/patrones          | GET    | Listar todos los patrones registrados                            |
| /api/estadisticas      | GET    | Consultar estadísticas de uso, feedback y patrones validados     |

---

## Diagrama de flujo: Realimentación y Aprendizaje

```
Usuario/Sistema
     |
     v
[Registrar análisis de conversación]
     |
     v
[Registrar feedback sobre análisis] <---+         +---> [Registrar patrón de manipulación]
     |                                  |         |
     v                                  |         v
[Base de datos sofisticada] <-----------+----+-->[Consultar patrones]
     |
     v
[Consultar estadísticas] <--------------+----+-->[Ajuste del bot / Aprendizaje]
```

---

## Exportar/Importar colección Postman

1. **Exportar colección:**
   - En Postman, haz clic derecho sobre la colección > Exportar > Formato v2.1.
   - Guarda el archivo `.json` y compártelo con tu equipo.
2. **Importar colección:**
   - Haz clic en “Importar” en Postman y selecciona el archivo `.json` exportado.

Puedes automatizar esto con scripts o integrarlo en tu CI/CD si lo deseas.

---

## Ejemplos avanzados de uso con curl y Postman

### Registrar feedback con autenticación (ejemplo de header opcional)
```sh
curl -X POST http://localhost:5000/api/feedback \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <tu_token>" \
  -d '{"analisis_id": 1, "usuario_id": 1, "tipo": "positivo", "comentario": "¡Muy útil!"}'
```

### Consultar patrones con header personalizado
```sh
curl http://localhost:5000/api/patrones \
  -H "X-Admin: true"
```

### Importar endpoints en Postman
- Copia la URL y el body de los ejemplos anteriores.
- Añade headers personalizados según sea necesario (por ejemplo, `Authorization`).
- Guarda las respuestas para análisis posterior.

---

## Preguntas frecuentes (FAQ)

**¿Puedo registrar feedback anónimo?**
- Sí, pero se recomienda asociar el feedback a un usuario para mejor trazabilidad.

**¿Qué ocurre si un patrón no es validado?**
- No será usado por el bot hasta que un administrador lo valide.

**¿Cómo se usan las estadísticas?**
- Permiten a admins y desarrolladores ajustar reglas, detectar abusos y mejorar el aprendizaje automático.

**¿Puedo automatizar la exportación/importación de Postman?**
- Sí, usando scripts o integraciones de CI/CD.

**¿Qué hago si detecto un falso positivo en un patrón?**
- Marca el patrón como no validado y revisa su expresión regular.

---

## Buenas prácticas para administradores y desarrolladores

- **Revisar y validar patrones:** Antes de marcar un patrón como validado, revisa su efectividad y evita falsos positivos.
- **Monitorizar feedback:** Analiza el feedback negativo para mejorar los modelos y reglas del bot.
- **Backup regular:** Realiza copias de seguridad de la base de datos `trueliebot_sophisticated.db` para evitar pérdida de datos.
- **Auditoría de logs:** Consulta la tabla `logs` para detectar anomalías, abusos o patrones emergentes.
- **Actualización de modelos:** Si integras aprendizaje automático, reentrena los modelos periódicamente usando los datos y feedback almacenados.
- **Privacidad:** No almacenes datos personales sensibles sin consentimiento y cumple la normativa vigente (GDPR, LOPD, etc).
- **Pruebas automatizadas:** Mantén y amplía los tests en `test_app.py` para asegurar la calidad y robustez de la API.
- **Documentación:** Actualiza el README y la documentación de endpoints cada vez que añadas nuevas funcionalidades.

---

### **Verificación de token de autenticación**

Para verificar el estado de un token de autenticación, utiliza el endpoint `/api/auth/verify`:

```sh
curl -X GET http://localhost:5000/api/auth/verify \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

Este endpoint te permitirá comprobar si un token es válido y está activo.

```VALUES ('Admin Demo', 'admin@trueliebot.com', 'pbkdf2:sha256:150000$trueliebot-admin-demo', 'admin');INSERT INTO usuarios (nombre, email, password_hash, rol)-- Usuario administrador (contraseña: trueliebot-admin-demo)VALUES ('Usuario Demo', 'demo@trueliebot.com', 'pbkdf2:sha256:150000$trueliebot-demo', 'user');INSERT INTO usuarios (nombre, email, password_hash, rol)-- Usuario de prueba (contraseña: trueliebot-demo));    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP    activo BOOLEAN NOT NULL DEFAULT TRUE,    rol TEXT NOT NULL DEFAULT 'user',    password_hash TEXT NOT NULL,    email TEXT UNIQUE NOT NULL,    nombre TEXT NOT NULL,    id INTEGER PRIMARY KEY AUTOINCREMENT,CREATE TABLE IF NOT EXISTS usuarios (```sqlSi quieres implementar una autenticación completa, deberías crear una tabla de usuarios en la base de datos:## 5. Añadir tabla de usuarios (opcional pero recomendado)

```sql
CREATE TABLE IF NOT EXISTS usuarios (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  rol TEXT NOT NULL DEFAULT 'user'
);
```
Este es un ejemplo de cómo podrías estructurar la tabla de usuarios en SQLite. Asegúrate de adaptarlo a tu base de datos y lenguaje de base de datos.
**Response:**
```json
{
  "message": "Token válido",
  "user_id": 1,
  "role": "user"
}
```
