# Lector Rápido RSVP

Una aplicación de escritorio moderna para lectura rápida utilizando el método RSVP (Rapid Serial Visual Presentation). Diseñada para mejorar la velocidad de lectura eliminando los movimientos oculares (sacadas).

## Características

- **Formatos Soportados**: Importa documentos PDF y Word (.docx).
- **Lectura RSVP**: Muestra palabras una a una centradas en un punto óptimo.
- **Interfaz Moderna**: 
  - Diseño oscuro para reducir fatiga visual.
  - Completamente responsiva (se adapta a cualquier tamaño de ventana).
  - Controles intuitivos tipo reproductor multimedia.
- **Personalización**:
  - Control de velocidad (WPM - Palabras por minuto).
  - Selector de tipografía.
  - Selector de color para la letra pivote (punto de enfoque).
- **Algoritmo Inteligente**: Pausas automáticas en palabras largas para una comprensión natural.

## Instalación

1. Clona el repositorio o descarga el código.
2. Instala las dependencias necesarias:

```bash
pip install -r requirements.txt
```

## Uso

Ejecuta el script principal:

```bash
python lector_rapido.py
```

1. Haz clic en **Importar** para cargar un archivo.
2. Ajusta la velocidad (WPM) a tu gusto.
3. Personaliza la fuente y el color si lo deseas.
4. Presiona **INICIAR** para comenzar a leer.

## Requisitos

- Python 3.x
- Librerías listadas en `requirements.txt` (`PyPDF2`, `python-docx`).
- `tkinter` (incluido generalmente con Python).

## Licencia

Este proyecto es de código abierto.

