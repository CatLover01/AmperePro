import numpy as np


def avancer_noeud(noeud_debut, dernier_fil, noeuds_eviter, fils_visites, cible, fils_possibles):
    prochain_fil = None
    prochain_noeud = None
    sens = 1

    for info in noeud_debut.info_voisins:
        fil = info[0]
        noeud = info[1]
        if fil != dernier_fil and fil.ignorer is False and fil in fils_possibles:

            # Retour au depart, fin du cycle
            if noeud == cible:
                prochain_fil = fil
                prochain_noeud = noeud

                # Sens normal si le nouveau noeud est le dernier noeud du fil
                if fil.noeuds[1] == noeud:
                    sens = 1
                else:
                    sens = -1
                return prochain_fil, prochain_noeud, sens, True

            # priorise les fils pas deja visites pour faire le moins de mailles possible
            # et refuse les noeuds deja visites
            if noeud not in noeuds_eviter and (prochain_fil is None or fil not in fils_visites):
                prochain_fil = fil
                prochain_noeud = noeud
                if fil.noeuds[1] == noeud:
                    sens = 1
                else:
                    sens = -1

    return prochain_fil, prochain_noeud, sens, False


def trouver_chemin(cible, fils_chemin, sens_fils, fils_visites, noeuds_chemin, fils_possibles):
    sequence_noeuds = [noeuds_chemin, []]
    index_sequence = len(sequence_noeuds) - 1
    noeud_present = noeuds_chemin[-1]
    try:
        dernier_fil = fils_chemin[-1]
    except IndexError:
        dernier_fil = None

    while True:
        noeuds_eviter = noeuds_chemin[:] + sequence_noeuds[index_sequence]

        nouveau_fil, nouveau_noeud, nouveau_sens, fini = avancer_noeud(noeud_present, dernier_fil, noeuds_eviter,
                                                                       fils_visites, cible, fils_possibles)

        if fini:
            fils_chemin.append(nouveau_fil)
            sens_fils.append(nouveau_sens)
            break

        if nouveau_fil is not None:
            sequence_noeuds.append([])
            sequence_noeuds[index_sequence].append(nouveau_noeud)
            noeud_present = nouveau_noeud
            index_sequence += 1
            fils_chemin.append(nouveau_fil)
            noeuds_chemin.append(nouveau_noeud)
            sens_fils.append(nouveau_sens)
            dernier_fil = nouveau_fil

        else:
            try:
                sequence_noeuds.pop()
                fils_chemin.pop()
                noeuds_chemin.pop()
                sens_fils.pop()
                noeud_present = noeuds_chemin[-1]
                index_sequence -= 1
                dernier_fil = fils_chemin[-1]
            except IndexError:
                break

    return fils_chemin, sens_fils


def trouver_mailles(fils):
    mailles = []
    sens_mailles = []
    fils_visites = []

    fils_bloques = []

    for fil_base in fils:
        if fil_base not in fils_visites and fil_base.ignorer is False:
            # On commence a noeud present et on veut se rendre a cible.
            cible = fil_base.noeuds[0]
            noeud_present = fil_base.noeuds[1]
            sequence_noeuds = [[noeud_present], []]
            sens_fils = [1]
            fils_cycle = [fil_base]
            # Probablement changer present = noeuds_cycle[-1] pour sequence[-2][-1]
            noeuds_cycle = [noeud_present]

            maille, sens_fils = trouver_chemin(cible, fils_cycle, sens_fils, fils_visites, noeuds_cycle, fils)

            if maille == []:
                fils_bloques.append(fil_base)
            else:
                fils_visites += fils_cycle
                mailles.append(fils_cycle)
                sens_mailles.append(sens_fils)

        elif fil_base.ignorer is True:
            fils_bloques.append(fil_base)

    return mailles, sens_mailles, fils_bloques


def get_voltage(fil_voltage, fils_courant):
    # On doit trouver la diff de potentiel aux noeuds du fil, donc il faut trouver un chemin de fils
    # On trouve le changement de voltage dans chaque fil avec delta V = R*I, sans oublier de rajouter les tensions
    # des batteries, et on va finir avec la diff de potentiel d'un noeud à l'autre
    cible = fil_voltage.noeuds[1]
    noeuds_chemin = [fil_voltage.noeuds[0]]

    fils_chemin, sens_fils = trouver_chemin(cible, [], [], [], noeuds_chemin, fils_courant)
    diff_potentiel = 0
    for i in range(len(fils_chemin)):
        fil = fils_chemin[i]
        sens = sens_fils[i]

        diff_potentiel -= sens * fil.resistance * fil.amperage
        diff_potentiel += sens * fil.tension

    return diff_potentiel * fil_voltage.trouver_sens(fil_voltage.composantes[0], fil_voltage.points)


def calculer_circuit(fils, noeuds, fils_voltmetre):
    mailles, sens_mailles, fils_bloques = trouver_mailles(fils)

    # liste des fils qui sont dans les mailles donc pas dans fils_bloques
    fils_courant = [fil for fil in fils if fil not in fils_bloques]

    # Les fils hors des mailles on automatiquement un ampérage nul
    for fil in fils_bloques:
        fil.definir_amperage(0)

    mat_a = np.zeros((len(mailles), len(fils)))
    mat_b = np.zeros((len(mailles), 1))
    # Ajoute les équations des mailles dans les matrices selon la loi des mailles
    for i in range(len(mailles)):
        maille_fils = mailles[i]
        maille_sens = sens_mailles[i]
        for k in range(len(maille_fils)):
            fil = maille_fils[k]
            sens = maille_sens[k]
            j = fils_courant.index(fil)

            mat_a[i, j] += sens * fil.resistance
            mat_b[i, 0] += sens * fil.tension

    # Ajoute les equations des noeuds selon la loi des noeuds dans les matrices
    for i in range(len(noeuds)):
        # Le premier noeud va être calculé dans les prochains noeuds, donc redondant
        if i == 0:
            continue

        noeud = noeuds[i]

        equation = np.zeros((1, len(fils)))
        for info in noeud.info_voisins:
            fil_voisin = info[0]
            if fil_voisin in fils_courant:
                j = fils_courant.index(fil_voisin)
                # 1 si c'est entrant et -1 si c'est sortant du noeud
                equation[0, j] = 1 if fil_voisin.noeuds[1] == noeud else -1

        mat_a = np.append(mat_a, equation, axis=0)
        mat_b = np.append(mat_b, [[0]], axis=0)

    x = np.linalg.lstsq(mat_a, mat_b, rcond=None)[0]
    recalculer = False
    nouveau_fils_courants = fils_courant.copy()
    for i in range(len(fils_courant)):
        amperage = x[i][0]
        fils_courant[i].definir_amperage(amperage)

        # On enleve les fils qui ont une diode en sens inverse du courant
        if fils_courant[i].sens_diode * x[i][0] < 0:
            nouveau_fils_courants.remove(fils_courant[i])
            fils_courant[i].definir_amperage(0)
            recalculer = True

    # En enlevant un fil il se peut que des fils ne soient plus dans au moins une maille
    # il faut donc retrouver les mailles et recréer les matrices
    # On va donc recalculer le circuit mais en prenant seulement les fils où le courant peut passer
    if recalculer:
        calculer_circuit(nouveau_fils_courants, noeuds, fils_voltmetre)
    else:
        for fil in fils_voltmetre:
            fil.composantes[0].diff_potentiel = get_voltage(fil, nouveau_fils_courants)
