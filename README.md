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

## Endpoint de integración con OpenAI

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
