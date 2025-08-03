---
layout: default
title: Resources
permalink: /resources/
---

# Resources

<div class="tab-container">
  <div class="tab-navigation">
    <button class="tab-button active" onclick="openTab(event, 'software')">Software</button>
    <button class="tab-button" onclick="openTab(event, 'datasets')">Datasets</button>
    <button class="tab-button" onclick="openTab(event, 'educational')">Educational Materials</button>
    <button class="tab-button" onclick="openTab(event, 'support')">Support & Training</button>
  </div>

  <div id="software" class="tab-content active">

## MacCoss Lab Software Tools

### Skyline
**Windows Client Tool for the visualization, analysis, and development of methods for quantitative mass spectrometry**
- **Free, open-source quantitative mass spectrometry software.** Skyline is a freely-available, open-source Windows client application for building Selected Reaction Monitoring (SRM) / Multiple Reaction Monitoring (MRM), Parallel Reaction Monitoring (PRM), Data Independent Acquisition (DIA/SWATH) and DDA with MS1 quantitative methods and analyzing the resulting mass spectrometer data. Its flexible configuration supports All Molecules. It aims to employ cutting-edge technologies for creating and iteratively refining targeted methods for large-scale quantitative mass spectrometry studies in life sciences.
- **Supports proteomics, metabolomics, and small molecule workflows.**
- **Vendor agnostic.** Can analyze data and generate methods for all major instrument vendors. Including Agilent, Bruker, Shimadzu, ThermoFisher, and Waters.
- **Download at**: [skyline.ms](https://skyline.ms/skyline.url)
- **External Tools**: Skyline has an external tool framework. We have a [tool store](http://skyline.ms/tools.url) with 20 tools currently available.
- **Source Code** is available as part of the [Proteowizard project](https://github.com/ProteoWizard/pwiz).

### Panorama
**Web-based repository for Skyline documents and colaboration**
- Panorama is a freely-available, open-source webserver for sharing experiments and validated assays that integrates into a Skyline proteomics workflow. Panorama can be installed on a local server, or you can request a project on the PanoramaWeb.org server, hosted by the MacCoss Lab at the University of Washington. Access privileges within a project may be customized, allowing you to control fully who has access to data you publish to Panorama.
- **Access**: [panoramaweb.org](https://panoramaweb.org)
- **Panorama Public**: One of six of the [ProteomeXchange](https://www.proteomexchange.org/) servers used by the proteomics community. Panorama Public simplifies the process of sharing datasets analyzed by [Skyline](https://skyline.ms/skyline.url).
- **Requirements**: Can be accessed within Skyline and from any modern browser (Chrome, Firefox, Safari, Edge)
- **Features**: Unique tools for data sharing, collaboration, quality control
- **API**: Programmatic access for automated workflows

### Limelight
**Open Source Server for the Analysis and Sharing of Data Dependent Acquisition Mass Spectrometry Results**
- Limelight is designed to provide you with the full-stack of proteomics results, regardless of which processing pipeline you used to search your data. Full-stack means that you have access to the global views of your data (such as statistically comparing conditions), to viewing lists of proteins and peptides, to individual PSMs and spectra–all showing the native scores from whichever pipeline you used. Additionally, all native scores from your pipeline are available to you for filtering–even when contrasting multiple searches that each used different pipelines.
- [Limelight](https://limelight.yeastrc.org/limelight/) can be installed locally or you can request an account on a server hosted at the University of Washington.
- Detailed documentation for using Limelight is available [here](https://limelight-ms.readthedocs.io/en/latest/#).
- **Source Code** is available on [GitHub](https://github.com/yeastrc/limelight-core).

### EncyclopeDIA
**Open source tool for peptide-centric analysis of data independent acquisition-mass spectrometry data**
- EncyclopeDIA is library search engine comprised of several algorithms for DIA data analysis and can search for peptides using either DDA-based spectrum libraries or DIA-based chromatogram libraries. Check out our manuscript describing EncyclopeDIA at Nature Communications ([Searle et al, 2018](https://www.nature.com/articles/s41467-018-07454-w)) for more information. EncyclopeDIA contains Walnut, an implementation of the PECAN ([Ting et al, 2017](https://www.nature.com/articles/nmeth.4390)) scoring system, to enable chromatogram library generation from FASTA protein sequence databases when spectrum libraries are unavailable. EncyclopeDIA also supports Prosit, a deep learning tool for generating peptide fragmentation spectra, as described in ([Searle et al, 2020](https://www.nature.com/articles/s41467-020-15346-1)). EncyclopeDIA also contains Thesaurus for localizing and quantifying PTMS with DIA experiments ([Searle et al, 2019]((https://www.nature.com/articles/s41592-019-0498-4)))

### Comet
**Comet is an open source fork of the original SEQUEST database tool for proteomics**
- Searching uninterpreted tandem mass spectra of peptides against sequence databases is the most common method used to identify peptides and proteins. Since this method was first developed in 1993, many commercial, free, and open source tools have been created over the years that accomplish this task. Although its history goes back two decades, the Comet search engine was first made publicly available in August 2012 on SourceForge under the Apache License, version 2.0. The repository was migrated to GitHub in September 2021.
- **Download and Documentation** are available on the UW Proteomics Resource [Github](https://uwpr.github.io/Comet/).
- **Support** is available via a [Google Groups](https://groups.google.com/g/comet-ms).
- **Source Code** is available on [GitHub](https://github.com/UWPR/Comet) under an Apache 2.0 license

  </div>

  <div id="datasets" class="tab-content">

## Public Datasets on [Panorama Public](http://panoramaweb.org/public.url)

**We have made available a number of mass spectrometry datasets on Panorama Public**

#### Recent Method Development & Instrumentation (2024-2025)

- **[Highly multiplex targeted proteomics assays using Stellar mass spectrometer](https://panoramaweb.org/project/Panorama%20Public/2025/MacCoss_MultiplexTargetedProteomics/begin.view?)** - Development of novel targeted proteomics methods for biofluids analysis (PXD065471)
- **[Orbitrap Astral Zoom prototype evaluation](https://panoramaweb.org/project/Panorama%20Public/2025/MacCoss_OrbitrapAstralZoom/begin.view?)** - Comprehensive evaluation of next-generation mass spectrometry instrumentation for quantitative proteomics (PXD064536)
- **[PRM Conductor tutorials](https://panoramaweb.org/project/Panorama%20Public/2025/MacCoss_PRMConductor/begin.view?)** - Educational materials and workflows for parallel reaction monitoring using Skyline external tools
- **[Carafe spectral library generation](https://panoramaweb.org/project/Panorama%20Public/2024/MacCoss_Carafe/begin.view?)** - Deep learning approach for high-quality in silico spectral libraries for DIA proteomics (PXD056793)
- **[Stellar MS characterization](https://panoramaweb.org/project/Panorama%20Public/2024/MacCoss_StellarMS/begin.view?)** - Complete characterization and benchmarking of the Stellar mass spectrometer platform (PXD052734)

#### Data Analysis & Computational Methods
- **[DIA to Triple Quad assay development](https://panoramaweb.org/project/Panorama%20Public/2025/MacCoss_DIAtoTripleQuad/begin.view?)** - Workflow for using data-independent acquisition to inform targeted assay development (PXD059611)
- **[Transformer model for DIA de novo sequencing](https://panoramaweb.org/project/Panorama%20Public/2024/MacCoss_TransformerDIA/begin.view?)** - AI-powered peptide sequencing from data-independent acquisition data (PXD053291)
- **[Quality control framework for proteomics](https://panoramaweb.org/project/Panorama%20Public/2024/MacCoss_QualityControl/begin.view?)** - Comprehensive guidelines and datasets for proteomics quality control (PXD051318)
- **[Dynamic DIA with real-time alignment](https://panoramaweb.org/project/Panorama%20Public/2023/MacCoss_DynamicDIA/begin.view?)** - Advanced data acquisition strategies for improved proteomics workflows (PXD038508)

#### Clinical & Biomedical Applications
- **[Drug-protein adduct detection in human liver](https://panoramaweb.org/project/Panorama%20Public/2024/MacCoss_DrugProteinAdducts/begin.view?)** - Novel methods for identifying covalent protein modifications from drug metabolism (PXD054246)
- **[Alzheimer's disease proteomics datasets](https://panoramaweb.org/project/Panorama%20Public/2024/MacCoss_AlzheimersProteomics/begin.view?)** - Multiple studies including peptide-centric quantitative proteomics for AD assessment (PXD034525, PXD025668)
- **[Apolipoprotein E isoform quantification](https://panoramaweb.org/project/Panorama%20Public/2023/MacCoss_ApoEIsoforms/begin.view?)** - Metrologically traceable measurements in cerebrospinal fluid (PXD038803)
- **[Mag-Net plasma proteome enrichment](https://panoramaweb.org/project/Panorama%20Public/2023/MacCoss_MagNetPlasma/begin.view?)** - Extracellular vesicle enrichment for enhanced plasma proteomics coverage (PXD042947)

#### Aging & Disease Research
- **[Mouse aging and neurodegeneration studies](https://panoramaweb.org/project/Panorama%20Public/2024/MacCoss_MouseAging/begin.view?)** - Comprehensive proteomics datasets from AD-BXD mouse models investigating hippocampus and prefrontal cortex (PXD045403, PXD045425)
- **[Skeletal muscle sarcopenia](https://panoramaweb.org/project/Panorama%20Public/2024/MacCoss_SkeletalMuscleSarcopenia/begin.view?)** - Proteomics analysis of age-related muscle changes in mouse models (PXD048723)
- **[Mouse heart aging studies](https://panoramaweb.org/project/Panorama%20Public/2023/MacCoss_MouseHeartAging/begin.view?)** - Age-related proteome and acetylome changes with therapeutic interventions (PXD027458, PXD024247)
- **[Drosophila aging metabolomics](https://panoramaweb.org/project/Panorama%20Public/2023/MacCoss_DrosophilaAging/begin.view?)** - Metabolome changes as biomarkers of aging in fruit fly models

#### Analytical Method Validation
- **[Glucagon and oxyntomodulin quantification](https://panoramaweb.org/project/Panorama%20Public/2024/MacCoss_GlucagonQuantification/begin.view?)** - LC-MS/MS method validation for peptide hormone analysis (PXD041410)
- **[FAIMS vs. quadrupole gas phase fractionation](https://panoramaweb.org/project/Panorama%20Public/2023/MacCoss_FAIMSvsQuadrupole/begin.view?)** - Comparative analysis of peptide separation techniques (PXD043458)
- **[Astral mass analyzer evaluation](https://panoramaweb.org/project/Panorama%20Public/2023/MacCoss_AstralEvaluation/begin.view?)** - Performance assessment for data-independent acquisition proteomics (PXD042704)
- **[Matrix-matched calibration curves](https://panoramaweb.org/project/Panorama%20Public/2022/MacCoss_MatrixMatchedCalibration/begin.view?)** - Standardization approaches for quantitative proteomics (PXD014815)

#### Large-Scale Community Resources
- **[LINCS phospho-proteomics datasets](https://panoramaweb.org/project/Panorama%20Public/2022/MacCoss_LINCSPhosphoproteomics/begin.view?)** - Chemical perturbation studies across multiple cell lines and conditions (PXD017458, PXD017459)
- **[Cancer proteomics inter-laboratory study](https://panoramaweb.org/project/Panorama%20Public/2022/MacCoss_CancerProteomics/begin.view?)** - Large-scale validation of multiplexed peptide assays for cancer biomarkers (>54 datasets)
- **[System suitability protocols](https://panoramaweb.org/project/Panorama%20Public/2021/MacCoss_SystemSuitability/begin.view?)** - Multi-site evaluation of LC-MRM-MS instrument performance standards (PXD010535)

#### Software & Workflow Development
- **[Skyline Batch processing](https://panoramaweb.org/project/Panorama%20Public/2022/MacCoss_SkylineBatch/begin.view?)** - User-friendly interfaces for high-throughput proteomics analysis (PXD029665, PXD029663)
- **[Limelight data sharing](https://panoramaweb.org/project/Panorama%20Public/2022/MacCoss_LimelightDataSharing/begin.view?)** - Open-source platforms for mass spectrometry data visualization and collaboration
- **[Small molecule analysis with Skyline](https://panoramaweb.org/project/Panorama%20Public/2021/MacCoss_SmallMoleculeSkyline/begin.view?)** - Metabolomics and lipidomics workflows using Skyline software

#### Specialized Applications
- **[Cross-linking mass spectrometry](https://panoramaweb.org/project/Panorama%20Public/2023/MacCoss_CrosslinkingMS/begin.view?)** - Protein-protein interaction studies using chemical cross-linking (PXD030871)
- **[Ion mobility spectrometry integration](https://panoramaweb.org/project/Panorama%20Public/2021/MacCoss_IonMobility/begin.view?)** - Multi-dimensional separation techniques for enhanced analysis (PXD010650)
- **[Post-translational modification analysis](https://panoramaweb.org/project/Panorama%20Public/2022/MacCoss_PTMAnalysis/begin.view?)** - Comprehensive PTM characterization in various biological systems
- **[Grizzly bear serum proteomics](https://panoramaweb.org/project/Panorama%20Public/2021/MacCoss_GrizzlyBearSerum/begin.view?)** - Wildlife proteomics applications demonstrating method versatility (PXD023555)

*All datasets include detailed experimental protocols, instrument settings, and analysis workflows. Many datasets are paired with published manuscripts and include both raw data and processed results accessible through Skyline.*

  </div>

  <div id="educational" class="tab-content">

## Educational Materials

### Skyline Webinars
**Interactive 90-minute tutorial webinars with Q&A sessions**

#### 2025
- **[#25: Comparing Acquisition Methods](https://skyline.ms/project/home/software/Skyline/events/2025%20Webinars/Webinar%2025/begin.view?)** (Jan 2025)

#### 2024
- **[#24: Skyline for Lipidomics](https://skyline.ms/project/home/software/Skyline/events/2024%20Webinars/Webinar%2024/begin.view?)** (Nov 2024)
- **[#23: Using Skyline Live Reports](https://skyline.ms/project/home/software/Skyline/events/2024%20Webinars/Webinar%2023/begin.view?)** (Sept 2024)

#### 2023 & 2021
- **[#22: Using DIA Data To Create SRM Methods](https://skyline.ms/project/home/software/Skyline/events/2023%20Webinars/Webinar%2022/begin.view?)** (Mar 2023)
- **[#21: Analysis of diaPASEF Data](https://skyline.ms/project/home/software/Skyline/events/2021%20Webinars/Webinar%2021/begin.view?)** (Dec 2021)
- **[#20: Using Skyline Batch for Large-Scale DIA](https://skyline.ms/project/home/software/Skyline/events/2021%20Webinars/Webinar%2020/begin.view?)** (July 2021)

#### 2020 & 2018
- **[#19: Ion Mobility Spectrum Filtering](https://skyline.ms/project/home/software/Skyline/events/2020%20Webinars/Webinar%2019/begin.view?)** (April 2020)
- **[#18: DIA Data Analysis Revisited](https://skyline.ms/project/home/software/Skyline/events/2020%20Webinars/Webinar%2018/begin.view?)** (April 2020)
- **[#17: PRM Method Dev and Data Analysis](https://skyline.ms/project/home/software/Skyline/events/2018%20Webinars/Webinar%2017/begin.view?)** (Jan 2018)

#### 2017 & 2016
- **[#16: Small Molecule Research](https://skyline.ms/project/home/software/Skyline/events/2017%20Webinars/Webinar%2016/begin.view?)** (Nov 2017)
- **[#15: Optimizing Large Scale DIA](https://skyline.ms/project/home/software/Skyline/events/2017%20Webinars/Webinar%2015/begin.view?)** (Apr 2017)
- **[#14: Large Scale DIA](https://skyline.ms/project/home/software/Skyline/events/2017%20Webinars/Webinar%2014/begin.view?)** (Jan 2017)

#### 2015
- **[#12: Isotope Labeled Standards](https://skyline.ms/project/home/software/Skyline/events/2015%20Webinars/Webinar%2012/begin.view?)** (Dec 2015)
- **[#11: Panorama and Panorama Public](https://skyline.ms/project/home/software/Skyline/events/2015%20Webinars/Webinar%2011/begin.view?)** (Oct 2015)
- **[#10: Working with Modifications](https://skyline.ms/project/home/software/Skyline/events/2015%20Webinars/Webinar%2010/begin.view?)** (Sep 2015)
- **[#9: PRM for PTM Studies](https://skyline.ms/project/home/software/Skyline/events/2015%20Webinars/Webinar%209/begin.view?)** (Aug 2015)

#### 2014
- **[#2: Jump Start DIA Analysis with DDA Data](https://skyline.ms/project/home/software/Skyline/events/2014%20Webinars/Webinar%202/begin.view?)** (Dec 2014)
- **[#1: Getting the Most Out of DDA Data](https://skyline.ms/project/home/software/Skyline/events/2014%20Webinars/Webinar%201/begin.view?)** (Nov 2014)

[**View all webinars**](https://skyline.ms/wiki/home/software/Skyline/page.view?name=webinars)

### Skyline Tutorials
**Hands-on tutorials with real data and step-by-step instructions**

#### Introductory
- **[Targeted Method Editing](https://skyline.ms/tutorial_method_edit.url)** (26 pages) - Learn the basics of creating and editing targeted methods
- **[Targeted Method Refinement](https://skyline.ms/tutorial_method_refine.url)** (28 pages) - Optimize your methods for better results
- **[Grouped Study Data Processing](https://skyline.ms/tutorial_grouped.url)** (70 pages) - Analyze grouped experimental data
- **[Existing & Quantitative Experiments](https://skyline.ms/tutorial_existing_quant.url)** (43 pages) - Work with existing data and quantitative analysis

#### Introduction to Full-Scan Acquisition Data
- **[Comparing PRM, DIA, and DDA](https://skyline.ms/tutorial_comp_acq.url)** (38 pages) - Compare different acquisition methods
- **[PRM With an Orbitrap](https://skyline.ms/tutorial_prm_orbi.url)** (44 pages) - Parallel reaction monitoring on Orbitrap instruments
- **[Basic Data Independent Acquisition](https://skyline.ms/tutorial_dia.url)** (40 pages) - Introduction to DIA analysis

#### Full-Scan Acquisition Data
- **[MS1 Full-Scan Filtering](https://skyline.ms/tutorial_ms1_filtering.url)** (41 pages) - Extract quantitative information from MS1 data
- **[DDA Search for MS1 Filtering](https://skyline.ms/tutorial_dda_search.url)** (19 pages) - Use DDA results to enhance MS1 analysis
- **[Parallel Reaction Monitoring (PRM)](https://skyline.ms/tutorial_prm.url)** (40 pages) - Comprehensive PRM workflow
- **[Analysis of DIA/SWATH Data](https://skyline.ms/tutorial_dia_swath.url)** (32 pages) - Process DIA and SWATH-MS data
- **[Analysis of diaPASEF Data](https://skyline.ms/tutorial_dia_pasef.url)** (36 pages) - Work with ion mobility DIA data
- **[Library-Free DIA/SWATH](https://skyline.ms/tutorial_dia_umpire_ttof.url)** (26 pages) - DIA analysis without spectral libraries

#### Small Molecules
- **[Small Molecule Targets](https://skyline.ms/tutorial_small_molecule.url)** (10 pages) - Basic small molecule analysis
- **[Small Molecule Method Development](https://skyline.ms/tutorial_small_method_ce.url)** (37 pages) - Develop targeted small molecule methods
- **[Small Mol. Multidimension Spec. Lib.](https://skyline.ms/tutorial_small_ims.url)** (23 pages) - Use ion mobility for small molecules
- **[Small Molecule Quantification](https://skyline.ms/tutorial_small_quant.url)** (27 pages) - Quantitative small molecule workflows
- **[Hi-Res Metabolomics](https://skyline.ms/tutorial_hi_res_metabolomics.url)** (17 pages) - High-resolution metabolomics analysis

#### Advanced Topics
- **[Absolute Quantification](https://skyline.ms/tutorial_absolute_quant.url)** (19 pages) - Calculate absolute protein concentrations
- **[Custom Reports](https://skyline.ms/tutorial_custom_reports.url)** (33 pages) - Create custom data reports
- **[Advanced Peak Picking Models](https://skyline.ms/tutorial_peak_picking.url)** (28 pages) - Optimize peak detection algorithms
- **[iRT Retention Time Prediction](https://skyline.ms/tutorial_irt.url)** (36 pages) - Use indexed retention times
- **[Collision Energy Optimization](https://skyline.ms/tutorial_optimize_ce.url)** (12 pages) - Optimize fragmentation conditions
- **[Ion Mobility Spectrum Filtering](https://skyline.ms/tutorial_ims.url)** (26 pages) - Advanced ion mobility analysis
- **[Spectral Library Explorer](https://skyline.ms/tutorial_library_explorer.url)** (22 pages) - Explore and manage spectral libraries
- **[Audit Logging](https://skyline.ms/tutorial_audit_log.url)** - Track document changes for compliance

[**View all tutorials**](https://skyline.ms/wiki/home/software/Skyline/page.view?name=tutorials)

### Skyline Videos
**Quick instructional videos for getting started**

- **[Video Demo 1: Creating SRM/MRM Methods](https://skyline.ms/labkey/wiki/home/software/Skyline/page.view?name=video_0-2)** (28 minutes) - Learn to create targeted methods
- **[Video Demo 2: Results Analysis and Method Refinement](https://skyline.ms/labkey/wiki/home/software/Skyline/page.view?name=video_0-5)** (25 minutes) - Analyze results and refine methods
- **[Video Demo 3: Importing Existing Experiments](https://skyline.ms/labkey/wiki/home/software/Skyline/page.view?name=video_0-5b)** (27 minutes) - Work with existing data and isotope standards
- **[Skyline Trailer Video](https://skyline.ms/labkey/wiki/home/software/Skyline/page.view?name=video_trailer)** - Overview of Skyline capabilities

[**View all videos**](https://skyline.ms/wiki/home/software/Skyline/page.view?name=videos)

### YouTube Channels
**Course content and instructional videos**

- **[Skyline Course at UW (2017 & 2018)](https://www.youtube.com/channel/UCOdJj3Spesm_U_2-N_FT7wg)** - University of Washington course materials
- **[May Institute at Northeastern University (2018-2020)](https://www.youtube.com/channel/UCnbUMFlIRLaY7fwfSintWuQ)** - Comprehensive proteomics course content
- **[Targeted Proteomics Course at ETH, Zurich (2016 & 2018)](https://www.youtube.com/channel/UCLLENascNxL22j3pntI7jVA/playlists)** - International course materials

[**View YouTube resources**](https://skyline.ms/wiki/home/software/Skyline/page.view?name=youtube)

### Skyline Tips
**Quick tips and troubleshooting guides**

- **Adduct Descriptions** - Understanding different adduct types
- **Working with Other Quantitative Tools** - Integration with external software
- **How to Display Multiple Peptides** - Visualization techniques
- **Terminology Cheat Sheet** - Key terms and definitions
- **How Skyline Builds Spectral Libraries** - Library construction process
- **ID Annotations Missing with Mascot Search Results** - Troubleshooting search imports
- **DIA Configuration for Thermo Q Exactive Instruments** - Instrument-specific settings
- **How Skyline Calculates Peak Areas and Heights** - Understanding quantification
- **Support for Bruker TOF Instruments** - Vendor-specific guidance
- **Recovering From a Broken Installation** - Troubleshooting installation issues
- **Sharing MS/MS Spectra with Manuscripts** - Publication guidelines
- **Share Skyline Documents in Manuscripts** - Document sharing best practices
- **Export SRM Methods for a Thermo LTQ** - Method export procedures
- **Skyline Lists** - Working with peptide and protein lists
- **Pivot Editor** - Advanced data manipulation
- **Result File Rules** - Managing multiple result files

[**View all tips**](https://skyline.ms/wiki/home/software/Skyline/page.view?name=tips)

### Panorama Documentation
**Comprehensive guides for using Panorama web-based repository**

#### Getting Started
- **Create a Folder in Panorama** - Set up project structure and organization
- **Folder Navigation in Panorama** - Navigate through project hierarchies
- **Adding Users to a Project** - Manage user access and permissions
- **Import Data Into Panorama** - Upload Skyline documents and results
- **Upload Raw Data** - Store mass spectrometry raw files
- **Upload Supplementary Files** - Include additional project materials

#### Data Management
- **Include Subfolders in Panorama Public Submission** - Organize complex datasets
- **Submit Data to Panorama Public** - Share data with the proteomics community
- **Data Validation for ProteomeXchange** - Ensure compliance with repository standards
- **Download Data From Panorama Public** - Access publicly available datasets
- **Finding Unimod matches** - Identify modification annotations

#### Advanced Features
- **Quality Control with AutoQC** - Automated instrument performance monitoring
- **[Document Version Tracking](https://www.labkey.org/Documentation/wiki-page.view?name=panoramaRevisionTrack)** - Track changes and document history
- **Adding Links in Wiki Pages** - Create interconnected documentation
- **Install Panorama** - Set up local Panorama installations

[**View all documentation**](https://panoramaweb.org/home/wiki-page.view?name=documentation) | [**LabKey Panorama Documentation**](https://www.labkey.org/Documentation/wiki-page.view?name=panorama)

### Panorama Tutorials
**Hands-on tutorials for Panorama workflows**

- **[Sharing Skyline Documents](https://panoramaweb.org/home/wiki-page.view?name=tutorials)** - Learn to upload and share Skyline documents in Panorama
- **[Panorama Chromatogram Libraries](https://panoramaweb.org/home/wiki-page.view?name=tutorials)** - Build and manage chromatogram libraries for DIA analysis
- **[Submit Data to Panorama Public](https://panoramaweb.org/home/wiki-page.view?name=tutorials)** - Complete workflow for making data publicly available

[**View all tutorials**](https://panoramaweb.org/home/wiki-page.view?name=tutorials)

### Panorama Webinars
**Educational webinars covering Panorama features and best practices**

#### Recent Webinars (2017-2021)
- **[System Suitability Best Practices with Skyline and Panorama](https://www.labkey.com/webinar/lc-ms-system-suitability-skyline-panorama/)** (June 29, 2021) - LabKey hosted webinar on QC workflows
- **[Introduction to Panorama](https://www.labkey.com/webinar/panorama-targeted-proteomics-research/)** (September 21, 2017) - LabKey hosted overview of Panorama capabilities

#### Skyline/Panorama Joint Webinars
- **[Panorama Public and Panorama AutoQC](https://brendanx-uw1.gs.washington.edu/labkey/project/home/software/Skyline/events/2015%20Webinars/Webinar%2011/begin.view?)** (October 20, 2015) - Skyline Tutorial Webinar #11

#### Historical Webinars (2013-2014)
- **[Panorama: Managing and Analyzing Large Datasets](https://www.youtube.com/watch?v=eZSoBU622Ws)** (August 19, 2014) - YouTube video
- **[Panorama targeted proteomics knowledge base](https://www.youtube.com/watch?v=YyPo0447VUM)** (August 8, 2013) - YouTube video

[**View all webinars**](https://panoramaweb.org/home/wiki-page.view?name=webinars)

  </div>

  <div id="support" class="tab-content">

## Support & Training

### Forums and Discussion
- [Skyline Support Board](https://skyline.ms/forum)
- [Panorama Support Board](https://panoramaweb.org/forum)

### Proteomics and Mass Spectrometry Courses
*Coming soon - comprehensive course listings and training opportunities*

  </div>
</div>

<style>
.tab-container {
  max-width: 100%;
}

.tab-navigation {
  display: flex;
  border-bottom: 2px solid #e0e0e0;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.tab-button {
  background-color: #f8f9fa;
  border: none;
  padding: 12px 24px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
  margin-right: 4px;
  margin-bottom: -2px;
  transition: all 0.3s ease;
  color: #333;
}

.tab-button:hover {
  background-color: #e9ecef;
  color: #0056b3;
}

.tab-button.active {
  background-color: #fff;
  border: 2px solid #e0e0e0;
  border-bottom: 2px solid #fff;
  color: #0056b3;
  font-weight: 600;
}

.tab-content {
  display: none;
  padding: 20px 0;
  animation: fadeIn 0.3s ease-in;
}

.tab-content.active {
  display: block;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
  .tab-navigation {
    flex-direction: column;
  }
  
  .tab-button {
    margin-right: 0;
    margin-bottom: 2px;
    border-radius: 4px;
  }
  
  .tab-button.active {
    border: 2px solid #0056b3;
  }
}
</style>

<script>
function openTab(evt, tabName) {
  var i, tabcontent, tablinks;
  
  // Hide all tab content
  tabcontent = document.getElementsByClassName("tab-content");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].classList.remove("active");
  }
  
  // Remove active class from all tab buttons
  tablinks = document.getElementsByClassName("tab-button");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].classList.remove("active");
  }
  
  // Show the selected tab content and mark button as active
  document.getElementById(tabName).classList.add("active");
  evt.currentTarget.classList.add("active");
  
  // Update URL hash without scrolling
  if (history.pushState) {
    history.pushState(null, null, '#' + tabName);
  } else {
    window.location.hash = '#' + tabName;
  }
}

// Handle initial load and hash changes
function handleHashChange() {
  var hash = window.location.hash.substring(1);
  var validTabs = ['software', 'datasets', 'educational', 'support'];
  
  if (hash && validTabs.includes(hash)) {
    // Find and click the corresponding tab button
    var buttons = document.getElementsByClassName('tab-button');
    for (var i = 0; i < buttons.length; i++) {
      if (buttons[i].getAttribute('onclick').includes(hash)) {
        buttons[i].click();
        break;
      }
    }
  }
}

// Listen for hash changes
window.addEventListener('hashchange', handleHashChange);

// Handle initial page load
document.addEventListener('DOMContentLoaded', function() {
  handleHashChange();
});
</script>

