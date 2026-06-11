# VEGO-AI Compliance Visualizer – Delivery Package

## What's inside

```
vego_visualizer_delivery/
├── visualize_compliance.py        ← the application (no changes needed)
├── visualize_config.yaml          ← pre-configured paths (relative, works anywhere)
├── requirements.txt               ← Python dependencies
├── models/                        ← student UML diagram files (.txt / .puml)
│   └── *.txt
├── compliance_vectors/            ← AgentC output – one JSON per evaluated case
│   └── agentC_case_*.json
└── guidelines/                    ← Reference guidelines produced by AgentB
    └── agentB_best_guidelines.json
```

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| **Python 3.9+** | Must be installed and on your PATH |
| **tkinter** | Bundled with Python on Windows & Linux. On macOS: `brew install python-tk@3.x` |
| **Pillow** *(optional)* | Enables zoom/resize on PlantUML diagrams |
| **Internet connection** | Diagrams are rendered via `plantuml.com` |

## Quick start

```bash
# 1 – (optional) create a virtual environment
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate         # Windows

# 2 – install Pillow (optional but recommended)
pip install -r requirements.txt

# 3 – run the visualizer
#     IMPORTANT: run from inside the delivery folder so relative paths work
cd path/to/vego_visualizer_delivery
python visualize_compliance.py
```

The app auto-loads the config file (`visualize_config.yaml`) which already
points to the bundled `models/`, `compliance_vectors/`, and `guidelines/`
folders – **no editing required**.

## Using the UI

1. **Aggregate** dropdown → select an `agentC_case_*.json` file.
   The matching model file is auto-selected in the **Model** dropdown.
2. The **Code** tab shows the raw PlantUML/text of the student model.
3. The **Diagram** tab renders the model via PlantUML (needs internet).
4. The **Compliance Vector** table lists each guideline with its status
   (Satisfied / Partially-Satisfied / Not-Satisfied) and evidence.
5. Click any row for full details in the **Details** panel.
6. Click the **📊 SUMMARY** row at the bottom for the overall case score.

### Loading your own files at runtime

| Button | What it opens |
|--------|---------------|
| **Browse Models…** | Folder of `.txt` / `.puml` model files |
| **Browse Vectors…** | Folder of compliance-vector JSON files |
| **Browse Guide(s)…** | A single reference-guidelines JSON file |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'tkinter'` | Install `python-tk` via your package manager |
| Diagram tab shows "Diagram error" | Check your internet connection; `plantuml.com` must be reachable |
| App opens but dropdowns are empty | Make sure you run `python visualize_compliance.py` **from inside** the delivery folder |
