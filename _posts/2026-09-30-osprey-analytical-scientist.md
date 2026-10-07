---
layout: post
title: "The Analytical Scientist Features Osprey and AI-Assisted Software Development in the MacCoss Lab"
date: 2026-09-30
categories: [interview, osprey, software, dia, ai]
---

*The Analytical Scientist* has published a feature article, ["Vibe Coding Moves Beyond the Proteomics Prototype"](https://theanalyticalscientist.com/issues/2026/articles/september/vibe-coding-moves-beyond-the-proteomics-prototype), describing how the MacCoss Lab used Claude to build and validate **Osprey**, a new open-source, peptide-centric search tool for data-independent acquisition (DIA) proteomics. The article includes interviews with Mike MacCoss and Brendan MacLean.

Osprey detects and scores peptides in DIA data, then writes out peak boundaries and a spectral library that Skyline reads directly. Mike built the original version entirely through natural-language prompting with Claude: roughly 30,000 functional lines of Rust plus about 12,000 lines of tests. Brendan then ported Osprey to C# for integration with ProteoWizard and Skyline, and neither of them typed a line of the code by hand.

The article focuses on what it takes to move AI-generated code past the prototype stage. An early translation looked convincing because identification counts matched, but deeper problems in the pipeline only surfaced weeks later. To catch issues like these, Brendan divided the pipeline into seven stages and compared the C# and Rust implementations at each one, moving on only when a stage produced virtually identical results. As Mike puts it, "Generating code is the easy part now. Knowing whether the code does what you asked is the hard part."

A key motivation for the project is reproducibility. Quantitative DIA analysis is currently dominated by closed-source tools, and Osprey is intended to provide a fully open alternative that integrates with the Skyline ecosystem.

Read the full article at [*The Analytical Scientist*](https://theanalyticalscientist.com/issues/2026/articles/september/vibe-coding-moves-beyond-the-proteomics-prototype), and find the Osprey source code on [GitHub](https://github.com/maccoss/osprey).
