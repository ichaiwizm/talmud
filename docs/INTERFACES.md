# Torah Analysis - Interfaces de Visualisation

## Architecture Générale

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND UNIFIÉ                          │
│                                                             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │
│  │ Constel │ │ Living  │ │ Emotion │ │ Voice   │  ...     │
│  │ lation  │ │ Scroll  │ │ Terrain │ │ Chamber │          │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘          │
│       │          │          │          │                   │
│       └──────────┴──────────┴──────────┘                   │
│                        │                                    │
│              ┌─────────▼─────────┐                         │
│              │   API Backend     │                         │
│              │   (FastAPI/Flask) │                         │
│              └─────────┬─────────┘                         │
│                        │                                    │
│              ┌─────────▼─────────┐                         │
│              │   Base de données │                         │
│              │   (SQLite/Turso)  │                         │
│              └───────────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

**Concept:** Un seul frontend React avec un sélecteur d'interfaces. Chaque interface est un module indépendant dans son propre dossier, partageant les composants communs et l'accès API.

---

## Les 12 Interfaces

---

### 1. Torah Constellation Map
**"Naviguez dans les Écritures comme les anciens naviguaient dans les cieux"**

#### Concept
Un champ d'étoiles 3D interactif où chaque verset est une étoile. Les relations entre versets forment des constellations lumineuses. Le "ciel nocturne" montre la Torah entière comme un cosmos de points lumineux interconnectés.

#### Caractéristiques
- **Propriétés des étoiles:**
  - Luminosité = intensité émotionnelle (`verse_sentiment.emotional_intensity`)
  - Couleur = émotion primaire (joie=or, peur=violet, amour=rose, émerveillement=blanc)
  - Taille = valeur gematria
- **Lignes de constellation:** Les références croisées (`cross_references`) tracent des lignes visibles
  - Style selon `reference_type`: pointillé pour allusion, solide pour citation, pulsant pour accomplissement
- **Nébuleuses divines:** Clusters autour des occurrences de noms divins avec couleurs distinctes
  - YHWH = bleu profond
  - ELOHIM = ambre
- **Navigation temporelle:** Glisser dans la chronologie et regarder les constellations se former/dissoudre

#### Stack Technique
- Three.js ou React Three Fiber (WebGL 3D)
- D3.js force-directed pour positionner les versets reliés
- GSAP pour les transitions fluides
- InstancedMesh pour render 5,846 étoiles efficacement

#### Données Utilisées
- `verse_sentiment` (emotional_intensity, primary_emotion)
- `cross_references` (source_verse_id, target_verse_id, reference_type)
- `divine_name_occurrences` (divine_name, verse_id)
- `torah_verses` (gematria_standard_total)
- `narrative_units`, `parshaot` pour les regroupements

---

### 2. The Living Scroll
**"Regardez la Torah respirer avec émotion et sens"**

#### Concept
Un parchemin horizontal infini qui rend le texte de la Torah comme un organisme vivant. Le texte hébreu se transforme et s'anime selon les données sous-jacentes: les lettres pulsent avec l'énergie de la gematria, les mots grandissent/rétrécissent selon leur poids sémantique.

#### Caractéristiques
- **Texte qui respire:** Les mots animent avec un rythme subtil
  - Fréquence du rythme corrélée à `tension_level` (haute tension = pulse rapide)
- **Illumination des racines:** Survoler un mot révèle sa racine hébraïque et illumine TOUS les autres mots partageant cette racine
  - Ex: "ברא" (créer) s'illumine à travers Genèse 1
- **Élévation des discours:** Les segments de discours direct s'élèvent au-dessus du texte de base
  - Parole divine = plus haute avec lueur éthérée
  - Dialogue humain = hauteur moyenne avec couleur spécifique au personnage
- **Vagues d'émotion:** Gradients de couleur en arrière-plan basés sur `primary_emotion` et `sentiment_polarity`
- **Brins ADN généalogiques:** En scrollant les généalogies, des hélices ADN apparaissent avec durées de vie visualisées

#### Stack Technique
- React + Framer Motion pour animations fluides du texte
- Polices variables (Inter/Noto Sans Hebrew) avec CSS custom properties
- HTML Canvas overlay pour effets de particules
- WebGL shader custom pour lueur des lettres basée sur gematria
- react-window pour virtual scrolling performant

#### Données Utilisées
- `torah_words` (gematria_standard, word_original)
- `hebrew_roots`, `word_roots` (root_letters, verb_form)
- `direct_speech` (speaker_id, addressee_id, is_divine_speech)
- `verse_sentiment` (tension_level, primary_emotion, sentiment_polarity)
- `genealogy` (lifespan_years)

---

### 3. Emotional Topology
**"Marchez sur le terrain des émotions sacrées"**

#### Concept
Une carte topographique 3D où le paysage émotionnel de la Torah est rendu comme géographie physique. Les montagnes s'élèvent aux moments d'émerveillement spirituel, les vallées descendent dans la tristesse, les plateaux marquent les passages neutres.

#### Caractéristiques
- **Génération du terrain:** Chaque verset génère hauteur et rugosité
  - `sentiment_polarity` (-1 à +1) + `emotional_intensity` (0-1) → hauteur
  - Joie = collines vertes, peur = pics escarpés, tristesse = canyons
- **Système météo divine:** `divine_sentiment` contrôle le ciel
  - PLEASED = lumière dorée
  - ANGRY = nuages d'orage avec éclairs aux versets spécifiques
  - MERCIFUL = pluie douce
  - GRIEVED = brouillard
- **Sentiers des personnages:** Entités nommées avec `character_emotions` laissent des marqueurs lumineux
  - Cliquer révèle leur parcours émotionnel à travers le paysage
- **Flore/Faune des motifs:** `recurring_motifs` et `symbolic_elements` apparaissent comme objets 3D
  - Motif "stérilité" = arbres flétris
  - Motif "eau" = ruisseaux
- **Monuments d'événements:** Événements majeurs = landmarks
  - THEOPHANY = balises lumineuses
  - COVENANT = pierres dressées
  - MIRACLE = cristaux flottants
  - DEATH = cairns commémoratifs

#### Stack Technique
- React Three Fiber avec drei helpers
- Heightmap generation via GPU.js
- Particle systems pour effets météo
- First-person ou orbit controls avec collision detection
- Web Workers pour pré-calcul du terrain mesh
- LOD (Level of Detail) et chunking pour performance

#### Données Utilisées
- `verse_sentiment` (sentiment_polarity, emotional_intensity, tension_level, divine_sentiment)
- `character_emotions` (character_id, emotion, trigger, resulting_action)
- `events` (event_type, is_miraculous, verse_start_id)
- `symbolic_elements` (element_name, element_type, symbolic_meaning)
- `recurring_motifs` (motif_name, occurrences)

---

### 4. The Voice Chamber
**"Entendez les conversations qui ont façonné l'histoire"**

#### Concept
Une expérience audio-visuelle immersive centrée entièrement sur les discours directs dans la Torah. L'interface présente les conversations comme des scènes dramatiques, visualisant qui parle à qui, le poids émotionnel des paroles.

#### Caractéristiques
- **Théâtre de conversation:** Vue split-screen dramatique
  - Locuteurs apparaissent de chaque côté
  - Quand Dieu parle à Abraham: gauche = nom divin utilisé avec contexte théologique, droite = Abraham
  - `speech_type` (command, blessing, prophecy, promise) colore l'atmosphère visuelle
- **Carte réseau des paroles:** Graphe interactif de TOUTES les relations de parole
  - Nœuds = entités (`TorahName`)
  - Arêtes = événements de parole
  - Filtrer par `speech_type`: voir uniquement bénédictions, uniquement commandements, uniquement prophéties
- **Panneau des sous-tons émotionnels:** Affiche ce que le locuteur ressent
  - Données `CharacterEmotion` (trigger, emotion, resulting_action) aux côtés de leurs paroles
- **Echo Finder:** Tracer quand des discours ultérieurs citent des antérieurs
  - Utilise `CrossReference` (type: `quotation`, `allusion`)
- **Statistiques de la voix divine:** Dashboard montrant comment les patterns de parole de Dieu changent
  - Fréquence, destinataires, types de discours, noms divins utilisés

#### Stack Technique
- React + Framer Motion pour transitions théâtrales
- D3.js force-directed graph pour réseau de parole
- Web Speech API ou audio pré-enregistré pour lecture optionnelle
- Endpoints: `/speech/between/{speaker}/{addressee}`, `/speech/type/{type}`

#### Données Utilisées
- `direct_speech` (speaker_id, addressee_id, speech_type, speech_text, is_divine_speech)
- `character_emotions` (emotion, trigger, resulting_action)
- `divine_name_occurrences` (divine_name, context_type, speaker_type)
- `cross_references` (reference_type = quotation/allusion)
- `torah_names` (name_canonical, name_type)

---

### 5. Journey Atlas
**"Chaque pas des chemins patriarcaux"**

#### Concept
Une carte géographique et temporelle animée qui suit les personnages à travers l'espace et le temps, montrant où ils ont voyagé, quels événements se sont produits à chaque lieu, qui ils ont rencontré.

#### Caractéristiques
- **Lecture animée du voyage:** Sélectionner un personnage (Abraham, Jacob, Moïse) et regarder leur voyage s'animer
  - Chaque arrêt pulse avec des marqueurs d'événements (`Event`)
  - Contrôles de vitesse pour ralentir aux moments importants (Moriah, Béthel, Sinaï)
- **Clusters d'événements par lieu:** Chaque lieu de `TorahName` (type: PLACE) devient cliquable
  - Expansion pour montrer TOUS les événements qui s'y sont produits
  - Béthel montre: rêve de l'échelle de Jacob, retour de Jacob, renommage en Israël
- **Timeline des rencontres:** À chaque lieu, montrer QUI le voyageur a rencontré
  - Utilise `EntityRelationship` et `EventParticipant`
- **Règle de durée de vie:** Pour les patriarches avec `Genealogy.lifespan_years`
  - Abraham: né, quitte Haran (75), Isaac né (100), Sarah meurt (137), meurt (175)
- **Vue parallèle des voyages:** Comparer côte à côte
  - Voyage d'Abraham vers Moriah vs voyage de Jacob vers Béthel
  - Les deux: départ, rencontre divine, nomination du lieu, construction d'autel

#### Stack Technique
- Leaflet.js ou Mapbox avec tileset Proche-Orient ancien custom
- Timeline scrubber avec verse_id comme axe temporel
- GSAP pour animation fluide des marqueurs de personnages
- Waypoints extraits de `EntityRelationship WHERE relationship_type IN ('travels_to', 'flees_to')`

#### Données Utilisées
- `entity_relationships` (relationship_type: travels_to, lives_in, born_in, dies_in, buried_in, flees_to)
- `events` (event_type, location_id, participants)
- `event_participants` (entity_id, role)
- `genealogy` (lifespan_years, age_at_first_child)
- `torah_names` (name_type = PLACE)

---

### 6. The Shoresh Navigator
**"Suivez les racines. Découvrez l'âme sémantique de la Torah"**

#### Concept
Une carte sémantique interactive et zoomable où les racines hébraïques (shoreshim) forment des constellations de sens. Les utilisateurs naviguent depuis une seule racine vers l'extérieur pour découvrir chaque mot dérivé.

#### Caractéristiques
- **Vue constellation des racines:** Graphe force-directed où chaque racine hébraïque est un nœud lumineux
  - Taille = nombre d'occurrences
  - Couleur = champ sémantique (création, mouvement, parole, émotion)
  - Clic sur une racine → expansion pour montrer tous les mots dérivés, groupés par binyan
- **Table de morphologie des binyanim:** Tableau de conjugaison interactif
  - Comment une racine apparaît en Qal, Niphal, Piel, Pual, Hiphil, Hophal, Hitpael
  - Chaque cellule lie aux versets Torah réels
  - Affiche `grammatical_features` (temps, personne, nombre, genre)
- **Timeline sémantique:** Timeline horizontale montrant où une racine apparaît
  - Heatmaps de densité par verset
  - Cette racine se concentre-t-elle dans les sections légales? narratives?
- **Réseau de racines apparentées:** Affiche `HebrewRoot.related_roots`
  - Ex: racines pour "marcher," "chemin," "voie" interconnectées
- **Carrousel mot-en-contexte:** Pour tout mot dérivé, défiler chaque occurrence avec texte hébreu surligné

#### Stack Technique
- D3.js force-directed graph pour constellation des racines
- React pour tables binyan et timeline
- SVG custom pour nœuds de texte hébreu
- WebGL optionnel pour grands réseaux de racines
- Routage basé URL pour partager des explorations spécifiques

#### Données Utilisées
- `hebrew_roots` (root_letters, root_transliteration, basic_meaning, occurrence_count, related_roots)
- `word_roots` (word_id, root_id, verb_form, grammatical_features)
- `torah_words` (word_original, word_normalized, verse_id, position)
- `torah_verses` (text_hebrew, text_english)

---

### 7. The Pattern Forge
**"Voyez l'architecture que les anciens ont créée"**

#### Concept
Un atelier de recherche spécialisé pour identifier, analyser et annoter les structures littéraires dans le texte de la Torah. Les chercheurs peuvent mapper visuellement chiasme, parallélisme, inclusio et autres patterns.

#### Caractéristiques
- **Canvas avec overlay structurel:** Voir tout passage avec markup structurel coloré
  - Pour chiasme (ABCB'A'), éléments correspondants partagent les couleurs
  - Connectés par lignes courbes
  - `pattern_notation` (e.g., "ABCB'A'") drive la visualisation
- **Highlighter du point focal:** Dans les structures chiastiques, le centre (C) contient souvent la clé théologique
  - Met automatiquement en évidence `focal_point_verse_ref`
- **Outil de comparaison de patterns:** Comparaison côte à côte de multiples structures du même type
  - Requêter tous les `structure_type = chiasmus` et afficher en galerie
  - Filtrer par livre, plage de versets, longueur du pattern
- **Atelier d'annotation:** Permettre aux utilisateurs de proposer de nouvelles structures littéraires
  - Dessiner des sélections sur le texte, assigner des labels (A, B, C...)
  - Sauvegarder brouillons, comparer aux `LiteraryStructure` existants
  - Exporter en JSON ou markdown formaté
- **Intégration expressions formulaires:** Référencer les structures avec les occurrences de `FormulaicExpression`
  - Une formule "toledot" peut marquer la limite d'une structure

#### Stack Technique
- React avec composant canvas custom pour overlays structurels
- Chemins SVG pour lignes de connexion
- Rendu texte hébreu avec gestion RTL propre
- Export LaTeX, Markdown, texte brut
- Comptes utilisateurs optionnels pour partage/discussion

#### Données Utilisées
- `literary_structures` (structure_type, pattern_notation, structural_elements, focal_point_verse_id)
- `formulaic_expressions` (formula_type, formula_hebrew, function)
- `formula_occurrences` (verse_id, position_in_verse)
- `torah_verses` (text_hebrew, text_english)

---

### 8. Covenant Architect
**"Construisez et explorez l'architecture sacrée des alliances bibliques"**

#### Concept
Une visualisation architecturale isométrique 3D où les alliances sont rendues comme des bâtiments sacrés interconnectés. Les utilisateurs construisent et explorent une "Cité des Alliances" virtuelle.

#### Caractéristiques
- **Structures d'alliance:** Chaque alliance (`Covenant`) rendue comme bâtiment unique
  - Alliance Noachique = dôme/arche avec arc-en-ciel
  - Alliance Abrahamique = complexe de tentes du désert (4 coins: terre/descendants/bénédiction/nations)
  - Alliance Sinaïtique = temple de montagne
- **Tours de promesses:** `covenant_elements` où `element_type='promise'` deviennent des tours
  - Hauteur de tour = combien de versets couvre la promesse
  - Lueur de tour = si promesse est `conditional` ou `unconditional`
- **Jardins d'obligations:** Commandements (`mitzvot` liés aux alliances) apparaissent comme éléments de jardin
  - Commandements positifs = plantes en fleur
  - Commandements négatifs = murs/barrières protecteurs
- **Fontaines de bénédiction / Gouffres de malédiction:** `blessings_curses`
  - Bénédictions = fontaines avec eau claire montante
  - Malédictions = rifts sombres
- **Chemins des personnages:** Chaînes de généalogie (`genealogy`) deviennent des chemins connectant les bâtiments
  - Comment l'alliance abrahamique coule à travers Isaac vers Jacob
  - `generation_from_abraham` détermine position sur le chemin

#### Stack Technique
- React + Spline ou Unity WebGL pour isométrique 3D
- Three.js avec shaders custom pour matériaux des bâtiments
- Click-to-explore avec transitions caméra fluides (GSAP)
- Génération procédurale des layouts de bâtiments
- Tone.js pour ambiances sonores changeant par bâtiment

#### Données Utilisées
- `covenants` (covenant_name, party_human, covenant_sign, covenant_type)
- `covenant_elements` (element_type, element_content, verse_id)
- `mitzvot` (mitzvah_type, domain, verse_id)
- `blessings_curses` (blessing_type, giver_id, recipient_id, is_conditional)
- `genealogy` (generation_from_abraham, father_id)

---

### 9. The Gematria Laboratory
**"Où les nombres parlent. Où les patterns émergent"**

#### Concept
Un environnement de recherche pour explorer les patterns de gematria avec rigueur statistique. Contrairement aux outils mystiques, conçu pour l'investigation académique: trouver mots avec valeurs équivalentes, découvrir patterns au niveau verset, comparer méthodes de calcul.

#### Caractéristiques
- **Explorateur d'équivalence de valeur:** Entrer une valeur (ex: 26 pour le Tétragramme)
  - Voir instantanément tous les mots, phrases et totaux de versets correspondants
  - Filtrer par livre, par méthode de calcul, par position du mot
- **Matrice de comparaison cross-méthode:** Pour tout mot ou phrase
  - Afficher matrice montrant sa valeur dans les 4 méthodes
  - Mettre en évidence quand différents mots partagent des valeurs dans plusieurs méthodes
  - Calculer probabilité de correspondance aléatoire
- **Analyse des totaux de versets:** Chaque verset a `gematria_standard_total` et `gematria_katan_total`
  - Visualiser comme heatmap à travers la Torah
  - Identifier versets avec valeurs significatives (multiples de 7, 12, 40)
- **Testeur d'hypothèses de pattern:** Chercheurs proposent hypothèses
  - "Tous les versets mentionnant Abraham ont gematria divisible par X"
  - L'outil exécute la requête, calcule p-values
  - Génère rapport séparant rigueur académique de spéculation mystique
- **Corrélation nom-valeur:** Référencer `TorahName` avec gematria de `TorahWord`
  - Pour chaque personnage, montrer valeur de leur nom
  - Mettre en évidence versets où cette valeur apparaît

#### Stack Technique
- Requêtes SQL optimisées sur colonnes gematria indexées
- Endpoints de calcul statistique (moyenne, médiane, écart-type, tests chi-carré)
- React avec tables de données virtualisées pour performance
- D3.js pour heatmaps et graphiques de distribution
- Export CSV pour analyse ultérieure en R ou Python

#### Données Utilisées
- `torah_words` (gematria_standard, gematria_katan, gematria_ordinal, gematria_atbash)
- `torah_verses` (gematria_standard_total, gematria_katan_total, word_count)
- `torah_names` (name_canonical, name_hebrew)
- Index: `ix_torah_words_gematria_std`, `ix_torah_words_gematria_katan`

---

### 10. Blessing Flow
**"Le fleuve des bénédictions à travers les générations"**

#### Concept
Un diagramme Sankey montrant comment les bénédictions coulent à travers l'arbre généalogique. Visualise le flux de bénédiction d'Isaac à Jacob à ses 12 fils, et les malédictions comme branches épineuses.

#### Caractéristiques
- **Flux Sankey des bénédictions:**
  - Nœuds = personnages de `torah_names`
  - Flux = bénédictions de `blessings_curses` où `giver_id` → `recipient_id`
  - Épaisseur du flux = importance/longueur de la bénédiction
- **Malédictions comme branches épineuses:**
  - Visualisation différente (rouge, épineuse) pour `blessing_type = CURSE`
- **Portes conditionnelles:** Pour bénédictions avec `is_conditional = true`
  - Afficher `condition_text` comme porte/barrière dans le flux
- **Catégories colorées:** Colorer par `category`
  - Patriarcale, sacerdotale, mosaïque, d'alliance, de lit de mort, prophétique
- **Timeline d'activation:** Scrubber temporel montrant quand chaque bénédiction est prononcée

#### Stack Technique
- D3.js Sankey diagram
- React pour contrôles et filtres
- SVG flows avec animations
- Intégration `Genealogy` pour structure de l'arbre

#### Données Utilisées
- `blessings_curses` (blessing_type, category, giver_id, recipient_id, content, is_conditional, condition_text)
- `genealogy` (person_id, father_id, mother_id)
- `torah_names` (name_canonical)
- `torah_verses` (pour contexte)

---

### 11. Divine Name Observatory
**"Observatoire des noms divins"**

#### Concept
Un dashboard analytique complet sur l'usage des noms divins (YHWH, Elohim, El Shaddai, etc.) à travers la Torah.

#### Caractéristiques
- **Heatmap de distribution:** Par livre et chapitre
  - Où YHWH domine vs où ELOHIM domine
  - Intensité = fréquence
- **Analyse par contexte:** Filtrer par `context_type`
  - Création, alliance, jugement, miséricorde, révélation, bénédiction, commandement
- **Qui prononce quel nom?** Grouper par `speaker_type`
  - Narrateur, Dieu (auto-référence), humain, ange
- **Patterns de co-occurrence:** Quand plusieurs noms divins apparaissent proches
- **Notes théologiques:** Afficher `theological_note` pour chaque occurrence
- **Forme grammaticale:** Montrer `grammatical_form` pour analyse linguistique

#### Stack Technique
- React + Recharts ou D3.js
- Heatmaps, bar charts, pie charts interactifs
- Filtres multi-critères
- Export des données pour recherche

#### Données Utilisées
- `divine_name_occurrences` (divine_name, divine_name_hebrew, context_type, speaker_type, grammatical_form, theological_note)
- `torah_verses` (ref, book, chapter)
- Enum `DivineNameType`: YHWH, ELOHIM, EL_SHADDAI, EL_ELYON, ADONAI, EL, EHYEH

---

### 12. Character Emotion Timeline
**"Le parcours émotionnel des héros bibliques"**

#### Concept
Une visualisation des arcs émotionnels des personnages principaux à travers le récit, montrant leurs hauts et bas émotionnels avec contexte.

#### Caractéristiques
- **Ligne du temps émotionnelle:** Axe horizontal = progression narrative (versets)
  - Axe vertical = valence émotionnelle (positif/négatif)
  - Points colorés par `emotion` (joie=or, peur=violet, colère=rouge, etc.)
- **Détails au survol:** Pour chaque point émotionnel
  - `trigger` (ce qui a causé l'émotion)
  - `resulting_action` (comment le personnage a répondu)
  - `expressed_how` (comment l'émotion est montrée)
- **Comparaison de parcours:** Overlay de plusieurs personnages
  - Joseph vs Jacob: qui a le parcours le plus tumultueux?
- **Moments de croisement:** Quand deux personnages ressentent la même émotion au même moment
  - Ex: Jacob et Ésaü lors de leurs retrouvailles
- **Filtres par émotion:** Voir uniquement moments de peur, ou uniquement moments de joie

#### Stack Technique
- React + timeline horizontale interactive
- D3.js pour graphique linéaire avec points interactifs
- Filtres et comparaison multi-personnages
- Animation de l'arc au scroll

#### Données Utilisées
- `character_emotions` (character_id, character_name, emotion, trigger, resulting_action, expressed_how, verse_id)
- `torah_names` (pour liste des personnages)
- `torah_verses` (pour contexte et positionnement)

---

## Structure des Dossiers Proposée

```
/talmud
├── frontend/                          # Frontend unifié React
│   ├── src/
│   │   ├── App.tsx                    # Router principal + sélecteur d'interfaces
│   │   ├── components/
│   │   │   ├── common/                # Composants partagés
│   │   │   │   ├── VerseDisplay.tsx
│   │   │   │   ├── HebrewText.tsx
│   │   │   │   └── Navigation.tsx
│   │   │   └── interfaces/            # Une interface = un dossier
│   │   │       ├── constellation/
│   │   │       │   ├── ConstellationMap.tsx
│   │   │       │   └── index.ts
│   │   │       ├── living-scroll/
│   │   │       │   ├── LivingScroll.tsx
│   │   │       │   └── index.ts
│   │   │       ├── emotional-topology/
│   │   │       ├── voice-chamber/
│   │   │       ├── journey-atlas/
│   │   │       ├── shoresh-navigator/
│   │   │       ├── pattern-forge/
│   │   │       ├── covenant-architect/
│   │   │       ├── gematria-lab/
│   │   │       ├── blessing-flow/
│   │   │       ├── divine-observatory/
│   │   │       └── emotion-timeline/
│   │   ├── api/                       # Client API partagé
│   │   └── hooks/                     # Hooks React partagés
│   └── package.json
│
├── api/                               # Backend API (FastAPI ou Flask)
│   ├── routes/
│   │   ├── verses.py
│   │   ├── names.py
│   │   ├── relationships.py
│   │   ├── theological.py
│   │   ├── linguistic.py
│   │   ├── enrichment.py
│   │   └── gematria.py
│   └── main.py
│
├── src/                               # Code existant (CLI + services)
│   ├── cli/
│   ├── db/
│   └── services/
│
└── docs/
    └── INTERFACES.md                  # Ce fichier
```

---

## Prochaines Étapes

1. **Créer le frontend unifié** avec React + sélecteur d'interfaces
2. **Créer l'API backend** (FastAPI recommandé) exposant les données
3. **Implémenter une interface à la fois** en commençant par la plus simple
4. **Ordre suggéré:**
   - Character Emotion Timeline (plus simple, bonne introduction)
   - Divine Name Observatory (dashboard classique)
   - The Living Scroll (interface de lecture de base)
   - Shoresh Navigator (exploration linguistique)
   - Puis les interfaces 3D plus complexes

---

## Technologies Recommandées

| Catégorie | Technologie |
|-----------|-------------|
| Frontend Framework | React 18 + TypeScript |
| State Management | Zustand ou TanStack Query |
| Routing | React Router v6 |
| UI Components | Radix UI ou shadcn/ui |
| Styling | Tailwind CSS |
| 3D Rendering | Three.js / React Three Fiber |
| 2D Visualization | D3.js |
| Charts | Recharts ou Visx |
| Animations | Framer Motion, GSAP |
| Maps | Leaflet.js ou Mapbox |
| Backend API | FastAPI (Python) |
| Database | SQLite existant ou Turso |
