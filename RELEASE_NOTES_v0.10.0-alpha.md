# PyGameMaker v0.10.0-alpha

This alpha release brings significant improvements to action implementation, physics support, and complete internationalization.

## Highlights

- **55% of actions now implemented** (66 out of 120 total actions)
- **Physics system** with gravity and friction support
- **Complete translations** for all 7 IDE languages
- **8 new high-priority actions** implemented

## New Actions Implemented

### Movement & Physics
- **Set Gravity** - Apply gravity to instances
- **Set Friction** - Apply friction to slow down movement
- **Wrap Around Room** - Instances wrap to opposite side when leaving room
- **Reverse Horizontal Direction** - Flip horizontal movement
- **Reverse Vertical Direction** - Flip vertical movement

### Drawing & Control
- **Set Drawing Color** - Set color for draw operations
- **Test Chance** - Random probability testing (1 in N chance)
- **Stop Sound** - Stop playing a specific sound

## Translation Improvements

- Complete translations for: English, German, French, Spanish, Italian, Russian, Ukrainian
- Fixed Help menu translations (About PyGameMaker)
- Fixed About dialog content translations for all languages
- Fixed Spanish translations that incorrectly showed French text
- Added Blockly block translations for all languages

## Technical Improvements

- Physics engine integration in game_runner.py
- Action auto-discovery pattern for cleaner code organization
- Improved no_more_lives and no_more_health event triggers
- Updated test suite for new game runner methods

## Installation

### Requirements
- Python 3.11+
- PySide6
- Pygame

### Quick Start
```bash
git clone https://github.com/Gabe1290/pythongm.git
cd pythongm
pip install -r requirements.txt
python main.py
```

## Known Limitations

- This is an alpha release - expect bugs and incomplete features
- 45% of actions still unimplemented
- Some advanced GameMaker features not yet available

## What's Next

- Implement remaining high-priority actions
- Improve HTML5 and mobile export
- Add more event types
- Performance optimizations

---

**Full Changelog**: https://github.com/Gabe1290/pythongm/compare/v0.9.0...v0.10.0-alpha
