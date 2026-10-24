<p align="center">
  <a href="https://doi.org/10.5281/zenodo.23610034"><img src="assets/hero.svg" alt="Strained Prismatic Geometry — the D6 honeycomb of five volumes and the appendices around the global substrate Spec ℤ → 𝔖" width="100%"></a>
</p>

<p align="center">
  <a href="https://doi.org/10.5281/zenodo.23610034"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.23610034.svg" alt="DOI"></a>
  <a href="https://creativecommons.org/licenses/by-nc-nd/4.0/"><img src="https://img.shields.io/badge/license-CC%20BY--NC--ND%204.0-0A131E?style=flat" alt="License: CC BY-NC-ND 4.0"></a>
  <a href="code/LICENSE"><img src="https://img.shields.io/badge/code-Apache%202.0-0A131E?style=flat" alt="Code: Apache 2.0"></a>
  <a href="https://github.com/AlienMuse/strained-prismatic-geometry/releases/tag/v1.0.0"><img src="https://img.shields.io/badge/release-1.0.0-1E5A88?style=flat" alt="Release 1.0.0"></a>
  <img src="https://img.shields.io/badge/pages-1%2C666-536372?style=flat" alt="1,666 pages">
  <img src="https://img.shields.io/badge/proof%20obligations-98%20open-536372?style=flat" alt="98 open proof obligations">
  <img src="https://img.shields.io/badge/series-06-536372?style=flat" alt="Series 06">
  <a href="VERIFY.md"><img src="https://img.shields.io/badge/OpenPGP-signed-B8913B?style=flat" alt="OpenPGP signed"></a>
  <a href="VERIFY.md"><img src="https://img.shields.io/badge/timestamps-RFC%203161%20%C2%B7%20Bitcoin-B8913B?style=flat" alt="RFC 3161 and Bitcoin timestamps"></a>
</p>

<p align="center">
  <b><a href="https://github.com/AlienMuse/strained-prismatic-geometry/releases/download/v1.0.0/Strained-Prismatic-Geometry-v1.0.0-Preview.pdf">Read the preview</a></b> (166 pages, 72.0 MB) ·
  <a href="#download">Download</a> ·
  <a href="#the-five-volumes">Volumes</a> ·
  <a href="#companion-code">Code</a> ·
  <a href="#citation">Cite</a> ·
  <a href="VERIFY.md">Verify</a> ·
  <a href="README.zh-CN.md">中文</a>
</p>

<br>

> *The integers are initial among commutative unital rings, and Spec ℤ is terminal among schemes. Ordinary
> arithmetic therefore has no intrinsic base direction beneath Spec ℤ.*
> <br>— Preface

**Strained Prismatic Geometry** — *Deformation over the Absolute Base and the abc Conjecture* — is a monograph in
five volumes bound as one. It is the sixth work in the WiseMotif Monograph of Mathematical Intelligence and belongs
to the Grothendieckian Programme as a self-contained system: one of the Programme's research subjects, a problem on
which its method of recursive mathematical discovery is carried through in full. A structure is proposed; it is
tested against the cases in which the answer is known; what survives is abstracted and the question is posed again,
in the manner of Grothendieck's rising sea.

The problem is the abc conjecture of Masser and Oesterlé, and the question is **why it is a theorem over function
fields, with a proof of half a page, and open over the integers; and what object would allow the function-field
proof to be imitated in arithmetic rather than merely admired.**

**The abc conjecture remains open. This work does not prove it.** It is not an exposition, verification, refutation
or reformulation of inter-universal Teichmüller theory, and it records the published disagreement about that theory
without adjudicating it. What it offers is the state of the question after the method has been applied without
concession: what the substrate would deliver, what it would need, and where each route to it stops.

<table>
  <tr>
    <td align="center"><b>5</b><br><sub>volumes,<br>bound as one</sub></td>
    <td align="center"><b>10 · 62</b><br><sub>parts ·<br>chapters</sub></td>
    <td align="center"><b>1,666</b><br><sub>pages</sub></td>
    <td align="center"><b>98</b><br><sub>named proof<br>obligations</sub></td>
    <td align="center"><b>14 · 22</b><br><sub>obstructions ·<br>critical experiments</sub></td>
    <td align="center"><b>186 · 242</b><br><sub>vector plates ·<br>references</sub></td>
    <td align="center"><b>61</b><br><sub>abctk<br>tests</sub></td>
  </tr>
</table>

## The idea: give Spec ℤ a base

Over a function field the polynomial abc theorem of Mason and Stothers is easy, because the proof runs on a base: one
differentiates along it, and Riemann–Hurwitz counts what the derivative sees. The proof consumes four inputs — a base,
a derivation along it, a non-zero sheaf of relative differentials and a degree–ramification formula (Chapter 2).
Over ℤ all four fail for one reason: ℤ is initial among commutative rings, so the cotangent complex of Spec ℤ over its
only base is zero, and **no 1-categorical repair that keeps an initial lift of ℤ can change this** (Obstruction 3.3.2, the no-go theorem for initial lifts).

The book changes the base. A **global substrate** 𝔖 is assembled from prismatic geometry and the Cartier–Witt stack
at every finite prime, a q-deformation over the Habiro ring valid at all primes at once, and condensed analytic
geometry at the real place, glued along the product formula, so that Spec ℤ → 𝔖 carries a relative cotangent
direction. Bad reduction becomes **strain** in that direction: a strain complex, a strain class and an arithmetic
Kodaira–Spencer class, whose function-field limit is the classical Kodaira–Spencer map.

| The method | What the book does |
|---|---|
| **Diagnose** | three proofs of Mason–Stothers, the absolute obstruction and its no-go theorem, eight design requirements, six decades of surrogates scored against them (Part 0) |
| **Construct** | δ-rings, prisms, the Cartier–Witt and syntomic stacks, the absolute base 𝔄; the Habiro ring, condensed and analytic geometry, the global substrate 𝔖 (Parts I–II) |
| **Deform** | the strain complex, the arithmetic Kodaira–Spencer class, log shells, the Θ-line, the gluing ∞-groupoid 𝒢 (Part III) |
| **Dilate** | the Θ-dilation q ↦ q<sup>λ</sup>, the dilation comparison theorem with an unconditional analytic core, multiradiality as descent (Part IV) |
| **Prove** | Theorem C, trace invariance under groupoids of identifications, unconditionally (Theorem 36.3.1) |
| **Descend** | Theorem A, the master inequality (Theorem 39.1.6), and Theorem B, abc over ℚ (Theorem 43.1.5), both conditional on named obligations (Parts V–VI) |
| **Compute** | certified Habiro and prismatic arithmetic, interval-certified trace benchmarks, the abc-verification engine, implemented in abctk (Part VII) |
| **Audit** | Lean 4 blueprints, the proof-obligation ledger, the obstruction atlas, twenty-two critical experiments and three kill criteria (Parts VIII–IX) |

## The five volumes

The five volumes and the appendices are bound as one book. Each cover below places its volume at the centre of the
D₆ honeycomb, with the formula its cell carries on the front cover of the book.

<table>
  <tr>
    <td width="33%" valign="top" align="center">
      <a href="docs/contents/volume-i.md"><img src="assets/covers/volume-1.jpg" alt="Volume I cover — The Problem and the Absolute Base" width="200"></a><br>
      <b>I · The Problem and the Absolute Base</b><br>
      <sub>Parts 0–I · 12 chapters · pp. 1–251</sub><br><br>
      <sub>The Masser–Oesterlé conjecture in its constant, finiteness and quality forms; Mason–Stothers proved three times; the absolute obstruction and the no-go theorem; eight requirements and an atlas of surrogates; δ-rings and Witt vectors, prisms and prismatic cohomology, the Cartier–Witt and syntomic stacks, F-gauges, Rees descent, the absolute base, Buium's jet spaces.</sub><br><br>
      <a href="docs/contents/volume-i.md">Contents</a> · <a href="https://github.com/AlienMuse/strained-prismatic-geometry/releases/download/v1.0.0/Strained-Prismatic-Geometry-v1.0.0-Complete.pdf">PDF</a>
    </td>
    <td width="33%" valign="top" align="center">
      <a href="docs/contents/volume-ii.md"><img src="assets/covers/volume-2.jpg" alt="Volume II cover — The Global Substrate and Its Deformation Theory" width="200"></a><br>
      <b>II · The Global Substrate and Its Deformation Theory</b><br>
      <sub>Parts II–III · 14 chapters · pp. 252–549</sub><br><br>
      <sub>q-de Rham cohomology, the Habiro ring and Habiro descent; condensed mathematics, analytic stacks and the archimedean gauge; the global substrate glued along the product formula; adelic curves; the strain complex, the arithmetic Kodaira–Spencer class, semistable models, log shells, the Θ-line, the gluing ∞-groupoid and the indeterminacy calculus.</sub><br><br>
      <a href="docs/contents/volume-ii.md">Contents</a> · <a href="https://github.com/AlienMuse/strained-prismatic-geometry/releases/download/v1.0.0/Strained-Prismatic-Geometry-v1.0.0-Complete.pdf">PDF</a>
    </td>
    <td width="33%" valign="top" align="center">
      <a href="docs/contents/volume-iii.md"><img src="assets/covers/volume-3.jpg" alt="Volume III cover — Dilation, Traces and the Master Inequality" width="200"></a><br>
      <b>III · Dilation, Traces and the Master Inequality</b><br>
      <sub>Parts IV–V · 14 chapters · pp. 550–841</sub><br><br>
      <sub>Dilation operators on gauge stacks and the Θ-dilation; functoriality, the dilation comparison theorem, multiradiality as descent, the dilation cocycle and the rigidity lemma; six-functor formalisms, categorical traces, Theorem C, heights as traces, arithmetic Riemann–Hurwitz, the master inequality and its constants.</sub><br><br>
      <a href="docs/contents/volume-iii.md">Contents</a> · <a href="https://github.com/AlienMuse/strained-prismatic-geometry/releases/download/v1.0.0/Strained-Prismatic-Geometry-v1.0.0-Complete.pdf">PDF</a>
    </td>
  </tr>
  <tr>
    <td width="33%" valign="top" align="center">
      <a href="docs/contents/volume-iv.md"><img src="assets/covers/volume-4.jpg" alt="Volume IV cover — The Descent to abc and Its Computation" width="200"></a><br>
      <b>IV · The Descent to abc and Its Computation</b><br>
      <sub>Parts VI–VII · 12 chapters · pp. 842–1100</sub><br><br>
      <sub>From the master inequality to Szpiro; the Frey–Hellegouarch curve and its complete 2-adic classification; Theorem B over ℚ, abc over number fields, consequences, uniformity, the extremal triples; certified computation in the Habiro ring, prismatic algorithms, interval-certified traces, the abc-verification engine and the reproducibility contract.</sub><br><br>
      <a href="docs/contents/volume-iv.md">Contents</a> · <a href="https://github.com/AlienMuse/strained-prismatic-geometry/releases/download/v1.0.0/Strained-Prismatic-Geometry-v1.0.0-Complete.pdf">PDF</a>
    </td>
    <td width="33%" valign="top" align="center">
      <a href="docs/contents/volume-v.md"><img src="assets/covers/volume-5.jpg" alt="Volume V cover — Formalisation, Audit and Prospects" width="200"></a><br>
      <b>V · Formalisation, Audit and Prospects</b><br>
      <sub>Parts VIII–IX · 10 chapters · pp. 1101–1291</sub><br><br>
      <sub>Lean 4 blueprints for the substrate and for the trace theorem; the proof-obligation ledger as a formal artefact; the multi-agent method and the sociology of verification; the obstruction atlas, falsifiability and kill criteria, the substrate beyond abc, what has been proved and what has not, a programme for the next decade.</sub><br><br>
      <a href="docs/contents/volume-v.md">Contents</a> · <a href="https://github.com/AlienMuse/strained-prismatic-geometry/releases/download/v1.0.0/Strained-Prismatic-Geometry-v1.0.0-Complete.pdf">PDF</a>
    </td>
    <td width="33%" valign="top" align="center">
      <a href="docs/contents/appendices.md"><img src="assets/covers/volume-6.jpg" alt="Appendices cover — Appendices A–J" width="200"></a><br>
      <b>Appendices A–J</b><br>
      <sub>10 appendices · bibliography · three indexes · pp. 1292–1599</sub><br><br>
      <sub>Higher categories, condensed and pyknotic mathematics, a prismatic compendium, tables of δ-rings and of the Habiro ring, Arakelov geometry, the glossary, the proof-obligation ledger, the atlas of the 186 plates and the computational resources; indexes of notation, names and subjects.</sub><br><br>
      <a href="docs/contents/appendices.md">Contents</a> · <a href="https://github.com/AlienMuse/strained-prismatic-geometry/releases/download/v1.0.0/Strained-Prismatic-Geometry-v1.0.0-Complete.pdf">PDF</a>
    </td>
  </tr>
</table>

<p align="center">
  <a href="https://github.com/AlienMuse/strained-prismatic-geometry/releases/download/v1.0.0/Strained-Prismatic-Geometry-v1.0.0-Complete.pdf"><img src="assets/covers/complete.jpg" alt="Front cover of the complete monograph — the D6 honeycomb around the global substrate" width="260"></a><br>
  <b>The complete monograph</b> · Volumes I–V and Appendices A–J · 1,666 pages · 83.0 MB
</p>

## Selected results

- **The no-go theorem for initial lifts (Obstruction 3.3.2).** For every 1-categorical algebraic repair keeping an initial lift
  of ℤ, the cotangent complex of that lift vanishes and every derivation into a split square-zero extension is
  trivial. *[NEW]*
- **Trace invariance, Theorem C (Theorem 36.3.1).** The categorical trace of an endomorphism of a dualisable object,
  equivariant for a connected ∞-groupoid of identifications, is a canonical point of End(𝟏)<sup>h𝒢</sup>, independent
  of every choice. Its instance over the substrate is conditional; the chapter states which part of the Scholze–Stix
  objection it addresses and which parts it leaves standing. *[NEW]*
- **The dilation comparison theorem (Theorem 30.1.4).** The finite-place and archimedean readings of the
  Θ-dilation differ by an explicit eta quotient, with the unconditional bound 24(λ+1)|q|(1−|q|)<sup>−2</sup>; the
  identification of the two routes with substrate constructions is conditional. *[CONDITIONAL]*
- **The master inequality, Theorem A (Theorem 39.1.6).** The strain trace is bounded by (1+ε) times the conductor
  and different terms plus a constant independent of the object, by an eight-step argument whose arithmetic weight
  rests on one obligation, PO-079. *[CONDITIONAL]*
- **Height Szpiro implies abc, with constants (Theorem 42.3.2).** The height form of Szpiro with exponent 6+δ
  gives abc with exponent 1+δ/6 and explicit constants; with the 2-adic reduction of the Frey curve proved again by
  Tate's algorithm (Theorem 42.5.4, *[REPROVED]*), the Diophantine endgame is unconditional. *[NEW]*
- **abc over ℚ, Theorem B (Theorem 43.1.5).** max(|a|,|b|,|c|) ≤ K<sub>B</sub>(ε) rad(abc)<sup>1+ε</sup>, conditional on
  sixty-one named obligations and three named hypotheses, every constant tracked. *[CONDITIONAL]*
- **What has been proved (Chapter 61).** The dependency closure of Theorems A and B as an explicit finite set
  (Proposition 61.1.2), the unconditional mathematical content (Proposition 61.1.9), the obligations that deserve
  immediate scepticism, and concrete kill conditions.

## What this work is — and is not

**It is** a foundational proposal with its full price attached: an exact diagnosis of why arithmetic has no base, a
proposed substrate whose local pillars are established mathematics and whose global assembly is a named, finite list
of proof obligations, an unconditional trace-invariance theorem, a conditional derivation of abc in which every
constant is tracked, and a computational and formal-verification architecture held to the level of certification it
has. Every substantive assertion carries one of six labels where it is made: **[KNOWN]** a result of the existing
literature, **[REPROVED]** a known result proved again here, **[NEW]** first proved here, unconditionally,
**[CONDITIONAL]** proved from named obligations, **[OPEN]** not proved here, **[DISPUTED]** a documented disagreement
recorded without adjudication.

**It is not** a proof of the abc conjecture. Theorems A and B are conditional on the ledger of Appendix H, and the
book says so on every page where they appear. It is not a verification or refutation of inter-universal Teichmüller
theory. No program here evaluates the strain trace: abctk certifies arithmetic inputs and explicit comparison
targets, and the comparison with the strain trace is recorded as open (PO-087–PO-089).

## Where to start

The routes are those of the *Leitfaden*.

| Route | Chapters |
|---|---|
| one afternoon | Epistemic Status, Leitfaden; 3; 5 and 61; 39 with Appendix H; 59; 55 |
| the shortest dependency-closed path to Theorem B | 1–32, 34–43, Appendices A and F |
| foundations | 1–18, 20–25, 27–28, 34–36, Appendix A |
| computational and reproducibility | 1–32, 34–52, Appendices A and F |
| the sceptical audit | 1–32, 34–55, 61, Appendices A, F and H |

The [preview](https://github.com/AlienMuse/strained-prismatic-geometry/releases/download/v1.0.0/Strained-Prismatic-Geometry-v1.0.0-Preview.pdf) contains the front matter — Series Note,
Abstract, Preface, Epistemic Status of This Book, the Leitfaden, notation, the contents and the lists of plates,
figures and tables — and the whole of Part 0.

## Download

| File | Pages | Size |
|---|---:|---:|
| [**Complete monograph**](https://github.com/AlienMuse/strained-prismatic-geometry/releases/download/v1.0.0/Strained-Prismatic-Geometry-v1.0.0-Complete.pdf) — Volumes I–V and Appendices A–J | 1,666 | 83.0 MB |
| [Preview](https://github.com/AlienMuse/strained-prismatic-geometry/releases/download/v1.0.0/Strained-Prismatic-Geometry-v1.0.0-Preview.pdf) — front matter and Part 0 | 166 | 72.0 MB |
| [Companion code](https://github.com/AlienMuse/strained-prismatic-geometry/releases/download/v1.0.0/Strained-Prismatic-Geometry-v1.0.0-code.zip) — abctk, Apache-2.0 | — | 60.7 KB |

The same files, with identical checksums, are archived at Zenodo: [doi:10.5281/zenodo.23610035](https://doi.org/10.5281/zenodo.23610035).
Covers are 600 ppi full-bleed; all fonts are embedded; the PDFs are linearised for fast opening.

## Companion code

[`code/`](code/) is abctk, the certified arithmetic kernel of the book, as published in the code archive of the
release: integer radicals and sieving, abc triples and their quality, the Frey–Hellegouarch curve and Tate's
algorithm, the function-field abc theorem, q-calculus and exact Habiro digits, truncated Witt vectors and Nygaard
data, heights, outward-rounded interval certificates, and the SQLite engine with canonical, content-addressed
reports. It uses the Python standard library only; its 61 tests each assert a statement the book prints, and
`examples/generate_ch50_51.py` regenerates every datum of Chapters 50–51. The code is licensed under the Apache
License 2.0 ([code/LICENSE](code/LICENSE)); the book is not.

```sh
cd code/python
python -m pytest tests -q                  # all 61 tests (pytest required)
python examples/generate_ch50_51.py        # regenerate the Chapter 50–51 data
```

## Citation

> Liu, V. (2026). *Strained Prismatic Geometry — Deformation over the Absolute Base and the abc Conjecture*
> (Research Architecture Edition 1, version 1.0.0). Zenodo. https://doi.org/10.5281/zenodo.23610034

```bibtex
@book{liu2026strainedprismatic,
  author    = {Liu, Vincent},
  title     = {Strained Prismatic Geometry --- Deformation over the Absolute Base and the {abc} Conjecture},
  series    = {WiseMotif Monograph of Mathematical Intelligence, Series 06},
  edition   = {Research Architecture Edition 1},
  version   = {1.0.0},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.23610034},
  url       = {https://doi.org/10.5281/zenodo.23610034}
}
```

GitHub's *Cite this repository* button uses [CITATION.cff](CITATION.cff). The concept DOI 10.5281/zenodo.23610034 always resolves to
the latest version; cite the version DOI 10.5281/zenodo.23610035 to refer to these exact files.

## Authenticity

Every file of the release is listed in `SHA256SUMS`, signed with OpenPGP and timestamped twice (RFC 3161 and
OpenTimestamps on Bitcoin). The signing key is the same as for Series 01–05.

Signing key fingerprint: `DA1A 1AEF D8B2 C17C FF3F 1D1B 3905 0F50 7A4F EC17`

GitHub releases of this repository are immutable. Copies obtained elsewhere that do not match `SHA256SUMS` are not
authentic. Three levels of verification: [VERIFY.md](VERIFY.md).

## License and AI use

The work is licensed under [CC BY-NC-ND 4.0](LICENSE): you may share it unchanged, with attribution, for
non-commercial purposes. Translations and other uses require written permission. As the copyright page states, the
code listings printed in the work and the abctk package are additionally available under the
[Apache License 2.0](LICENSES/Apache-2.0.txt). Details: [NOTICE.md](NOTICE.md) · Name use:
[TRADEMARKS.md](TRADEMARKS.md).

**Text and data mining rights are reserved** under Article 4(3) of Directive (EU) 2019/790. Training or fine-tuning
machine-learning models on the work is not permitted without written permission. Individual readers may use AI
tools to read, search, explain or translate the work for their own study. Full policy:
[TDM-AND-AI-POLICY.md](TDM-AND-AI-POLICY.md).

## Contributing

The Epistemic Status of the book states it plainly: the most valuable response is not agreement but a demonstration
that one of the obligations is false, that a declared dependency is circular, that a computation in Chapter 59 comes
out the other way, or that a proof tagged [NEW] does not close. Three kinds of contribution matter most:

- **Refutation** — any of the twenty-two critical experiments or three kill criteria of Chapter 59, or a false
  obligation in the ledger of Appendix H.
- **Construction** — a proof of any of the ninety-eight obligations PO-001–PO-098, beginning with those Chapter 61
  ranks as most load-bearing.
- **Reproduction** — an independent check of abctk against the book's tables, or a Lean statement of an obligation
  of Chapters 53–55.

Report errors through an [errata issue](https://github.com/AlienMuse/strained-prismatic-geometry/issues/new?template=errata.yml). Accepted corrections are
acknowledged by name in the next edition (see [ERRATA.md](ERRATA.md)).

---

<p align="center"><sub>
  <a href="https://wisemotif.ai">WiseMotif Monograph of Mathematical Intelligence</a> · Series 06 · Mathematics and Artificial Intelligence<br>
  Series 01: <a href="https://github.com/AlienMuse/grothendieckian-machine"><i>GAI-MUA: The Grothendieckian Machine</i></a> ·
  Series 02: <a href="https://github.com/AlienMuse/topos-native-intelligence"><i>GM-Omega-Infinity: Topos-Native Intelligence</i></a> ·
  Series 03: <a href="https://github.com/AlienMuse/arithmetic-spectral-descent"><i>Arithmetic Spectral Descent</i></a> ·
  Series 04: <a href="https://github.com/AlienMuse/fractured-adelic-geometry"><i>Fractured Adelic Geometry</i></a> ·
  Series 05: <a href="https://github.com/AlienMuse/the-archimedean-prism"><i>The Archimedean Prism</i></a><br>
  © 2026 Vincent Liu
</sub></p>
