# Guide de Contribution pour AutoSavePro

Merci de considérer contribuer à AutoSavePro !
Ce guide vous aidera à comprendre comment contribuer au projet.

## Structure du Projet

```
AutoSavePro/
├── autosave/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── watcher.py
│   │   └── saver.py
│   ├── gui/
│   │   ├── __init__.py
│   │   └── main_window.py
│   ├── apps/
│   │   ├── __init__.py
│   │   ├── bloc_notes.py
│   │   ├── photoshop.py
│   │   ├── aftereffects.py
│   │   └── office365.py
│   └── utils/
│       ├── __init__.py
│       └── file_utils.py
├── icons/
│   ├── aftereffects.png
│   ├── illustrator.png
│   ├── office365.png
│   ├── photoshop.png
│   ├── plus.png
│   └── powerpoint.png
├── main.py
├── scheduler.py
├── requirements.txt
├── README.md
└── LICENSE
```

## Fonctionnalités

- Sauvegarde automatique pour de nombreuses applications
- Interface utilisateur intuitive pour configurer les sauvegardes
- Personnalisation de la fréquence de sauvegarde
- Restauration facile des sauvegardes précédentes
- Ajout flexible de nouvelles applications à sauvegarder

## Pour Commencer

1. **Forker le dépôt** : Cliquez sur le bouton "Fork" en haut à droite de cette page pour créer une copie du dépôt sur votre compte GitHub.
2. **Cloner votre fork** : Clonez votre dépôt forké sur votre machine locale en utilisant la commande :
   ```bash
   git clone https://github.com/VOTRE_NOM_UTILISATEUR/AutoSavePro.git
   ```
3. **Créer une branche** : Créez une nouvelle branche pour votre travail :
   ```bash
   git checkout -b ma-branche-fonctionnalite
   ```
4. **Installer les dépendances** : Installez les dépendances requises en utilisant :
   ```bash
   pip install -r requirements.txt
   ```

## Comment Contribuer

### Ajouter le Support pour une Nouvelle Application

1. **Créer un nouveau fichier** : Dans le répertoire `autosave/apps/`, créez un nouveau fichier pour l'application que vous souhaitez ajouter (par exemple, `sublime_text.py`).
2. **Implémenter le gestionnaire** : Implémentez la logique pour détecter et sauvegarder les fichiers pour la nouvelle application. Utilisez `bloc_notes.py` comme référence.
3. **Mettre à jour le watcher** : Mettez à jour `autosave/core/watcher.py` pour inclure le nouveau gestionnaire d'application.
4. **Tester vos modifications** : Assurez-vous que vos modifications fonctionnent comme prévu en testant avec la nouvelle application.
5. **Soumettre une pull request** : Poussez vos modifications sur votre fork et soumettez une pull request au dépôt principal.

### Améliorer les Fonctionnalités Existantes

1. **Identifier la fonctionnalité** : Identifiez la fonctionnalité que vous souhaitez améliorer ou le bug que vous souhaitez corriger.
2. **Apporter vos modifications** : Implémentez vos améliorations ou corrections de bugs.
3. **Tester vos modifications** : Assurez-vous que vos modifications fonctionnent comme prévu.
4. **Soumettre une pull request** : Poussez vos modifications sur votre fork et soumettez une pull request au dépôt principal.

### Bonnes Pratiques

- **Code propre et lisible** : Assurez-vous que votre code est propre et bien commenté.
- **Tests** : Ajoutez des tests pour vos nouvelles fonctionnalités ou corrections de bugs.
- **Documentation** : Mettez à jour la documentation si nécessaire.

## Communication

Si vous avez des questions ou besoin d'aide, n'hésitez pas à ouvrir une issue sur GitHub ou à contacter les mainteneurs du projet.

Merci pour vos contributions et votre aide à améliorer AutoSavePro !
```
