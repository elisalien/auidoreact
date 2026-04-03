# Audioreactive Visualizer

Visualiseur audioreactif multi-modes avec shaders GLSL génératifs et sortie Spout pour Resolume.

## Installation

```bash
# Créer un environnement virtuel (recommandé)
python -m venv venv
venv\Scripts\activate    # Windows

# Installer les dépendances
pip install -r requirements.txt

# Optionnel: Spout (Windows uniquement)
pip install SpoutGL
```

## Lancement

```bash
python main.py

# Lister les périphériques audio disponibles
python main.py --list-devices
```

## Contrôles

| Touche | Action |
|--------|--------|
| `1-5` | Changer de mode |
| `←` / `→` | Parcourir les presets du mode actif |
| `↑` / `↓` | Ajuster la sensibilité audio |
| `F` | Plein écran |
| `S` | Activer/désactiver Spout |
| `R` | Reset des framebuffers (feedback) |
| `H` | Afficher/masquer le HUD (titre) |
| `Espace` | Pause |
| `Échap` | Quitter |

## Modes & Presets

### Mode 1 — Fluid Noise Landscapes
Terrains abstraits FBM avec domain warping piloté par l'audio.
- **Deep Ocean** — bleus profonds, lent, réponse basses
- **Volcanic** — rouges/oranges, agressif, haute réactivité
- **Aurora Borealis** — verts/cyans/violets, éthéré
- **Midnight Bloom** — violets/roses/magentas, organique

### Mode 2 — Particle Constellation
Champ de particules avec connexions et trails persistants.
- **Nebula** — oranges/roses chauds, dense, drift lent
- **Neural Net** — cyan/blanc/bleu, connecté, rapide
- **Fireflies** — fond sombre, points jaune/vert, épars
- **Stardust** — blanc/argent/bleu pâle, cosmique

### Mode 3 — Reaction-Diffusion
Modèle Gray-Scott dont les paramètres chimiques sont modulés par l'audio.
- **Coral Reef** — roses/oranges/crème, croissance organique
- **Mycelium** — vert sombre/bleu bioluminescent
- **Acid Bath** — néons vert/jaune/magenta, haut contraste
- **Petri Dish** — blancs/bleus cliniques, scientifique

### Mode 4 — Kaleidoscope Géométrique
Miroirs polaires avec formes géométriques internes.
- **Sacred Geometry** — or/blanc/bleu profond, 12+ segments
- **Prism** — arc-en-ciel, 6-8 segments
- **Obsidian Mirror** — monochrome sombre, 4-6 segments
- **Neon Mandala** — rose vif/cyan/violet, 8-10 segments

### Mode 5 — Glitch Brutalist HUD
Interface cyberpunk déconstruite par l'audio.
- **PHASE(S)** — violet/cyan/rose (palette PHASE(S))
- **Matrix Terminal** — vert sur noir, data rain
- **Surveillance** — désaturé, grain, froid
- **Vaporwave** — rose/bleu/violet, rétro 80s

## Architecture

```
audioreactive-viz/
├── main.py              # Boucle principale, fenêtre GLFW, contrôles
├── audio_engine.py      # Capture audio + analyse FFT
├── renderer.py          # Shaders, FBOs, Spout
├── presets.py           # 20 presets (5 modes × 4)
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

## Sortie Spout

Sur Windows avec SpoutGL installé, l'app envoie une texture nommée `AudioReactiveViz` accessible dans Resolume, OBS, etc. Activer/désactiver avec `S`.

## Notes techniques

- Résolution par défaut: 1280×720 (modifiable dans `main.py`)
- VSync activée pour limiter à 60fps
- Les shaders Reaction-Diffusion tournent 4 itérations/frame pour la fluidité
- Le feedback buffer permet les trails et accumulations visuelles
- L'analyse FFT extrait : basses (20-250Hz), médiums (250-4kHz), aigus (4-16kHz), RMS, détection de beat
