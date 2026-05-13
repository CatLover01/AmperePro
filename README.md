# AmpèrePro

AmpèrePro est une application d'apprentissage sur des concepts en électricité basée sur la simulation en temps réel de
circuits électriques. Elle permet d'explorer les concepts fondamentaux via un mode libre et un mode jeu, afind de rendre
l'apprentissage plus interactif.

Le projet vise à aide les étudiants et enseignants à mieux comprendre les circuits électriques, leurs composantes et
leurs comportements dans différents scénarios.

## Prérequis

- Python (3.12+)
- Pyside6
- NumPy
- dacite

## Installation

Installe les packages nécéssaires avec :

```bash
pip install -r requirements.txt
```

Le point d'entrée de l'application est `main.py`.

## Tests

Les tests unitaires sont situés dans le dossier `tests/` et peuvent être exécutés avec :

```bash
python -m unittest discover tests
```

## Licence

Ce projet est sous la licence MIT, voir [LICENSE](./LICENSE) pour plus de détails.