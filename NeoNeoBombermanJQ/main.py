
import math
import random
from collections import deque
from dataclasses import dataclass, field

import pygame

from niveles import NIVELES
from sprites import crear_sprites, icono, texto_pixel


# Medidas y reglas fáciles de modificar.
CASILLA = 48
COLUMNAS, FILAS = 15, 11
ANCHO, ALTO = 800, 704
ORIGEN = (40, 144)
MECHA = 2.5
DURACION_FUEGO = 0.65
DIRECCIONES = [(0, -1), (0, 1), (-1, 0), (1, 0)]
FONDO = (27, 25, 54)
PANEL = (43, 43, 83)
TEXTO = (255, 249, 220)
TENUE = (156, 167, 206)
JUGADORES = [(255, 100, 178), (64, 175, 255)]


@dataclass
class Actor:
    """Una única clase pequeña sirve para jugadores y enemigos."""
    x: float
    y: float
    tipo: str = "jugador"
    numero: int = 0
    vidas: int = 3
    velocidad: float = 3.5
    capacidad: int = 1
    alcance: int = 2
    inmune: float = 1.5
    destino: tuple | None = None
    direccion: tuple = (0, 1)
    animacion: float = 0
    impulso: float = 0
    recarga: float = 0

    @property
    def casilla(self):
        return int(self.x + 0.5), int(self.y + 0.5)

    @property
    def vivo(self):
        return self.vidas > 0


@dataclass
class Bomba:
    casilla: tuple
    propietario: int
    alcance: int
    tiempo: float = MECHA
    permiso_salida: set = field(default_factory=set)


class Juego:
    def __init__(self):
        # Inicializar solo vídeo y fuentes evita depender de un dispositivo de audio.
        pygame.display.init()
        self.ventana = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
        pygame.display.set_caption("NeoNeoBomberman")
        self.lienzo = pygame.Surface((ANCHO, ALTO))
        self.reloj = pygame.time.Clock()
        self.sprites = crear_sprites()
        self.iconos = {t: icono(t) for t in ("bomba", "fuego", "botas", "vida", "escudo")}
        self.cache_texto = {}
        self.tiles = []
        self.ejecutando = True
        self.estado = "menu"
        self.cooperativo = False
        self.nivel = 0
        self.botones = []
        self.jugadores = []

    # ---------- Crear y reiniciar la campaña ----------
    def comenzar(self, cooperativo=False):
        self.cooperativo = cooperativo
        self.nivel = 0
        self.cargar_nivel()

    def cargar_nivel(self):
        datos = NIVELES[self.nivel]
        self.azar = random.Random(datos["semilla"])
        self.acento = datos["color"]
        self.mapa = [[1 if x in (0, COLUMNAS - 1) or y in (0, FILAS - 1)
                      or (x % 2 == 0 and y % 2 == 0) else 0
                      for x in range(COLUMNAS)] for y in range(FILAS)]
        self.salida = (13, 9)
        self.bombas = []
        self.fuegos = []
        self.objetos = {}
        self.ocultos = {}
        self.avisos = []
        self.transcurrido = 0
        self.jefe = None
        self.jugadores = [Actor(1, 1, numero=0)]
        if self.cooperativo:
            self.jugadores.append(Actor(13, 1, numero=1))
        velocidades = {"babosa": 1.85, "cazador": 2.30, "corredor": 2.55, "fantasma": 1.70}
        self.enemigos = [Actor(x, y, tipo=t, vidas=1, inmune=0,
                              velocidad=velocidades[t] + 0.08 * self.nivel, recarga=1.0)
                         for x, y, t in datos["enemigos"]]
        # Las esquinas de aparición tienen un pequeño refugio despejado.
        protegidas = {(x, y) for x in range(1, 4) for y in range(1, 4)}
        protegidas |= {(x, y) for x in range(11, 14) for y in range(1, 4)}
        protegidas |= {e.casilla for e in self.enemigos} | {self.salida}
        if self.nivel < 5:
            for y in range(1, FILAS - 1):
                for x in range(1, COLUMNAS - 1):
                    if self.mapa[y][x] == 0 and (x, y) not in protegidas:
                        if self.azar.random() < datos["bloques"]:
                            self.mapa[y][x] = 2
            # Cada mapa incluye mejoras garantizadas, repartidas entre las cajas.
            cajas = [(x, y) for y in range(FILAS) for x in range(COLUMNAS) if self.mapa[y][x] == 2]
            self.azar.shuffle(cajas)
            for pos, mejora in zip(cajas, ["bomba", "fuego", "botas", "vida"] * 3):
                self.ocultos[pos] = mejora
            self.objetos[(3, 1)] = "bomba"
            if self.cooperativo:
                self.objetos[(11, 1)] = "bomba"
        else:
            # Arena abierta en la parte superior y pilares como refugio abajo.
            for y in range(1, 6):
                for x in range(1, COLUMNAS - 1):
                    self.mapa[y][x] = 0
            vida_jefe = 9 if self.cooperativo else 6
            self.jefe = {"pos": (7, 3), "vida": vida_jefe, "max": vida_jefe,
                         "inmune": 0.0, "ataque": 2.8, "patron": 0}
            for jugador in self.jugadores:
                jugador.capacidad = 2
                jugador.alcance = 3
            self.objetos = {(1, 7): "vida", (13, 7): "vida", (7, 9): "fuego"}
        self.crear_tiles(datos["suelo"])
        self.estado = "jugando"

    # ---------- Colisiones y movimiento por casillas ----------
    def dentro(self, pos):
        return 0 <= pos[0] < COLUMNAS and 0 <= pos[1] < FILAS

    def libre(self, pos, actor=None):
        if not self.dentro(pos):
            return False
        terreno = self.mapa[pos[1]][pos[0]]
        if terreno == 1 or (terreno == 2 and not (actor and actor.tipo == "fantasma")):
            return False
        if self.jefe and self.jefe["vida"] > 0 and pos == self.jefe["pos"]:
            return False
        for bomba in self.bombas:
            if bomba.casilla == pos:
                return actor is not None and actor.tipo == "jugador" and actor.numero in bomba.permiso_salida
        return True

    def mover(self, actor, direccion, dt):
        if actor.destino is None and direccion != (0, 0):
            x, y = actor.casilla
            destino = (x + direccion[0], y + direccion[1])
            actor.direccion = direccion
            if self.libre(destino, actor):
                actor.destino = destino
        if actor.destino is not None:
            dx, dy = actor.destino[0] - actor.x, actor.destino[1] - actor.y
            distancia = math.hypot(dx, dy)
            rapidez = actor.velocidad * (1.7 if actor.tipo == "corredor" and actor.impulso > 0 else 1)
            paso = rapidez * dt
            actor.animacion += dt * (11 if actor.impulso > 0 else 7)
            if distancia <= paso:
                actor.x, actor.y = actor.destino
                actor.destino = None
            else:
                actor.x += dx / distancia * paso
                actor.y += dy / distancia * paso
        else:
            actor.animacion = 0

    def colocar_bomba(self, jugador):
        if not jugador.vivo:
            return
        pos = jugador.casilla
        if any(b.casilla == pos for b in self.bombas):
            return
        if sum(b.propietario == jugador.numero for b in self.bombas) >= jugador.capacidad:
            return
        permiso = {j.numero for j in self.jugadores if j.vivo and j.casilla == pos}
        self.bombas.append(Bomba(pos, jugador.numero, jugador.alcance, permiso_salida=permiso))

    def zona_explosion(self, origen, alcance):
        celdas = {origen}
        for dx, dy in DIRECCIONES:
            for paso in range(1, alcance + 1):
                pos = (origen[0] + dx * paso, origen[1] + dy * paso)
                if not self.dentro(pos) or self.mapa[pos[1]][pos[0]] == 1:
                    break
                celdas.add(pos)
                if self.mapa[pos[1]][pos[0]] == 2 or any(b.casilla == pos for b in self.bombas):
                    break
        return celdas

    def explotar(self, primera):
        """Resolver toda la cadena una sola vez; las cajas se quitan al final."""
        pendientes = [primera]
        resueltas = []
        zonas = []
        while pendientes:
            bomba = pendientes.pop()
            if any(bomba is b for b in resueltas):
                continue
            resueltas.append(bomba)
            zona = self.zona_explosion(bomba.casilla, bomba.alcance)
            zonas.append(zona)
            for otra in self.bombas:
                if otra.casilla in zona and not any(otra is b for b in resueltas):
                    pendientes.append(otra)
        for bomba in resueltas:
            self.bombas.remove(bomba)
        destruidas = set()
        for zona in zonas:
            self.fuegos.append({"celdas": zona, "tiempo": DURACION_FUEGO,
                                "jefe_golpeado": False, "bomba": True})
            for x, y in zona:
                if self.mapa[y][x] == 2:
                    destruidas.add((x, y))
        for x, y in destruidas:
            self.mapa[y][x] = 0
            if (x, y) in self.ocultos:
                self.objetos[(x, y)] = self.ocultos.pop((x, y))

    def peligros(self, anticipacion):
        """Amenazas próximas; una cadena adelanta también la segunda bomba."""
        peligro = set().union(*(f["celdas"] for f in self.fuegos)) if self.fuegos else set()
        zonas = [self.zona_explosion(b.casilla, b.alcance) for b in self.bombas]
        tiempos = [b.tiempo for b in self.bombas]
        for _ in self.bombas:
            for i, zona in enumerate(zonas):
                for j, bomba in enumerate(self.bombas):
                    if bomba.casilla in zona:
                        tiempos[j] = min(tiempos[j], tiempos[i])
        for zona, tiempo in zip(zonas, tiempos):
            if tiempo <= anticipacion:
                peligro |= zona
        for aviso in self.avisos:
            if aviso["tiempo"] <= anticipacion:
                peligro |= aviso["celdas"]
        return peligro

    def buscar_paso(self, enemigo, objetivos, peligro, escapar=False):
        """Búsqueda corta compartida por los perseguidores y las huidas."""
        cola = deque([(enemigo.casilla, None)])
        vistos = {enemigo.casilla}
        fuego = set().union(*(f["celdas"] for f in self.fuegos)) if self.fuegos else set()
        while cola:
            pos, paso = cola.popleft()
            if paso is not None and ((escapar and pos not in peligro) or (not escapar and pos in objetivos)):
                return paso
            for dx, dy in DIRECCIONES:
                vecina = (pos[0] + dx, pos[1] + dy)
                if (vecina not in vistos and self.libre(vecina, enemigo) and vecina not in fuego
                        and (escapar or vecina not in peligro)):
                    vistos.add(vecina)
                    cola.append((vecina, paso or (dx, dy)))
        return None

    def direccion_enemigo(self, enemigo):
        x, y = enemigo.casilla
        anticipacion = 0.8 if enemigo.tipo in ("cazador", "fantasma") else 0.50
        peligro = self.peligros(anticipacion)
        fuego = set().union(*(f["celdas"] for f in self.fuegos)) if self.fuegos else set()
        opciones = [d for d in DIRECCIONES if self.libre((x + d[0], y + d[1]), enemigo)
                    and (x + d[0], y + d[1]) not in fuego]
        if not opciones:
            enemigo.impulso = 0
            return (0, 0)
        if enemigo.casilla in peligro:
            paso = self.buscar_paso(enemigo, set(), peligro, escapar=True)
            if paso:
                enemigo.impulso = 0
                return paso
        seguras = [d for d in opciones if (x + d[0], y + d[1]) not in peligro]
        opciones = seguras or opciones
        vivos = [j for j in self.jugadores if j.vivo]
        if not vivos:
            return (0, 0)
        cercano = min(vivos, key=lambda j: abs(j.x - x) + abs(j.y - y))
        distancia = abs(cercano.x - x) + abs(cercano.y - y)
        if enemigo.tipo == "corredor":
            if enemigo.impulso > 0 and enemigo.direccion in opciones:
                return enemigo.direccion
            if enemigo.recarga <= 0:
                for dx, dy in opciones:
                    for pasos in range(1, 6):
                        pos = (x + dx * pasos, y + dy * pasos)
                        if not self.libre(pos, enemigo) or pos in peligro:
                            break
                        if pos == cercano.casilla:
                            enemigo.impulso = 0.65
                            enemigo.recarga = 2.3
                            return (dx, dy)
        # El verde patrulla, pero persigue al acercarse; rojo y fantasma buscan siempre.
        if enemigo.tipo in ("cazador", "fantasma") or (enemigo.tipo == "babosa" and distancia <= 4):
            paso = self.buscar_paso(enemigo, {j.casilla for j in vivos}, peligro)
            if paso:
                return paso
        # El corredor intenta cerrar distancia incluso antes de ver una línea de embestida.
        if enemigo.tipo == "corredor" and self.azar.random() < 0.65:
            return min(opciones, key=lambda d: abs(x + d[0] - cercano.x) + abs(y + d[1] - cercano.y))
        inversa = (-enemigo.direccion[0], -enemigo.direccion[1])
        opciones = [d for d in opciones if d != inversa] or opciones
        if enemigo.direccion in opciones and self.azar.random() < 0.75:
            return enemigo.direccion
        return self.azar.choice(opciones)

    # ---------- Reglas del jefe y actualización de la partida ----------
    def jefe_abierto(self):
        return self.transcurrido % 7 >= 3

    def actualizar_jefe(self, dt):
        if not self.jefe or self.jefe["vida"] <= 0:
            return
        self.jefe["inmune"] = max(0, self.jefe["inmune"] - dt)
        self.jefe["ataque"] -= dt
        if self.jefe["ataque"] <= 0:
            celdas = set()
            for jugador in self.jugadores:
                if jugador.vivo:
                    celdas |= self.zona_explosion(jugador.casilla, 1)
            furioso = self.jefe["vida"] <= self.jefe["max"] / 2
            patron = self.jefe["patron"]
            if furioso or patron % 3 == 1:
                if patron % 2 == 0:
                    fila = self.azar.choice([3, 5, 7, 9])
                    celdas |= {(x, fila) for x in range(1, 14)}
                else:
                    columna = self.azar.choice([3, 5, 7, 9, 11])
                    celdas |= {(columna, y) for y in range(1, 10)}
            self.avisos.append({"celdas": celdas, "tiempo": 1.25})
            self.jefe["patron"] += 1
            self.jefe["ataque"] = 2.0 if furioso else 2.8

    def herir(self, jugador):
        if jugador.vivo and jugador.inmune <= 0:
            jugador.vidas -= 1
            jugador.inmune = 1.8

    def actualizar(self, dt, teclas):
        if self.estado != "jugando":
            return
        self.transcurrido += dt
        for jugador in self.jugadores:
            jugador.inmune = max(0, jugador.inmune - dt)
            if not jugador.vivo:
                continue
            arriba, abajo, izquierda, derecha = (
                (pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d) if jugador.numero == 0
                else (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT))
            direccion = (0, 0)
            for tecla, vector in ((arriba, (0, -1)), (abajo, (0, 1)),
                                  (izquierda, (-1, 0)), (derecha, (1, 0))):
                if teclas[tecla]:
                    direccion = vector
                    break
            self.mover(jugador, direccion, dt)
            mejora = self.objetos.pop(jugador.casilla, None)
            if mejora == "bomba":
                jugador.capacidad = min(3, jugador.capacidad + 1)
            elif mejora == "fuego":
                jugador.alcance = min(5, jugador.alcance + 1)
            elif mejora == "botas":
                jugador.velocidad = min(4.8, jugador.velocidad + 0.4)
            elif mejora == "vida":
                jugador.vidas = min(3, jugador.vidas + 1)
        for bomba in self.bombas:
            bomba.permiso_salida &= {j.numero for j in self.jugadores if j.vivo and j.casilla == bomba.casilla}
        # Enemigos: decidir únicamente al llegar al centro de una casilla.
        for enemigo in self.enemigos:
            if enemigo.vivo:
                enemigo.impulso = max(0, enemigo.impulso - dt)
                enemigo.recarga = max(0, enemigo.recarga - dt)
                direccion = self.direccion_enemigo(enemigo) if enemigo.destino is None else (0, 0)
                self.mover(enemigo, direccion, dt)
        for fuego in self.fuegos:
            fuego["tiempo"] -= dt
        self.fuegos = [f for f in self.fuegos if f["tiempo"] > 0]
        for bomba in self.bombas[:]:
            bomba.tiempo -= dt
        fuego_actual = set().union(*(f["celdas"] for f in self.fuegos)) if self.fuegos else set()
        for bomba in self.bombas[:]:
            if bomba in self.bombas and (bomba.tiempo <= 0 or bomba.casilla in fuego_actual):
                self.explotar(bomba)
        self.actualizar_jefe(dt)
        for aviso in self.avisos[:]:
            aviso["tiempo"] -= dt
            if aviso["tiempo"] <= 0:
                self.fuegos.append({"celdas": aviso["celdas"], "tiempo": 0.65,
                                    "jefe_golpeado": True, "bomba": False})
                self.avisos.remove(aviso)
        for fuego in self.fuegos:
            for jugador in self.jugadores:
                if jugador.casilla in fuego["celdas"]:
                    self.herir(jugador)
            for enemigo in self.enemigos:
                if enemigo.casilla in fuego["celdas"]:
                    enemigo.vidas = 0
            if (self.jefe and self.jefe["vida"] > 0 and fuego["bomba"]
                    and self.jefe["pos"] in fuego["celdas"] and not fuego["jefe_golpeado"]):
                # Cada explosión se evalúa una sola vez contra el escudo.
                fuego["jefe_golpeado"] = True
                if self.jefe_abierto() and self.jefe["inmune"] <= 0:
                    self.jefe["vida"] -= 1
                    self.jefe["inmune"] = 0.7
        self.enemigos = [e for e in self.enemigos if e.vivo]
        for jugador in self.jugadores:
            if any(math.hypot(jugador.x - e.x, jugador.y - e.y) < 0.65 for e in self.enemigos):
                self.herir(jugador)
        if not any(j.vivo for j in self.jugadores):
            self.estado = "derrota"
        elif self.jefe and self.jefe["vida"] <= 0:
            self.estado = "victoria"
        elif self.nivel < 5 and not self.enemigos:
            if any(j.vivo and j.casilla == self.salida for j in self.jugadores):
                self.estado = "completado"

    # ---------- Entrada: teclado y botones ----------
    def accion(self, nombre):
        if nombre == "solo":
            self.comenzar(False)
        elif nombre == "coop":
            self.comenzar(True)
        elif nombre == "continuar":
            self.estado = "jugando"
        elif nombre == "siguiente":
            self.nivel += 1
            self.cargar_nivel()
        elif nombre == "reintentar":
            self.cargar_nivel()
        elif nombre == "menu":
            self.estado = "menu"
        elif nombre == "salir":
            self.ejecutando = False

    def posicion_raton(self, pos):
        ancho, alto = self.ventana.get_size()
        escala = min(ancho / ANCHO, alto / ALTO)
        return ((pos[0] - (ancho - ANCHO * escala) / 2) / escala,
                (pos[1] - (alto - ALTO * escala) / 2) / escala)

    def evento(self, evento):
        if evento.type == pygame.QUIT:
            self.ejecutando = False
        elif evento.type == pygame.WINDOWFOCUSLOST and self.estado == "jugando":
            self.estado = "pausa"
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos = self.posicion_raton(evento.pos)
            for rect, accion in self.botones:
                if rect.collidepoint(pos):
                    self.accion(accion)
                    break
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                if self.estado == "jugando":
                    self.estado = "pausa"
                elif self.estado == "pausa":
                    self.estado = "jugando"
                else:
                    self.estado = "menu"
                return
            if self.estado == "menu":
                if evento.key in (pygame.K_1, pygame.K_RETURN):
                    self.comenzar(False)
                elif evento.key == pygame.K_2:
                    self.comenzar(True)
            elif self.estado == "jugando":
                if evento.key == pygame.K_SPACE:
                    self.colocar_bomba(self.jugadores[0])
                elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.cooperativo:
                    self.colocar_bomba(self.jugadores[1])
            elif evento.key == pygame.K_RETURN:
                acciones = {"completado": "siguiente", "derrota": "reintentar",
                            "pausa": "continuar", "victoria": "menu"}
                if self.estado in acciones:
                    self.accion(acciones[self.estado])
            elif evento.key == pygame.K_r and self.estado in ("derrota", "pausa"):
                self.cargar_nivel()

    # ---------- Pixel art e interfaz mínima ----------
    def texto(self, texto, x, y, escala=2, color=TEXTO, centro=False):
        clave = (texto, escala, color)
        if clave not in self.cache_texto:
            self.cache_texto[clave] = texto_pixel(texto, escala, color)
        imagen = self.cache_texto[clave]
        r = imagen.get_rect(center=(x, y)) if centro else imagen.get_rect(topleft=(x, y))
        self.lienzo.blit(imagen, r)

    def caja(self, rect, color=PANEL, borde=(107, 117, 176)):
        rect = pygame.Rect(rect)
        pygame.draw.rect(self.lienzo, (12, 13, 33), rect.move(4, 4))
        pygame.draw.rect(self.lienzo, color, rect)
        pygame.draw.rect(self.lienzo, borde, rect, 2)
        pygame.draw.line(self.lienzo, tuple(min(255, c + 20) for c in color),
                         (rect.x + 3, rect.y + 3), (rect.right - 4, rect.y + 3), 2)

    def rect_casilla(self, pos, margen=0):
        return pygame.Rect(ORIGEN[0] + pos[0] * CASILLA + margen,
                           ORIGEN[1] + pos[1] * CASILLA + margen,
                           CASILLA - 2 * margen, CASILLA - 2 * margen)

    def boton(self, etiqueta, x, y, ancho, accion, principal=False):
        r = pygame.Rect(x, y, ancho, 48)
        encima = r.collidepoint(self.posicion_raton(pygame.mouse.get_pos()))
        color = (255, 209, 69) if principal else ((88, 102, 177) if encima else (59, 67, 123))
        self.caja(r, color, (255, 245, 175) if principal else (144, 169, 236))
        self.texto(etiqueta, r.centerx, r.centery, 2, FONDO if principal else TEXTO, True)
        if encima:
            self.texto(">", x + 10, r.centery, 2, FONDO if principal else TEXTO, True)
        self.botones.append((r, accion))

    def crear_tiles(self, suelo):
        self.tiles = []
        for variante in range(2):
            t = pygame.Surface((16, 16))
            tono = tuple(max(0, c - variante * 5) for c in suelo)
            t.fill(tono)
            oscuro = tuple(max(0, c - 12) for c in tono)
            claro = tuple(min(255, c + 9) for c in tono)
            pygame.draw.line(t, oscuro, (0, 15), (15, 15))
            pygame.draw.line(t, oscuro, (15, 0), (15, 15))
            for x, y in ((3, 5), (11, 11)) if variante else ((5, 11), (12, 3)):
                pygame.draw.rect(t, claro, (x, y, 2, 1))
            self.tiles.append(pygame.transform.scale(t, (48, 48)))
        muro = pygame.Surface((16, 16))
        muro.fill((44, 48, 82))
        pygame.draw.rect(muro, (125, 142, 185), (1, 1, 14, 14))
        pygame.draw.rect(muro, (190, 206, 235), (1, 1, 13, 4))
        pygame.draw.rect(muro, (85, 102, 151), (2, 12, 13, 3))
        pygame.draw.line(muro, (76, 89, 135), (1, 8), (14, 8))
        pygame.draw.line(muro, (76, 89, 135), (8, 1), (8, 7))
        pygame.draw.line(muro, (76, 89, 135), (4, 9), (4, 14))
        self.tiles.append(pygame.transform.scale(muro, (48, 48)))
        caja = pygame.Surface((16, 16))
        caja.fill((87, 45, 49))
        pygame.draw.rect(caja, (199, 104, 54), (1, 1, 14, 14))
        pygame.draw.rect(caja, (248, 167, 76), (1, 1, 14, 2))
        for x in (5, 10):
            pygame.draw.rect(caja, (135, 66, 48), (x, 3, 1, 12))
        pygame.draw.rect(caja, (255, 192, 94), (1, 6, 14, 2))
        pygame.draw.rect(caja, (150, 76, 47), (1, 13, 14, 2))
        for x in (2, 12):
            for y in (2, 11):
                pygame.draw.rect(caja, (255, 213, 127), (x, y, 2, 2))
        self.tiles.append(pygame.transform.scale(caja, (48, 48)))

    def dibujar_icono(self, tipo, x, y, medida=32):
        imagen = self.iconos[tipo]
        if medida != 16:
            imagen = pygame.transform.scale(imagen, (medida, medida))
        self.lienzo.blit(imagen, (int(x), int(y)))

    def dibujar_actor(self, actor):
        clave = f"p{actor.numero}" if actor.tipo == "jugador" else actor.tipo
        frame = int(actor.animacion) % 2
        px = ORIGEN[0] + (actor.x + 0.5) * CASILLA
        py = ORIGEN[1] + (actor.y + 0.5) * CASILLA
        if actor.tipo != "fantasma":
            pygame.draw.rect(self.lienzo, (34, 54, 54), (int(px - 15), int(py + 15), 30, 5))
        if actor.impulso > 0:
            pygame.draw.rect(self.lienzo, (255, 237, 107), (int(px - 21), int(py - 25), 42, 46), 2)
        self.lienzo.blit(self.sprites[clave][frame], (int(px - 24), int(py - 30)))

    def dibujar_mapa(self):
        self.caja((ORIGEN[0] - 6, ORIGEN[1] - 6, 732, 540), (24, 31, 52), self.acento)
        for y, fila in enumerate(self.mapa):
            for x, tipo in enumerate(fila):
                tile = self.tiles[(x + y) % 2 if tipo == 0 else tipo + 1]
                self.lienzo.blit(tile, self.rect_casilla((x, y)))
        if self.nivel < 5:
            r = self.rect_casilla(self.salida, 5)
            abierto = not self.enemigos
            pygame.draw.rect(self.lienzo, (24, 38, 56), r)
            pygame.draw.rect(self.lienzo, (109, 250, 192) if abierto else (179, 158, 100), r, 3)
            if abierto:
                pygame.draw.rect(self.lienzo, (68, 189, 155), r.inflate(-12, -6))
                pygame.draw.polygon(self.lienzo, TEXTO, [(r.x + 12, r.y + 9), (r.x + 24, r.centery), (r.x + 12, r.bottom - 9)])
            else:
                for y in (r.y + 12, r.y + 24):
                    pygame.draw.line(self.lienzo, (179, 158, 100), (r.x + 3, y), (r.right - 4, y), 3)
        colores = {"bomba": (116, 200, 255), "fuego": (255, 211, 89),
                   "botas": (129, 249, 207), "vida": (255, 158, 210)}
        for pos, mejora in self.objetos.items():
            r = self.rect_casilla(pos, 5)
            pygame.draw.rect(self.lienzo, (28, 32, 62), r.move(2, 3))
            pygame.draw.rect(self.lienzo, colores[mejora], r)
            pygame.draw.rect(self.lienzo, (255, 247, 215), r, 2)
            self.dibujar_icono(mejora, r.x + 3, r.y + 3)
        for aviso in self.avisos:
            for pos in aviso["celdas"]:
                r = self.rect_casilla(pos, 2)
                pygame.draw.rect(self.lienzo, (255, 95, 116), r, 3)
                if int(self.transcurrido * 7) % 2:
                    pygame.draw.line(self.lienzo, (255, 222, 118), (r.x + 10, r.y + 10), (r.right - 10, r.bottom - 10), 3)
                    pygame.draw.line(self.lienzo, (255, 222, 118), (r.right - 10, r.y + 10), (r.x + 10, r.bottom - 10), 3)
        for bomba in self.bombas:
            r = self.rect_casilla(bomba.casilla)
            self.dibujar_icono("bomba", r.x + 6, r.y + 3, 36)
            color = JUGADORES[bomba.propietario]
            pygame.draw.rect(self.lienzo, color, (r.x + 14, r.bottom - 8, 20, 3))
            if int(bomba.tiempo * 8) % 2:
                pygame.draw.rect(self.lienzo, (255, 243, 176), (r.x + 27, r.y + 1, 6, 6))
        for actor in sorted(self.enemigos + self.jugadores, key=lambda a: a.y):
            if actor.vivo and not (actor.tipo == "jugador" and actor.inmune > 0 and int(self.transcurrido * 10) % 2):
                self.dibujar_actor(actor)
        if self.jefe and self.jefe["vida"] > 0:
            r = self.rect_casilla(self.jefe["pos"])
            self.lienzo.blit(self.sprites["jefe"][int(self.transcurrido * 3) % 2], (r.x - 12, r.y - 20))
            if not self.jefe_abierto():
                escudo = r.inflate(20, 20)
                pygame.draw.rect(self.lienzo, (98, 219, 255), escudo, 3)
                self.dibujar_icono("escudo", r.centerx - 10, r.y - 35, 20)
            elif int(self.transcurrido * 5) % 2:
                pygame.draw.rect(self.lienzo, (255, 216, 82), (r.centerx - 3, r.y - 30, 6, 6))
        for fuego in self.fuegos:
            for pos in fuego["celdas"]:
                r = self.rect_casilla(pos)
                color = (255, 112, 36) if fuego["bomba"] else (255, 61, 107)
                pygame.draw.rect(self.lienzo, color, r.inflate(-6, -6))
                pygame.draw.rect(self.lienzo, (255, 191, 51), r.inflate(-14, -14))
                pygame.draw.rect(self.lienzo, (255, 249, 171), r.inflate(-25, -25))
                for dx, dy in DIRECCIONES:
                    if (pos[0] + dx, pos[1] + dy) in fuego["celdas"]:
                        if dx:
                            conexion = pygame.Rect(r.centerx, r.y + 12, 25, 24) if dx > 0 else pygame.Rect(r.x, r.y + 12, 25, 24)
                        else:
                            conexion = pygame.Rect(r.x + 12, r.centery, 24, 25) if dy > 0 else pygame.Rect(r.x + 12, r.y, 24, 25)
                        pygame.draw.rect(self.lienzo, (255, 191, 51), conexion)

    def tarjeta_jugador(self, jugador, x):
        color = JUGADORES[jugador.numero]
        self.caja((x, 18, 244, 94), PANEL, color)
        self.lienzo.blit(pygame.transform.scale(self.sprites[f"p{jugador.numero}"][0], (28, 32)), (x + 10, 29))
        self.texto(f"P{jugador.numero + 1}", x + 48, 34, 2, color)
        for i in range(3):
            if i < jugador.vidas:
                self.dibujar_icono("vida", x + 118 + i * 30, 30, 24)
            else:
                pygame.draw.rect(self.lienzo, (80, 67, 107), (x + 121 + i * 30, 38, 17, 12), 2)
        for i, (tipo, valor) in enumerate((("bomba", jugador.capacidad), ("fuego", jugador.alcance),
                                          ("botas", 1 + round((jugador.velocidad - 3.5) / 0.4)))):
            px = x + 14 + i * 78
            self.dibujar_icono(tipo, px, 72, 24)
            self.texto(str(valor), px + 35, 78, 2)
        if not jugador.vivo:
            pygame.draw.line(self.lienzo, (255, 83, 112), (x + 10, 30), (x + 38, 60), 3)
            pygame.draw.line(self.lienzo, (255, 83, 112), (x + 38, 30), (x + 10, 60), 3)

    def dibujar_panel(self):
        self.tarjeta_jugador(self.jugadores[0], 40)
        if self.cooperativo:
            self.tarjeta_jugador(self.jugadores[1], 516)
        else:
            self.caja((516, 18, 244, 94), PANEL, (131, 147, 209))
            for i, tipo in enumerate(("babosa", "cazador", "corredor", "fantasma")):
                x = 527 + i * 58
                self.lienzo.blit(pygame.transform.scale(self.sprites[tipo][0], (28, 32)), (x, 31))
                self.texto(str(sum(e.tipo == tipo for e in self.enemigos)), x + 14, 87, 2, TEXTO, True)
        if self.jefe:
            self.lienzo.blit(pygame.transform.scale(self.sprites["jefe"][0], (32, 32)), (348, 25))
            self.dibujar_icono("fuego" if self.jefe_abierto() else "escudo", 400, 27, 28)
            pygame.draw.rect(self.lienzo, (13, 18, 42), (310, 74, 180, 18))
            vida = max(0, int(174 * self.jefe["vida"] / self.jefe["max"]))
            pygame.draw.rect(self.lienzo, (255, 105, 139), (313, 77, vida, 12))
        else:
            self.texto(f"{self.nivel + 1} / 5", 400, 35, 2, TEXTO, True)
            self.lienzo.blit(pygame.transform.scale(self.sprites["cazador"][0], (24, 27)), (352, 63))
            self.texto(str(len(self.enemigos)), 407, 76, 2, TEXTO, True)
        for i in range(6):
            r = pygame.Rect(326 + i * 25, 118, 16, 8)
            pygame.draw.rect(self.lienzo, self.acento if i <= self.nivel else (67, 64, 105), r)

    def dibujar_menu(self):
        for y in range(24, ALTO, 48):
            for x in range(24, ANCHO, 48):
                pygame.draw.rect(self.lienzo, (37, 35, 68), (x, y, 4, 4))
        self.caja((100, 100, 600, 510), (35, 35, 71), (111, 134, 215))
        colores = [(255, 111, 168), (255, 213, 80), (104, 225, 208), (116, 181, 255), (184, 147, 255), (255, 165, 91)]
        titulo = "NeoNeoBomberman"
        inicio = (ANCHO - (len(titulo) * 30 - 5)) // 2
        for i, letra in enumerate(titulo):
            x = inicio + i * 30
            color = colores[i % len(colores)]
            self.texto(letra, x + 3, 168, 5, (12, 15, 36))
            self.texto(letra, x, 165, 5, color)
        fila = ["p0", "babosa", "cazador", "corredor", "fantasma", "p1"]
        for i, tipo in enumerate(fila):
            self.lienzo.blit(self.sprites[tipo][0], (208 + i * 68, 270))
        self.boton("SOLO", 208, 360, 384, "solo", True)
        self.boton("COOPERATIVO", 208, 426, 384, "coop")
        self.boton("SALIR", 208, 492, 384, "salir")

    def dibujar_superposicion(self):
        velo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        velo.fill((12, 13, 38, 195))
        self.lienzo.blit(velo, (0, 0))
        self.caja((100, 249, 600, 220), (43, 43, 83), self.acento)
        titulos = {"pausa": "PAUSA", "completado": "NIVEL SUPERADO", "derrota": "DERROTA", "victoria": "FIN"}
        self.texto(titulos[self.estado], 400, 309, 3, TEXTO, True)
        if self.estado == "pausa":
            self.boton("SEGUIR", 128, 389, 170, "continuar", True)
            self.boton("REINTENTAR", 315, 389, 170, "reintentar")
            self.boton("MENU", 502, 389, 170, "menu")
        elif self.estado == "completado":
            self.boton("SIGUIENTE", 264, 389, 272, "siguiente", True)
        elif self.estado == "derrota":
            self.boton("REINTENTAR", 172, 389, 220, "reintentar", True)
            self.boton("MENU", 412, 389, 216, "menu")
        elif self.estado == "victoria":
            self.boton("MENU", 264, 389, 272, "menu", True)

    def dibujar(self):
        self.lienzo.fill(FONDO)
        self.botones = []
        if self.estado == "menu":
            self.dibujar_menu()
        else:
            self.dibujar_mapa()
            self.dibujar_panel()
            if self.estado != "jugando":
                self.dibujar_superposicion()
        ancho, alto = self.ventana.get_size()
        escala = min(ancho / ANCHO, alto / ALTO)
        medida = (max(1, int(ANCHO * escala)), max(1, int(ALTO * escala)))
        # Vecino más cercano: los píxeles no se difuminan al cambiar el tamaño.
        imagen = pygame.transform.scale(self.lienzo, medida) if medida != (ANCHO, ALTO) else self.lienzo
        self.ventana.fill((12, 13, 33))
        self.ventana.blit(imagen, ((ancho - medida[0]) // 2, (alto - medida[1]) // 2))
        pygame.display.flip()

    def ejecutar(self):
        while self.ejecutando:
            # Limitar el salto temporal evita atravesar obstáculos tras arrastrar la ventana.
            dt = min(self.reloj.tick(60) / 1000, 0.05)
            for evento in pygame.event.get():
                self.evento(evento)
            self.actualizar(dt, pygame.key.get_pressed())
            self.dibujar()
        pygame.quit()


if __name__ == "__main__":
    Juego().ejecutar()
