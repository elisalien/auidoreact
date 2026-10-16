# Auidoreact — Audioreactive Visualizer

> Visualiseur audioréactif multi-modes avec shaders GLSL génératifs et sortie Spout pour Resolume.

![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-informational) ![Python](https://img.shields.io/badge/Python-ModernGL-blue) ![Shaders](https://img.shields.io/badge/shaders-GLSL-orange) ![Spout](https://img.shields.io/badge/output-Spout%20(Windows)-blueviolet)

## À propos

Application Python qui capte l'entrée audio, en extrait l'énergie par bandes (FFT) et pilote en temps réel cinq familles de shaders GLSL génératifs (20 presets au total). Sur Windows, l'image peut être envoyée en Spout vers Resolume, OBS, etc.

Le code se trouve dans [`audioreactive-viz/`](audioreactive-viz/) (voir aussi son [README](audioreactive-viz/README.md)).

## Fonctionnalités

- 5 modes × 4 presets, changement à chaud au clavier
- Analyse FFT : basses (20–250 Hz), médiums (250 Hz–4 kHz), aigus (4–16 kHz), RMS, détection de beat
- Panneau Dear ImGui (touche `Tab`) avec sliders pour les 4 paramètres de chaque mode
- Feedback buffer pour les trails et accumulations visuelles
- Sortie Spout (texture `AudioReactiveViz`) sur Windows avec SpoutGL

### Modes & presets

**Mode 1 — Fluid Noise Landscapes** : terrains abstraits FBM avec domain warping piloté par l'audio.
- **Deep Ocean** — bleus profonds, lent, réponse basses
- **Volcanic** — rouges/oranges, agressif, haute réactivité
- **Aurora Borealis** — verts/cyans/violets, éthéré
- **Midnight Bloom** — violets/roses/magentas, organique

**Mode 2 — Particle Constellation** : champ de particules avec connexions et trails persistants.
- **Nebula** — oranges/roses chauds, dense, drift lent
- **Neural Net** — cyan/blanc/bleu, connecté, rapide
- **Fireflies** — fond sombre, points jaune/vert, épars
- **Stardust** — blanc/argent/bleu pâle, cosmique

**Mode 3 — Reaction-Diffusion** : modèle Gray-Scott dont les paramètres chimiques sont modulés par l'audio.
- **Coral Reef** — roses/oranges/crème, croissance organique
- **Mycelium** — vert sombre/bleu bioluminescent
- **Acid Bath** — néons vert/jaune/magenta, haut contraste
- **Petri Dish** — blancs/bleus cliniques, scientifique

**Mode 4 — Kaleidoscope Géométrique** : miroirs polaires avec formes géométriques internes.
- **Sacred Geometry** — or/blanc/bleu profond, 12+ segments
- **Prism** — arc-en-ciel, 6-8 segments
- **Obsidian Mirror** — monochrome sombre, 4-6 segments
- **Neon Mandala** — rose vif/cyan/violet, 8-10 segments

**Mode 5 — Glitch Brutalist HUD** : interface cyberpunk déconstruite par l'audio.
- **PHASE(S)** — violet/cyan/rose (palette PHASE(S))
- **Matrix Terminal** — vert sur noir, data rain
- **Surveillance** — désaturé, grain, froid
- **Vaporwave** — rose/bleu/violet, rétro 80s

## Installation

Prérequis : Python 3 et une entrée audio.

**Lancement rapide** — les scripts créent un environnement virtuel `.venv`, installent les dépendances puis lancent l'app :

```bash
cd audioreactive-viz
run.bat        # Windows (installe aussi SpoutGL)
./run.sh       # Linux / macOS
```

**Installation manuelle :**

```bash
cd audioreactive-viz

# Créer un environnement virtuel (recommandé)
python -m venv venv
venv\Scripts\activate    # Windows

# Installer les dépendances
pip install -r requirements.txt

# Optionnel : Spout (Windows uniquement)
pip install SpoutGL
```

## Utilisation

```bash
python main.py

# Lister les périphériques audio disponibles
python main.py --list-devices
```

### Contrôles

| Touche | Action |
|--------|--------|
| `1-5` | Changer de mode |
| `←` / `→` | Parcourir les presets du mode actif |
| `↑` / `↓` | Ajuster la sensibilité audio |
| `Tab` | Afficher/masquer le panneau de paramètres (ImGui) |
| `F` | Plein écran |
| `S` | Activer/désactiver Spout |
| `R` | Reset des framebuffers (feedback) |
| `H` | Afficher/masquer le HUD (titre) |
| `Espace` | Pause |
| `Échap` | Quitter |

### Sortie Spout

Sur Windows avec SpoutGL installé, l'app envoie une texture nommée `AudioReactiveViz` accessible dans Resolume, OBS, etc. Activer/désactiver avec `S`.

### Notes techniques

- Résolution par défaut : 1280×720 (modifiable dans `main.py`)
- VSync activée pour limiter à 60 fps
- Les shaders Reaction-Diffusion tournent 4 itérations/frame pour la fluidité

## Structure du projet

```
audioreactive-viz/
├── main.py              # Boucle principale, fenêtre GLFW, contrôles
├── audio_engine.py      # Capture audio + analyse FFT
├── renderer.py          # Shaders, FBOs, Spout
├── presets.py           # 20 presets (5 modes × 4)
├── gui.py               # Panneau Dear ImGui (sliders de paramètres)
├── run.bat / run.sh     # Scripts d'installation + lancement
├── shaders/
│   ├── common.glsl      # Fonctions noise/hash partagées
│   ├── fullscreen.vert  # Vertex shader quad plein écran
│   ├── fluid_noise.frag
│   ├── particles.frag
│   ├── reaction_diffusion.frag
│   ├── colorize_rd.frag # Colorisation reaction-diffusion
│   ├── kaleidoscope.frag
│   └── glitch_hud.frag
└── requirements.txt
```

## Stack technique

Python, ModernGL, GLFW, PyOpenGL, NumPy, sounddevice, Pillow, Dear ImGui (pyimgui), GLSL, SpoutGL (optionnel).

## Crédits & licence

Aucune licence n'est spécifiée — tous droits réservés.

---

<p align="center">
  Fait par <a href="https://github.com/elisalien">Élisalien</a> ·
  <a href="https://gitlab.com/elisalien/catalog">Catalogue des shaders, sources & logiciels</a>
</p>
