# Companion code — Strained Prismatic Geometry

This is the code that accompanies *Strained Prismatic Geometry — Deformation over the Absolute Base and the abc Conjecture* (WiseMotif Monograph of Mathematical Intelligence, Series 06) (Research Architecture Edition 1, version 1.0.0), by Vincent Liu, licensed under the Apache
License 2.0 (`LICENSE`); the monograph itself is licensed under CC BY-NC-ND 4.0. The abc conjecture remains open;
nothing here proves it, and no program here evaluates the strain trace of the book (PO-087–PO-089 remain open).

| folder | what it is | book |
|---|---|---|
| `python/abctk/` | the certified arithmetic kernel: integer radicals and sieving, abc triples and their quality, the Frey–Hellegouarch curve and Tate's algorithm, the function-field abc theorem, q-calculus and exact Habiro digits, truncated Witt vectors and Nygaard data, heights, outward-rounded interval certificates, and the SQLite engine with canonical, content-addressed reports | Ch. 47–53 |
| `python/tests/` | 61 tests; each asserts a statement the book prints | Ch. 52 |
| `python/examples/` | `generate_ch50_51.py`, which regenerates every datum of Chapters 50–51, and its output `ch50_51_results.json` | Ch. 50–51 |

## Reproduce

Python 3.10 or later; the package uses the standard library only (tested: Python 3.11.9). From this folder:

```sh
cd python
python -m pytest tests -q                  # all 61 tests (pytest required)
python tests/test_abctk.py                 # without pytest: the 37 tests of test_abctk.py
python examples/generate_ch50_51.py        # regenerate the Chapter 50–51 data (writes examples/ch50_51_results.json)
```

`REPRODUCIBILITY.md` is the C-3 report of the final edition: the tests; the regenerated Chapter 50–51 data compared
field by field with the shipped `ch50_51_results.json` (timings and timestamps excepted); and the abc records the book
prints, recomputed exactly.

## Changes from the working tree

The files are the author's working tree, with the documentation edits listed in `CODE-EDITS.md` and an SPDX licence
header on every Python file. No line of program code is changed.
