# Instructions du projet

## Publication future.now et archives

- Conserver le design actuel de l’accueil (palette salon, images, header, favoris avec fermeture, footer et conclusions détachées) lors des prochaines éditions.
- La page `Archives/index.html` doit afficher uniquement les 30 éditions les plus récentes, triées par date décroissante. Retirer les liens excédentaires de la liste à chaque publication, sans supprimer les anciens fichiers HTML.
- Chaque nouvelle archive reprend le design de l’accueil, sa date propre et les chemins de ressources adaptés. Conserver le contenu et les sources des éditions existantes.

## Versions française et anglaise

- Publier chaque édition et les 30 archives dans les deux langues, avec un sélecteur FR / EN menant à la même page. Routes anglaises sous `/en/`.
- Conserver les liens sources, montants, noms propres, dates et la mention de traduction automatique. Relire les titres et contrôler les chiffres avant publication.
- Génération : `python scripts/build-english.py . --cache translations/fr-en.json --overrides translations/en-overrides.json` (beautifulsoup4). Le script échoue si un texte manque. Ne pas publier une page à moitié traduite.
- `scripts/translate-missing.py` complète le cache avec un modèle local Argos français-anglais (CTranslate2). Dépendances : beautifulsoup4, ctranslate2, sentencepiece. Le modèle n’est pas inclus. Les corrections vont dans en-overrides.json.
- Vérification : `python scripts/check-languages.py .`, puis contrôle du rendu et du passage entre langues dans le navigateur.
