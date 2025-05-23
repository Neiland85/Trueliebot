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
