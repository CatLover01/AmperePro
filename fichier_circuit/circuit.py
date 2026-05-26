from PySide6.QtCore import QSize, QPointF, QLineF, QPoint
from PySide6.QtGui import QColorConstants, QPen, Qt, QAction, QIcon, QPixmap, QColor
from PySide6.QtWidgets import (QGraphicsScene, QGraphicsView, QPushButton, QDialog,
                               QHBoxLayout, QToolBar, QGraphicsPixmapItem, QGraphicsRectItem, QInputDialog,
                               QGraphicsLineItem, QGraphicsItemGroup)
import math
import numpy as np

from button import ToolTipButton
from fichier_circuit.fil import Fil
from fichier_circuit.noeud import Noeud
from composantes import toolbar_composantes, Composante, TypeComposante
from fichier_circuit.calculateur_courant import calculer_circuit
from sauvegarde import Sauvegarde, FilDTO, NoeudDTO


class Circuit(QGraphicsScene):
    def __init__(self, mainwindow, sauvegarde: Sauvegarde, id_circuit: str):
        super().__init__()
        self.main_window = mainwindow
        self.scene_size = QSize(2000, 2000)
        self.largeur = self.scene_size.width()
        self.hauteur = self.scene_size.height()

        self.dessine = False
        self.dernier_point = None

        self.lignes: list[QGraphicsLineItem] = []
        self.noeuds: list[Noeud] = []
        self.points_avant_pivot = []
        self.fil_complet = False
        self.nouveau_fil = None

        # listes pour le rollback
        self.ajouts = []
        self.composantes_jetes = []
        self.fils_jetes = []
        self.modifications = []
        # les ajouts seront 1, les jetés seront 2, composantes tournées seront 3 et composantes modifiées seront 4
        self.operations = []
        self.tournes = []

        # pour les composantes
        self.toolbar = None
        self._selection = "main"
        self.composante_selectionnee = None
        self.image_composante = None
        self.couleur_recouvre = None
        self.accepter_modification = True
        self.accepter_positionnement = False
        self.zones_surbrillance = []
        self.fils_surbrillance = []
        self.composante_surbrillance = None
        self.grid_par_dessus = []

        # La distance entre chaque ligne dans le grid
        self.taille_grid = 20

        self.mat_i0 = 0
        self.mat_j0 = 0
        self.dessiner_fond_grid()

        largeur_fil_base = 200
        hauteur_fil_base = 140

        self.graphics_view = GraphicsView(self)
        self.main_window.setCentralWidget(self.graphics_view)
        self.graphics_view.setMinimumSize(self.scene_size)
        self.graphics_view.setScene(self)

        if id_circuit is None:
            fil_base, self.mat_points = self.dessiner_circuit_base(largeur_fil_base, hauteur_fil_base)
            self.fils = [fil_base]

            # Note: on garde le circuit de base mais quand les fils pourront être ajouter sans toucher un autre fil,
            # on pourra enlever la fonction si dessus
        else:
            circuit = sauvegarde.get_circuit(id_circuit)
            noeuds: list[Noeud] = []
            fils: list[Fil] = []
            for noeud in circuit.noeuds:
                noeuds.append(Noeud.from_dto(noeud))
            for fil in circuit.fils:
                fils.append(Fil.from_dto(fil, self))

            self.noeuds = noeuds
            self.fils = fils

            # TODO(hugo): je ne trouve pas la fonction pour générer la matrice a partir des fils et noeuds
            # self.mat_points = np.array(...)

        self.sauvegarde = sauvegarde
        self.id = id_circuit

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
    def fils_surbrillance(self):
        return self._fils_surbrillance

    @fils_surbrillance.setter
    def fils_surbrillance(self, fils_surbrillance):
        self._fils_surbrillance = fils_surbrillance

    @property
    def grid_par_dessus(self):
        return self._grid_par_dessus

    @grid_par_dessus.setter
    def grid_par_dessus(self, grid_par_dessus):
        self._grid_par_dessus = grid_par_dessus

    @property
    def allouer_fermeture(self):
        return self._allouer_fermeture

    @allouer_fermeture.setter
    def allouer_fermeture(self, allouer_fermeture):
        self._allouer_fermeture = allouer_fermeture

    def sauvegarder_triggered(self):
        # Si l'id est None, on demande un nom pour le circuit + on le créé
        if self.id is None:
            nom, ok = QInputDialog.getText(self.main_window, "Nouveau circuit", "Entre le nom de ton circuit")
            if nom and ok:
                self.id = self.sauvegarde.creation_circuit_libre(nom)
            else:
                # Si l'utilisateur a dismiss(quitter) le dialog pour le nom du circuit on annuler la création du circuit
                return

        fils, noeuds = self.serialiser_circuit()
        self.sauvegarde.modifie_circuit(self.id, fils, noeuds)

    def serialiser_circuit(self) -> tuple[list[FilDTO], list[NoeudDTO]]:
        # Map internal object id to index (on devrait probablement avoir un id pour chaque noeud / fil / composante)
        noeud_to_index = {n: i for i, n in enumerate(self.noeuds)}
        fil_to_index = {f: i for i, f in enumerate(self.fils)}

        fils = [f.to_dto(noeud_to_index) for f in self.fils]
        noeuds = [n.to_dto(fil_to_index, noeud_to_index) for n in self.noeuds]
        return fils, noeuds

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
            # si la dernière opération est d'ajouter un élément, on le supprime grâce à sa position qu'on a enregistrée.
            dernier_ajout = self.ajouts.pop()
            self.jeter_element(dernier_ajout, False)

        elif dernier == 2:
            composante = self.composantes_jetes.pop()
            #si c'est une composante, on la réinsère comme la première fois.
            if isinstance(composante, Composante):
                self.image_composante = composante.image_item
                self.inserer_composante(composante, False)
            else:
                pass

        elif dernier == 3:
            # on veut annuler le fait d'avoir tourner une composante de 180 degrés. Cela revient à la tourner à nouveau.
            composante = self.tournes.pop()
            # le isinstance rassure python mais c'est une certitude puisque le cas contraire ne se serait pas rendu
            # jusqu'au rollback.
            if isinstance(composante, Composante):
                self.tourner_image_composante(composante.points_fil[1], False)

        else:
            # annuler la plus récente modification à une composante.
            dernier_element = self.modifications.pop()
            collision = self.modifications.pop()
            valeur = self.modifications.pop()

            if dernier_element == 1:
                # remettre dernière valeur tension
                collision.rollback(valeur)

            elif dernier_element == 2:
                # remettre dernière valeur résistance
                collision.rollback(valeur)

            elif dernier_element == 3:
                # dans ce cas, le rollback revient à faire l'action. Les autres valeurs sont inutiles,
                # elles n'ont été stockées que par soucis d'unicité de la liste
                collision.double_clique_gauche(self.taille_grid)
                collision.fil.calculs()
                self.update_courant()

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
    def ajouter_ligne(self, xi: float, yi: float, x: float, y: float) -> QGraphicsLineItem:
        pen = QPen(QColorConstants.Black)
        largeur_crayon = 3
        pen.setWidthF(largeur_crayon)
        ligne = self.addLine(xi, yi, x, y, pen)

        return ligne

    # TODO: quand on pourra ajouter des fils sans qu'ils soient attachés à d'autres fils, enlever cette méthode
    def dessiner_circuit_base(self, largeur_circuit: int, hauteur_circuit: int):
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

        print("=" * 70)

    # trouve ce qui est dans le grid à la position donnée
    def verifier_collision(self, pos: QPointF):
        x, y = self.pos_selon_grid(pos)
        pos_i, pos_j = self.pos_to_mat(x, y)

        max_i = self.mat_points.shape[0] - 1
        max_j = self.mat_points.shape[1] - 1

        # False si a la meme position qu'avant
        if QPointF(x, y) == self.dernier_point:
            return False
        elif max_i >= pos_i >= 0 and max_j >= pos_j >= 0:
            touche = self.mat_points[pos_i, pos_j]
            if touche is not None and (
                    isinstance(touche, Noeud) or isinstance(touche, Composante) or isinstance(touche, Fil)):
                return touche

        return None

    def clic_gauche_fil(self, pos: QPointF):
        # return tous les points dans le grid selon la ligne
        def get_points_ligne(debut_ligne_clic: QPointF, fin_ligne_clic: QPointF) -> list[QPointF]:
            diff_x = fin_ligne_clic.x() - debut_ligne_clic.x()
            diff_y = fin_ligne_clic.y() - debut_ligne_clic.y()
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

            points_clic = []
            for k in range(nb_points):
                pos_x = debut_ligne_clic.x() + (k + 1) * self.taille_grid * sens_x
                pos_y = debut_ligne_clic.y() + (k + 1) * self.taille_grid * sens_y
                points_clic.append(QPointF(pos_x, pos_y))

            return points_clic

        # met une reference au fil partout où il touche dans la matrice points
        def mettre_fil_mat(ligne_clic: QGraphicsLineItem, fil_clic: Fil):
            debut_ligne_clic = ligne_clic.line().p1()
            fin_ligne_clic = ligne_clic.line().p2()
            points_clic = get_points_ligne(debut_ligne_clic, fin_ligne_clic)

            i_fin, j_fin = self.pos_to_mat(points_clic[-1].x(), points_clic[-1].y())
            self.agrandir_matrice(i_fin, j_fin)

            for point_clic in points_clic:
                i, j = self.pos_to_mat(point_clic.x(), point_clic.y())
                if not isinstance(self.mat_points[i, j], Fil) and not isinstance(self.mat_points[i, j], Noeud):
                    self.mat_points[i, j] = fil_clic

            return debut_ligne_clic, fin_ligne_clic, points_clic

        fil_touche = self.verifier_collision(pos)
        x, y = self.pos_selon_grid(pos)

        if not self.dessine:
            # lorsque le fil est pas démarré et que le clic démarre à un fil, un nouveau fil est commencé
            if isinstance(fil_touche, Fil) or isinstance(fil_touche, Noeud):
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

            self.dernier_point = None
            fil_noeud1 = self.verifier_collision(points[0])

            if isinstance(fil_noeud1, Fil):
                noeud_debut = Noeud(points[0])
                self.noeuds.append(noeud_debut)

                fil_noeud1.ajouter_noeud(points[0], noeud_debut)
            else:
                noeud_debut = fil_noeud1

            fil_noeud2 = self.verifier_collision(fin_ligne)

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
            point_a_garder = points[math.floor(len(points)/2)]
            self.ajouts.append(point_a_garder)

            self.nouveau_fil.calculs()
            self.nouveau_fil = None

            self.operations.append(1)
            self.rollback_possible()

            self.main_click()
            self.update_courant()

        else:
            point = self.lignes[-1].line().p2()
            est_premier_point = point == self.points_avant_pivot[0]
            sur_pivot = point == self.lignes[-1].line().p1()
            touche_fil_noeud = isinstance(fil_touche, Fil) or isinstance(fil_touche, Noeud)

            # lorsque le fil n'est pas complet, crée un nouveau pivot au fil pour que l'usager puisse changer de sens
            if not est_premier_point and not sur_pivot and not touche_fil_noeud:
                debut_ligne, fin_ligne, points_apres_pivot = mettre_fil_mat(self.lignes[-1], self.nouveau_fil)
                ligne = self.ajouter_ligne(fin_ligne.x(), fin_ligne.y(), fin_ligne.x(), fin_ligne.y())

                self.points_avant_pivot += points_apres_pivot
                self.lignes.append(ligne)
                self.dernier_point = QPointF(fin_ligne.x(), fin_ligne.y())
                self.continuer_dessin(pos)

    def fil_accepte(self, position: QPointF):
        # TODO: valider que l'on peut mettre un fil (pas de composantes, pas collé à un autre fil
        pass

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
            self.dernier_point = None

    # Vérifie si i et j sont hors de la matrice, si c'est le cas, agrandit la matrice pour pouvoir les inclure
    def agrandir_matrice(self, i: int, j: int):
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

    def continuer_dessin(self, pos: QPointF):
        collision = self.verifier_collision(pos)
        # Ajuste la dernière ligne pour qu'elle s'étende du pivot à la position selon grid du curseur
        if collision is not False:
            curs_x, curs_y = self.pos_selon_grid(pos)

            ligne = self.lignes[-1]
            pivot = ligne.line().p1()

            diff_x = curs_x - pivot.x()
            diff_y = curs_y - pivot.y()

            if diff_x == 0 == diff_y:
                ligne_p2_x = pivot.x()
                ligne_p2_y = pivot.y()
            else:
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
                            touche = 0
                        else:
                            try:
                                touche = self.mat_points[ligne_i, ligne_j]
                            except IndexError:
                                touche = 0

                        if isinstance(touche, Fil) or isinstance(touche, Noeud):
                            x_avant = ligne_p2_x - self.taille_grid * sens_x
                            y_avant = ligne_p2_y - self.taille_grid * sens_y
                            if touche == self.nouveau_fil or QPointF(x_avant, y_avant) == self.points_avant_pivot[0]:
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
                else:
                    ligne_p2_x, ligne_p2_y = dernier_point.x(), dernier_point.y()

            ligne.setLine(QLineF(pivot.x(), pivot.y(), ligne_p2_x, ligne_p2_y))

    # retourne la position dans la scene d'un point dans la matrice points
    # Jamais utilisée pour l'instant, possiblement à retirer un jour
    def mat_to_pos(self, i, j):
        x = (j * self.taille_grid) + self.mat_j0
        y = (i * self.taille_grid) + self.mat_i0

        return x, y

    # retourne la position dans la matrice points d'une position dans la scène
    def pos_to_mat(self, x: float, y: float):
        mat_i = round((y - self.mat_i0) / self.taille_grid)
        mat_j = round((x - self.mat_j0) / self.taille_grid)

        return mat_i, mat_j

    # retourne la position d'un point selon les positions possibles créées par le grid
    def pos_selon_grid(self, pos: QPointF):
        x = round(pos.x() / self.taille_grid) * self.taille_grid
        x = max(min(x, math.floor(self.scene_size.width() / self.taille_grid) * self.taille_grid), 0)
        y = round(pos.y() / self.taille_grid) * self.taille_grid
        y = max(min(y, math.floor(self.scene_size.height() / self.taille_grid) * self.taille_grid), 0)

        return x, y

    def creer_toolbar(self):
        self.toolbar = QToolBar()

        # 2. Force the Toolbar to check for updates on mouse release
        self.toolbar.updateGeometry()
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)
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
        poubelle_bouton = ToolTipButton("Poubelle")
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
        for composante_classe in toolbar_composantes.values():
            bouton = ToolTipButton(composante_classe().nom)
            bouton.setIcon(QIcon(composante_classe().image_toolbar))
            bouton.setIconSize(QSize(45, 45))
            bouton.clicked.connect(lambda _, c=composante_classe: self.composante_toolbar_clicked(c))
            self.toolbar.addWidget(bouton)

        self.main_window.addToolBar(self.toolbar)

    def supprimer_toolbar(self):
        self.main_window.removeToolBar(self.toolbar)
        self.toolbar.deleteLater()
        self.toolbar = None

    def main_click(self):
        if self.selection == "fil":
            self.clic_droit_fil()

        if self.image_composante:
            self.annuler_signalement()
            self.removeItem(self.image_composante)
            self.image_composante = None

        self.selection = "main"

    def clic_gauche_main(self):
        pass

    def poubelle_click(self):
        if self.selection == "fil":
            self.clic_droit_fil()

        self.selection = "poubelle"

    def composante_toolbar_clicked(self, composante_classe):
        if self.selection == "fil":
            self.clic_droit_fil()

        if composante_classe in toolbar_composantes.values():
            self.selection = "composante"
            self.composante_selectionnee = composante_classe()

            if self.image_composante is not None:
                self.removeItem(self.image_composante)
                self.image_composante = None

            types_signes = [TypeComposante.Amperemetre, TypeComposante.Voltmetre]
            if self.composante_selectionnee.type in types_signes:
                self.image_composante = QGraphicsItemGroup()

                pixmap_signes = QPixmap("images/circuit/signes.png")
                signes_scalise = pixmap_signes.scaled(self.taille_grid * 2, self.taille_grid * 2)
                item_signes = QGraphicsPixmapItem(signes_scalise)
                item_signes.setOffset(-self.taille_grid, -self.taille_grid)
                self.composante_selectionnee.image_item = item_signes
                self.image_composante.addToGroup(item_signes)

                image_comp = QPixmap(self.composante_selectionnee.image_circuit)
                image_comp_scalise = image_comp.scaled(self.taille_grid * 2, self.taille_grid * 2)
                item_img_comp = QGraphicsPixmapItem(image_comp_scalise)
                item_img_comp.setOffset(-self.taille_grid, -self.taille_grid)
                self.composante_selectionnee.item_comp = item_img_comp
                self.image_composante.addToGroup(item_img_comp)

                self.image_composante.setPos(self.taille_grid, self.taille_grid)
                perimetre = item_signes.boundingRect()
            else:
                pixmap = QPixmap(self.composante_selectionnee.image_circuit)
                pixmap_scalise = pixmap.scaled(self.taille_grid * 2, self.taille_grid * 2)
                self.image_composante = QGraphicsPixmapItem(pixmap_scalise)

                self.image_composante.setPos(self.taille_grid, self.taille_grid)
                self.image_composante.setOffset(-self.taille_grid, -self.taille_grid)
                self.composante_selectionnee.image_item = self.image_composante

                perimetre = self.image_composante.boundingRect()

            self.image_composante.setZValue(3)
            self.addItem(self.image_composante)

            self.couleur_recouvre = QGraphicsRectItem(perimetre, self.image_composante)
            self.couleur_recouvre.setOpacity(0.3)
            self.couleur_recouvre.setZValue(1)
            self.couleur_recouvre.setBrush(QColor(218, 44, 44))
            self.addItem(self.couleur_recouvre)
            self.accepter_modification = True

    def fil_click(self):
        self.selection = "fil"

        if self.image_composante is not None:
            self.removeItem(self.image_composante)
            self.image_composante = None

    # Refait les calculs du courant
    def update_courant(self):
        if len(self.fils) > 1:
            fils_voltmetre = []
            for fil in self.fils:
                if len(fil.composantes) == 1 and fil.composantes[0].type == TypeComposante.Voltmetre:
                    fils_voltmetre.append(fil)

            calculer_circuit(self.fils, self.noeuds, fils_voltmetre)

        else:
            fil = self.fils[0]
            try:
                amperes = fil.tension / fil.resistance
                fil.definir_amperage(amperes)
                if fil.sens_diode * amperes < 0 or fil.ignorer is True:
                    fil.definir_amperage(0)

            except ZeroDivisionError:
                if fil.tension == 0:
                    fil.definir_amperage(0)
                else:
                    amperes = 99999999999999
                    if fil.tension < 0:
                        amperes *= -1

                    if fil.sens_diode * amperes < 0 or fil.ignorer is True:
                        amperes = 0

                    fil.definir_amperage(amperes)

    def inserer_composante(self, composante: Composante, rollback: bool):
        if self.image_composante:
            points_fil, points_cote = self.points_composante(self.image_composante.rotation())
            composante.points_fil = points_fil
            composante.points_cote = points_cote
            point_milieu = points_fil[1]
            fil = self.verifier_collision(point_milieu)
            # on enleve la surbrillance
            if self.couleur_recouvre is not None:
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
            composante.fil = fil

            # on reset les variables liées à l'ajout de composantes
            self.accepter_modification = False
            self.image_composante = None

            # on retourne à la main
            self.main_click()

            # on update les infos liées à l'ajout pour le rollback si on ne vient pas du rollback
            if rollback:
                self.operations.append(1)
                self.ajouts.append(point_milieu)
                self.rollback_possible()

            # On recalcule le courant
            self.update_courant()

    def clic_droit_composante(self):
        rotation_initiale = self.image_composante.rotation()
        self.image_composante.setRotation(rotation_initiale + 90)

        types_signes = [TypeComposante.Amperemetre, TypeComposante.Voltmetre]
        if self.composante_selectionnee.type in types_signes:
            self.composante_selectionnee.item_comp.setRotation(-rotation_initiale - 90)

    def points_composante(self, rotation: float):
        x_mult, y_mult = (round(-math.cos(math.radians(rotation))),
                          round(-math.sin(math.radians(rotation))))

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
            collision = self.verifier_collision(point)
            if not isinstance(collision, Fil):
                self.accepter_positionnement = False
                break

        # verifie que ya pas collision avec un autre fil trop proche
        if self.accepter_positionnement:
            for point in points_vide:
                collision = self.verifier_collision(point)
                if collision is not None and collision != 0:
                    self.accepter_positionnement = False
                    break

        self.couleur_image()

    def couleur_image(self):
        # vert si on peut placer la composante, rouge sinon
        if not self.accepter_positionnement:
            self.couleur_recouvre.setBrush(QColor(218, 44, 44))
        else:
            self.couleur_recouvre.setBrush(QColor(44, 246, 44))

    def signaler_effacement(self, position_scene: QPointF):
        x, y = self.pos_selon_grid(position_scene)
        composante = self.verifier_collision(QPointF(x, y))

        if isinstance(composante, Composante):
            # on met la composante sous la souris en rouge
            self.composante_rouge(composante)

        elif isinstance(composante, Fil):
            # si on est sur un fil, celui-ci et toute ses composantes deviennent rouge.
            fil = composante
            if len(self.fils) != 1:
                fil.signaler_effacement()
                self.fils_surbrillance.append(fil)
                for element in fil.composantes:
                    self.composante_rouge(element)

        else:
            # si on est sur rien, on s'assure que rien n'est surbrillé
            # cela se passe également si on est sur un noeud pour éviter la confusion de l'utilisateur et du programme
            self.annuler_signalement()

    def annuler_signalement(self):
        if self.zones_surbrillance:
            for zone in self.zones_surbrillance:
                self.removeItem(zone)
            self.zones_surbrillance = []
            self.composante_surbrillance = None
        if self.fils_surbrillance:
            for fil in self.fils_surbrillance:
                fil.definir_amperage(fil.amperage)

    def composante_rouge(self, composante: Composante):
        if composante == self.composante_surbrillance:
            return

        point_milieu = composante.points_fil[1]

        # si la souris recouvre une composante, on le signale en la mettant en rouge.
        coin_sup_gauche_x = point_milieu.x() - self.taille_grid
        coin_sup_gauche_y = point_milieu.y() - self.taille_grid
        zone_rouge = QGraphicsRectItem(coin_sup_gauche_x, coin_sup_gauche_y, self.taille_grid * 2,
                                       self.taille_grid * 2)
        zone_rouge.setOpacity(1)
        zone_rouge.setZValue(1)
        zone_rouge.setBrush(QColor(218, 44, 44))
        self.composante_surbrillance = composante
        self.zones_surbrillance.append(zone_rouge)
        self.addItem(zone_rouge)

    def jeter_element(self, position: QPointF, rollback: bool):
        x, y = self.pos_selon_grid(position)
        composante = self.verifier_collision(QPointF(x, y))

        if isinstance(composante, Composante):
            # ménage visuel composante
            self.removeItem(composante.image_item)

            if hasattr(composante, "item_comp"):
                self.removeItem(composante.item_comp)

            self.annuler_signalement()
            self.retirer_elements(composante)

            # les fils redeviennent des fils
            for point_fil in composante.points_fil:
                i, j = self.pos_to_mat(point_fil.x(), point_fil.y())
                self.mat_points[i, j] = composante.fil

            for point_cote in composante.points_cote:
                i, j = self.pos_to_mat(point_cote.x(), point_cote.y())
                self.mat_points[i, j] = None

            composante.fil.composantes.remove(composante)
            composante.fil.calculs()

            self.update_courant()
            composante.nettoyer()

            # on ajuste pour rollback si on provient de clic gauche et pas du rollback (si rollback = True)
            if rollback:
                self.composantes_jetes.append(composante)
                self.operations.append(2)

        elif isinstance(composante, Fil):
            #ménage visuel
            # on supprime d'abord les composantes du fil
            for element in composante.composantes.copy():
                self.jeter_element(element.points_fil[1], False)

            composante.enlever_fil()
            self.annuler_signalement()

            if rollback:
                self.composantes_jetes.append(composante)
                self.operations.append(2)

    def deplacer_composante(self, position):
        x, y = self.pos_selon_grid(position)

        # évite que la composante soit à moitié sortie de la grid
        pos_max_x = self.scene_size.width() - self.taille_grid
        pos_max_y = self.scene_size.height() - self.taille_grid
        x = max(min(x, pos_max_x), self.taille_grid)
        y = max(min(y, pos_max_y), self.taille_grid)

        self.image_composante.setPos(x, y)

    def retirer_elements(self, composante: Composante):
        items = composante.items
        for item in items:
            self.removeItem(item)

    # Modification d'une composante lors du double click gauche
    def modifier_composante(self, position: QPointF):
        x, y = self.pos_selon_grid(position)
        composante = self.verifier_collision(QPointF(x, y))
        if isinstance(composante, Composante):
            a_modifier = [TypeComposante.Resistor, TypeComposante.Batterie, TypeComposante.Interrupteur]
            # il n'y a que ces composantes qui ont quelque chose à modifier
            if composante.type in a_modifier:
                ancienne_valeur, genre = composante.double_clique_gauche(self.taille_grid)
                self.update_courant()
                if ancienne_valeur > -1:
                    self.modifications.append(ancienne_valeur)
                    self.modifications.append(composante)
                    self.modifications.append(genre)
                    self.operations.append(4)
            # ces composantes affichent une fenetre ou pas et aucune autre opération ne doit être effectuée
            else:
                composante.double_clique_gauche(self.taille_grid)

    def tourner_image_composante(self, position: QPointF, rollback: bool):
        x, y = self.pos_selon_grid(position)
        collision = self.verifier_collision(QPointF(x, y))

        if isinstance(collision, Composante):
            collision.tourner()

            collision.points_fil.reverse()
            collision.points_cote.reverse()
            collision.fil.calculs()

            if rollback:
                self.operations.append(3)
                self.tournes.append(collision)

            self.update_courant()


class GraphicsView(QGraphicsView):

    def __init__(self, scene):
        super().__init__(scene)
        self.scene = scene
        self.viewport().setMouseTracking(True)
        self.bouge_vue = False
        self.derniere_pos = QPoint(0, 0)

        self.setSceneRect(0, 0, 10000, 10000)
        self.horizontalScrollBar().setValue(self.scene.largeur / 2 + self.scene.main_window.width())
        self.verticalScrollBar().setValue(self.scene.hauteur / 2 + self.scene.main_window.height())

    def mousePressEvent(self, event):
        position_scene = self.mapToScene(event.position().toPoint())
        if event.button() == Qt.MouseButton.LeftButton:
            if self.scene.selection == "fil":
                self.scene.clic_gauche_fil(position_scene)

            elif self.scene.selection == "main":
                self.bouge_vue = True
                self.derniere_pos = event.position().toPoint()

            elif self.scene.selection == "composante" and self.scene.accepter_positionnement:
                self.scene.inserer_composante(self.scene.composante_selectionnee, True)

            elif self.scene.selection == "poubelle" and self.scene.zones_surbrillance:
                self.scene.jeter_element(position_scene, True)

        if event.button() == Qt.MouseButton.RightButton:
            if self.scene.selection == "fil":
                self.scene.clic_droit_fil()
            if self.scene.selection == "composante" and self.scene.accepter_modification is True:
                self.scene.clic_droit_composante()
                self.scene.valider_position()

    def mouseMoveEvent(self, event):
        position_scene = self.mapToScene(event.position().toPoint())
        if self.scene.selection == "fil" and self.scene.dessine:
            self.scene.continuer_dessin(position_scene)

        elif self.scene.selection == "composante" and self.scene.accepter_modification is True:
            position_scene = self.mapToScene(event.position().toPoint())
            self.scene.deplacer_composante(position_scene)
            self.scene.valider_position()

        elif self.scene.selection == "poubelle":
            self.scene.signaler_effacement(position_scene)

        elif self.scene.selection == "main" and self.bouge_vue:
            diff_pos = event.position().toPoint() - self.derniere_pos
            pos_vue_x = self.horizontalScrollBar().value() - diff_pos.x()
            pos_vue_y = self.verticalScrollBar().value() - diff_pos.y()

            # Ajuste la position de la souris et empêche que la vue sorte de la scene
            self.horizontalScrollBar().setValue(min(pos_vue_x, self.scene.largeur - self.scene.main_window.width()))
            self.verticalScrollBar().setValue(min(pos_vue_y, self.scene.hauteur - self.scene.main_window.height()))

            self.derniere_pos = event.position().toPoint()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.bouge_vue = False
        else:
            super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.scene.selection == "main":
                position_scene = self.mapToScene(event.position().toPoint())
                self.scene.modifier_composante(position_scene)

        elif event.button() == Qt.MouseButton.RightButton:
            if self.scene.selection == "main":
                position_scene = self.mapToScene(event.position().toPoint())
                self.scene.tourner_image_composante(position_scene, True)

    def wheelEvent(self, event):
        # Empêche que la molette soit utilisée pour éviter que l'utilisateur sort des limites
        pass
