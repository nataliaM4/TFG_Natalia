# TFG Natalia · Demo web de segmentación de tumores cerebrales
 
Aplicación web sencilla que permite probar el modelo U-Net entrenado
en este Trabajo de Fin de Grado para la segmentación automática de tumores
cerebrales en imágenes de resonancia magnética (dataset BraTS 2020).
 
Permite elegir un caso del conjunto de test (al azar o desde una galería),
ver sus 4 secuencias MRI (FLAIR, T1, T1ce, T2) y su máscara real, generar la
predicción del modelo, y comparar visualmente el resultado junto con el
coeficiente Dice obtenido.
 
## Estructura del proyecto
 
```
TFG_WEB/
├── app.py                     # Servidor Flask: rutas de página y de API
├── requirements.txt           # Dependencias de Python
│
├── model/
│   └── modelo_final.keras     # Modelo U-Net entrenado
│
├── data/
│   ├── X_demo.npy       # Casos de test ya preprocesados (30, 240, 240, 4)
│   └── y_demo.npy       # Máscaras reales de test (30, 240, 240, 1)
│
├── templates/                 # Páginas HTML (Flask/Jinja)
│   ├── index.html             # Pantalla principal
│   ├── gallery.html           # Galería de los 30 casos de test
│   ├── preview.html           # Vista previa de un caso antes de usarlo
│   └── upload.html            # Página para cargar imágenes propias y generar la predicción
│
├── static/
│   ├── css/style.css
│   ├── js/
│   │   ├── main.js
│   │   ├── gallery.js
│   │   ├── preview.js
│   │   └── upload.js
│   └── img/ejemplo_fondo.png                   # Imagen de fondo (marca de agua), opcional
└── 
```
 
## Instalación y arranque en local
 
1. Clona o descarga este repositorio.
2. Instala las dependencias:
```bash
   pip install -r requirements.txt
```
 
3. Arranca el servidor:
```bash
   python app.py
```
 
4. Abre el navegador en **http://127.0.0.1:5000**
   > ⚠️ No abras `templates/index.html` haciendo doble clic en el archivo:
   > la página necesita que Flask la sirva para funcionar correctamente

## Cómo se usa
 
- **Imagen aleatoria**: carga un caso al azar del conjunto de test.
- **Ver imágenes**: abre una galería con los 30 casos disponibles; al
  hacer clic en uno se abre una vista previa con sus 4 secuencias y la
  máscara real, y un botón "Usar esta imagen" para cargarlo en la
  pantalla principal.
- **Elegir imgen**: abre una pantalla con 4 espacios para cargar imágenes
  propias del usuario. Deben ser de 240x240 píxeles y se deben subir las
  4 secuencias para poder realizar la predicción. En esta página también se
  genera la predicción con el ejemplo subido.
- **Generar predicción**: ejecuta el modelo sobre el caso cargado y
  muestra la máscara predicha junto con el coeficiente Dice respecto a
  la máscara real.

## Modelo y datos
 
El modelo (`model/modelo_final.keras`) se carga con `compile=False`,
ya que esta aplicación solo necesita predecir, no
entrenar.
 
Los arrays de test (`data/X_demo.npy` y `data/y_demo.npy`)
contienen 30 de los 251 casos usados para evaluar el modelo en la
memoria del TFG, ya preprocesados exactamente igual que en el notebook
de entrenamiento (normalización Z-Score, secuencias apiladas en el
orden FLAIR, T1, T1ce, T2).
 
## Notas sobre el despliegue en local
 
El servidor que se arranca con `python app.py` es un servidor de
**desarrollo** (así lo indica el propio aviso de Flask al arrancar):
solo es accesible desde el ordenador donde se ejecuta
(`http://127.0.0.1:5000` = localhost).