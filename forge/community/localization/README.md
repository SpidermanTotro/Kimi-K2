# Localization Framework
# THE FORGE AI - Phase 5: Community Growth

This directory contains localization resources for Kimi K2.

## Supported Languages

- `en`: English (default)
- `zh`: Chinese (Simplified)
- `es`: Spanish
- `fr`: French
- `de`: German
- `ja`: Japanese

## Adding a New Language

1. Create language file:
   ```bash
   python add_language.py --lang es --name "Spanish"
   ```

2. Translate strings in `translations/es.json`

3. Test translations:
   ```bash
   python validate_translations.py --lang es
   ```

## Translation Files

Translation files are in JSON format:

```json
{
  "common": {
    "welcome": "Bienvenido",
    "error": "Error",
    "success": "Éxito"
  },
  "benchmarks": {
    "running": "Ejecutando pruebas",
    "complete": "Completado"
  }
}
```

## Usage

```python
from localization import Translator

# Initialize translator
t = Translator(language="es")

# Get translation
print(t.get("common.welcome"))  # Output: "Bienvenido"
```

## Contributing Translations

1. Fork the repository
2. Add/update translations
3. Submit pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

## Translation Quality

- Use native speakers
- Maintain context
- Follow terminology
- Test thoroughly
