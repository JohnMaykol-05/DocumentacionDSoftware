# NeoNeoBomberman

Campaña de cinco niveles y jefe final, individual o cooperativa en un mismo teclado.
Estética pixel art original, colores vivos y formas cuadradas.
Sin sonido, música, puntuación, ranking ni arquitectura compleja.

## Ejecutar en Windows

Requiere Python 3.10 o superior. Verificado con Python 3.12 y pygame-ce 2.5.7.

1. Extrae todo el ZIP.
2. Abre `instalar.bat` una sola vez para preparar el entorno.
3. Abre `jugar.bat` cada vez que quieras iniciar el juego.

También puedes abrir esta carpeta en VS Code y ejecutar:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Si `py` no está disponible pero tienes Python instalado, usa `python` en su lugar.
No es necesario activar el entorno virtual. Internet solo es necesario para instalar Pygame-ce.

Linux/macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

## Controles

| Acción | Jugador 1 | Jugador 2 |
|---|---|---|
| Movimiento | WASD | Flechas |
| Bomba | Espacio | Enter |
| Pausa | Esc | Esc |

Menú: clic en los botones, o 1 para solo y 2 para cooperativo.
Enter confirma las pantallas de fin de nivel, derrota y pausa; R reintenta desde pausa o derrota.
Al cambiar a otra ventana, el juego se pausa automáticamente.

## Cambios de esta versión

- Título y nombre de ventana: NeoNeoBomberman.
- Pantalla de inicio estática, sin animaciones.
- Suelos de colores por nivel, ladrillos, cajas de madera y bordes cuadrados.
- Fuente de píxeles, menú reducido e interfaz compacta sobre el tablero.
- Eliminada la pantalla de ayuda y todos sus accesos.
- Eliminados las guías, los consejos, las introducciones y los títulos decorativos de la partida.
- Mejoras con dibujos: bomba, llama, bota y corazón; ya no usan letras como iconos.
- Jugadores con casco, rostro, guantes, cinturón y botas; rosa y azul para distinguirlos.
- Exactamente dos sprites por jugador, por tipo de enemigo y para el jefe.
- Animación de pasos al moverse; dos poses alternadas para enemigos y jefe.
- Cuatro enemigos con siluetas, colores y comportamientos diferentes.
- Más enemigos y mayor velocidad progresiva respecto a la primera versión.
- El jefe alterna ataques dirigidos con filas o columnas y acelera en su segunda fase.
- Escalado sin suavizado para conservar los bordes de los píxeles.

## Enemigos

| Aspecto | Tipo | Comportamiento |
|---|---|---|
| Verde, gelatinoso | Babosa | Patrulla y persigue cuando el jugador se acerca. |
| Rojo, con cuernos | Cazador | Busca caminos para perseguir y rodear obstáculos. |
| Amarillo, con antenas | Corredor | Acelera en línea recta al detectar un jugador, con una pausa entre embestidas. |
| Morado, ojos turquesa | Fantasma | Persigue atravesando cajas; los muros y las bombas lo detienen. |

Los enemigos evitan fuego activo y reaccionan a bombas próximas a explotar.
Los cazadores y fantasmas reaccionan antes. El cálculo también reconoce bombas activadas en cadena.
Todos los enemigos normales caen con una explosión: la dificultad depende de su movimiento.

## Reglas

- Las bombas tardan 2,5 segundos; las llamas duran 0,65 segundos.
- Las explosiones también dañan al jugador que las coloca y a su compañero.
- Los muros bloquean el fuego y las cajas detienen la explosión que las destruye.
- Una bomba alcanzada por otra explota en cadena.
- Se puede salir de la bomba recién colocada; después no se puede atravesar.
- Elimina a los enemigos y entra en la puerta de la esquina inferior derecha.
- Los jugadores empiezan cada escenario con tres vidas; vidas y mejoras se reinician al avanzar.
- Si un compañero cae, el otro puede terminar el nivel para recuperarlo.
- Si todos caen, el nivel se puede repetir sin límite de intentos.
- El progreso no se guarda al cerrar la aplicación.

| Icono | Efecto |
|---|---|
| Bomba | Más bombas simultáneas, hasta 3. |
| Llama | Más alcance, hasta 5 casillas. |
| Bota | Mayor velocidad. El número del HUD indica el grado de mejora. |
| Corazón | Recupera una vida, hasta 3. |

Las mejoras permanecen aunque haya fuego encima; espera a que termine para recogerlas.
El contorno bajo una bomba identifica a su propietario.
La puerta se ilumina en verde al desaparecer todos los enemigos.

## Jefe final

Tiene 6 puntos de vida en solitario y 9 en cooperativo.
El escudo azul dura 3 segundos; después queda vulnerable durante 4.
El icono superior cambia de escudo a llama durante la vulnerabilidad.
Anticipa la detonación: las bombas solo dañan al jefe cuando está vulnerable.
Las casillas rojas avisan con 1,25 segundos antes de cada ataque.
Al perder la mitad de su vida aumenta la frecuencia y añade filas o columnas a cada ataque.
Empiezas la arena con dos bombas y alcance de tres casillas.

## Código sencillo

| Archivo | Función |
|---|---|
| `main.py` | Bucle, colisiones, reglas, enemigos, menú y dibujo. |
| `niveles.py` | Datos de los cinco mapas y la arena final. |
| `sprites.py` | Dibujo de dos fotogramas por personaje, iconos y fuente pixelada. |
| `requirements.txt` | Dependencia del proyecto. |
| `test_juego.py` | Pruebas de reglas, enemigos y navegación. |
| `instalar.bat` / `jugar.bat` | Accesos opcionales para Windows. |

Los sprites se generan una sola vez en memoria mediante figuras básicas.
No hay carpetas de recursos externas, gestores adicionales ni jerarquías extensas.
`Actor`, `Bomba` y `Juego` mantienen la estructura de la primera versión.
Para cambiar la dificultad, edita los enemigos y la densidad de cajas en `niveles.py`.
Los mapas usan semillas fijas para conservar su distribución al reintentar.

## Verificación

```powershell
.\.venv\Scripts\python.exe -m unittest -v test_juego.py
```

Incluye 19 pruebas: colisiones, cadenas, pausa, cooperativo, avance, jefe, embestidas,
fantasmas, evasión, ausencia de ayuda y exactamente dos fotogramas distintos por personaje.

## Problemas habituales

- `No module named pygame`: instala `requirements.txt` con el mismo Python que ejecuta el juego.
- `No module named sprites` o `niveles`: extrae el ZIP completo; los tres archivos deben estar juntos.
- Algunos teclados limitan las pulsaciones simultáneas: prueba otro teclado o ajusta las teclas en `main.py`.
- Si aparece un error al abrir, usa `jugar.bat` o la terminal para leerlo.

Mantener en futuras versiones: sin audio ni puntuación y con una estructura pequeña.
Todos los gráficos son originales; no se incluyen recursos del arcade original.
