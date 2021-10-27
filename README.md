# Hearth
An inviting place for interoperable reporting of medical imaging data.

Hearth aims to be an extensible, open source, interoperable medical imaging report creation tool.
Quantitative results from segmentation of medical images are defined using templates, relating image labels to definitions in medical ontologies such as SNOMED-CT.
The general nature of the templates allow for output into a variety of standard file formats.

## Overview
Our initial implementation builds off of [`fs2dicom`](https://github.com/corticometrics/fs2dicom), a tool to convert [FreeSurfer](https://surfer.nmr.mgh.harvard.edu/) outputs to DICOM.
`fs2dicom` creates DICOM-SEG images as well as a DICOM-SR representing volumetric measurements of the different structures in the SEG image.
Hearth extends this, creating FHIR JSON output of the same volumetric measures.

### Supported inputs and outputs
Hearth provides templates for FreeSurfer's `aseg` output as a proof of concept.
Creating new templates would allow any supported image to be processed.

#### Inputs
- .mgh (to DICOM-SEG)
- .nii (to DICOM-SEG)
- .nii.gz (to DICOM-SEG)
- FreeSurfer .stats files (to report output)

#### Outputs
- FHIR JSON DiagnosticReport resource
- DICOM-SR Template ID 1500 (TID 1500) Measurement Report


## Acknowledgments
This work has been funded by the following NIH grant:
- R43EB030910