# Adobe Round 1A – PDF Outline Extraction

This project is designed for the Adobe Submission Hackathon (Round 1A). It extracts clean, structured outlines (Title, H1, H2, H3) from academic or technical PDFs using font features, layout cues, and logical scoring. The solution is fully containerized with Docker.

---
## 📁 Project Structure

```
Round_1A/
├── app/                         # Core application logic
│   ├── __init__.py              # Init file
│   ├── features.py              # Font clustering, heading scoring, etc.
│   ├── main.py                  # CLI to run the PDF extractor
│   ├── outline_extractor.py     # Main logic for title + outline extraction
│   ├── pdf_parser.py            # Extracts text spans from PDFs using PyMuPDF
│   └── title_extractor.py       # Extracts title from top spans
├── input/                       # Folder containing PDFs to be processed
│   └── example.pdf
├── output/                      # JSON output files will be saved here
│   └── example.json
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker build script
└── README.md                    # Project documentation
```
## Features

- **PDF Parsing** using PyMuPDF (`fitz`)
- **Font size clustering** to identify body vs heading fonts
- **Point-based heading scoring** (bold, centered, x-alignment, etc.)
- **Numbered heading detection** (e.g., "1.", "2.1", etc.)
- **Heading concatenation** for multi-line headings
- **Debugging support** with span logs and font stats
- **Dockerized** for consistent local/offline execution

## Setup Instructions

### Option 1: Run with Docker (Recommended)

#### 1. **Build the Docker image**

```bash
docker build --platform linux/amd64 -t round1a-solution:latest .
````

#### 2. **Run the container**

```bash
docker run --rm -v ${PWD}/Round_1A/input:/app/input -v ${PWD}/Round_1A/output:/app/output round1a-solution:latest
```

> Replace `${PWD}` with the full path to your `Round_1A` folder if on Windows.

---

### Option 2: Run Locally with Python (non-Docker)

#### 1. Create and activate a virtual environment

```bash
cd Round_1A
python -m venv venv
venv\Scripts\activate    # On Windows
# Or: source venv/bin/activate on Linux/Mac
```

#### 2. Install dependencies

```bash
pip install -r requirements.txt
```

#### 3. Run the solution

```bash
python -m app.main --input input --output output
```

---

## Input Format

Place your input PDFs inside the `input/` folder.

```
Round_1A/
└── input/
    ├── doc1.pdf
    └── doc2.pdf
```

---

## Output Format

Each PDF will produce a `.json` file inside the `output/` folder.

Example: `output/doc1.json`

```json
{
  "title": "Introduction to Deep Learning",
  "outline": [
    {
      "heading": "1. Introduction",
      "level": "H1"
    },
    {
      "heading": "1.1 Background",
      "level": "H2"
    },
    {
      "heading": "1.1.1 History",
      "level": "H3"
    }
  ]
}
```

---

## Debugging (Optional)

During development, logs and parsed spans are dumped to:

```
parsed_spans_debug.txt
```

---

## Design Highlights

* Font clustering identifies dominant body text size
* Heading scores are assigned using multiple cues:

  * Font size
  * Boldness
  * Line length
  * X-position (alignment)
  * Numbering patterns
* Headings that are purely numbers are filtered out
* Heading level assignment doesn’t depend solely on font size clustering

---

## Dependencies

* Python 3.9+
* PyMuPDF
* scikit-learn
* numpy
* tqdm

(see `requirements.txt`)

---
## 🏁 License

This project is submitted as part of the Adobe Submission Hackathon. License and usage will be governed by hackathon rules.
