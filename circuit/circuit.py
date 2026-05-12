from PySide6.QtCore import QSize, QPointF, QLineF
from PySide6.QtGui import QColorConstants, QPen, Qt, QAction, QIcon, QPixmap, QColor
from PySide6.QtWidgets import (QGraphicsScene, QGraphicsView, QPushButton, QDialog,
                               QHBoxLayout, QToolBar, QGraphicsPixmapItem, QGraphicsRectItem, QInputDialog,
                               QGraphicsLineItem)
import math
import numpy as np

from button import ToolTipButton
from .fil import Fil
from .noeud import Noeud
from composantes import toolbar_composantes, Composante, Type
from sauvegarde import Sauvegarde


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

        self.lignes: list[QGraphicsLineItem] = []
        self.noeuds: list[Noeud] = []
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
        self.zones_surbrillance = None
        self.composante_surbrillance = None
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
            dernier_ajout = self.ajouts.pop()
            if isinstance(dernier_ajout, Fil):
                dernier_ajout.enlever_fil()
                self.fils.remove(dernier_ajout)
                # TODO : mettre à jour la vérification de collisions pour fils après qu'un ait été retiré
            else:
                self.jeter_element(dernier_ajout, False)

        elif dernier == 2:
            composante = self.composantes_jetes.pop()
            if isinstance(composante, Composante):
                self.image_composante = composante.image_item
                self.inserer_composante(composante)

        elif dernier == 3:
            composante = self.tournes.pop()
            if isinstance(composante, Composante):
                composante.tourner()

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
    def ajouter_ligne(self, xi: float, yi: float, x: float, y: float) -> QGraphicsLineItem:
        pen = QPen(QColorConstants.Black)
        largeur_crayon = 3
        pen.setWidthF(largeur_crayon)
        ligne = self.addLine(xi, yi, x, y, pen)

        return ligne

    # TODO: quand on pourra charger les saves, enlever cette méthode et avoir en tout temps la save de la matrice de
    # base pour la charger comme n'importe quel circuit
    def dessiner_circuit_base(self, largeur_circuit: int, hauteur_circuit: int):
        gauche = self.largeur / 2 - largeur_circuit / 2
        droite = self.largeur / 2 + largeur_circuit / 2
        haut = self.hauteur / 2 - hauteur_circuit / 2
        bas = self.hauteur / 2 + hauteur_circuit / 2

        gauche_haut = self.pos_selon_grid(QPointF(gauche, haut))
        gauche, haut = gauche_haut.x(), gauche_haut.y()
        droite_bas = self.pos_selon_grid(QPointF(droite, bas))
        droite, bas = droite_bas.x(), droite_bas.y()

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
    def verifier_collision_fil(self, pos: QPointF) -> Noeud | Fil | Composante | None:
        grid_pos = self.pos_selon_grid(pos)
        pos_i, pos_j = self.pos_to_mat(grid_pos.x(), grid_pos.y())

        max_i = self.mat_points.shape[0] - 1
        max_j = self.mat_points.shape[1] - 1

        if grid_pos == self.dernier_point:
            return None

        if max_i >= pos_i >= 0 and max_j >= pos_j >= 0:
            touche = self.mat_points[pos_i, pos_j]
            if touche is not None and (
                    isinstance(touche, Composante) or isinstance(touche, Fil) or isinstance(touche, Noeud)):
                return touche

        return None

    def clic_gauche_fil(self, pos: QPointF):
        # return tous les points dans le grid selon la ligne
        def get_points_ligne(debut_ligne: QPointF, fin_ligne: QPointF) -> list[QPointF]:
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
        def mettre_fil_mat(ligne: QGraphicsLineItem, fil: Fil):
            debut_ligne = ligne.line().p1()
            fin_ligne = ligne.line().p2()
            points = get_points_ligne(debut_ligne, fin_ligne)

            # Si la liste de points est vide
            if not points:
                return debut_ligne, fin_ligne, points

            i_fin, j_fin = self.pos_to_mat(points[-1].x(), points[-1].y())
            self.agrandir_matrice(i_fin, j_fin)

            for point in points:
                i, j = self.pos_to_mat(point.x(), point.y())
                if not isinstance(self.mat_points[i, j], Fil) and not isinstance(self.mat_points[i, j], Noeud):
                    self.mat_points[i, j] = fil

            return debut_ligne, fin_ligne, points

        fil_touche = self.verifier_collision_fil(pos)
        grid_pos = self.pos_selon_grid(pos)
        if not self.dessine:
            # lorsque le fil est pas démarré et que le clic démarre à un fil, un nouveau fil est commencé
            if fil_touche is not None:
                self.dessine = True
                ligne = self.ajouter_ligne(grid_pos.x(), grid_pos.y(), grid_pos.x(), grid_pos.y())
                self.lignes.append(ligne)
                self.dernier_point = grid_pos

                self.points_avant_pivot.append(grid_pos)

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
        elif (grid_pos != self.points_avant_pivot[0] and not isinstance(fil_touche, Fil)
              and not isinstance(fil_touche, Noeud)):
            debut_ligne, fin_ligne, points_apres_pivot = mettre_fil_mat(self.lignes[-1], self.nouveau_fil)
            ligne = self.ajouter_ligne(fin_ligne.x(), fin_ligne.y(), fin_ligne.x(), fin_ligne.y())

            self.points_avant_pivot += points_apres_pivot
            self.lignes.append(ligne)
            self.dernier_point = QPointF(fin_ligne.x(), fin_ligne.y())
            self.continuer_dessin(pos)

    def fil_accepte(self, position: QPointF):
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
        noeud_zero._voltage = 0
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
        collision = self.verifier_collision_fil(pos)

        # Ajuste la dernière ligne pour qu'elle s'étende du pivot à la position selon grid du curseur
        if collision is not None or self.dessine:
            grid_pos = self.pos_selon_grid(pos)

            ligne = self.lignes[-1]
            pivot = ligne.line().p1()

            diff_x = grid_pos.x() - pivot.x()
            diff_y = grid_pos.y() - pivot.y()

            if abs(diff_x) > abs(diff_y):
                sens_x = 1
                if diff_x < 0:
                    sens_x = -1
                sens_y = 0
                x = grid_pos.x()
                y = pivot.y()

            else:
                sens_y = 1
                if diff_y < 0:
                    sens_y = -1
                sens_x = 0
                x = pivot.x()
                y = grid_pos.y()

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
    def pos_to_mat(self, x: float, y: float):
        mat_i = round((y - self.mat_i0) / self.taille_grid)
        mat_j = round((x - self.mat_j0) / self.taille_grid)

        return mat_i, mat_j

    # retourne la position d'un point selon les positions possibles créées par le grid
    def pos_selon_grid(self, pos: QPointF) -> QPointF:
        x = round(pos.x() / self.taille_grid) * self.taille_grid
        x = max(min(x, math.floor(self.scene_size.width() / self.taille_grid) * self.taille_grid), 0)
        y = round(pos.y() / self.taille_grid) * self.taille_grid
        y = max(min(y, math.floor(self.scene_size.height() / self.taille_grid) * self.taille_grid), 0)

        return QPointF(x, y)

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
        for composante_class in toolbar_composantes.values():
            bouton = ToolTipButton(composante_class().nom)
            bouton.setIcon(QIcon(composante_class().image_toolbar))
            bouton.setIconSize(QSize(45, 45))
            bouton.clicked.connect(lambda _, c=composante_class: self.composante_toolbar_clicked(c))
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

    def composante_toolbar_clicked(self, composante):
        if composante in toolbar_composantes.values():
            self.selection = "composante"
            self.composante_selectionnee = composante()

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

    def inserer_composante(self, composante: Composante):
        if self.image_composante:
            composante.image_item = self.image_composante

            points_fil, points_cote = self.points_composante(self.image_composante.rotation())
            composante.points_fil = points_fil
            composante.points_cote = points_cote
            point_milieu = points_fil[1]
            fil = self.verifier_collision_fil(point_milieu)
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
            self.ajouts.append(point_milieu)
            self.rollback_possible()

    def clic_droit_composante(self):
        liste_refusee = [Type.Amperemetre, Type.Voltmetre]
        if self.composante_selectionnee.type not in liste_refusee:
            self.image_composante.setRotation(self.image_composante.rotation() + 90)

    def points_composante(self, rotation: float):
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
                if collision is not None:
                    self.accepter_positionnement = False
                    break

        self.couleur_image()

        # Essaye dans l'autre sens si cest un amperemetre ou voltmetre et que ca fonctionne pas deja
        if ((
                self.composante_selectionnee.type == Type.Amperemetre or self.composante_selectionnee.type == Type.Voltmetre)
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

    def signaler_effacement(self, position_scene: QPointF):
        new_pos = self.pos_selon_grid(position_scene)
        composante = self.verifier_collision_fil(new_pos)
        if composante:
            if isinstance(composante, Composante):
                # si la composante est déjà surbrillée, rien ne sert de faire ça
                if composante != self.composante_surbrillance:

                    if self.zones_surbrillance:
                        self.removeItem(self.zones_surbrillance)
                        self.zones_surbrillance = None

                    image = composante.image_item
                    point_milieu = image._pos()
                    # si la souris recouvre une composante, on le signale en la mettant en rouge.
                    coin_sup_gauche_x = point_milieu.x() - self.taille_grid
                    coin_sup_gauche_y = point_milieu.y() - self.taille_grid
                    zone_rouge = QGraphicsRectItem(coin_sup_gauche_x, coin_sup_gauche_y, self.taille_grid * 2,
                                                   self.taille_grid * 2)
                    zone_rouge.setOpacity(1)
                    zone_rouge.setZValue(1)
                    zone_rouge.setBrush(QColor(218, 44, 44))
                    self.composante_surbrillance = composante
                    self.zones_surbrillance = zone_rouge
                    self.addItem(zone_rouge)
            else:
                # TODO: raisonnement pour fil
                pass

        else:
            if self.zones_surbrillance:
                self.removeItem(self.zones_surbrillance)
                self.zones_surbrillance = None
                self.composante_surbrillance = None

    def jeter_element(self, position, rollback):
        pos = self.pos_selon_grid(position)
        composante = self.verifier_collision_fil(pos)
        if isinstance(composante, Composante):
            # ménage visuel composante
            self.removeItem(composante.image_item)
            self.removeItem(self.zones_surbrillance)
            self.retirer_elements(composante)
            self.zones_surbrillance = None

            # TODO: retirer la composante du fil. C'est impératif que cela redevienne un fil à l'emplacement de la composante.
            # TODO: possibilité de poursuivre la méthode nettoyer composante (si une autre manière est choisie aucun problème)
            composante.nettoyer()

            # on ajuste pour rollback si on provient de clic gauche et pas du rollback (si rollback = True)
            if rollback:
                self.composantes_jetes.append(composante)
                self.operations.append(2)

    def deplacer_composante(self, position):
        grid_pos = self.pos_selon_grid(position)

        # évite que la composante soit à moitié sortie de la grid
        pos_max_x = self.scene_size.width() - self.taille_grid
        pos_max_y = self.scene_size.height() - self.taille_grid
        x = max(min(grid_pos.x(), pos_max_x), self.taille_grid)
        y = max(min(grid_pos.y(), pos_max_y), self.taille_grid)

        self.image_composante.setPos(x, y)

    def retirer_elements(self, composante: Composante):
        items = composante.items
        for item in items:
            self.removeItem(item)

    # Modification d'une composante lors du double click gauche
    def modifier_composante(self, position: QPointF):
        grid_pos = self.pos_selon_grid(position)
        composante = self.verifier_collision_fil(grid_pos)
        a_modifier = [Type.Resistor, Type.Batterie, Type.Interrupteur]
        a_afficher = [Type.Amperemetre, Type.Voltmetre]
        # il n'y a que ces composantes qui ont quelque chose à modifier
        if composante.type in a_modifier:
            ancienne_valeur, genre = composante.double_clique_gauche(self.taille_grid)
            if ancienne_valeur > -1:
                self.modifications.append(ancienne_valeur)
                self.modifications.append(composante)
                self.modifications.append(genre)
                self.operations.append(4)
        # ces composantes affichent une fenetre, mais aucune autre opération ne doit être effectuée
        elif composante.type in a_afficher:
            composante.double_clique_gauche(self.taille_grid)
        # sinon, on ignore le clic
        else:
            return

    def tourner_image_composante(self, position: QPointF):
        pos = self.pos_selon_grid(position)
        composante = self.verifier_collision_fil(pos)

        if isinstance(composante,
                      Composante) and composante.type != Type.Amperemetre and composante.type != Type.Voltmetre:
            composante.tourner()
            self.operations.append(3)
            self.tournes.append(composante)


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

            elif self.scene.selection == "poubelle" and self.scene.zones_surbrillance:
                self.scene.jeter_element(position_scene, True)

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
            self.scene.deplacer_composante(position_scene)
            self.scene.valider_position()
        elif self.scene.selection == "poubelle":
            self.scene.signaler_effacement(position_scene)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if not self.scene.image_composante:
                position_scene = self.mapToScene(event.position().toPoint())
                self.scene.modifier_composante(position_scene)

        elif event.button() == Qt.MouseButton.RightButton:
            if not self.scene.image_composante:
                position_scene = self.mapToScene(event.position().toPoint())
                self.scene.tourner_image_composante(position_scene)
