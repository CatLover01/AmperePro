import numpy as np


def avancer_noeud(noeud_debut, dernier_fil, noeuds_eviter, fils_visites, cible):
    prochain_fil = None
    prochain_noeud = None
    sens = 1

    for info in noeud_debut.info_voisins:
        fil = info[0]
        noeud = info[1]
        if fil != dernier_fil:

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

            # priorise les fils pas deja visites pour faire le moins de mailles possible et refuse les noeuds deja visites
            if noeud not in noeuds_eviter and (prochain_fil is None or fil not in fils_visites):
                prochain_fil = fil
                prochain_noeud = noeud
                if fil.noeuds[1] == noeud:
                    sens = 1
                else:
                    sens = -1

    return prochain_fil, prochain_noeud, sens, False


def trouver_cycle(cible, fils_cycle, sens_fils, fils_visites, noeuds_cycle, sequence_noeuds):
    index_sequence = len(sequence_noeuds) - 1
    noeud_present = noeuds_cycle[-1]
    try:
        dernier_fil = fils_cycle[-1]
    except IndexError:
        dernier_fil = None

    while True:
        noeuds_eviter = noeuds_cycle[:] + sequence_noeuds[index_sequence]

        nouveau_fil, nouveau_noeud, nouveau_sens, fini = avancer_noeud(noeud_present, dernier_fil,
                                                                       noeuds_eviter, fils_visites, cible)

        if fini:
            fils_cycle.append(nouveau_fil)
            sens_fils.append(nouveau_sens)
            break

        if nouveau_fil is not None:
            sequence_noeuds.append([])
            sequence_noeuds[index_sequence].append(nouveau_noeud)
            noeud_present = nouveau_noeud
            index_sequence += 1
            fils_cycle.append(nouveau_fil)
            noeuds_cycle.append(nouveau_noeud)
            sens_fils.append(nouveau_sens)
            dernier_fil = nouveau_fil

        else:
            sequence_noeuds.pop()
            fils_cycle.pop()
            noeuds_cycle.pop()
            sens_fils.pop()
            noeud_present = noeuds_cycle[-1]
            index_sequence -= 1
            dernier_fil = fils_cycle[-1]

    return fils_cycle, sens_fils


def trouver_mailles(fils):
    mailles = []
    sens_mailles = []
    fils_visites = []

    for fil_base in fils:
        if fil_base not in fils_visites:
            # On commence a noeud present et on veut se rendre a cible.
            cible = fil_base.noeuds[0]
            noeud_present = fil_base.noeuds[1]
            sequence_noeuds = [[noeud_present], []]
            sens_fils = [1]
            fils_cycle = [fil_base]
            # Probablement changer present = noeuds_cycle[-1] pour sequence[-2][-1]
            noeuds_cycle = [noeud_present]

            maille, sens_fils = trouver_cycle(cible, fils_cycle, sens_fils, fils_visites, noeuds_cycle, sequence_noeuds)

            fils_visites += fils_cycle
            mailles.append(fils_cycle)
            sens_mailles.append(sens_fils)

    return mailles, sens_mailles


def enlever_fil(mat_A, mat_B, mailles, sens_mailles, fils, fil_enlever):
    j = fils.index(fil_enlever)

    # On enleve la tension du fil dans les mailles ou il est present
    for i in range(len(mailles)):
        if fil_enlever in mailles[i]:
            index_fil_maille = mailles[i].index(fil_enlever)
            mat_B[i, 0] -= sens_mailles[i][index_fil_maille] * fil_enlever.tension

    # On enleve la presence du fil dans toutes les equations
    mat_A[:, j] = 0


def envoyer_resultats(mat_A, mat_B, mailles, sens_mailles, fils):

    x = np.linalg.lstsq(mat_A, mat_B, rcond=None)[0]
    for i in range(len(x)):
        fil = fils[i]
        amperage = x[i][0]
        # Si c'est pas du meme sens que les diode, enleve le fil de la matrice et recalcule
        if fil.sens_diode * amperage < 0:
            enlever_fil(mat_A, mat_B, mailles, sens_mailles, fils, fil)
            envoyer_resultats(mat_A, mat_B, mailles, sens_mailles, fils)
            break
        else:
            fil.definir_amperage(amperage)


def calculer_circuit(fils, noeuds):
    mailles, sens_mailles = trouver_mailles(fils)

    mat_A = np.zeros((len(mailles), len(fils)))
    mat_B = np.zeros((len(mailles), 1))

    for i in range(len(mailles)):
        maille_fils = mailles[i]
        maille_sens = sens_mailles[i]
        for k in range(len(maille_fils)):
            fil = maille_fils[k]
            sens = maille_sens[k]
            j = fils.index(fil)

            mat_A[i, j] += sens * fil.resistance
            mat_B[i, 0] += sens * fil.tension

    # Ajoute les equations des noeuds selon la loi des noeuds dans les matrices
    for i in range(len(noeuds)):
        # Le premier noeud va être calculé dans les prochains noeuds, donc redondant
        if i == 0:
            continue

        noeud = noeuds[i]

        equation = np.zeros((1, len(fils)))
        for info in noeud.info_voisins:
            fil_voisin = info[0]
            j = fils.index(fil_voisin)
            equation[0, j] = 1 if fil_voisin.noeuds[1] == noeud else -1

        mat_A = np.append(mat_A, equation, axis=0)
        mat_B = np.append(mat_B, [[0]], axis=0)

    for fil in fils:
        # On enleve les fils a ignorer
        if fil.ignorer:
            enlever_fil(mat_A, mat_B, mailles, sens_mailles, fils, fil)

    envoyer_resultats(mat_A, mat_B, mailles, sens_mailles, fils)
