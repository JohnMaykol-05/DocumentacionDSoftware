"""Pruebas de reglas importantes. Ejecutar: python -m unittest -v test_juego.py"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import unittest
from collections import defaultdict, deque
import pygame
from main import Juego, Bomba, Actor, COLUMNAS, FILAS


class Reglas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.juego = Juego()

    def setUp(self):
        self.juego.comenzar(True)
        self.juego.estado = "jugando"
        self.teclas = defaultdict(bool)

    def vaciar(self):
        g = self.juego
        for y in range(1, FILAS - 1):
            for x in range(1, COLUMNAS - 1):
                g.mapa[y][x] = 0
        g.enemigos = []
        g.objetos = {}
        g.ocultos = {}

    def test_muro_y_caja_detienen_el_fuego(self):
        self.vaciar()
        g = self.juego
        g.mapa[3][5] = 2
        g.mapa[1][3] = 1
        zona = g.zona_explosion((3, 3), 4)
        self.assertIn((5, 3), zona)
        self.assertNotIn((6, 3), zona)
        self.assertNotIn((3, 1), zona)

    def test_cadena_explota_una_vez_y_revela_objeto(self):
        self.vaciar()
        g = self.juego
        g.mapa[3][7] = 2
        g.ocultos[(7, 3)] = "fuego"
        g.bombas = [Bomba((3, 3), 0, 3), Bomba((5, 3), 1, 3)]
        g.explotar(g.bombas[0])
        self.assertEqual(len(g.bombas), 0)
        self.assertEqual(len(g.fuegos), 2)
        self.assertEqual(g.mapa[3][7], 0)
        self.assertEqual(g.objetos[(7, 3)], "fuego")
        self.assertTrue(all((8, 3) not in f["celdas"] for f in g.fuegos))

    def test_bomba_duplicada_capacidad_y_permiso_salida(self):
        g = self.juego
        j = g.jugadores[0]
        g.colocar_bomba(j)
        g.colocar_bomba(j)
        self.assertEqual(len(g.bombas), 1)
        self.assertTrue(g.libre((1, 1), j))
        j.x = 2
        g.actualizar(0.01, self.teclas)
        self.assertFalse(g.libre((1, 1), j))
        g.colocar_bomba(j)
        self.assertEqual(len(g.bombas), 1)

    def test_movimiento_no_cruza_muros(self):
        g = self.juego
        j = g.jugadores[0]
        for _ in range(60):
            g.mover(j, (-1, 0), 1 / 60)
        self.assertEqual(j.casilla, (1, 1))
        for _ in range(20):
            g.mover(j, (1, 0), 1 / 60)
        self.assertGreater(j.x, 1)
        self.assertEqual(j.y, 1)

    def test_pausa_congela_bombas_y_jefe(self):
        g = self.juego
        g.nivel = 5
        g.cargar_nivel()
        g.colocar_bomba(g.jugadores[0])
        g.estado = "pausa"
        antes = (g.bombas[0].tiempo, g.transcurrido, g.jefe["ataque"])
        g.actualizar(10, self.teclas)
        self.assertEqual(antes, (g.bombas[0].tiempo, g.transcurrido, g.jefe["ataque"]))

    def test_dano_unico_y_supervivencia_cooperativa(self):
        g = self.juego
        j = g.jugadores[0]
        j.inmune = 0
        g.fuegos = [{"celdas": {j.casilla}, "tiempo": 0.65, "bomba": True, "jefe_golpeado": False}] * 2
        g.actualizar(0.01, self.teclas)
        self.assertEqual(j.vidas, 2)
        j.vidas = 0
        g.actualizar(0.01, self.teclas)
        self.assertEqual(g.estado, "jugando")
        g.jugadores[1].vidas = 0
        g.actualizar(0.01, self.teclas)
        self.assertEqual(g.estado, "derrota")

    def test_campana_cinco_niveles_y_jefe(self):
        g = self.juego
        for nivel in range(5):
            self.assertEqual(g.nivel, nivel)
            g.estado = "jugando"
            g.enemigos = []
            g.jugadores[0].vidas = 0
            g.jugadores[1].x, g.jugadores[1].y = g.salida
            g.actualizar(0.01, self.teclas)
            self.assertEqual(g.estado, "completado")
            g.accion("siguiente")
            self.assertEqual(g.jugadores[0].vidas, 3)
        self.assertEqual(g.nivel, 5)
        self.assertIsNotNone(g.jefe)

    def test_escudo_bloquea_y_explosion_no_repite_dano(self):
        g = self.juego
        g.nivel = 5
        g.cargar_nivel()
        g.estado = "jugando"
        vida = g.jefe["vida"]
        def fuego():
            return {"celdas": {g.jefe["pos"]}, "tiempo": 0.65, "bomba": True, "jefe_golpeado": False}
        g.fuegos = [fuego()]
        g.actualizar(0.01, self.teclas)
        self.assertEqual(g.jefe["vida"], vida)
        g.transcurrido = 3.1
        g.fuegos = [fuego()]
        g.actualizar(0.01, self.teclas)
        self.assertEqual(g.jefe["vida"], vida - 1)
        g.actualizar(0.01, self.teclas)
        self.assertEqual(g.jefe["vida"], vida - 1)
        g.jefe["vida"] = 1
        g.jefe["inmune"] = 0
        g.fuegos = [fuego()]
        g.actualizar(0.01, self.teclas)
        self.assertEqual(g.estado, "victoria")

    def test_ataque_jefe_avisa_antes_de_hacer_dano(self):
        g = self.juego
        g.nivel = 5
        g.cargar_nivel()
        g.estado = "jugando"
        g.jugadores[0].inmune = 0
        g.jefe["ataque"] = 0
        g.actualizar(0.01, self.teclas)
        self.assertEqual(g.jugadores[0].vidas, 3)
        self.assertTrue(g.avisos)
        for _ in range(80):
            g.actualizar(1 / 60, self.teclas)
        self.assertEqual(g.jugadores[0].vidas, 2)

    def test_todos_los_mapas_son_transitables_destruyendo_cajas(self):
        g = self.juego
        for nivel in range(6):
            g.nivel = nivel
            g.cargar_nivel()
            vistos, cola = {(1, 1)}, deque([(1, 1)])
            while cola:
                x, y = cola.popleft()
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    pos = (x + dx, y + dy)
                    if pos not in vistos and g.dentro(pos) and g.mapa[pos[1]][pos[0]] != 1:
                        vistos.add(pos)
                        cola.append(pos)
            self.assertIn(g.salida, vistos)
            self.assertTrue(all(e.casilla in vistos for e in g.enemigos))
            self.assertTrue(all(g.mapa[j.casilla[1]][j.casilla[0]] == 0 for j in g.jugadores))

    def test_mejoras_y_reintento_limpian_estado(self):
        g = self.juego
        self.vaciar()
        j = g.jugadores[0]
        g.objetos[j.casilla] = "bomba"
        g.actualizar(0.01, self.teclas)
        self.assertEqual(j.capacidad, 2)
        g.colocar_bomba(j)
        g.accion("reintentar")
        self.assertFalse(g.bombas)
        self.assertFalse(g.fuegos)
        self.assertEqual(g.estado, "jugando")

    def test_eventos_de_teclado_pausa_y_cooperativo(self):
        g = self.juego
        g.evento(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
        self.assertEqual(len(g.bombas), 1)
        self.assertEqual(g.bombas[0].propietario, 1)
        g.evento(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
        self.assertEqual(g.estado, "pausa")
        g.evento(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
        self.assertEqual(g.estado, "jugando")

    def test_fantasma_cruza_cajas_pero_no_muros(self):
        self.vaciar()
        g = self.juego
        g.mapa[3][4] = 2
        g.mapa[3][5] = 1
        fantasma = Actor(3, 3, tipo="fantasma")
        cazador = Actor(3, 3, tipo="cazador")
        self.assertTrue(g.libre((4, 3), fantasma))
        self.assertFalse(g.libre((4, 3), cazador))
        self.assertFalse(g.libre((5, 3), fantasma))
        for _ in range(20):
            g.mover(fantasma, (1, 0), 1 / 60)
        self.assertGreater(fantasma.x, 3)

    def test_corredor_embiste_solo_con_linea_despejada(self):
        self.vaciar()
        g = self.juego
        g.jugadores = [Actor(7, 5)]
        corredor = Actor(3, 5, tipo="corredor", recarga=0)
        self.assertEqual(g.direccion_enemigo(corredor), (1, 0))
        self.assertGreater(corredor.impulso, 0)
        corredor.impulso = corredor.recarga = 0
        g.mapa[5][5] = 1
        g.direccion_enemigo(corredor)
        self.assertEqual(corredor.impulso, 0)

    def test_cazador_rodea_obstaculos_y_babosa_persigue_de_cerca(self):
        self.vaciar()
        g = self.juego
        g.jugadores = [Actor(6, 5)]
        g.mapa[5][4] = 1
        cazador = Actor(3, 5, tipo="cazador")
        self.assertIn(g.direccion_enemigo(cazador), [(0, -1), (0, 1)])
        g.mapa[5][4] = 0
        self.assertEqual(g.direccion_enemigo(Actor(3, 5, tipo="babosa")), (1, 0))

    def test_enemigo_huye_y_reconoce_peligro_de_cadenas(self):
        self.vaciar()
        g = self.juego
        g.bombas = [Bomba((2, 3), 0, 3, tiempo=0.2), Bomba((5, 3), 1, 3, tiempo=2)]
        self.assertIn((5, 5), g.peligros(0.8))
        enemigo = Actor(5, 5, tipo="cazador")
        d = g.direccion_enemigo(enemigo)
        self.assertNotIn((5 + d[0], 5 + d[1]), g.peligros(0.8))

    def test_solo_dos_fotogramas_distintos_por_personaje(self):
        g = self.juego
        for tipo, frames in g.sprites.items():
            self.assertEqual(len(frames), 2, tipo)
            self.assertNotEqual(pygame.image.tobytes(frames[0], "RGBA"),
                                pygame.image.tobytes(frames[1], "RGBA"), tipo)

    def test_jefe_alterna_patrones_y_acelera_al_perder_vida(self):
        g = self.juego
        g.nivel = 5
        g.cargar_nivel()
        g.jefe["ataque"] = 0
        g.actualizar_jefe(0.01)
        primera_zona = g.avisos[-1]["celdas"]
        g.jefe["ataque"] = 0
        g.actualizar_jefe(0.01)
        self.assertGreater(len(g.avisos[-1]["celdas"]), len(primera_zona))
        cadencia_normal = g.jefe["ataque"]
        g.jefe["vida"] = g.jefe["max"] // 2
        g.jefe["ataque"] = 0
        g.actualizar_jefe(0.01)
        self.assertLess(g.jefe["ataque"], cadencia_normal)

    def test_menu_minimo_sin_ayuda_y_sin_textos_de_guia(self):
        g = self.juego
        g.estado = "menu"
        g.dibujar()
        self.assertEqual({accion for _, accion in g.botones}, {"solo", "coop", "salir"})
        g.comenzar(True)
        g.dibujar()
        textos = {clave[0] for clave in g.cache_texto}
        self.assertFalse(any("WASD" in t or "ESPACIO" in t or "COMO" in t for t in textos))


if __name__ == "__main__":
    unittest.main()
