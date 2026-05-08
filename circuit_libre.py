from PySide6.QtCore import QSize, QPointF, QRect, QFile, QTextStream, QLineF, QRectF
from PySide6.QtGui import QColorConstants, QPen, Qt, QBrush, QAction, QIcon, QPixmap, QColor, QImage
from PySide6.QtWidgets import (QGraphicsScene, QGraphicsView, QPushButton, QDialog,
                               QHBoxLayout, QToolBar, QLabel, QGraphicsPixmapItem, QGraphicsRectItem, QInputDialog)
import math
import numpy as np

from button import ToolTipButton
from composantes import toolbar_composantes, Composante
from sauvegarde import Sauvegarde


class Noeud:
    def __init__(self, pos):
        self.voltage = 0
        self.info_voisins = []
        self.pos = pos

    @property
    def voltage(self):
        return self._voltage

    @voltage.setter
    def voltage(self, voltage):
        self._voltage = voltage

    @property
    def voisins(self):
        return self._info_voisins

    @voisins.setter
    def voisins(self, voisins):
        self._info_voisins = voisins

    @property
    def position(self):
        return self._pos

    @position.setter
    def position(self, position):
        self._pos = position

    # Rajoute un fil lié et l'autre noeud qui touche au fil
    def ajouter_info(self, fil, noeud_voisin):
        nouveau_voisin = [fil, noeud_voisin]
        if nouveau_voisin not in self.info_voisins:
            self.info_voisins.append(nouveau_voisin)

    # Enlève les informations relatives à un fil
    def enlever_info_fil(self, fil):
        for k in range(len(self.info_voisins)):
            if self.info_voisins[k][0] == fil:
                del self.info_voisins[k]
                break

    # Retire le noeud et merge les fils qui étaient séparés par ce noeud
    def enlever_noeud(self, scene):
        # le premier fil doit finir par self sinon switch
        # le dernier fil doit commencer par self sinon switch

        # TODO Ça marche pas TABARNAK
        if len(self.info_voisins) == 1:
            i, j = scene.pos_to_mat(self.pos.x(), self.pos.y())
            scene.mat_points[i, j] = self.info_voisins[0][0]
            scene.noeuds.remove(self)
            scene.visualiser_matrice()

        else:
            fil_depart = self.info_voisins[0][0]
            if fil_depart.noeuds[0] == self:
                fil_depart.lignes.reverse()
                fil_depart.noeuds.reverse()
                fil_depart.composantes.reverse()
                fil_depart.points.reverse()

            fil_fin = self.info_voisins[1][0]
            if fil_fin.noeuds[1] == self:
                fil_fin.lignes.reverse()
                fil_fin.noeuds.reverse()
                fil_fin.composantes.reverse()
                fil_fin.points.reverse()

            # fil_depart va devenir le merge des deux fils
            fil_depart.lignes += fil_fin.lignes
            fil_depart.noeuds[1] = fil_fin.noeuds[1]
            fil_depart.composantes += fil_fin.composantes

            fil_fin.points.append(self.pos)
            fil_depart.points += fil_fin.points

            fil_depart.noeuds[0].enlever_info_fil(fil_depart)
            fil_depart.noeuds[0].ajouter_info(fil_depart, fil_depart.noeuds[1])
            fil_depart.noeuds[1].enlever_info_fil(fil_fin)
            fil_depart.noeuds[1].ajouter_info(fil_depart, fil_depart.noeuds[0])

            scene.fils.remove(fil_fin)

            for point in fil_fin.points:
                i, j = scene.pos_to_mat(point.x(), point.y())
                scene.mat_points[i, j] = fil_depart

            scene.noeuds.remove(self)

            scene.visualiser_matrice()


class Fil:
    def __init__(self, scene, points, lignes):
        self.scene = scene
        self.points = points
        self.noeuds = None
        self.lignes = lignes

        # self.resistance, self.tension = self.calculs()
        self.composantes = []

        self.tension = 0
        self.resistance = 0

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, points):
        self._points = points

    @property
    def noeuds(self):
        return self._noeuds

    @noeuds.setter
    def noeuds(self, noeuds):
        self._noeuds = noeuds

    @property
    def lignes(self):
        return self._lignes

    @lignes.setter
    def lignes(self, lignes):
        self._lignes = lignes

    @property
    def tension(self):
        return self._tension

    @tension.setter
    def tension(self, tension):
        self._tension = tension

    @property
    def resistance(self):
        return self._resistance

    @resistance.setter
    def resistance(self, resistance):
        self._resistance = resistance

    # Calcul la tension et la résistance relative dans le fil
    def calculs(self):
        res = 0
        tension = 0
        for composante in self.composantes:
            if hasattr(composante, 'resistance'):
                res += composante.resistance
            if hasattr(composante, 'tension'):
                tension += composante.tension
        return res, tension

    def ajouter_composante(self, composante):
        def index_comp(index_point):
            for i in range(len(self.composantes)):
                pos_comp = self.composantes[i].points_fil[1]
                index_comp_points = self.points.index(pos_comp)

                if index_point <= index_comp_points:
                    return i
            return 0

        if composante.nom == "Batterie":
            index_point_depart = self.points.index(composante.points_fil[0])
            index_point_fin = self.points.index(composante.points_fil[-1])

            sens_comp = 1
            if index_point_depart > index_point_fin:
                sens_comp = -1

            self.composantes.insert(index_comp(index_point_depart), composante)

            self.resistance += composante.resistance
            self.tension += sens_comp * composante.tension
        else:
            index_milieu = self.points.index(composante.points_fil[1])

            self.composantes.insert(index_comp(index_milieu), composante)

            self.resistance += composante.resistance

    # Ajoute un noeud au fil, ce qui sépare le fil en deux fils distincts
    def ajouter_noeud(self, pos: QPointF, noeud: Noeud):
        index_point = self.points.index(pos)
        points_avant = self.points[:index_point]
        points_apres = self.points[index_point + 1:]

        for i in range(len(self.lignes)):
            ligne = self.lignes[i]
            p1 = ligne.line().p1()
            p2 = ligne.line().p2()
            x_max, x_min = max(p1.x(), p2.x()), min(p1.x(), p2.x())
            y_max, y_min = max(p1.y(), p2.y()), min(p1.y(), p2.y())
            if x_max >= pos.x() >= x_min and y_max >= pos.y() >= y_min:
                ligne.setLine(QLineF(p1, pos))

                nouvelle_ligne = self.scene.ajouter_ligne(pos.x(), pos.y(), p2.x(), p2.y())
                self.lignes.insert(i + 1, nouvelle_ligne)

                lignes_avant = self.lignes[:i + 1]
                lignes_apres = self.lignes[i + 1:]
                break

        # Quand y'a pas de noeud, le fil ne se split pas, mais le début commence maintenant au noeud
        if self.noeuds is None:
            self.points = points_apres.copy() + points_avant.copy()
            self.lignes = lignes_apres.copy() + lignes_avant.copy()
            self.noeuds = [noeud, noeud]
        else:
            comp_avant = []
            comp_apres = []
            for i in range(len(self.composantes)):
                pos_comp = self.composantes[i].points_fil[1]
                index_comp_points = self.points.index(pos_comp)

                if index_point < index_comp_points:
                    comp_avant = self.composantes[:i]
                    comp_apres = self.composantes[i:]
                    break

            nouveau_fil = Fil(self.scene, points_apres, lignes_apres.copy())
            nouveau_fil.noeuds = [noeud, self.noeuds[1]]
            nouveau_fil.composantes = comp_apres.copy()
            self.scene.fils.append(nouveau_fil)

            for point_apres in points_apres:
                i, j = self.scene.pos_to_mat(point_apres.x(), point_apres.y())
                self.scene.mat_points[i, j] = nouveau_fil

            self.noeuds[0].enlever_info_fil(self)
            self.noeuds[0].ajouter_info(self, noeud)

            if self.noeuds[0] != self.noeuds[1]:
                self.noeuds[1].enlever_info_fil(self)
            self.noeuds[1].ajouter_info(nouveau_fil, noeud)

            noeud.ajouter_info(self, self.noeuds[0])
            noeud.ajouter_info(nouveau_fil, self.noeuds[0])

            self.composantes = comp_avant.copy()
            self.noeuds = [self.noeuds[0], noeud]
            self.points = points_avant.copy()
            self.lignes = lignes_avant.copy()

    # TODO faire en sorte que les noeuds soient pas retirés si ils sont connectés à plus de deux fils
    def enlever_fil(self):
        for point in self.points:
            i, j = self.scene.pos_to_mat(point.x(), point.y())
            self.scene.mat_points[i, j] = None

        self.scene.rapetisser_matrice()
        self.scene.visualiser_matrice()

        self.noeuds[0].enlever_info_fil(self)
        if len(self.noeuds[0].info_voisins) <= 2:
            self.noeuds[0].enlever_noeud(self.scene)

        self.noeuds[1].enlever_info_fil(self)
        if len(self.noeuds[1].info_voisins) <= 2:
            self.noeuds[1].enlever_noeud(self.scene)

        for composante in self.composantes:
            self.scene.removeItem(composante)
        for ligne in self.lignes:
            self.scene.removeItem(ligne)


class Circuit(QGraphicsScene):
    def __init__(self, mainwindow, sauvegarde: Sauvegarde, id: str, mat: list | None):
        super().__init__()
        self.main_window = mainwindow
        self.scene_size = QSize(500, 500)
        self.graphics_view = GraphicsView(self, mainwindow)
        self.main_window.setCentralWidget(self.graphics_view)
        self.graphics_view.setMinimumSize(self.scene_size)
        self.graphics_view.setScene(self)

        self.largeur = self.scene_size.width()
        self.hauteur = self.scene_size.height()
        # La distance entre chaque ligne dans le grid
        self.taille_grid = 20

        self.mat_i0 = 0
        self.mat_j0 = 0
        self.dessiner_fond_grid()

        largeur_fil_base = 200
        hauteur_fil_base = 140

        self.debut_matrice_i = None
        self.debut_matrice_j = None

        self.dessine = False
        self.dernier_point = None

        self.lignes = []
        self.noeuds = []
        self.points_avant_pivot = []
        self.fil_complet = False
        self.nouveau_fil = None

        if mat is None:
            fil_base, self.mat_points = self.dessiner_circuit_base(largeur_fil_base, hauteur_fil_base)
            self.fils = [fil_base]
        else:
            self.mat_points = np.array(mat)
            # TODO: générer les fils a partir de la matrice?
            self.fils = []

        self.sauvegarde = sauvegarde
        self.id = id

        # listes pour le rollback
        self.ajouts = []
        self.composantes_jetes = []
        self.fils_jetes = []
        self.dernier_jete = []
        self.modifications = []
        # les ajouts seront 1, les jetés seront 2, composantes tournées seront 3 et composantes modifiées seront 4
        self.operations = []
        self.tournes = []

        # pour les composantes
        self.toolbar = None
        self.selection = None
        self.composante_selectionnee = None
        self.image_composante = None
        self.couleur_recouvre = None
        self.accepter_modification = True
        self.accepter_positionnement = False
        self.zones_surbrillance = []
        self.zones_blanches = []
        self.grid_par_dessus = []

        # Menubar
        self.barre_menu = self.main_window.menuBar()
        self.menu_options = self.barre_menu.addMenu("Options")
        self.menu_naviguer = self.barre_menu.addMenu("Naviguer")
        self.allouer_fermeture = True

        # sauvegarder
        sauvegarder_action = QAction("Sauvegarder", self)
        sauvegarder_action.setShortcut("Ctrl+S")
        sauvegarder_action.setIcon(QIcon("images/menubar/disquette.png"))
        self.menu_options.addAction(sauvegarder_action)
        sauvegarder_action.triggered.connect(self.sauvegarder_triggered)

        # rollback
        self._annuler_action = QAction("RollBack", self)
        self._annuler_action.setShortcut("Ctrl+Z")
        self._annuler_action.setIcon(QIcon("images/menubar/rollback.png"))
        self._annuler_action.triggered.connect(self.rollback_triggered)
        self._annuler_action.setEnabled(False)
        self.menu_options.addAction(self._annuler_action)

        # Quitter
        quitter_action = QAction("Quitter", self)
        quitter_action.setShortcut("Ctrl+Q")
        quitter_action.triggered.connect(self.main_window.close)
        self.menu_naviguer.addAction(quitter_action)

    @property
    def taille_grid(self):
        return self._taille_grid

    @taille_grid.setter
    def taille_grid(self, taille):
        self._taille_grid = taille

    @property
    def mat_i0(self):
        return self._mat_i0

    @mat_i0.setter
    def mat_i0(self, mat_i0):
        self._mat_i0 = mat_i0

    @property
    def mat_j0(self):
        return self._mat_j0

    @mat_j0.setter
    def mat_j0(self, mat_j0):
        self._mat_j0 = mat_j0

    @property
    def debut_matrice_i(self):
        return self._debut_matrice_i

    @debut_matrice_i.setter
    def debut_matrice_i(self, debut_matrice_i):
        self._debut_matrice_i = debut_matrice_i

    @property
    def debut_matrice_j(self):
        return self._debut_matrice_j

    @debut_matrice_j.setter
    def debut_matrice_j(self, debut_matrice_j):
        self._debut_matrice_j = debut_matrice_j

    @property
    def dessine(self):
        return self._dessine

    @dessine.setter
    def dessine(self, dessine):
        self._dessine = dessine

    @property
    def dernier_point(self):
        return self._dernier_point

    @dernier_point.setter
    def dernier_point(self, dernier_point):
        self._dernier_point = dernier_point

    @property
    def lignes(self):
        return self._lignes

    @lignes.setter
    def lignes(self, lignes):
        self._lignes = lignes

    @property
    def noeuds(self):
        return self._noeuds

    @noeuds.setter
    def noeuds(self, noeuds):
        self._noeuds = noeuds

    @property
    def points_avant_pivot(self):
        return self._points_avant_pivot

    @points_avant_pivot.setter
    def points_avant_pivot(self, points_avant_pivot):
        self._points_avant_pivot = points_avant_pivot

    @property
    def fil_complet(self):
        return self._fil_complet

    @fil_complet.setter
    def fil_complet(self, fil_complet):
        self._fil_complet = fil_complet

    @property
    def nouveau_fil(self):
        return self._nouveau_fil

    @nouveau_fil.setter
    def nouveau_fil(self, nouveau_fil):
        self._nouveau_fil = nouveau_fil

    @property
    def fils(self):
        return self._fils

    @fils.setter
    def fils(self, fils):
        self._fils = fils

    @property
    def sauvegarde(self):
        return self._sauvegarde

    @sauvegarde.setter
    def sauvegarde(self, sauvegarder):
        self._sauvegarde = sauvegarder

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id_id):
        self._id = id_id

    @property
    def ajouts(self):
        return self._ajouts

    @ajouts.setter
    def ajouts(self, ajouts):
        self._ajouts = ajouts

    @property
    def composantes_jetes(self):
        return self._composantes_jetes

    @composantes_jetes.setter
    def composantes_jetes(self, composantes_jetes):
        self._composantes_jetes = composantes_jetes

    @property
    def fils_jetes(self):
        return self._fils_jetes

    @fils_jetes.setter
    def fils_jetes(self, fils_jetes):
        self._fils_jetes = fils_jetes

    @property
    def dernier_jetes(self):
        return self._dernier_jetes

    @dernier_jetes.setter
    def dernier_jetes(self, dernier_jetes):
        self._dernier_jetes = dernier_jetes

    @property
    def modifications(self):
        return self._modifications

    @modifications.setter
    def modifications(self, modifications):
        self._modifications = modifications

    @property
    def operations(self):
        return self._operations

    @operations.setter
    def operations(self, operations):
        self._operations = operations

    @property
    def selection(self):
        return self._selection

    @selection.setter
    def selection(self, selection):
        self._selection = selection

    @property
    def composante_selectionnee(self):
        return self._composante_selectionnee

    @composante_selectionnee.setter
    def composante_selectionnee(self, composante_selectionnee):
        self._composante_selectionnee = composante_selectionnee

    @property
    def image_composante(self):
        return self._image_composante

    @image_composante.setter
    def image_composante(self, image_composante):
        self._image_composante = image_composante

    @property
    def accepter_modification(self):
        return self._accepter_modification

    @accepter_modification.setter
    def accepter_modification(self, accepter_modification):
        self._accepter_modification = accepter_modification

    @property
    def accepter_positionnement(self):
        return self._accepter_positionnement

    @accepter_positionnement.setter
    def accepter_positionnement(self, accepter_positionnement):
        self._accepter_positionnement = accepter_positionnement

    @property
    def zones_surbrillance(self):
        return self._zones_surbrillance

    @zones_surbrillance.setter
    def zones_surbrillance(self, zones_surbrillance):
        self._zones_surbrillance = zones_surbrillance

    @property
    def zones_blanches(self):
        return self._zones_blanches

    @zones_blanches.setter
    def zones_blanches(self, zones_blanches):
        self._zones_blanches = zones_blanches

    @property
    def grid_par_dessus(self):
        return self._grid_par_dessus

    @grid_par_dessus.setter
    def grid_par_dessus(self, grid_par_dessus):
        self._grid_par_dessus = grid_par_dessus

    @property
    def composantes(self):
        return self._composantes

    @composantes.setter
    def composantes(self, composantes):
        self._composantes = composantes

    @property
    def nombre_de_rotations(self):
        return self._nombre_de_rotations

    @nombre_de_rotations.setter
    def nombre_de_rotations(self, nombre_de_rotations):
        self._nombre_de_rotations = nombre_de_rotations

    def sauvegarder_triggered(self):
        # Si l'id est None, on demande un nom pour le circuit + on le créé
        if self.id is None:
            nom, ok = QInputDialog.getText(self.main_window, "Nouveau circuit", "Entre le nom de ton circuit")
            if nom and ok:
                self.id = self.sauvegarde.creation_circuit_libre(nom)
            else:
                # Si l'utilisateur a dismiss(quitter) le dialog pour le nom du circuit, on annuler la création du circuit
                return
        else:
            self.sauvegarde.modifie_circuit(self.id, self.mat_points.tolist())

    def rollback_possible(self):
        # à partir du moment où un élément est dans opérations, on peut rollback
        if self.operations:
            self._annuler_action.setEnabled(True)
        else:
            # si on a rollback toutes les opérations, on ne peut plus le faire
            self._annuler_action.setEnabled(False)

    def rollback_triggered(self):
        dernier = self.operations[-1]
        if dernier == 1:
            dernier_ajout = self.ajouts[-1]
            if isinstance(dernier_ajout, Fil):
                dernier_ajout.enlever_fil()
                self.fils.remove(dernier_ajout)
                # TODO : mettre à jour la vérification de collisions pour fils après qu'un ait été retiré
            else:
                # enlever la dernière composante du dessin (donc les 3 dernières infos ajoutées)
                pass

            self.ajouts.pop()

        elif dernier == 2:
            dernier_jete = self.dernier_jete[-1]
            if dernier_jete == "fil":
                # replacer le fil enlevé (et toute sa "bande")
                pass
            else:
                # on sort les éléments supprimés de "jeter" pour les ajouter à "composante"
                index = self.composantes_jetes.pop()
                position = self.composantes_jetes.pop()
                image = self.composantes_jetes.pop()
                composante = self.composantes_jetes.pop()

                # on réajoute au fil la composante "réapparue"
                # fil = self.verifier_collision_fil(position)
                # self.fils[fil - 1].ajouter_composante(composante)

                # on remet l'image sur le circuit
                image_a_ajouter = image
                image_a_ajouter.setPos(position)
                self.addItem(image_a_ajouter)
                # on lui réajoute un carré blanc
                coin_sup_gauche_x = position.x() - self.taille_grid
                coin_sup_gauche_y = position.y() - self.taille_grid
                zone_blanche = QGraphicsRectItem(coin_sup_gauche_x, coin_sup_gauche_y, self.taille_grid * 2,
                                                 self.taille_grid * 2)
                zone_blanche.setOpacity(1)
                zone_blanche.setZValue(0)
                zone_blanche.setBrush(QColor(255, 255, 255))
                self.addItem(zone_blanche)
                self.zones_blanches.append(zone_blanche)

                # on remet le grid où la composante
                # on stocke les lignes ajoutées dans une liste pour ensuite la supprimée si besoin
                bloc_de_lignes = []
                pen = QPen(QColorConstants.Gray)
                # ajoute les lignes horizontale
                multiple = -1
                while multiple <= 1:
                    x1 = position.x() - self.taille_grid
                    x2 = position.x() + self.taille_grid
                    y = position.y() + multiple * self.taille_grid

                    ligne = self.addLine(x1, y, x2, y, pen)
                    ligne.setZValue(2.5)
                    bloc_de_lignes.append(ligne)
                    multiple += 1

                # ajoute lignes verticales
                multiple = -1
                while multiple <= 1:
                    y1 = position.y() - self.taille_grid
                    y2 = position.y() + self.taille_grid
                    x = position.x() + multiple * self.taille_grid

                    ligne = self.addLine(x, y1, x, y2, pen)
                    ligne.setZValue(2.5)
                    bloc_de_lignes.append(ligne)
                    multiple += 1

                self.grid_par_dessus.append(bloc_de_lignes)
                self.grid_par_dessus.append(position)

            self.dernier_jete.pop()

        elif dernier == 3:
            collision = self.tournes.pop()
            self.operation_tourner(collision)

        else:
            # annuler la plus récente modification à une composante.
            dernier_element = self.modifications.pop()
            operation = dernier_element[0]

            if operation == "Batterie":
                # TODO: remettre voltage batterie précédent
                pass

            elif operation == "Résistor":
                # Todo: remettre dernière résistance
                pass

            elif operation == "Interrupteur":
                # Todo: ouvrir ou fermer interrupteur
                pass

        self.operations.pop()
        self.rollback_possible()

    def quitter_triggered(self):
        avertissement = QDialog()
        # on ne peut pas cliquer sur le "x" du QDialog (ainsi on gère à 100% le clsoe event)
        avertissement.setWindowFlags(avertissement.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)
        avertissement.setWindowTitle("Voulez-vous Sauvegarder?")
        avertissement.setModal(True)

        layout_dialogue = QHBoxLayout()
        avertissement.setLayout(layout_dialogue)

        # comme si on n'avait jamais souhaité quitter
        bouton_annuler = QPushButton("Annuler")
        bouton_annuler.clicked.connect(avertissement.close)
        bouton_annuler.clicked.connect(self.refuser_fermeture)

        bouton_sauvegarder_et_quitter_total = QPushButton("Sauvegarder et Quitter")
        bouton_sauvegarder_et_quitter_total.clicked.connect(lambda: self.sauvegarder_et_quitter(avertissement))

        # ferme les deux fenêtres (dialogue et principale)
        bouton_quitter_sans_sauvegarder = QPushButton("quitter sans sauvegarder")
        bouton_quitter_sans_sauvegarder.clicked.connect(avertissement.close)
        layout_dialogue.addWidget(bouton_sauvegarder_et_quitter_total)
        layout_dialogue.addWidget(bouton_quitter_sans_sauvegarder)
        layout_dialogue.addWidget(bouton_annuler)
        avertissement.exec()

        return self.allouer_fermeture

    def sauvegarder_et_quitter(self, dialog):
        # sauvegarde le circuit et ferme tout
        dialog.close()
        self.sauvegarder_triggered()
        self.main_window.close()

    def refuser_fermeture(self):
        self.allouer_fermeture = False

    # première méthode non liée au menu à propos
    # Dessine le fond et le grid
    def dessiner_fond_grid(self):
        self.setBackgroundBrush(QColorConstants.White)
        self.setSceneRect(0, 0, self.largeur, self.hauteur)

        pen = QPen(QColorConstants.Gray)

        # Lignes horizontales
        for i in range(math.ceil(self.hauteur / self.taille_grid) + 1):
            x1 = 0
            x2 = self.largeur
            y = i * self.taille_grid

            self.addLine(x1, y, x2, y, pen)

        # Lignes verticales
        for i in range(math.ceil(self.largeur / self.taille_grid) + 1):
            y1 = 0
            y2 = self.hauteur
            x = i * self.taille_grid

            self.addLine(x, y1, x, y2, pen)

    # ajoute une ligne dans la scene selon les coordonnées du début et de fin
    def ajouter_ligne(self, xi, yi, x, y):
        pen = QPen(QColorConstants.Black)
        largeur_crayon = 3
        pen.setWidthF(largeur_crayon)
        ligne = self.addLine(xi, yi, x, y, pen)

        return ligne

    # TODO: quand on pourra charger les saves, enlever cette méthode et avoir en tout temps la save de la matrice de
    # base pour la charger comme n'importe quel circuit
    def dessiner_circuit_base(self, largeur_circuit, hauteur_circuit):
        gauche = self.largeur / 2 - largeur_circuit / 2
        droite = self.largeur / 2 + largeur_circuit / 2
        haut = self.hauteur / 2 - hauteur_circuit / 2
        bas = self.hauteur / 2 + hauteur_circuit / 2

        gauche, haut = self.pos_selon_grid(QPointF(gauche, haut))
        droite, bas = self.pos_selon_grid(QPointF(droite, bas))

        ligne_haut = self.ajouter_ligne(gauche, haut, droite, haut)
        ligne_droite = self.ajouter_ligne(droite, haut, droite, bas)
        ligne_bas = self.ajouter_ligne(droite, bas, gauche, bas)
        ligne_gauche = self.ajouter_ligne(gauche, bas, gauche, haut)

        fil_base = Fil(self, [], [ligne_haut, ligne_droite, ligne_bas, ligne_gauche])

        nb_points_x = round((droite - gauche) / self.taille_grid) + 1
        nb_points_y = round((bas - haut) / self.taille_grid) + 1

        self.mat_i0 = haut
        self.mat_j0 = gauche
        matrice_points = np.empty((nb_points_y, nb_points_x), dtype=object)

        points_droite = []
        points_gauche = []
        # lignes verticales
        for k in range(nb_points_y):
            y = haut + k * self.taille_grid

            mat_i, mat_j = self.pos_to_mat(droite, y)
            matrice_points[mat_i, mat_j] = fil_base
            points_droite.append(QPointF(droite, y))

            mat_i, mat_j = self.pos_to_mat(gauche, y)
            matrice_points[mat_i, mat_j] = fil_base
            points_gauche.append(QPointF(gauche, y))

        points_haut = []
        points_bas = []
        # lignes horizontales
        for k in range(nb_points_x - 2):
            x = gauche + (k + 1) * self.taille_grid

            mat_i, mat_j = self.pos_to_mat(x, haut)
            matrice_points[mat_i, mat_j] = fil_base
            points_haut.append(QPointF(x, haut))

            mat_i, mat_j = self.pos_to_mat(x, bas)
            matrice_points[mat_i, mat_j] = fil_base
            points_bas.append(QPointF(x, bas))

        points_bas.reverse()
        points_gauche.reverse()
        points = points_haut + points_droite + points_bas + points_gauche
        fil_base.points = points

        return fil_base, matrice_points

    # À enlever dans le futur, méthode permettant de print la matrice points pour mieux la visualiser et déterminer les
    # erreurs possibles
    def visualiser_matrice(self):
        for i in range(self.mat_points.shape[0]):
            liste = []
            len_j = self.mat_points.shape[1]
            for j in range(len_j):
                try:
                    num = str(self.fils.index(self.mat_points[i, j]) + 1)
                except ValueError:
                    if isinstance(self.mat_points[i, j], Noeud):
                        num = "x"
                    elif isinstance(self.mat_points[i, j], Composante):
                        num = "c"
                    else:
                        num = "0"
                liste.append(num)
            print(liste)

        print("===============================================================================")

    # trouve ce qui est dans le grid à la position donnée
    def verifier_collision_fil(self, pos):
        x, y = self.pos_selon_grid(pos)
        pos_i, pos_j = self.pos_to_mat(x, y)

        max_i = self.mat_points.shape[0] - 1
        max_j = self.mat_points.shape[1] - 1

        if QPointF(x, y) == self.dernier_point:
            return 0
        elif pos_i <= max_i and pos_i >= 0 and pos_j <= max_j and pos_j >= 0:
            touche = self.mat_points[pos_i, pos_j]
            if touche is not None and isinstance(touche, object):
                return touche
            else:
                return 0
        else:
            return 0

    def clic_gauche_fil(self, pos):
        # return tous les points dans le grid selon la ligne
        def get_points_ligne(debut_ligne, fin_ligne):
            diff_x = fin_ligne.x() - debut_ligne.x()
            diff_y = fin_ligne.y() - debut_ligne.y()
            if abs(diff_x) > abs(diff_y):
                sens_x = 1
                if diff_x < 0:
                    sens_x = -1
                sens_y = 0
            else:
                sens_y = 1
                if diff_y < 0:
                    sens_y = -1
                sens_x = 0

            nb_points = round((diff_x * sens_x + diff_y * sens_y) / self.taille_grid)

            points = []
            for k in range(nb_points):
                pos_x = debut_ligne.x() + (k + 1) * self.taille_grid * sens_x
                pos_y = debut_ligne.y() + (k + 1) * self.taille_grid * sens_y
                points.append(QPointF(pos_x, pos_y))

            return points

        # met une reference au fil partout où il touche dans la matrice points
        def mettre_fil_mat(ligne, fil):
            debut_ligne = ligne.line().p1()
            fin_ligne = ligne.line().p2()
            points = get_points_ligne(debut_ligne, fin_ligne)

            i_fin, j_fin = self.pos_to_mat(points[-1].x(), points[-1].y())
            self.agrandir_matrice(i_fin, j_fin)

            for point in points:
                i, j = self.pos_to_mat(point.x(), point.y())
                if not isinstance(self.mat_points[i, j], Fil) and not isinstance(self.mat_points[i, j], Noeud):
                    self.mat_points[i, j] = fil

            return debut_ligne, fin_ligne, points

        fil_touche = self.verifier_collision_fil(pos)
        x, y = self.pos_selon_grid(pos)
        if not self.dessine:
            # lorsque le fil est pas démarré et que le clic démarre à un fil, un nouveau fil est commencé
            if fil_touche != 0:
                self.dessine = True
                ligne = self.ajouter_ligne(x, y, x, y)
                self.lignes.append(ligne)
                self.dernier_point = QPointF(x, y)

                self.points_avant_pivot.append(QPointF(x, y))

                fil = Fil(self, [], [])
                self.nouveau_fil = fil
                self.fils.append(fil)

        # Lorsque le fil est complet, ajoute les noeuds et ajuste les fils et la matrice en fonction de ceux-ci
        elif self.fil_complet:
            debut_ligne, fin_ligne, points_apres_pivot = mettre_fil_mat(self.lignes[-1], self.nouveau_fil)

            # Ajouter noeud a premier et dernier point
            points = self.points_avant_pivot + points_apres_pivot

            self.dernier_point = False
            fil_noeud1 = self.verifier_collision_fil(points[0])

            if isinstance(fil_noeud1, Fil):
                noeud_debut = Noeud(points[0])
                self.noeuds.append(noeud_debut)

                fil_noeud1.ajouter_noeud(points[0], noeud_debut)
            else:
                noeud_debut = fil_noeud1

            fil_noeud2 = self.verifier_collision_fil(fin_ligne)

            if isinstance(fil_noeud2, Fil):
                noeud_fin = Noeud(fin_ligne)
                self.noeuds.append(noeud_fin)

                fil_noeud2.ajouter_noeud(fin_ligne, noeud_fin)
            else:
                noeud_fin = fil_noeud2

            self.nouveau_fil.points = points[1:-1]

            self.nouveau_fil.lignes = self.lignes.copy()
            self.nouveau_fil.noeuds = [noeud_debut, noeud_fin]

            noeud_debut.ajouter_info(self.nouveau_fil, noeud_fin)
            noeud_fin.ajouter_info(self.nouveau_fil, noeud_debut)

            noeud_i, noeud_j = self.pos_to_mat(points[0].x(), points[0].y())
            self.mat_points[noeud_i, noeud_j] = noeud_debut
            noeud_i, noeud_j = self.pos_to_mat(fin_ligne.x(), fin_ligne.y())
            self.mat_points[noeud_i, noeud_j] = noeud_fin

            self.rapetisser_matrice()

            self.lignes = []
            self.points_avant_pivot = []
            self.dessine = False
            self.ajouts.append(self.nouveau_fil)
            self.nouveau_fil = None

            self.operations.append(1)
            self.rollback_possible()


        # lorsque le fil n'est pas complet, crée un nouveau pivot au fil pour que l'usager puisse changer de sens
        elif (QPointF(x, y) != self.points_avant_pivot[0] and not isinstance(fil_touche, Fil)
              and not isinstance(fil_touche, Noeud)):
            debut_ligne, fin_ligne, points_apres_pivot = mettre_fil_mat(self.lignes[-1], self.nouveau_fil)
            ligne = self.ajouter_ligne(fin_ligne.x(), fin_ligne.y(), fin_ligne.x(), fin_ligne.y())

            self.points_avant_pivot += points_apres_pivot
            self.lignes.append(ligne)
            self.dernier_point = QPointF(fin_ligne.x(), fin_ligne.y())
            self.continuer_dessin(pos)

    def fil_accepte(self, position):
        # TODO: valider que l'on peut mettre un fil (pas de composantes, pas collé à un autre fil
        pass

    # Calcul l'ensemble des voltages aux noeuds si le premier noeuds est 0V.
    # C'est seulement la différence de potentiel qui compte donc c'est pas grave d'avoir un voltage déja choisi
    # pour un seul noeud
    # À partir de ça, les ampérages et différences de potentiels pourront être calculés selon delta V = RI
    def calculer_voltage(self):
        mat_A = np.zeros((len(self.noeuds) - 1, len(self.noeuds) - 1))
        mat_B = np.zeros((len(self.noeuds) - 1, 1))

        noeud_zero = self.noeuds[-1]
        noeud_zero.voltage = 0
        for i in range(len(self.noeuds) - 1):
            j_noeud = i
            for info in self.noeuds[i].info_voisins:
                j_voisin = info[1]
                fil = info[0]

                mat_A[i, j_noeud] += 1 / fil.resistance
                mat_B[i, 0] -= fil.tension / fil.resistance
                if self.noeuds[j_voisin] != noeud_zero:
                    mat_A[i, j_voisin] -= 1 / fil.resistance

        mat_X = np.linalg.solve(mat_A, mat_B)
        for i in range(len(mat_X)):
            self.noeuds[i].voltage = mat_X[i][0]

    def clic_droit_fil(self):
        # Annule le fil entrain d'être dessiné et enlève ses références dans la matrice points
        if self.dessine:
            for ligne in self.lignes:
                self.removeItem(ligne)

            for point in self.points_avant_pivot:
                i, j = self.pos_to_mat(point.x(), point.y())
                if point != self.points_avant_pivot[0]:
                    self.mat_points[i, j] = None

            self.fils.remove(self.nouveau_fil)
            self.nouveau_fil = None

            self.points_avant_pivot = []
            self.rapetisser_matrice()

            self.dessine = False
            self.lignes = []

    # Vérifie si i et j sont hors de la matrice, si c'est le cas, agrandit la matrice pour pouvoir les inclure
    def agrandir_matrice(self, i, j):
        def agrandir(i_ajout, j_ajout, position, axe):
            matrice_ajout = np.zeros((i_ajout, j_ajout))
            if position == 0:
                matrices = (matrice_ajout, self.mat_points)
            else:
                matrices = (self.mat_points, matrice_ajout)

            self.mat_points = np.concatenate(matrices, axis=axe)

        mat_size_i, mat_size_j = self.mat_points.shape
        if j < 0:
            agrandir(mat_size_i, abs(j), 0, 1)
            self.mat_j0 -= self.taille_grid * abs(j)
            return i, j + 1

        elif j > mat_size_j - 1:
            agrandir(mat_size_i, j - mat_size_j + 1, 1, 1)

        elif i < 0:
            agrandir(abs(i), mat_size_j, 0, 0)
            self.mat_i0 -= self.taille_grid * abs(i)
            return i + 1, j

        elif i > mat_size_i - 1:
            agrandir(i - mat_size_i + 1, mat_size_j, 1, 0)

        return i, j

    # Vérifie si il y a des rangés vides, si c'est le cas, rapetisse la matrice
    def rapetisser_matrice(self):
        len_i = self.mat_points.shape[0]
        len_j = self.mat_points.shape[1]

        for i in reversed(range(len_i)):
            ligne_vide = True
            for j in range(len_j):
                if isinstance(self.mat_points[i, j], Fil) or isinstance(self.mat_points[i, j], Noeud):
                    ligne_vide = False
                    break
            if ligne_vide:
                self.mat_points = np.delete(self.mat_points, i, 0)
                len_i -= 1
            else:
                break

        for i in range(len_i):
            ligne_vide = True
            for j in range(len_j):
                if isinstance(self.mat_points[0, j], Fil) or isinstance(self.mat_points[0, j], Noeud):
                    ligne_vide = False
                    break
            if ligne_vide:
                self.mat_points = np.delete(self.mat_points, 0, 0)
                self.mat_i0 += self.taille_grid
                len_i -= 1
            else:
                break

        for j in reversed(range(len_j)):
            colonne_vide = True
            for i in range(len_i):
                if isinstance(self.mat_points[i, j], Fil):
                    colonne_vide = False
                    break
            if colonne_vide:
                self.mat_points = np.delete(self.mat_points, j, 1)
                len_j -= 1
            else:
                break

        for j in range(len_j):
            colonne_vide = True
            for i in range(len_i):
                if isinstance(self.mat_points[i, 0], Fil) or isinstance(self.mat_points[i, 0], Noeud):
                    colonne_vide = False
                    break
            if colonne_vide:
                self.mat_points = np.delete(self.mat_points, 0, 1)
                self.mat_j0 += self.taille_grid
            else:
                break

    def continuer_dessin(self, pos):
        collision = self.verifier_collision_fil(pos)

        # Ajuste la dernière ligne pour qu'elle s'étende du pivot à la position selon grid du curseur
        if collision is not None:
            curs_x, curs_y = self.pos_selon_grid(pos)

            ligne = self.lignes[-1]
            pivot = ligne.line().p1()

            diff_x = curs_x - pivot.x()
            diff_y = curs_y - pivot.y()

            if abs(diff_x) > abs(diff_y):
                sens_x = 1
                if diff_x < 0:
                    sens_x = -1
                sens_y = 0
                x = curs_x
                y = pivot.y()

            else:
                sens_y = 1
                if diff_y < 0:
                    sens_y = -1
                sens_x = 0
                x = pivot.x()
                y = curs_y

            dernier_point = ligne.line().p2()
            if QPointF(x, y) != dernier_point:
                self.fil_complet = False

                ligne_p2_x = pivot.x() + self.taille_grid * sens_x
                ligne_p2_y = pivot.y() + self.taille_grid * sens_y

                ligne_i, ligne_j = self.pos_to_mat(ligne_p2_x, ligne_p2_y)

                while True:
                    if ligne_i < 0 or ligne_j < 0:
                        mat_num = 0
                    else:
                        try:
                            mat_num = self.mat_points[ligne_i, ligne_j]
                        except IndexError:
                            mat_num = 0

                    if isinstance(mat_num, Fil) or isinstance(mat_num, Noeud):
                        x_avant = ligne_p2_x - self.taille_grid * sens_x
                        y_avant = ligne_p2_y - self.taille_grid * sens_y
                        if mat_num == self.nouveau_fil or QPointF(x_avant, y_avant) == self.points_avant_pivot[0]:
                            ligne_p2_x = x_avant
                            ligne_p2_y = y_avant
                        else:
                            self.fil_complet = True

                        break

                    if ligne_p2_x == x and ligne_p2_y == y:
                        break

                    ligne_i += sens_y
                    ligne_j += sens_x
                    ligne_p2_x += self.taille_grid * sens_x
                    ligne_p2_y += self.taille_grid * sens_y

                ligne.setLine(QLineF(pivot.x(), pivot.y(), ligne_p2_x, ligne_p2_y))

    # retourne la position dans la scene d'un point dans la matrice points
    # Jamais utilisée pour l'instant, possiblement à retirer un jour
    def mat_to_pos(self, i, j):
        x = (j * self.taille_grid) + self.mat_j0
        y = (i * self.taille_grid) + self.mat_i0

        return x, y

    # retourne la position dans la matrice points d'une position dans la scène
    def pos_to_mat(self, x, y):
        mat_i = round((y - self.mat_i0) / self.taille_grid)
        mat_j = round((x - self.mat_j0) / self.taille_grid)

        return mat_i, mat_j

    # retourne la position d'un point selon les positions possibles créées par le grid
    def pos_selon_grid(self, pos):
        x = round(pos.x() / self.taille_grid) * self.taille_grid
        x = max(min(x, math.floor(self.scene_size.width() / self.taille_grid) * self.taille_grid), 0)
        y = round(pos.y() / self.taille_grid) * self.taille_grid
        y = max(min(y, math.floor(self.scene_size.height() / self.taille_grid) * self.taille_grid), 0)

        return x, y

    def creer_toolbar(self):
        self.toolbar = QToolBar()
        # ne permet pas à l'utilisateur de cacher la toolbar.
        self.toolbar.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)

        # Ajoute le bouton main à la toolbar
        main_icone = QIcon("images/toolbar/main.png")
        main_bouton = ToolTipButton("Main")
        main_bouton.setIcon(main_icone)
        main_bouton.setIconSize(QSize(45, 45))
        main_bouton.clicked.connect(self.main_click)
        self.toolbar.addWidget(main_bouton)

        # ajoute le bouton poubelle à la toolbar
        poubelle_icone = QIcon("images/toolbar/poubelle.webp")
        poubelle_bouton = ToolTipButton("Main")
        poubelle_bouton.setIcon(poubelle_icone)
        poubelle_bouton.setIconSize(QSize(45, 45))
        poubelle_bouton.clicked.connect(self.poubelle_click)
        self.toolbar.addWidget(poubelle_bouton)

        # ajoute le bouton fil à la toolbar
        fil_icone = QIcon("images/toolbar/fil.png")
        fil_bouton = ToolTipButton("Fil")
        fil_bouton.setIcon(fil_icone)
        fil_bouton.setIconSize(QSize(45, 45))
        fil_bouton.clicked.connect(self.fil_click)
        self.toolbar.addWidget(fil_bouton)

        # Ajouter un bouton dans la toolbar pour chaque composante
        for composante in toolbar_composantes.values():
            bouton = ToolTipButton(composante.nom)
            bouton.setIcon(QIcon(composante.image_toolbar))
            bouton.setIconSize(QSize(45, 45))
            bouton.clicked.connect(lambda _, c=composante: self.composante_toolbar_clicked(c))
            self.toolbar.addWidget(bouton)

        self.main_window.addToolBar(self.toolbar)

    def supprimer_toolbar(self):
        self.main_window.removeToolBar(self.toolbar)
        self.toolbar.deleteLater()
        self.toolbar = None

    def main_click(self):
        self.selection = "main"

    def clic_gauche_main(self):
        pass

    def poubelle_click(self):
        self.selection = "poubelle"

        # TODO: faire en sorte que composante devant souris devienne rouge
        pass
        """# on doit passer du point central au coin supérieur gauche
        coin_sup_gauche_x = emplacement.x() - self.taille_grid
        coin_sup_gauche_y = emplacement.y() - self.taille_grid
        zone_surbrillance = QGraphicsRectItem(coin_sup_gauche_x, coin_sup_gauche_y, self.taille_grid * 2,
                                                  self.taille_grid * 2)
        zone_surbrillance.setOpacity(0.3)
        zone_surbrillance.setZValue(2)
        zone_surbrillance.setBrush(QColor(218, 44, 44))
        self.addItem(zone_surbrillance)"""

    def composante_toolbar_clicked(self, composante):
        if composante in toolbar_composantes.values():
            self.selection = "composante"
            self.composante_selectionnee = composante.__class__()

            if self.image_composante is not None:
                self.removeItem(self.image_composante)
                self.image_composante = None

            pixmap = QPixmap(self.composante_selectionnee.image_circuit)
            pixmap_scalise = pixmap.scaled(self.taille_grid * 2, self.taille_grid * 2)
            self.image_composante = QGraphicsPixmapItem(pixmap_scalise)
            self.image_composante.setPos(self.taille_grid, self.taille_grid)
            self.image_composante.setOffset(-self.taille_grid, -self.taille_grid)
            self.image_composante.setZValue(3)
            self.addItem(self.image_composante)
            self.accepter_modification = True

            perimetre = self.image_composante.boundingRect()
            self.couleur_recouvre = QGraphicsRectItem(perimetre, self.image_composante)
            self.couleur_recouvre.setOpacity(0.3)
            self.couleur_recouvre.setZValue(1)
            self.couleur_recouvre.setBrush(QColor(218, 44, 44))
            self.addItem(self.couleur_recouvre)

    def fil_click(self):
        self.selection = "fil"

        if self.image_composante is not None:
            self.removeItem(self.image_composante)
            self.image_composante = None

    def inserer_composante(self, composante):
        if self.image_composante:
            composante.image_item = self.image_composante

            points_fil, points_cote = self.points_composante(self.image_composante.rotation())
            composante.points_fil = points_fil
            composante.points_cote = points_cote
            point_milieu = points_fil[1]
            fil = self.verifier_collision_fil(point_milieu)
            # on enleve la surbrillance
            self.removeItem(self.couleur_recouvre)
            self.couleur_recouvre = None
            # on cache le fil sous la composante
            coin_sup_gauche_x = point_milieu.x() - self.taille_grid
            coin_sup_gauche_y = point_milieu.y() - self.taille_grid
            zone_blanche = QGraphicsRectItem(coin_sup_gauche_x, coin_sup_gauche_y, self.taille_grid * 2,
                                             self.taille_grid * 2)
            zone_blanche.setOpacity(1)
            zone_blanche.setZValue(1)
            zone_blanche.setBrush(QColor(255, 255, 255))
            self.addItem(zone_blanche)
            self.zones_blanches.append(zone_blanche)

            composante.items.append(zone_blanche)

            # on remet le grid où la composante
            pen = QPen(QColorConstants.Gray)
            # ajoute les lignes horizontale
            for i in range(3):
                x1 = point_milieu.x() - self.taille_grid
                x2 = point_milieu.x() + self.taille_grid
                y = point_milieu.y() + (i - 1) * self.taille_grid

                ligne = self.addLine(x1, y, x2, y, pen)
                ligne.setZValue(2.5)
                composante.items.append(ligne)

            # ajoute lignes verticales
            for i in range(3):
                y1 = point_milieu.y() - self.taille_grid
                y2 = point_milieu.y() + self.taille_grid
                x = point_milieu.x() + (i - 1) * self.taille_grid

                ligne = self.addLine(x, y1, x, y2, pen)
                ligne.setZValue(2.5)
                composante.items.append(ligne)

            for point in points_fil + points_cote:
                i, j = self.pos_to_mat(point.x(), point.y())
                i, j = self.agrandir_matrice(i, j)
                self.mat_points[i, j] = composante

            fil.ajouter_composante(composante)

            # on reset les variables liées à l'ajout de composantes
            self.accepter_modification = False
            self.image_composante = None
            # on update les infos liées à l'ajout pour le rollback
            self.operations.append(1)
            self.ajouts.append(composante)
            self.rollback_possible()

    def clic_droit_composante(self):
        liste_refusee = ["Ampèremètre", "Voltmètre"]
        if self.composante_selectionnee.nom not in liste_refusee:
            self.image_composante.setRotation(self.image_composante.rotation() + 90)

    def points_composante(self, rotation):
        x_mult, y_mult = (round(-math.cos(math.radians(rotation))),
                          round(math.sin(math.radians(rotation))))

        milieu = self.image_composante.scenePos()
        # Les points du milieu qui doivent etre connecté au fil
        point_debut = QPointF(milieu.x() + x_mult * self.taille_grid, milieu.y() + y_mult * self.taille_grid)
        point_fin = QPointF(milieu.x() - x_mult * self.taille_grid, milieu.y() - y_mult * self.taille_grid)
        points_fil = [point_debut, milieu, point_fin]

        # Les points ou ca doit etre vide
        points_vide = []
        for i in range(3):
            if y_mult == 0:
                points_vide.append(QPointF(milieu.x() + (i - 1) * self.taille_grid, milieu.y() + self.taille_grid))
                points_vide.append(QPointF(milieu.x() + (i - 1) * self.taille_grid, milieu.y() - self.taille_grid))
            else:
                points_vide.append(QPointF(milieu.x() + self.taille_grid, milieu.y() + (i - 1) * self.taille_grid))
                points_vide.append(QPointF(milieu.x() - self.taille_grid, milieu.y() + (i - 1) * self.taille_grid))

        return points_fil, points_vide

    def valider_position(self):
        points_fil, points_vide = self.points_composante(self.image_composante.rotation())

        self.accepter_positionnement = True
        # verifie que ya un fil tout au long du milieu
        for point in points_fil:
            collision = self.verifier_collision_fil(point)
            if not isinstance(collision, Fil):
                self.accepter_positionnement = False
                break

        # verifie que ya pas collision avec un autre fil au trop proche
        if self.accepter_positionnement:
            for point in points_vide:
                collision = self.verifier_collision_fil(point)
                if collision != 0:
                    self.accepter_positionnement = False
                    break

        self.couleur_image()

        # Essaye dans l'autre sens si cest un amperemetre ou voltmetre et que ca fonctionne pas deja
        if ((self.composante_selectionnee.nom == "Ampèremètre" or self.composante_selectionnee.nom == "Voltmètre")
                and self.image_composante.rotation() == 0 and self.accepter_positionnement is False):
            self.image_composante.setRotation(90)
            self.valider_position()
            self.image_composante.setRotation(0)

    def couleur_image(self):
        # vert si on peut placer la composante, rouge sinon
        if not self.accepter_positionnement:
            self.couleur_recouvre.setBrush(QColor(218, 44, 44))
        else:
            self.couleur_recouvre.setBrush(QColor(44, 246, 44))

    # TODO
    def jeter_composante(self, position):
        a_jeter = None
        for zone in self.zones_surbrillance:
            position_curseur_traduite = zone.mapFromScene(position)
            if zone.contains(position_curseur_traduite):
                a_jeter = zone
                break

        if a_jeter:
            # on split la liste en 3: avant l'élément (si jamais), l'élément et après l'élément (si jamais)
            point_a_trouver = a_jeter.mapToScene(a_jeter.rect().center())
            index = self.composantes.index(point_a_trouver)

            if index > 2:
                liste_avant = self.composantes[0:index - 2]

            else:
                liste_avant = []

            element = self.composantes[index - 2:index + 1]

            if index != len(self.composantes) - 1:
                liste_apres = self.composantes[index + 1:]
            else:
                liste_apres = []

            # on recrée self.composantes sans celle enlevée
            self.composantes = liste_avant
            for i in liste_apres:
                self.composantes.append(i)

            position_supprimee = element.pop()
            image_composante_supprimee = element.pop()
            composante_supprimee = element.pop()

            # on retire de la scène l'image de la composante et le carré rouge associé
            self.removeItem(image_composante_supprimee)
            self.removeItem(a_jeter)

            # on enleve le carré blanc et le grid supplémentaire
            self.retirer_carre_blanc(position_supprimee)
            self.supprimer_lignes_supplementaires(position_supprimee)

            # on note ce qu'on vient d'enlever pour le rollback
            self.operations.append(2)
            self.composantes_jetes.append(composante_supprimee)
            self.composantes_jetes.append(image_composante_supprimee)
            self.composantes_jetes.append(position_supprimee)
            self.composantes_jetes.append(math.floor(index / 3))
            self.dernier_jete.append("composante")

            self.selection = None
            if hasattr(self, "zones_surbrillance"):
                for item in self.zones_surbrillance:
                    self.removeItem(item)

    def deplacer_composante(self, position):
        x, y = self.pos_selon_grid(position)

        # évite que la composante soit à moitié sortie de la grid
        pos_max_x = self.scene_size.width() - self.taille_grid
        pos_max_y = self.scene_size.height() - self.taille_grid
        x = max(min(x, pos_max_x), self.taille_grid)
        y = max(min(y, pos_max_y), self.taille_grid)

        self.image_composante.setPos(x, y)

    def retirer_carre_blanc(self, position):
        lieu_a_retirer = QPointF(position.x() - self.taille_grid, position.y() - self.taille_grid)
        elements = self.items(lieu_a_retirer)
        for element in elements:
            if element in self.zones_blanches:
                self.removeItem(element)
                self.zones_blanches.remove(element)

    def modifier_composante(self, position):
        x, y = self.pos_selon_grid(position)
        collision = self.verifier_collision_fil(QPointF(x, y))
        if isinstance(collision, Composante):
            modification, ignorer = collision.clique(self.taille_grid)
            self.modifications.append(modification, collision)
            # TODO faire en sorte de save la modification dans les rollbacks

        self.operations.append(4)

    def tourner_image_composante(self, position):
        x, y = self.pos_selon_grid(position)
        collision = self.verifier_collision_fil(QPointF(x, y))

        if isinstance(collision, Composante) and collision.nom != "Ampèremètre" and collision.nom != "Voltmètre":
            self.operation_tourner(collision)
            self.operations.append(3)
            self.tournes.append(collision)

    @staticmethod
    def operation_tourner(collision):
        collision.image_item.setRotation(collision.image_item.rotation() + 180)

class GraphicsView(QGraphicsView):

    def __init__(self, scene, main_window):
        super().__init__(scene)
        self.scene = scene
        self.viewport().setMouseTracking(True)

    def mousePressEvent(self, event):
        position_scene = self.mapToScene(event.position().toPoint())
        if event.button() == Qt.MouseButton.LeftButton:
            if self.scene.selection == "fil":
                self.scene.clic_gauche_fil(position_scene)

            elif self.scene.selection == "main":
                pass
                # TODO: si on souhaite utiliser la main, connecter cela à def clic_gauche_main

            elif self.scene.selection == "composante" and self.scene.accepter_positionnement:
                self.scene.inserer_composante(self.scene.composante_selectionnee)

            elif self.scene.selection == "poubelle":
                self.scene.jeter_composante(position_scene)

        if event.button() == Qt.MouseButton.RightButton:
            if self.scene.selection == "fil":
                self.scene.clic_droit_fil()
            if self.scene.selection == "composante" and self.scene.accepter_modification == True:
                self.scene.clic_droit_composante()
                self.scene.valider_position()

    def mouseMoveEvent(self, event):
        position_scene = self.mapToScene(event.position().toPoint())
        if self.scene.selection == "fil" and self.scene.dessine:
            self.scene.continuer_dessin(position_scene)
        elif self.scene.selection == "composante" and self.scene.accepter_modification == True:
            position_scene = self.mapToScene(event.position().toPoint())
            self.scene.deplacer_composante(position_scene)
            self.scene.valider_position()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if not self.scene.image_composante:
                position_scene = self.mapToScene(event.position().toPoint())
                self.scene.modifier_composante(position_scene)

        elif event.button() == Qt.MouseButton.RightButton:
            if not self.scene.image_composante:
                position_scene = self.mapToScene(event.position().toPoint())
                self.scene.tourner_image_composante(position_scene)


class LoisPhysiques:
    @staticmethod
    def loi_ohm(resistance, tension):
        intensite = tension / resistance
        return intensite

    @staticmethod
    def resistance_serie(*args):
        res_eq = 0
        for arg in args:
            res_eq += arg
        return res_eq

    @staticmethod
    def resistance_parallele(*args):
        res_eq = 0
        for arg in args:
            res_eq += 1 / arg
        return 1 / res_eq
