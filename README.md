# ut-ml-p39-church-books

## 1. Install dependencies
**Tested only with python 3.7**

```pip install -r requirements.txt```

## 2. Run Transkribus and extract results

Upload book pages into Transkribus, run a HTR model and export XML files containing the transcriptions to a separate folder.

## 3. Run program to extract surnames from Transkribus files

Run `main.py` on the folder with transcriptions (XML) from Transkribus.

Example of a command line run:

```python main.py --transkribus-folder ~/transkribus_data/page/```

For documentation about the available options run:

```python main.py --help```

