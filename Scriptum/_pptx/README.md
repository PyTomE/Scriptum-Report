# Subfolder overview
This is the pptx part o the main module and collects all functions and modules that are specific to pptx

## Usage and Test Instructions
- This folder requires python-pptx to be installed.
- Tests are in global folder tests/01_current/CreatePPTfromTemplate.ipynb.
  
## Organization
- the module `reportPptx.py` is the main entry
- `base.py` contains the base class "PptElement"
- the modules for Images, Paragraphs/Texts, Tables are pairwise organized in "simple" Elements and "more complex" Templates


