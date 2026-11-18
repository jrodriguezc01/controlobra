# PlantaControl

Aplicación local en Python y Streamlit para controlar avances de obra sobre planos. Los datos, las imágenes de los planos y el historial se guardan en `data/obra.db`.

## Inicio en Windows

Desde PowerShell, en la carpeta del proyecto:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Streamlit muestra la dirección local. En otra computadora, crea un entorno con Python 3.12 e instala las dependencias con `python -m pip install -r requirements.txt`.

## Demostración

1. Pulsa **Abrir demo de Briones Luco** en la barra lateral. Se carga la planta 4 del HTML de referencia con 15 departamentos, 27 partidas por departamento y avances simulados. La demo es independiente de las obras existentes.
2. Haz clic en un departamento sobre el plano, selecciona una partida y registra un avance con fecha y observación. En **Dibujar** puedes marcar vértices, previsualizar contornos de OpenCV o corregir un recinto.
3. Cambia la fecha de corte y revisa **Dashboard**, **Matriz**, **Historial** y **Carta Gantt**.
4. Descarga Excel o PDF desde **Informes**. En **Respaldo** puedes exportar el JSON completo y restaurarlo. La restauración sustituye el contenido de la base activa.

## Criterios de cálculo

- El avance programado se interpola linealmente por días calendario. Si inicio y término coinciden, pasa a 100 % en esa fecha.
- El avance real al corte usa el último registro hasta ese día. Si falta un registro, el indicador operativo usa 0 % y el historial muestra la celda vacía.
- El avance se pondera por el peso de cada partida. Si los pesos suman cero, el indicador aparece vacío. Las partidas dadas de baja se conservan en el historial.
- La desviación es real menos programado. Hay atraso por debajo de la tolerancia seleccionada. La severidad se clasifica en leve hasta 10 pp, moderada hasta 20 pp, alta hasta 35 pp y crítica por encima de 35 pp.
- El importador CSV agrega registros de avance. Usa `partida_id`, `fecha_corte` en formato AAAA-MM-DD, `porcentaje_real` y `observacion` opcional. Los ID se incluyen en la hoja **Detalle** del Excel. Si se registra más de un avance en la misma fecha, prevalece el último guardado.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```
