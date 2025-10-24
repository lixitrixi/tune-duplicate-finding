## Installation

Run the following commands to install and set up the venv:
```
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## Usage

To run the tool:
```
python mark_duplicates.py <input_file.xls> <output_file.csv>
```

Currently only Excel is supported for input, and CSV for output.
