---
name: pydicom
description: Use pydicom to read, inspect, write, transform, and safely preflight local DICOM datasets and pixel data. Applies to DICOM metadata, transfer syntaxes, compression plugins, frames, private elements, JSON, and bounded de-identification review.
---

# pydicom

Use pydicom for DICOM dataset I/O and pixel processing. Version 3.0.2 is the
current stable release reviewed here. It fixes CVE-2026-32711, a crafted
DICOMDIR path-traversal issue. pydicom 3.0.2 declares Python `>=3.10`; its
bundled DICOM dictionary is 2024c, while the live DICOM Standard may be newer.

## Mandatory safety boundary

- Work only with local data that the user is authorized to access.
- DICOM metadata, file names, private elements, overlays, structured content,
  and pixels may contain protected health information (PHI).
- Never print `Dataset`, export full metadata/JSON, or log element values by
  default. Use a documented allowlist and aggregate output.
- pydicom is a general DICOM framework, not a diagnostic viewer. Pixel output,
  validation, conversion, and plugin availability are not diagnostic claims.
- De-identification is profile-, purpose-, recipient-, jurisdiction-, and
  threat-context-specific. It requires privacy/DICOM expert verification.
- Never claim that a tag-removal script is DICOM PS3.15, HIPAA, GDPR, or other
  compliance. Preserve originals and audit derived outputs.
- Treat deterministic pseudonymization keys and UID maps as re-identification
  secrets: use least privilege and encrypted/managed secret storage, never
  commit, sync, log, or share them with derivatives, and define backup,
  rotation, revocation, and destruction procedures. A leaked key invalidates
  the intended separation; rotation also changes deterministic mappings.
- Set explicit input-file, file-count, frame-count, decoded-byte, and output
  limits before parsing untrusted or unusually large datasets.

## Installation

Create or activate an isolated environment, then install the exact reviewed
release:

```bash
uv pip install "pydicom==3.0.2"
```

Uncompressed pixel arrays and image rendering:

```bash
uv pip install "pydicom==3.0.2" "numpy==2.5.1" "Pillow==12.3.0"
```

Install only the transfer-syntax plugins required by the deployment:

```bash
# JPEG/JPEG-LS, JPEG 2000/HTJ2K, and faster RLE through pylibjpeg
uv pip install "numpy==2.5.1" "pylibjpeg==2.1.0" \
  "pylibjpeg-libjpeg==2.4.0" "pylibjpeg-openjpeg==2.5.0" \
  "pylibjpeg-rle==2.2.0"

# JPEG-LS encoder/decoder
uv pip install "numpy==2.5.1" "pyjpegls==1.5.1"

# Alternative decoder with platform-specific wheels
uv pip install "python-gdcm==3.2.6"
```

Plugin licenses and wheels differ by package/platform; review them before
deployment. Pillow has documented decoding limitations and pydicom cautions
that plugin output must be independently checked.

Native codec wheels widen the supply-chain and memory-safety boundary. For a
controlled deployment, resolve these exact pins on a trusted build host, lock
and verify wheel hashes/provenance, mirror approved artifacts internally, scan
them, and install with hash enforcement rather than resolving from the public
index at runtime.

## Choose the workflow

1. Need an aggregate overview: run `scripts/extract_metadata.py`.
2. Need bounded technical checks: run `scripts/dicom_inventory.py`.
3. Need codec deployment preflight: run
   `scripts/transfer_syntax_inspector.py`.
4. Need frame/memory planning: run `scripts/pixel_frame_planner.py`.
5. Need one non-diagnostic rendered frame: run
   `scripts/dicom_to_image.py`.
6. Need a pseudonymized derivative: read the de-identification section, create
   a site-reviewed action profile, then run `scripts/anonymize_dicom.py` and
   `scripts/deidentification_audit.py`.
7. Need to check a sensitive UID map: run
   `scripts/uid_mapping_validator.py`.

## Read datasets safely

`dcmread()` returns a `FileDataset`, a `Dataset` subclass with File Format
state such as `file_meta`, preamble, and original encoding.

```python
from pathlib import Path
import pydicom

path = Path("authorized/input.dcm")
ds = pydicom.dcmread(
    path,
    stop_before_pixels=True,
    specific_tags=[
        "SOPClassUID",
        "Modality",
        "Rows",
        "Columns",
        "NumberOfFrames",
    ],
)

technical = {
    "sop_class": ds.get("SOPClassUID"),
    "modality": ds.get("Modality"),
    "rows": ds.get("Rows"),
    "columns": ds.get("Columns"),
}
```

Use:

- `stop_before_pixels=True` for metadata-only work.
- `specific_tags=[...]` for a minimum allowlist.
- `defer_size="1 MiB"` when a later write must preserve large values.
- `force=False` (default). `force=True` only bypasses the File Format header
  check; it does not prove the bytes are valid DICOM.

Do not call `print(ds)`, `repr(ds)`, or iterate values into logs on clinical
data.

## Dataset, DataElement, and sequences

Access standard elements by keyword and check for absence:

```python
modality = ds.get("Modality", "UNSPECIFIED")
if "ReferencedImageSequence" in ds:
    for item in ds.ReferencedImageSequence:
        referenced_class = item.get("ReferencedSOPClassUID")
```

Tag access, such as `ds[0x0010, 0x0010]`, returns a `DataElement`; its `.value`
is separate. `Sequence` behaves like a list of nested `Dataset` items. Privacy
actions must recurse through every sequence item, not only the top level.

When creating a file, use `FileMetaDataset` for group `0002`, keep dataset and
file-meta SOP UIDs consistent, set a Transfer Syntax UID, and write in enforced
File Format:

```python
from pydicom import dcmwrite
from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.uid import CTImageStorage, ExplicitVRLittleEndian, generate_uid

meta = FileMetaDataset()
meta.MediaStorageSOPClassUID = CTImageStorage
meta.MediaStorageSOPInstanceUID = generate_uid()
meta.TransferSyntaxUID = ExplicitVRLittleEndian

ds = FileDataset(None, {}, file_meta=meta, preamble=b"\0" * 128)
ds.SOPClassUID = meta.MediaStorageSOPClassUID
ds.SOPInstanceUID = meta.MediaStorageSOPInstanceUID
# Add all attributes required by the selected IOD before writing.
dcmwrite("new.dcm", ds, enforce_file_format=True, overwrite=False)
```

`write_like_original` is deprecated in pydicom 3.0; use
`enforce_file_format`. A successful write is not full PS3.3 IOD conformance.

## UIDs and transfer syntax

The File Meta Information Transfer Syntax UID controls dataset encoding and
pixel compression:

```python
ts = ds.file_meta.TransferSyntaxUID
summary = {
    "uid": str(ts),
    "name": ts.name,
    "compressed": ts.is_compressed,
    "implicit_vr": ts.is_implicit_VR,
    "little_endian": ts.is_little_endian,
}
```

pydicom 3.0 chooses write encoding from the Transfer Syntax UID before legacy
dataset flags. Do not replace structural UIDs (Transfer Syntax, SOP Class, or
coding-scheme UIDs) during pseudonymization. Instance/reference UID replacement
must be one-to-one and consistent across the complete declared scope.

Read [references/transfer_syntaxes.md](references/transfer_syntaxes.md) before
compression, decompression, or encapsulation.

## Pixel data and frames

The stable `pydicom.pixels` API supports path-based, frame-specific decoding:

```python
from pydicom.pixels import pixel_array

# Reads only the selected frame where the source permits it.
frame = pixel_array("authorized/image.dcm", index=0, raw=False)
```

Shape semantics:

- grayscale single frame: `(rows, columns)`
- grayscale multi-frame: `(frames, rows, columns)`
- color single frame: `(rows, columns, samples)`
- color multi-frame: `(frames, rows, columns, samples)`

`raw=False` converts YCbCr pixel data to RGB when possible; `raw=True` retains
the decoded color space after mandatory minimal processing. Use
`iter_pixels(path, indices=[...])` for bounded multi-frame iteration.

For grayscale display, apply transforms in this order:

```python
from pydicom.pixels import apply_modality_lut, apply_voi_lut

modality_values = apply_modality_lut(frame, ds)
display_values = apply_voi_lut(modality_values, ds, index=0)
```

Modality LUT/rescale and VOI/windowing change display/value semantics.
MONOCHROME1 may require presentation inversion. Palette Color requires
`apply_color_lut()`. Presentation states and ICC behavior may require a
validated viewer. Never use per-frame min/max normalization for quantitative
analysis.

## Compression, decompression, and encapsulation

- Accessing `pixel_array` decodes as needed but does not change the dataset.
- `Dataset.decompress()` changes Pixel Data in place, sets Explicit VR Little
  Endian, updates image metadata, and generates a new SOP Instance UID by
  default.
- `Dataset.compress(uid)` changes Pixel Data and Transfer Syntax in place and
  generates a new SOP Instance UID by default.
- pydicom 3.0 built-in/found encoders cover RLE Lossless, JPEG-LS, and JPEG
  2000 combinations documented in the stable plugin matrix.
- Each compressed frame is separately encoded and then encapsulated. Use
  `encapsulate()` or `encapsulate_extended()` for externally encoded frames.
- Read frames with current `pydicom.encaps.generate_frames()` or `get_frame()`;
  legacy encapsulation generator names are deprecated for pydicom 4.

Always inspect capabilities first, limit decoded bytes/frames, and verify pixel
correctness independently. Lossy compression acceptability is outside pydicom
and the DICOM encoding specification.

## DICOM JSON and private elements

`Dataset.to_json()`, `to_json_dict()`, and `Dataset.from_json()` implement the
DICOM JSON Model, but pydicom documents JSON support as beta. Full JSON may
inline binary data and expose every identifier and pixel payload. Do not emit
it as a metadata report. A `BulkDataURI` handler introduces separate storage,
authorization, and retrieval obligations.

Private elements are not standardized and may contain PHI:

```python
# Recursive removal, but not sufficient de-identification by itself.
ds.remove_private_tags()
```

Retain private elements only under an explicit reviewed safe-private policy.
Read [references/common_tags.md](references/common_tags.md) for tag access,
privacy classes, and standard pointers.

## De-identification workflow

DICOM PS3.15 Annex E explicitly states that confidentiality profiles do not
guarantee removal of all identifying information and do not replace a complete
de-identification process.

1. Define purpose, recipients, linkage needs, regulations, threat model, and
   acceptable re-identification risk.
2. Select the Basic Application Level Confidentiality Profile and needed
   options (pixel, recognizable visual features, graphics, structured content,
   descriptors, temporal information, patient characteristics, devices,
   institutions, UIDs, and safe private data).
3. Preserve source objects unchanged in controlled storage.
4. Apply every action recursively, including nested sequences.
5. Replace instance/reference UIDs consistently across the complete scope;
   preserve structural UIDs.
6. Decide date/time handling explicitly. A fixed shift can preserve intervals
   but partial dates, time zones, standalone times, leap days, longitudinal
   linkage, and external events require reviewed policy.
7. Inspect pixels, overlays, graphics, structured content, and recognizable
   visual features. Do not infer clean pixels from missing metadata or set
   `BurnedInAnnotation=NO` without verification.
8. Rebuild File Meta Information and preamble to prevent leakage.
9. Run technical validation and a de-identification audit, then perform expert
   verification and documented risk review.

The bundled script intentionally sets `PatientIdentityRemoved` to `NO` because
it cannot establish successful de-identification.

## Helper CLIs

All `--help` paths are dependency-free. The tools perform no network access and
emit no DICOM values beyond narrow technical allowlists.

Bundled content consists of the two linked references, the documented helper
scripts, and synthetic tests. The pydicom runtime dependency is installed from
the pinned PyPI release.

```bash
# Redacted aggregate metadata
python scripts/extract_metadata.py authorized/ --recursive

# Metadata-only technical inventory
python scripts/dicom_inventory.py authorized/ --recursive

# Installed codec/plugin capabilities
python scripts/transfer_syntax_inspector.py --input authorized/image.dcm

# Frame shape, byte, and transform plan
python scripts/pixel_frame_planner.py authorized/image.dcm --frames 0,2-4

# One non-diagnostic frame
python scripts/dicom_to_image.py authorized/image.dcm frame.png \
  --acknowledge-pixel-phi

# Create a secret key, then a scoped pseudonymized derivative plus audit
python scripts/anonymize_dicom.py --generate-uid-key project.key
python scripts/anonymize_dicom.py authorized/in.dcm derived/out.dcm \
  --uid-key-file project.key --uid-scope export-v1 \
  --audit-report derived/out.audit.json

# Audit candidate metadata; no pixel decompression
python scripts/deidentification_audit.py derived/out.dcm

# Validate an explicitly requested sensitive UID mapping
python scripts/uid_mapping_validator.py derived/uid-map.json \
  --uid-key-file project.key --uid-scope export-v1
```

The generated raw key file is a controlled-local convenience and is created
with owner-only permissions. For production, materialize key bytes from an
approved secret manager into a locked ephemeral file, restrict access to the
de-identification service, and securely remove it afterward. Store any optional
UID map separately from derivatives; it directly links original and replacement
identifiers.

## pydicom 3.0 migration notes

- `read_file()` and `write_file()` were removed; use `dcmread()` and
  `dcmwrite()`.
- `write_like_original` is deprecated; use `enforce_file_format`.
- `pydicom.pixel_data_handlers` is deprecated for removal in v4; use
  `pydicom.pixels`.
- `Dataset.pixel_array` uses the new pixels backend by default and converts
  YCbCr to RGB when possible.
- `JPEGLossless` now means UID `1.2.840.10008.1.2.4.57`;
  `JPEGLosslessSV1` is `.70`.
- `Dataset.is_little_endian` and `is_implicit_VR` are deprecated for v4.

## Sources (verified 2026-07-23)

- [pydicom 3.0.2 on PyPI](https://pypi.org/project/pydicom/) — released
  2026-03-19; Python `>=3.10`.
- [pydicom releases](https://github.com/pydicom/pydicom/releases) — 3.0.2 and
  CVE-2026-32711 details.
- [Stable release notes](https://pydicom.github.io/pydicom/stable/release_notes/index.html)
- [Stable installation guide](https://pydicom.github.io/pydicom/stable/tutorials/installation.html)
- [Dataset basics](https://pydicom.github.io/pydicom/stable/tutorials/dataset_basics.html)
- [Stable pixel tutorial](https://pydicom.github.io/pydicom/stable/tutorials/pixel_data/introduction.html)
- [Stable pixel plugins](https://pydicom.github.io/pydicom/stable/guides/user/image_data_handlers.html)
- [Stable compression tutorial](https://pydicom.github.io/pydicom/stable/tutorials/pixel_data/compressing.html)
- [Stable DICOM JSON tutorial](https://pydicom.github.io/pydicom/stable/tutorials/dicom_json.html)
- [Stable private-element guide](https://pydicom.github.io/pydicom/stable/guides/user/private_data_elements.html)
- [Current DICOM Standard](https://www.dicomstandard.org/current)
- [DICOM PS3.3](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/PS3.3.html),
  [PS3.5](https://dicom.nema.org/medical/dicom/current/output/chtml/part05/PS3.5.html),
  [PS3.6](https://dicom.nema.org/medical/dicom/current/output/chtml/part06/PS3.6.html),
  and [PS3.15](https://dicom.nema.org/medical/dicom/current/output/html/part15.html)

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/pydicom/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/common_tags.md`

# DICOM data elements, tags, and privacy review

This is a working guide, not a complete DICOM dictionary or an attribute
confidentiality profile. pydicom 3.0.2 bundles the 2024c public dictionary; use
the live DICOM PS3.3/PS3.6 and the selected IOD when correctness depends on a
newer edition.

## Privacy boundary

DICOM metadata and pixels may contain PHI. Do not print a complete `Dataset`,
serialize the full dataset to JSON, or copy arbitrary values into logs. Tag
names that appear technical can still identify a person through site-specific
values, free text, private data, UIDs, dates, devices, or linkage with external
records.

DICOM PS3.15 Annex E says that applying attribute actions does not guarantee
that the Information Object is de-identified. A valid workflow must select a
profile/options for its context and include expert verification and
re-identification risk review.

## pydicom access model

```python
from pydicom import dcmread
from pydicom.tag import Tag

ds = dcmread(
    "authorized/input.dcm",
    stop_before_pixels=True,
    specific_tags=["SOPClassUID", "Modality", "Rows", "Columns"],
)

modality = ds.get("Modality", "UNSPECIFIED")
element = ds.get_item(Tag(0x0008, 0x0016))
```

- Keyword access (`ds.Modality`) returns the value and raises `AttributeError`
  when absent.
- `ds.get("Modality", default)` is safer for optional elements.
- Tag indexing (`ds[0x0008, 0x0016]`) returns a `DataElement`; read `.value`
  only when authorized.
- A tag consists of a 16-bit group and 16-bit element.
- Standard public tags generally use even groups. Private data uses odd groups
  and private creator blocks.
- `Dataset` contains `DataElement` objects. A value with VR `SQ` is a
  `Sequence` of nested `Dataset` items.

## Narrow technical allowlist

The following values are commonly useful for bounded technical inventory.
They do not make an entire record safe to disclose.

| Tag | Keyword | VR | Technical use |
|---|---|---|---|
| (0008,0016) | SOPClassUID | UI | Identifies the standardized SOP Class |
| (0008,0060) | Modality | CS | Modality code |
| (0002,0010) | TransferSyntaxUID | UI | File encoding/compression |
| (0028,0002) | SamplesPerPixel | US | Samples per pixel |
| (0028,0004) | PhotometricInterpretation | CS | Pixel color/monochrome interpretation |
| (0028,0006) | PlanarConfiguration | US | Color sample layout |
| (0028,0008) | NumberOfFrames | IS | Declared frames |
| (0028,0010) | Rows | US | Rows per frame |
| (0028,0011) | Columns | US | Columns per frame |
| (0028,0100) | BitsAllocated | US | Storage bits per sample |
| (0028,0101) | BitsStored | US | Meaningful bits per sample |
| (0028,0102) | HighBit | US | Highest stored bit |
| (0028,0103) | PixelRepresentation | US | Unsigned (0) or signed (1) |
| (0028,0301) | BurnedInAnnotation | CS | Declared burned-in annotation status |
| (0028,0302) | RecognizableVisualFeatures | CS | Declared recognizable-feature status |
| (0028,2110) | LossyImageCompression | CS | Whether lossy compression occurred |

`BurnedInAnnotation=NO` is a declaration, not proof that pixels are clean.
Absence, `YES`, or another value requires review. Even `NO` does not address
recognizable facial/anatomic features or matching against source images.

## Instance, relationship, and spatial elements

These values are technically important but can enable linkage or reveal
individual context. Do not emit them in default reports.

| Tag | Keyword | Privacy/semantic concern |
|---|---|---|
| (0008,0018) | SOPInstanceUID | Instance identifier; may support linkage |
| (0020,000D) | StudyInstanceUID | Study-level linkage |
| (0020,000E) | SeriesInstanceUID | Series-level linkage |
| (0020,0052) | FrameOfReferenceUID | Spatial/reference linkage |
| (0008,1155) | ReferencedSOPInstanceUID | Cross-instance relationship |
| (0020,0032) | ImagePositionPatient | Patient-coordinate position |
| (0020,0037) | ImageOrientationPatient | Patient-coordinate orientation |
| (0028,0030) | PixelSpacing | Physical sample spacing |
| (0018,0050) | SliceThickness | Nominal reconstructed thickness |
| (0018,0088) | SpacingBetweenSlices | Center-to-center spacing when defined |

Do not sort a series only by `SliceLocation` or assume `SliceThickness` equals
inter-slice spacing. Reconstruct geometry from the applicable IOD, orientation,
position, frame functional groups, and validated series membership.

## Direct and quasi-identifiers

The following examples are not exhaustive. PS3.15 Table E.1-1 and the chosen
options control action selection, including nested occurrences.

| Tag | Keyword | Typical risk |
|---|---|---|
| (0010,0010) | PatientName | Direct identifier |
| (0010,0020) | PatientID | Direct/local identifier |
| (0010,0021) | IssuerOfPatientID | Identifier namespace |
| (0010,0030) | PatientBirthDate | Date/quasi-identifier |
| (0010,0032) | PatientBirthTime | Time/quasi-identifier |
| (0010,0040) | PatientSex | Patient characteristic |
| (0010,1010) | PatientAge | Patient characteristic |
| (0010,1020) | PatientSize | Patient characteristic |
| (0010,1030) | PatientWeight | Patient characteristic |
| (0010,1040) | PatientAddress | Direct identifier |
| (0010,2154) | PatientTelephoneNumbers | Direct identifier |
| (0010,4000) | PatientComments | Free text |
| (0008,0050) | AccessionNumber | Order/study linkage |
| (0020,0010) | StudyID | Local study identifier |
| (0040,1001) | RequestedProcedureID | Order linkage |
| (0040,0009) | ScheduledProcedureStepID | Workflow linkage |
| (0008,0090) | ReferringPhysicianName | Person identifier |
| (0008,1050) | PerformingPhysicianName | Person identifier |
| (0008,1070) | OperatorsName | Person identifier |
| (0008,0080) | InstitutionName | Organization identifier |
| (0008,0081) | InstitutionAddress | Organization/location identifier |
| (0008,1010) | StationName | Device/site identifier |
| (0018,1000) | DeviceSerialNumber | Device identifier |
| (0008,1030) | StudyDescription | Potential free text |
| (0008,103E) | SeriesDescription | Potential free text |
| (0018,1030) | ProtocolName | Site/user-entered text |

Required IOD type matters. A PS3.15 action can remove (`X`), zero (`Z`),
replace with a valid dummy value (`D`), replace a UID consistently (`U`), keep
(`K`), or clean (`C`), with conditional combinations. Blind deletion can make
an instance non-conformant.

## Dates and times

Common date/time elements include:

| Tag | Keyword | VR |
|---|---|---|
| (0008,0012) | InstanceCreationDate | DA |
| (0008,0013) | InstanceCreationTime | TM |
| (0008,0020) | StudyDate | DA |
| (0008,0030) | StudyTime | TM |
| (0008,0021) | SeriesDate | DA |
| (0008,0031) | SeriesTime | TM |
| (0008,0022) | AcquisitionDate | DA |
| (0008,0032) | AcquisitionTime | TM |
| (0008,002A) | AcquisitionDateTime | DT |
| (0008,0023) | ContentDate | DA |
| (0008,0033) | ContentTime | TM |

VR syntax:

- `DA`: `YYYYMMDD`
- `TM`: `HHMMSS.FFFFFF` with permitted truncation
- `DT`: `YYYYMMDDHHMMSS.FFFFFF&ZZXX` with permitted truncation

Date/time handling is not solved by replacing every value with a constant.
Review:

- whether full dates or modified dates are allowed by the selected PS3.15
  option;
- one consistent shift across the intended longitudinal scope;
- leap days, range limits, partial precision, time zones, and midnight
  crossings;
- standalone `TM` values that cannot be shifted safely without a paired date;
- interval preservation and external event linkage;
- IOD Type 1/2 requirements and scientific utility.

Record the policy and caveats without logging original values.

## UIDs: replace instance relationships, not semantics

UID VR is `UI`, but not every UID is an identifier to pseudonymize.

Usually structural/semantic and preserved:

- Transfer Syntax UID
- SOP Class UID and Referenced SOP Class UID
- coding/context/template UIDs defined by standards
- implementation UID handling according to rebuilt File Meta Information

Often instance/reference linkage requiring profile-directed, consistent
replacement:

- Study, Series, SOP Instance, and Frame of Reference UIDs
- Referenced SOP Instance UIDs in sequences
- synchronization, concatenation, tracking, specimen, and transaction UIDs

Use one-to-one replacement over the declared scope. A keyed deterministic
mapping can maintain consistency, but the key/map is sensitive. Replacing UIDs
does not itself prevent pixel or metadata matching and must not create false
confidence.

## Sequences and recursive traversal

Identifiers may occur at any nesting depth:

```python
def visit(dataset):
    for element in dataset:
        if element.VR == "SQ":
            for item in element.value:
                visit(item)
        else:
            review(element.tag, element.keyword, element.VR)
```

Bound recursion depth and total elements for untrusted files. Do not print
values from the callback. pydicom's `Dataset.walk()` is also recursive by
default, and `remove_private_tags()` uses recursive traversal.

## Private data

Private elements use odd group numbers and a private creator block. Their
semantics are vendor-defined and names may be unknown or non-unique. Access by
tag or `PrivateBlock`, not by the descriptive display name.

```python
private_count = sum(1 for element in ds.iterall() if element.tag.is_private)
```

`Dataset.remove_private_tags()` recursively removes private elements, but:

- private removal alone is not de-identification;
- standard elements, sequences, pixels, graphics, and overlays still matter;
- some private elements may be scientifically necessary;
- the PS3.15 Retain Safe Private Option requires evidence that retained
  elements are safe and removal/processing of all others.

Default to remove or reject private data. Explicit retention needs a reviewed
allowlist and provenance.

## Pixel, graphics, and structured content

Potential identifying content is not limited to `(7FE0,0010) PixelData`:

- Float/Double Float Pixel Data
- overlays in repeating `60xx` groups
- retired curves in `50xx` groups
- presentation-state graphics and annotations
- Structured Report text/content items
- waveforms, encapsulated documents, spectra, and other bulk content
- full-face images and recognizable head/neck reconstructions

The PS3.15 Clean Pixel Data, Clean Recognizable Visual Features, Clean
Graphics, and Clean Structured Content options address different risks.
Human review may be required, and cleaning can impair utility.

## DICOM JSON

`Dataset.to_json()` and `to_json_dict()` preserve DICOM element content.
Binary data is either base64 `InlineBinary` or represented by `BulkDataURI`.
Therefore:

- JSON is not a safe metadata summary;
- full JSON can contain the same PHI as the source dataset;
- a bulk-data handler must enforce storage and retrieval authorization;
- pydicom 3.0.2 documents JSON support as beta.

Use `scripts/extract_metadata.py` for allowlisted aggregate inventory.

## Sources (verified 2026-07-23)

- [pydicom 3.0.2 dataset basics](https://pydicom.github.io/pydicom/stable/tutorials/dataset_basics.html)
- [pydicom core elements](https://pydicom.github.io/pydicom/stable/guides/user/base_element.html)
- [pydicom private elements](https://pydicom.github.io/pydicom/stable/guides/user/private_data_elements.html)
- [pydicom DICOM JSON tutorial](https://pydicom.github.io/pydicom/stable/tutorials/dicom_json.html)
- [DICOM PS3.3 2026c, Information Object Definitions](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/PS3.3.html)
- [DICOM PS3.3 Image Pixel Module](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.7.6.3.html)
- [DICOM PS3.5, Data Structures and Encoding](https://dicom.nema.org/medical/dicom/current/output/chtml/part05/PS3.5.html)
- [DICOM PS3.5 private elements](https://dicom.nema.org/medical/dicom/current/output/chtml/part05/sect_7.8.2.html)
- [DICOM PS3.6, Data Dictionary](https://dicom.nema.org/medical/dicom/current/output/chtml/part06/PS3.6.html)
- [DICOM PS3.15 2026c, Annex E confidentiality profiles](https://dicom.nema.org/medical/dicom/current/output/html/part15.html)

### `references/transfer_syntaxes.md`

# Transfer syntaxes, pixel plugins, and encapsulation

Transfer Syntax UID `(0002,0010)` identifies the encoding rules for the
dataset, including VR encoding, byte order, and pixel compression. This guide
targets stable pydicom 3.0.2. Always use the applicable DICOM PS3.5/PS3.6 and
the deployment's conformance statements for interoperability decisions.

## Inspect before decoding

```python
from pydicom import dcmread

ds = dcmread(
    "authorized/image.dcm",
    stop_before_pixels=True,
    specific_tags=[
        "Rows",
        "Columns",
        "NumberOfFrames",
        "SamplesPerPixel",
        "BitsAllocated",
        "BitsStored",
        "PhotometricInterpretation",
    ],
)
ts = ds.file_meta.TransferSyntaxUID
technical = {
    "uid": str(ts),
    "name": ts.name,
    "compressed": ts.is_compressed,
    "implicit_vr": ts.is_implicit_VR,
    "little_endian": ts.is_little_endian,
}
```

Do not infer decoder support from the UID name. Run:

```bash
python scripts/transfer_syntax_inspector.py --input authorized/image.dcm
python scripts/pixel_frame_planner.py authorized/image.dcm --frames 0
```

Plugin availability is not proof that a particular codestream, bit depth,
color representation, or platform is handled correctly.

## Native and dataset-compressed transfer syntaxes

| Name | UID | Encoding | pydicom constant |
|---|---|---|---|
| Implicit VR Little Endian | 1.2.840.10008.1.2 | implicit VR, little endian | `ImplicitVRLittleEndian` |
| Explicit VR Little Endian | 1.2.840.10008.1.2.1 | explicit VR, little endian | `ExplicitVRLittleEndian` |
| Deflated Explicit VR Little Endian | 1.2.840.10008.1.2.1.99 | deflated dataset | `DeflatedExplicitVRLittleEndian` |
| Explicit VR Big Endian | 1.2.840.10008.1.2.2 | explicit VR, big endian; retired | `ExplicitVRBigEndian` |

Explicit VR Big Endian was retired in 2006 and should not be selected for new
objects. pydicom can read it, but endianness conversion when writing is not an
automatic `Dataset.save_as()` operation.

The default DICOM network Transfer Syntax is Implicit VR Little Endian. This is
not a recommendation to omit File Meta Information from files.

## Encapsulated image transfer syntaxes

| Family | Name | UID | Loss |
|---|---|---|---|
| JPEG | JPEG Baseline 8-bit | 1.2.840.10008.1.2.4.50 | lossy |
| JPEG | JPEG Extended 12-bit | 1.2.840.10008.1.2.4.51 | lossy |
| JPEG | JPEG Lossless Process 14 | 1.2.840.10008.1.2.4.57 | lossless |
| JPEG | JPEG Lossless Process 14 SV1 | 1.2.840.10008.1.2.4.70 | lossless |
| JPEG-LS | JPEG-LS Lossless | 1.2.840.10008.1.2.4.80 | lossless |
| JPEG-LS | JPEG-LS Near-Lossless | 1.2.840.10008.1.2.4.81 | near-lossless |
| JPEG 2000 | JPEG 2000 Lossless Only | 1.2.840.10008.1.2.4.90 | lossless |
| JPEG 2000 | JPEG 2000 | 1.2.840.10008.1.2.4.91 | lossless or lossy in DICOM; pydicom encoding treats it as lossy |
| HTJ2K | HTJ2K Lossless | 1.2.840.10008.1.2.4.201 | lossless |
| HTJ2K | HTJ2K RPCL Lossless | 1.2.840.10008.1.2.4.202 | lossless |
| HTJ2K | HTJ2K | 1.2.840.10008.1.2.4.203 | lossy/lossless by syntax rules |
| RLE | RLE Lossless | 1.2.840.10008.1.2.5 | lossless |

In pydicom 3.0, `JPEGLossless` is `.57`; use `JPEGLosslessSV1` for `.70`.

Video, JPIP-referenced, encapsulated uncompressed, JPEG XL, and other current
DICOM transfer syntaxes exist but are not all decoded by pydicom's pixel API.
Consult PS3.6 and the installed `get_decoder()` result instead of assuming that
all registered UIDs are supported.

## Stable 3.0.2 decompression plugins

The stable pydicom matrix reports these main choices:

| Transfer-syntax family | Typical pydicom plugin dependencies |
|---|---|
| Native/deflated | pydicom + NumPy |
| RLE Lossless | built-in pydicom; `pylibjpeg-rle`; GDCM |
| JPEG Baseline/Extended | `pylibjpeg-libjpeg`; GDCM; Pillow with JPEG support |
| JPEG Lossless | `pylibjpeg-libjpeg`; GDCM |
| JPEG-LS | `pyjpegls`; `pylibjpeg-libjpeg`; GDCM |
| JPEG 2000 | `pylibjpeg-openjpeg`; GDCM; Pillow with OpenJPEG |
| HTJ2K | `pylibjpeg-openjpeg` |

Pinned reviewed installations:

```bash
uv pip install "pydicom==3.0.2" "numpy==2.5.1"

uv pip install "pylibjpeg==2.1.0" \
  "pylibjpeg-libjpeg==2.4.0" \
  "pylibjpeg-openjpeg==2.5.0" \
  "pylibjpeg-rle==2.2.0"

uv pip install "pyjpegls==1.5.1"
uv pip install "Pillow==12.3.0"
uv pip install "python-gdcm==3.2.6"
```

Install only what is required. Review transitive/package licensing:
`pylibjpeg-libjpeg` has different licensing from MIT pydicom.

Important stable documentation limitations include:

- Pillow performs transformations that pydicom describes as not always
  reversible and is not the preferred general decoder.
- Pillow JPEG Extended support requires 8 Bits Allocated.
- Pillow JPEG 2000 multi-sample support is constrained by bit depth.
- GDCM has syntax/bit-depth limits; pydicom rejects known incorrect JPEG-LS
  combinations for older GDCM releases.
- `pylibjpeg-openjpeg` and other plugins have their own maximum bit depths.
- pydicom's built-in RLE implementation is slower than compiled alternatives.

Never silently fall back in a validated workflow. Pin a plugin explicitly with
`decoding_plugin=...`, record versions, and compare results against independent
test vectors.

## Frame-specific decoding

Stable pydicom 3.0 adds path-based APIs that can reduce memory use:

```python
from pydicom.pixels import iter_pixels, pixel_array

first = pixel_array("authorized/multiframe.dcm", index=0)

for frame in iter_pixels(
    "authorized/multiframe.dcm",
    indices=[0, 2, 4],
):
    process_bounded_frame(frame)
```

Always calculate limits from:

- Rows and Columns
- Samples per Pixel
- Bits Allocated and decoded NumPy item size
- Number of Frames
- expected intermediate arrays for rescale/window/color conversion

The compressed file size is not a safe proxy for decoded memory. Metadata can
also disagree with the codestream.

Default decoding performs mandatory pixel unpacking and may convert YCbCr to
RGB. `raw=True` suppresses optional color conversion, not mandatory processing
such as bit unpacking.

## Decoder and encoder introspection

```python
from pydicom.pixels import get_decoder, get_encoder
from pydicom.uid import JPEG2000Lossless

decoder = get_decoder(JPEG2000Lossless)
decoder_report = {
    "available": decoder.is_available,
    "plugins": decoder.available_plugins,
    "missing": decoder.missing_dependencies,
}

try:
    encoder = get_encoder(JPEG2000Lossless)
except NotImplementedError:
    encoder = None
```

`is_available` means at least one implementation is importable. It does not
guarantee support for every image or correctness of output.

## In-place decompression behavior

```python
from pydicom import dcmread

ds = dcmread("compressed.dcm")
ds.decompress(
    decoding_plugin="pylibjpeg",
    generate_instance_uid=True,
)
```

`Dataset.decompress()`:

- decodes and replaces Pixel Data in the dataset;
- updates image-pixel metadata as needed;
- sets Transfer Syntax UID to Explicit VR Little Endian;
- generates a new SOP Instance UID by default;
- may convert YCbCr to RGB by default (`as_rgb=False` controls this).

This is a semantic modification. Write to a new file, keep source provenance,
and use `enforce_file_format=True, overwrite=False`.

## Compression behavior

pydicom 3.0.2 directly exposes dataset compression for:

- RLE Lossless (built-in pydicom and optional plugins)
- JPEG-LS Lossless/Near-Lossless (`pyjpegls`)
- JPEG 2000 Lossless/JPEG 2000 (`pylibjpeg-openjpeg`)

```python
from pydicom import dcmread, dcmwrite
from pydicom.uid import RLELossless

ds = dcmread("uncompressed.dcm")
ds.compress(
    RLELossless,
    encoding_plugin="pydicom",
    generate_instance_uid=True,
)
dcmwrite("rle-derived.dcm", ds, enforce_file_format=True, overwrite=False)
```

Compression:

- replaces Pixel Data with an encapsulated codestream;
- updates Transfer Syntax UID;
- generates a new SOP Instance UID by default;
- requires Image Pixel attributes consistent with the encoded stream.

Lossy compression decisions and clinical acceptability are outside pydicom and
PS3.5. Record method, ratio, derivation, and quality effects according to the
applicable IOD/workflow.

## Encapsulation rules

For encapsulated Pixel Data:

- each frame is compressed separately;
- frame codestreams are encapsulated into fragments;
- Pixel Data VR is `OB`;
- the dataset is explicit VR little endian at the dataset-structure level;
- a Basic Offset Table may be empty;
- Extended Offset Table/Lengths can locate large/multi-fragment frames.

Access existing encapsulated data:

```python
from pydicom.encaps import generate_frames, get_frame

frame0 = get_frame(
    ds.PixelData,
    0,
    number_of_frames=int(ds.get("NumberOfFrames", 1)),
)

for encoded_frame in generate_frames(
    ds.PixelData,
    number_of_frames=int(ds.get("NumberOfFrames", 1)),
):
    inspect_bounded_codestream(encoded_frame)
```

Create encapsulated Pixel Data from externally encoded frame bytes:

```python
from pydicom.encaps import encapsulate_extended

pixel_data, offsets, lengths = encapsulate_extended(encoded_frames)
ds.PixelData = pixel_data
ds.ExtendedOffsetTable = offsets
ds.ExtendedOffsetTableLengths = lengths
ds["PixelData"].VR = "OB"
```

Set a matching Transfer Syntax UID and consistent Image Pixel metadata.
`get_frame_offsets()`, `generate_pixel_data_frame()`, and other legacy
encapsulation helpers are deprecated for removal in pydicom 4; use
`parse_basic_offsets()`, `generate_fragments()`,
`generate_fragmented_frames()`, and `generate_frames()`.

## Writing and transfer-syntax conversion

pydicom 3.0 resolves encoding in this priority:

1. File Meta Information Transfer Syntax UID
2. explicit `implicit_vr`/`little_endian` arguments
3. deprecated dataset encoding flags
4. original encoding

```python
from pydicom import dcmwrite

dcmwrite(
    "derived.dcm",
    ds,
    enforce_file_format=True,
    overwrite=False,
)
```

Changing only `TransferSyntaxUID` does not compress/decompress Pixel Data.
Likewise, `Dataset.save_as()` does not automatically convert between little and
big endian. Use the documented pixel and writer APIs, then validate the
derived instance.

## Validation checklist

- Transfer Syntax UID is present, valid, and matches the encoded dataset.
- SOP Class/Instance UIDs match File Meta Information.
- Rows, Columns, Samples per Pixel, Bits Allocated/Stored, High Bit, Pixel
  Representation, Photometric Interpretation, Planar Configuration, and
  Number of Frames match the codestream.
- Decoder/encoder plugin and version are recorded.
- Frame count and decompressed memory are bounded before decode.
- Lossy/lossless status and derivation attributes are correct.
- Derived SOP Instance UID/provenance behavior is intentional.
- Pixel values, frame order, color, signedness, modality transform, and VOI are
  independently verified.
- No diagnostic or conformance conclusion is based only on pydicom success.

## Sources (verified 2026-07-23)

- [pydicom 3.0.2 pixel plugin matrix](https://pydicom.github.io/pydicom/stable/guides/user/image_data_handlers.html)
- [pydicom 3.0.2 Pixel Data API](https://pydicom.github.io/pydicom/stable/reference/pixels.html)
- [Pixel access tutorial](https://pydicom.github.io/pydicom/stable/tutorials/pixel_data/introduction.html)
- [Compression/decompression tutorial](https://pydicom.github.io/pydicom/stable/tutorials/pixel_data/compressing.html)
- [pydicom 3.0 release notes](https://pydicom.github.io/pydicom/stable/release_notes/index.html)
- [DICOM PS3.3 Image Pixel Module](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.7.6.3.html)
- [DICOM PS3.5, Data Structures and Encoding](https://dicom.nema.org/medical/dicom/current/output/chtml/part05/PS3.5.html)
- [DICOM PS3.5 encapsulated pixel transfer syntaxes](https://dicom.nema.org/medical/dicom/current/output/chtml/part05/sect_A.4.html)
- [DICOM PS3.6, Data Dictionary and UID registry](https://dicom.nema.org/medical/dicom/current/output/chtml/part06/PS3.6.html)
- PyPI versions reviewed 2026-07-23:
  [pydicom](https://pypi.org/project/pydicom/),
  [NumPy](https://pypi.org/project/numpy/),
  [Pillow](https://pypi.org/project/Pillow/),
  [pylibjpeg](https://pypi.org/project/pylibjpeg/),
  [pylibjpeg-libjpeg](https://pypi.org/project/pylibjpeg-libjpeg/),
  [pylibjpeg-openjpeg](https://pypi.org/project/pylibjpeg-openjpeg/),
  [pylibjpeg-rle](https://pypi.org/project/pylibjpeg-rle/),
  [pyjpegls](https://pypi.org/project/pyjpegls/), and
  [python-gdcm](https://pypi.org/project/python-gdcm/)

### `scripts/__init__.py`

```python
"""Local-only bounded helper CLIs for the pydicom skill."""
```

### `scripts/_common.py`

```python
"""Shared, dependency-light safety helpers for the pydicom skill CLIs."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import stat
import sys
import tempfile
from collections import Counter
from collections.abc import Callable, Iterable, Mapping
from pathlib import Path, PurePath
from typing import Any

SCHEMA_VERSION = "1.1"
PYDICOM_VERSION = "3.0.2"
NUMPY_VERSION = "2.5.1"
PILLOW_VERSION = "12.3.0"

KIB = 1024
MIB = 1024**2
GIB = 1024**3
DEFAULT_MAX_INPUT_BYTES = 512 * MIB
HARD_MAX_INPUT_BYTES = 16 * GIB
DEFAULT_MAX_OUTPUT_BYTES = 512 * MIB
HARD_MAX_OUTPUT_BYTES = 16 * GIB
DEFAULT_MAX_DECOMPRESSED_BYTES = 256 * MIB
HARD_MAX_DECOMPRESSED_BYTES = 4 * GIB
DEFAULT_MAX_FILES = 1_000
HARD_MAX_FILES = 100_000
DEFAULT_MAX_ELEMENTS = 200_000
HARD_MAX_ELEMENTS = 2_000_000
DEFAULT_MAX_FRAMES = 1_000
HARD_MAX_FRAMES = 1_000_000
MAX_JSON_BYTES = 8 * MIB
MAX_REPORT_BYTES = 32 * MIB
MAX_SEQUENCE_DEPTH = 64

_URI_PREFIXES = (
    "http:",
    "https:",
    "ftp:",
    "file:",
    "s3:",
    "gs:",
    "ssh:",
    "data:",
)
_SIZE_PATTERN = re.compile(r"^\s*(\d+)\s*(B|KIB|MIB|GIB)?\s*$", re.IGNORECASE)
_UID_PATTERN = re.compile(r"^[0-9]+(?:\.[0-9]+)*$")
_SAFE_PLUGIN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")

TEXT_VRS = frozenset(
    {
        "AE",
        "AS",
        "CS",
        "DA",
        "DT",
        "LO",
        "LT",
        "PN",
        "SH",
        "ST",
        "TM",
        "UC",
        "UI",
        "UR",
        "UT",
    }
)

# These are structural or coding UIDs, not instance identifiers. They must not be
# replaced merely because their VR is UI.
STRUCTURAL_UID_KEYWORDS = frozenset(
    {
        "AffectedSOPClassUID",
        "CodingSchemeUID",
        "ContextGroupExtensionCreatorUID",
        "ContextGroupLocalVersion",
        "DeviceUID",
        "ImplementationClassUID",
        "MediaStorageSOPClassUID",
        "PrivateInformationCreatorUID",
        "ReferencedSOPClassUID",
        "RelatedGeneralSOPClassUID",
        "RequestedSOPClassUID",
        "SOPClassUID",
        "TransferSyntaxUID",
    }
)

UID_REMAP_KEYWORDS = frozenset(
    {
        "AcquisitionUID",
        "ConcatenationUID",
        "ContrastBolusAgentNumber",
        "DimensionOrganizationUID",
        "DoseReferenceUID",
        "FiducialUID",
        "FrameOfReferenceUID",
        "IrradiationEventUID",
        "MediaStorageSOPInstanceUID",
        "ObservationUID",
        "ReferencedDoseReferenceUID",
        "ReferencedFiducialsUID",
        "ReferencedFrameOfReferenceUID",
        "ReferencedGeneralPurposeScheduledProcedureStepTransactionUID",
        "ReferencedObservationUID",
        "ReferencedSOPInstanceUID",
        "SeriesInstanceUID",
        "SOPInstanceUID",
        "SpecimenUID",
        "StorageMediaFileSetUID",
        "StudyInstanceUID",
        "SynchronizationFrameOfReferenceUID",
        "TemplateExtensionCreatorUID",
        "TemplateExtensionOrganizationUID",
        "TrackingUID",
        "TransactionUID",
        "TreatmentPositionGroupUID",
        "TreatmentSessionUID",
        "UID",
    }
)

# A conservative starter profile. It is intentionally not represented as a
# DICOM PS3.15 conformance implementation.
DEFAULT_ACTIONS: dict[str, str] = {
    "AccessionNumber": "empty",
    "AcquisitionContextSequence": "remove",
    "AcquisitionComments": "remove",
    "AdmittingDiagnosesCodeSequence": "remove",
    "AdmittingDiagnosesDescription": "remove",
    "Allergies": "remove",
    "ClinicalTrialProtocolID": "remove",
    "ClinicalTrialProtocolName": "remove",
    "ClinicalTrialSiteID": "remove",
    "ClinicalTrialSiteName": "remove",
    "ClinicalTrialSponsorName": "remove",
    "ClinicalTrialSubjectID": "pseudonym",
    "ClinicalTrialSubjectReadingID": "pseudonym",
    "ContentSequence": "remove",
    "CurrentPatientLocation": "remove",
    "DataSetTrailingPadding": "remove",
    "DeidentificationMethod": "remove",
    "DeidentificationMethodCodeSequence": "remove",
    "DerivationDescription": "remove",
    "DeviceSerialNumber": "remove",
    "DigitalSignaturesSequence": "remove",
    "DocumentTitle": "remove",
    "EncryptedAttributesSequence": "remove",
    "EncapsulatedDocument": "remove",
    "EncapsulatedDocumentLength": "remove",
    "EthnicGroup": "remove",
    "FillerOrderNumberImagingServiceRequest": "empty",
    "GraphicAnnotationSequence": "remove",
    "HL7InstanceIdentifier": "remove",
    "IconImageSequence": "remove",
    "ImageComments": "remove",
    "InstitutionAddress": "remove",
    "InstitutionCodeSequence": "remove",
    "InstitutionName": "remove",
    "InstitutionalDepartmentName": "remove",
    "InsurancePlanIdentification": "remove",
    "IssuerOfAccessionNumberSequence": "remove",
    "IssuerOfAdmissionID": "remove",
    "IssuerOfPatientID": "remove",
    "IssuerOfPatientIDQualifiersSequence": "remove",
    "MACParametersSequence": "remove",
    "MedicalAlerts": "remove",
    "MedicalRecordLocator": "remove",
    "MilitaryRank": "remove",
    "MIMETypeOfEncapsulatedDocument": "remove",
    "NameOfPhysiciansReadingStudy": "remove",
    "Occupation": "remove",
    "OperatorsIdentificationSequence": "remove",
    "OperatorsName": "remove",
    "OriginalAttributesSequence": "remove",
    "OtherPatientIDs": "remove",
    "OtherPatientIDsSequence": "remove",
    "OtherPatientNames": "remove",
    "PatientAddress": "remove",
    "PatientAge": "remove",
    "PatientBirthName": "remove",
    "PatientComments": "remove",
    "PatientID": "pseudonym",
    "PatientInsurancePlanCodeSequence": "remove",
    "PatientMotherBirthName": "remove",
    "PatientName": "pseudonym",
    "PatientReligiousPreference": "remove",
    "PatientSex": "remove",
    "PatientSize": "remove",
    "PatientState": "remove",
    "PatientTelephoneNumbers": "remove",
    "PatientWeight": "remove",
    "PerformedLocation": "remove",
    "PerformedProcedureStepDescription": "remove",
    "PerformedStationAETitle": "remove",
    "PerformedStationGeographicLocationCodeSequence": "remove",
    "PerformedStationName": "remove",
    "PerformingPhysicianIdentificationSequence": "remove",
    "PerformingPhysicianName": "remove",
    "PersonAddress": "remove",
    "PersonIdentificationCodeSequence": "remove",
    "PersonName": "remove",
    "PersonTelephoneNumbers": "remove",
    "PhysiciansOfRecord": "remove",
    "PhysiciansOfRecordIdentificationSequence": "remove",
    "PhysiciansReadingStudyIdentificationSequence": "remove",
    "PlacerOrderNumberImagingServiceRequest": "empty",
    "ProtocolName": "remove",
    "ReasonForImagingServiceRequest": "remove",
    "ReasonForRequestedProcedure": "remove",
    "ReferringPhysicianAddress": "remove",
    "ReferringPhysicianIdentificationSequence": "remove",
    "ReferringPhysicianName": "remove",
    "ReferringPhysicianTelephoneNumbers": "remove",
    "RegionOfResidence": "remove",
    "RequestAttributesSequence": "remove",
    "RequestedProcedureComments": "remove",
    "RequestedProcedureDescription": "remove",
    "RequestedProcedureID": "empty",
    "RequestingPhysician": "remove",
    "RequestingService": "remove",
    "ResponsibleOrganization": "remove",
    "ResponsiblePerson": "remove",
    "ResponsiblePersonRole": "remove",
    "ScheduledPerformingPhysicianIdentificationSequence": "remove",
    "ScheduledPerformingPhysicianName": "remove",
    "ScheduledProcedureStepDescription": "remove",
    "ScheduledProcedureStepID": "empty",
    "SeriesDescription": "remove",
    "ServiceEpisodeDescription": "remove",
    "ServiceEpisodeID": "remove",
    "SmokingStatus": "remove",
    "SpecialNeeds": "remove",
    "SpecimenAccessionNumber": "remove",
    "SpecimenIdentifier": "remove",
    "StationName": "remove",
    "StudyDescription": "remove",
    "StudyID": "empty",
    "TextComments": "remove",
    "TextString": "remove",
    "TextValue": "remove",
    "UnformattedTextValue": "remove",
    "AudioComments": "remove",
    "AudioSampleData": "remove",
}

SENSITIVE_KEYWORDS = frozenset(
    set(DEFAULT_ACTIONS)
    | {
        "PatientBirthDate",
        "PatientBirthTime",
        "PatientIdentityRemoved",
        "StudyDate",
        "StudyTime",
        "SeriesDate",
        "SeriesTime",
        "AcquisitionDate",
        "AcquisitionTime",
        "AcquisitionDateTime",
        "ContentDate",
        "ContentTime",
        "InstanceCreationDate",
        "InstanceCreationTime",
        *UID_REMAP_KEYWORDS,
    }
)

TECHNICAL_KEYWORDS = (
    "SOPClassUID",
    "Modality",
    "Rows",
    "Columns",
    "NumberOfFrames",
    "SamplesPerPixel",
    "PhotometricInterpretation",
    "PlanarConfiguration",
    "BitsAllocated",
    "BitsStored",
    "HighBit",
    "PixelRepresentation",
    "PixelSpacing",
    "RescaleSlope",
    "RescaleIntercept",
    "RescaleType",
    "WindowCenter",
    "WindowWidth",
    "VOILUTFunction",
    "BurnedInAnnotation",
    "RecognizableVisualFeatures",
    "LossyImageCompression",
)


class ToolError(ValueError):
    """Expected validation, dependency, or bounded local-I/O failure."""


def bounded_int(value: Any, *, name: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool):
        raise ToolError(f"{name} must be an integer")
    try:
        result = int(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ToolError(f"{name} must be an integer") from exc
    if not minimum <= result <= maximum:
        raise ToolError(f"{name} must be between {minimum} and {maximum}")
    return result


def parse_size(
    value: str | int,
    *,
    name: str,
    minimum: int = 1,
    maximum: int = HARD_MAX_INPUT_BYTES,
) -> int:
    if isinstance(value, int):
        result = value
    elif isinstance(value, str):
        match = _SIZE_PATTERN.fullmatch(value)
        if not match:
            raise ToolError(f"{name} must be an integer byte count or B/KiB/MiB/GiB")
        result = int(match.group(1))
        unit = (match.group(2) or "B").upper()
        result *= {"B": 1, "KIB": KIB, "MIB": MIB, "GIB": GIB}[unit]
    else:
        raise ToolError(f"{name} must be a byte-size string")
    return bounded_int(result, name=name, minimum=minimum, maximum=maximum)


def require_text(
    value: Any, *, name: str, minimum: int = 1, maximum: int = 1_000
) -> str:
    if not isinstance(value, str) or not minimum <= len(value) <= maximum:
        raise ToolError(f"{name} must be a string of length {minimum}..{maximum}")
    if any(ord(character) < 32 for character in value):
        raise ToolError(f"{name} must not contain control characters")
    return value


def safe_plugin_name(value: str) -> str:
    if not _SAFE_PLUGIN.fullmatch(value):
        raise ToolError("decoding plugin name is invalid")
    return value


def _reject_path_text(value: str) -> None:
    stripped = value.strip()
    lowered = stripped.casefold()
    if not stripped or "\x00" in value or stripped.startswith("~"):
        raise ToolError("path must be nonempty, local, and contain no NUL")
    if "://" in lowered or lowered.startswith(_URI_PREFIXES):
        raise ToolError("only local filesystem paths are accepted")
    if ".." in PurePath(stripped).parts:
        raise ToolError("parent traversal is not accepted")


def _absolute(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path)))


def _reject_symlink_components(path: Path) -> None:
    absolute = _absolute(path)
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current /= part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise ToolError("a path component could not be inspected") from exc
        if stat.S_ISLNK(mode):
            raise ToolError("symlink path components are not accepted")


def checked_root(value: str | os.PathLike[str]) -> Path:
    raw = os.fspath(value)
    _reject_path_text(raw)
    candidate = _absolute(Path(raw))
    _reject_symlink_components(candidate)
    try:
        resolved = candidate.resolve(strict=True)
        info = resolved.stat()
    except OSError as exc:
        raise ToolError("root directory is not accessible") from exc
    if not stat.S_ISDIR(info.st_mode):
        raise ToolError("root must be a directory")
    return resolved


def _within_root(path: Path, root: Path) -> None:
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ToolError("path escapes the declared root") from exc


def checked_input(
    value: str | os.PathLike[str],
    *,
    root: str | os.PathLike[str] = ".",
    kind: str = "file",
    max_bytes: int = DEFAULT_MAX_INPUT_BYTES,
) -> Path:
    raw = os.fspath(value)
    _reject_path_text(raw)
    root_path = checked_root(root)
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = root_path / candidate
    candidate = _absolute(candidate)
    _reject_symlink_components(candidate)
    try:
        resolved = candidate.resolve(strict=True)
        info = resolved.stat()
    except OSError as exc:
        raise ToolError("input path is not accessible") from exc
    _within_root(resolved, root_path)
    if kind == "file" and not stat.S_ISREG(info.st_mode):
        raise ToolError("input must be a regular file")
    if kind == "dir" and not stat.S_ISDIR(info.st_mode):
        raise ToolError("input must be a directory")
    if kind == "any" and not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)):
        raise ToolError("input must be a regular file or directory")
    if stat.S_ISREG(info.st_mode):
        if info.st_nlink != 1:
            raise ToolError("multiply linked input files are not accepted")
        if not 0 <= info.st_size <= max_bytes:
            raise ToolError("input file exceeds the configured byte limit")
    return resolved


def checked_output(
    value: str | os.PathLike[str],
    *,
    root: str | os.PathLike[str] = ".",
    force: bool = False,
) -> Path:
    raw = os.fspath(value)
    _reject_path_text(raw)
    root_path = checked_root(root)
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = root_path / candidate
    candidate = _absolute(candidate)
    _reject_symlink_components(candidate)
    parent = candidate.parent
    try:
        parent = parent.resolve(strict=True)
    except OSError as exc:
        raise ToolError("output parent directory must already exist") from exc
    _within_root(parent, root_path)
    destination = parent / candidate.name
    if destination.exists():
        if destination.is_symlink() or not destination.is_file():
            raise ToolError("existing output is not a regular file")
        if not force:
            raise ToolError("refusing to overwrite existing output")
    return destination


def checked_output_directory(
    value: str | os.PathLike[str],
    *,
    root: str | os.PathLike[str] = ".",
) -> Path:
    raw = os.fspath(value)
    _reject_path_text(raw)
    root_path = checked_root(root)
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = root_path / candidate
    candidate = _absolute(candidate)
    _reject_symlink_components(candidate)
    parent = candidate.parent
    try:
        parent = parent.resolve(strict=True)
    except OSError as exc:
        raise ToolError("output directory parent must already exist") from exc
    _within_root(parent, root_path)
    destination = parent / candidate.name
    if destination.exists():
        if destination.is_symlink() or not destination.is_dir():
            raise ToolError("existing destination is not a regular directory")
    else:
        try:
            destination.mkdir(mode=0o700)
        except OSError as exc:
            raise ToolError("output directory could not be created") from exc
    return destination.resolve(strict=True)


def paths_overlap(first: Path, second: Path) -> bool:
    first = first.resolve(strict=False)
    second = second.resolve(strict=False)
    return first == second or first in second.parents or second in first.parents


def collect_local_files(
    source: Path,
    *,
    max_files: int,
    max_bytes: int,
    recursive: bool = True,
) -> list[Path]:
    bounded_int(max_files, name="max_files", minimum=1, maximum=HARD_MAX_FILES)
    if source.is_file():
        return [source]
    files: list[Path] = []
    stack = [source]
    while stack:
        directory = stack.pop()
        try:
            entries = sorted(
                os.scandir(directory), key=lambda entry: entry.name.casefold()
            )
        except OSError as exc:
            raise ToolError("input directory cannot be scanned") from exc
        for entry in entries:
            try:
                if entry.is_symlink():
                    raise ToolError("symlinks in input directories are rejected")
                if entry.is_dir(follow_symlinks=False):
                    if recursive:
                        stack.append(Path(entry.path))
                    continue
                if not entry.is_file(follow_symlinks=False):
                    continue
                path = Path(entry.path).resolve(strict=True)
                info = path.stat()
                if info.st_nlink != 1:
                    raise ToolError("multiply linked input files are rejected")
                if info.st_size > max_bytes:
                    raise ToolError("an input file exceeds the configured byte limit")
                files.append(path)
                if len(files) > max_files:
                    raise ToolError("input file-count limit exceeded")
            except OSError as exc:
                raise ToolError(
                    "an input directory entry could not be inspected"
                ) from exc
    return sorted(files, key=lambda path: path.as_posix().casefold())


def _reject_json_constant(value: str) -> None:
    raise ToolError(f"non-finite JSON number is not accepted: {value}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ToolError(f"duplicate JSON key is not accepted: {key}")
        result[key] = value
    return result


def load_json(path: Path, *, max_bytes: int = MAX_JSON_BYTES) -> Any:
    if path.stat().st_size > max_bytes:
        raise ToolError("JSON input exceeds the configured byte limit")
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(
                handle,
                object_pairs_hook=_unique_object,
                parse_constant=_reject_json_constant,
            )
    except ToolError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ToolError("input is not valid bounded UTF-8 JSON") from exc


def json_bytes(document: Any) -> bytes:
    try:
        payload = (
            json.dumps(
                document,
                allow_nan=False,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n"
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ToolError("report cannot be serialized as strict JSON") from exc
    if len(payload) > MAX_REPORT_BYTES:
        raise ToolError("report exceeds the hard report-size limit")
    return payload


def emit_json(document: Any) -> None:
    sys.stdout.buffer.write(json_bytes(document))


def fail_json(tool: str, exc: Exception) -> int:
    message = (
        str(exc)[:500]
        if isinstance(exc, ToolError)
        else f"operation failed ({type(exc).__name__})"
    )
    emit_json(
        {
            "error": type(exc).__name__,
            "message": message,
            "ok": False,
            "tool": tool,
        }
    )
    return 2


def atomic_write(
    destination: Path,
    payload: bytes,
    *,
    force: bool = False,
    max_bytes: int = MAX_REPORT_BYTES,
) -> None:
    if len(payload) > max_bytes:
        raise ToolError("generated output exceeds the configured byte limit")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o600)
        if destination.exists() and not force:
            raise ToolError("refusing to overwrite existing output")
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)


def atomic_generated_file(
    destination: Path,
    *,
    writer: Callable[[Path], None],
    validator: Callable[[Path], None] | None = None,
    force: bool = False,
    max_bytes: int = HARD_MAX_OUTPUT_BYTES,
) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.",
        suffix=destination.suffix or ".tmp",
        dir=destination.parent,
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        os.chmod(temporary, 0o600)
        writer(temporary)
        info = temporary.stat()
        if not stat.S_ISREG(info.st_mode) or info.st_size > max_bytes:
            raise ToolError("generated output exceeds the configured byte limit")
        if validator is not None:
            validator(temporary)
        with temporary.open("rb") as handle:
            os.fsync(handle.fileno())
        if destination.exists() and not force:
            raise ToolError("refusing to overwrite existing output")
        os.replace(temporary, destination)
    except ToolError:
        raise
    except Exception as exc:
        raise ToolError("generated output could not be safely written") from exc
    finally:
        temporary.unlink(missing_ok=True)


def require_pydicom() -> Any:
    try:
        import pydicom
    except ImportError as exc:
        raise ToolError(
            f"pydicom is required; install with: uv pip install pydicom=={PYDICOM_VERSION}"
        ) from exc
    if pydicom.__version__ != PYDICOM_VERSION:
        raise ToolError(
            f"this skill is verified with pydicom=={PYDICOM_VERSION}; "
            f"found {pydicom.__version__}"
        )
    return pydicom


def require_pixel_stack() -> tuple[Any, Any, Any]:
    pydicom = require_pydicom()
    try:
        import numpy
        from PIL import Image
    except ImportError as exc:
        raise ToolError(
            "pixel conversion requires pinned NumPy and Pillow; install with: "
            f"uv pip install pydicom=={PYDICOM_VERSION} "
            f"numpy=={NUMPY_VERSION} Pillow=={PILLOW_VERSION}"
        ) from exc
    return pydicom, numpy, Image


def safe_dcmread(
    path: Path,
    *,
    stop_before_pixels: bool,
    force: bool = False,
    defer_size: str | int | None = None,
    specific_tags: Iterable[str | int] | None = None,
) -> Any:
    pydicom = require_pydicom()
    try:
        return pydicom.dcmread(
            path,
            defer_size=defer_size,
            stop_before_pixels=stop_before_pixels,
            force=force,
            specific_tags=list(specific_tags) if specific_tags is not None else None,
        )
    except Exception as exc:
        raise ToolError("DICOM input could not be parsed") from exc


def element_tag(element: Any) -> str:
    return f"({int(element.tag.group):04X},{int(element.tag.element):04X})"


def valid_uid(value: Any) -> bool:
    if not isinstance(value, str) or not 1 <= len(value) <= 64:
        return False
    if not _UID_PATTERN.fullmatch(value):
        return False
    return all(
        component == "0" or not component.startswith("0")
        for component in value.split(".")
    )


def derive_uid(original: str, *, key: bytes, scope: str) -> str:
    if not valid_uid(original):
        raise ToolError("an instance UID selected for remapping is invalid")
    digest = hmac.new(
        key,
        b"pydicom-skill-uid-v1\0"
        + scope.encode("utf-8")
        + b"\0"
        + original.encode("ascii"),
        hashlib.sha256,
    ).digest()[:16]
    number = int.from_bytes(digest, "big") or 1
    result = f"2.25.{number}"
    if not valid_uid(result):
        raise ToolError("derived UID is invalid")
    return result


def derive_token(value: str, *, key: bytes, scope: str, length: int = 24) -> str:
    digest = hmac.new(
        key,
        b"pydicom-skill-token-v1\0"
        + scope.encode("utf-8")
        + b"\0"
        + value.encode("utf-8", errors="surrogatepass"),
        hashlib.sha256,
    ).hexdigest()
    return digest[:length].upper()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def frame_count(dataset: Any) -> tuple[int, list[str]]:
    warnings: list[str] = []
    raw = dataset.get("NumberOfFrames", 1)
    try:
        count = int(raw)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ToolError("NumberOfFrames is not an integer") from exc
    if count == 0:
        warnings.append("NumberOfFrames is zero; pydicom treats it as one")
        count = 1
    if count < 1:
        raise ToolError("NumberOfFrames must be positive")
    return count, warnings


def pixel_plan(
    dataset: Any,
    *,
    max_frames: int = HARD_MAX_FRAMES,
    max_decompressed_bytes: int = HARD_MAX_DECOMPRESSED_BYTES,
) -> dict[str, Any]:
    rows = bounded_int(dataset.get("Rows"), name="Rows", minimum=1, maximum=1_000_000)
    columns = bounded_int(
        dataset.get("Columns"), name="Columns", minimum=1, maximum=1_000_000
    )
    samples = bounded_int(
        dataset.get("SamplesPerPixel", 1),
        name="SamplesPerPixel",
        minimum=1,
        maximum=256,
    )
    frames, warnings = frame_count(dataset)
    bounded_int(frames, name="NumberOfFrames", minimum=1, maximum=max_frames)
    if "DoubleFloatPixelData" in dataset:
        bits_allocated = 64
        pixel_element = "DoubleFloatPixelData"
    elif "FloatPixelData" in dataset:
        bits_allocated = 32
        pixel_element = "FloatPixelData"
    else:
        bits_allocated = bounded_int(
            dataset.get("BitsAllocated"),
            name="BitsAllocated",
            minimum=1,
            maximum=64,
        )
        pixel_element = "PixelData"
    pixels_per_frame = rows * columns * samples
    packed_bytes_per_frame = (pixels_per_frame * bits_allocated + 7) // 8
    decoded_item_bytes = (
        1
        if bits_allocated <= 8
        else 2
        if bits_allocated <= 16
        else 4
        if bits_allocated <= 32
        else 8
    )
    bytes_per_frame = pixels_per_frame * decoded_item_bytes
    total_bytes = bytes_per_frame * frames
    if total_bytes > max_decompressed_bytes:
        raise ToolError(
            "estimated decompressed pixel data exceeds the configured limit"
        )
    if frames > 1:
        shape = (
            [frames, rows, columns]
            if samples == 1
            else [frames, rows, columns, samples]
        )
    else:
        shape = [rows, columns] if samples == 1 else [rows, columns, samples]
    return {
        "bits_allocated": bits_allocated,
        "bytes_per_frame": bytes_per_frame,
        "columns": columns,
        "estimated_decompressed_bytes": total_bytes,
        "frames": frames,
        "native_packed_bytes_per_frame": packed_bytes_per_frame,
        "pixel_element": pixel_element,
        "rows": rows,
        "samples_per_pixel": samples,
        "shape": shape,
        "warnings": warnings,
    }


def counter_dict(counter: Counter[str]) -> dict[str, int]:
    return {key: counter[key] for key in sorted(counter)}


def validate_profile(document: Any) -> dict[str, Any]:
    if not isinstance(document, Mapping):
        raise ToolError("action profile must be a JSON object")
    allowed = {"name", "version", "actions", "private_policy", "date_policy"}
    unknown = sorted(set(document) - allowed)
    if unknown:
        raise ToolError(f"action profile has unsupported keys: {', '.join(unknown)}")
    name = require_text(document.get("name"), name="profile name", maximum=128)
    version = require_text(document.get("version"), name="profile version", maximum=32)
    raw_actions = document.get("actions", {})
    if not isinstance(raw_actions, Mapping) or len(raw_actions) > 2_000:
        raise ToolError("profile actions must be an object with at most 2000 entries")
    actions = dict(DEFAULT_ACTIONS)
    valid_actions = {"empty", "keep", "pseudonym", "remove", "uid"}
    for raw_key, raw_action in raw_actions.items():
        key = require_text(raw_key, name="action key", maximum=128)
        action = require_text(raw_action, name=f"action for {key}", maximum=16)
        if action not in valid_actions:
            raise ToolError(f"unsupported action for {key}")
        actions[key] = action
    private_policy = document.get("private_policy", "remove")
    if private_policy not in {"keep", "reject", "remove"}:
        raise ToolError("private_policy must be keep, reject, or remove")
    date_policy = document.get("date_policy", "empty")
    if date_policy not in {"empty", "keep", "shift"}:
        raise ToolError("date_policy must be empty, keep, or shift")
    return {
        "actions": actions,
        "date_policy": date_policy,
        "name": name,
        "private_policy": private_policy,
        "version": version,
    }


def starter_profile() -> dict[str, Any]:
    return {
        "actions": dict(DEFAULT_ACTIONS),
        "date_policy": "empty",
        "name": "bounded-starter",
        "private_policy": "remove",
        "version": "1.1",
    }
```

### `scripts/anonymize_dicom.py`

```python
#!/usr/bin/env python3
"""Create a bounded, pseudonymized DICOM derivative without compliance claims.

This local-only helper preserves the source file and writes a new output. DICOM
metadata, file names, private elements, overlays, structured content, and pixel
data may contain PHI. The starter profile is deliberately incomplete: select a
profile for the intended context and obtain privacy/DICOM expert verification.
"""

from __future__ import annotations

import argparse
import os
import secrets
import stat
import sys
from collections import Counter
from collections.abc import Sequence as SequenceValue
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from _common import (
    DEFAULT_MAX_ELEMENTS,
    DEFAULT_MAX_INPUT_BYTES,
    DEFAULT_MAX_OUTPUT_BYTES,
    HARD_MAX_ELEMENTS,
    HARD_MAX_INPUT_BYTES,
    HARD_MAX_OUTPUT_BYTES,
    MAX_SEQUENCE_DEPTH,
    SCHEMA_VERSION,
    STRUCTURAL_UID_KEYWORDS,
    TEXT_VRS,
    UID_REMAP_KEYWORDS,
    ToolError,
    atomic_generated_file,
    atomic_write,
    bounded_int,
    checked_input,
    checked_output,
    counter_dict,
    derive_token,
    derive_uid,
    element_tag,
    emit_json,
    fail_json,
    json_bytes,
    load_json,
    parse_size,
    paths_overlap,
    require_pydicom,
    require_text,
    safe_dcmread,
    sha256_text,
    starter_profile,
    validate_profile,
)

TOOL = "anonymize_dicom"
PIXEL_KEYWORDS = {"DoubleFloatPixelData", "FloatPixelData", "PixelData"}


def _load_key(path: Path) -> bytes:
    info = path.stat()
    if os.name != "nt":
        if stat.S_IMODE(info.st_mode) & 0o077:
            raise ToolError("UID key permissions must deny group and other access")
        if hasattr(os, "getuid") and info.st_uid != os.getuid():
            raise ToolError("UID key must be owned by the current user")
    payload = path.read_bytes()
    if len(payload) == 64:
        try:
            payload = bytes.fromhex(payload.decode("ascii"))
        except (UnicodeError, ValueError):
            pass
    if len(payload) < 32:
        raise ToolError("UID key must contain at least 32 bytes of secret material")
    return payload[:128]


def _map_scalar_uid(
    value: Any, *, key: bytes, scope: str, mapping: dict[str, str]
) -> str:
    original = str(value)
    replacement = mapping.get(original)
    if replacement is None:
        replacement = derive_uid(original, key=key, scope=scope)
        mapping[original] = replacement
    return replacement


def _map_uid_value(
    value: Any, *, key: bytes, scope: str, mapping: dict[str, str]
) -> Any:
    if isinstance(value, SequenceValue) and not isinstance(value, (str, bytes)):
        return [
            _map_scalar_uid(item, key=key, scope=scope, mapping=mapping)
            for item in value
        ]
    return _map_scalar_uid(value, key=key, scope=scope, mapping=mapping)


def _pseudonym_value(value: Any, *, keyword: str, key: bytes, scope: str) -> str:
    token = derive_token(str(value), key=key, scope=scope)
    if keyword == "PatientName":
        return f"PSEUDONYM^{token}"
    return f"P-{token}"


def _shift_date_text(value: Any, days: int) -> tuple[str, bool]:
    text = str(value)
    if len(text) != 8 or not text.isdigit():
        return "", False
    try:
        shifted = date(int(text[:4]), int(text[4:6]), int(text[6:8])) + timedelta(
            days=days
        )
    except (ValueError, OverflowError):
        return "", False
    return shifted.strftime("%Y%m%d"), True


def _shift_datetime_text(value: Any, days: int) -> tuple[str, bool]:
    text = str(value)
    if len(text) < 8 or not text[:8].isdigit():
        return "", False
    shifted, ok = _shift_date_text(text[:8], days)
    return (shifted + text[8:], True) if ok else ("", False)


def _date_action(
    element: Any,
    *,
    date_policy: str,
    date_shift_days: int | None,
    retain_times: bool,
    counters: Counter[str],
) -> None:
    vr = str(element.VR)
    if date_policy == "keep":
        counters["dates_kept"] += 1
        return
    if date_policy == "empty":
        element.value = ""
        counters["dates_or_times_emptied"] += 1
        return
    if date_shift_days is None:
        raise ToolError("date shift policy requires --date-shift-days")
    if vr == "TM":
        if retain_times:
            counters["standalone_times_retained"] += 1
        else:
            element.value = ""
            counters["standalone_times_emptied"] += 1
        return
    if isinstance(element.value, SequenceValue) and not isinstance(
        element.value, (str, bytes)
    ):
        values = list(element.value)
    else:
        values = [element.value]
    shifted_values: list[str] = []
    for value in values:
        if vr == "DA":
            shifted, ok = _shift_date_text(value, date_shift_days)
        else:
            shifted, ok = _shift_datetime_text(value, date_shift_days)
        shifted_values.append(shifted)
        counters["dates_shifted" if ok else "unshiftable_dates_emptied"] += 1
    element.value = shifted_values if len(shifted_values) > 1 else shifted_values[0]


def _looks_instance_uid(keyword: str) -> bool:
    return keyword in UID_REMAP_KEYWORDS or keyword.endswith(
        ("InstanceUID", "FrameOfReferenceUID")
    )


def transform_dataset(
    dataset: Any,
    *,
    profile: dict[str, Any],
    key: bytes,
    scope: str,
    date_shift_days: int | None,
    retain_times: bool,
    allow_private_retention: bool,
    allow_date_retention: bool,
    max_elements: int,
) -> tuple[dict[str, Any], dict[str, str]]:
    """Apply the bounded starter/profile actions in place."""

    actions = profile["actions"]
    private_policy = profile["private_policy"]
    date_policy = profile["date_policy"]
    if private_policy == "keep" and not allow_private_retention:
        raise ToolError(
            "private retention requires --allow-private-retention and expert review"
        )
    if date_policy == "keep" and not allow_date_retention:
        raise ToolError("date retention requires --allow-date-retention")
    if date_policy == "shift" and date_shift_days is None:
        raise ToolError("date shift policy requires --date-shift-days")
    if date_policy != "shift" and date_shift_days is not None:
        raise ToolError("--date-shift-days is only valid with date policy shift")
    if retain_times and date_policy != "shift":
        raise ToolError("--retain-times is only valid with date policy shift")

    counters: Counter[str] = Counter()
    unresolved_text: Counter[str] = Counter()
    unresolved_uids: Counter[str] = Counter()
    uid_mapping: dict[str, str] = {}
    stack: list[tuple[Any, int]] = [(dataset, 0)]
    seen_elements = 0
    pixel_present = False
    burned_in_status = str(dataset.get("BurnedInAnnotation", "")).upper()
    recognizable_status = str(dataset.get("RecognizableVisualFeatures", "")).upper()

    while stack:
        current, depth = stack.pop()
        if depth > MAX_SEQUENCE_DEPTH:
            raise ToolError("sequence nesting exceeds the hard depth limit")
        for element in list(current):
            seen_elements += 1
            if seen_elements > max_elements:
                raise ToolError("data-element limit exceeded")
            keyword = element.keyword or element_tag(element)
            group = int(element.tag.group)

            if keyword in PIXEL_KEYWORDS:
                pixel_present = True
                counters["pixel_elements_preserved"] += 1
                continue

            if element.tag.is_private:
                counters["private_elements_seen"] += 1
                if private_policy == "reject":
                    raise ToolError("private elements present under reject policy")
                if private_policy == "remove":
                    del current[element.tag]
                    counters["private_elements_removed"] += 1
                    continue
                counters["private_elements_retained"] += 1

            if 0x5000 <= group <= 0x50FF or 0x6000 <= group <= 0x60FF:
                del current[element.tag]
                counters["overlay_or_curve_elements_removed"] += 1
                continue

            action = actions.get(keyword, actions.get(element_tag(element)))
            if action == "remove":
                del current[element.tag]
                counters["elements_removed"] += 1
                continue
            if action == "empty":
                element.value = [] if str(element.VR) == "SQ" else ""
                counters["elements_emptied"] += 1
                continue
            if action == "pseudonym":
                if str(element.VR) not in TEXT_VRS or str(element.VR) == "UI":
                    raise ToolError(
                        "pseudonym action is only valid for non-UID text elements"
                    )
                element.value = _pseudonym_value(
                    element.value,
                    keyword=keyword,
                    key=key,
                    scope=scope,
                )
                counters["elements_pseudonymized"] += 1
                continue
            if action == "uid":
                if str(element.VR) != "UI":
                    raise ToolError("uid action is only valid for UI elements")
                element.value = _map_uid_value(
                    element.value,
                    key=key,
                    scope=scope,
                    mapping=uid_mapping,
                )
                counters["uid_elements_remapped"] += 1
                continue
            if action == "keep":
                counters["profile_keep_actions"] += 1
                continue

            if str(element.VR) == "SQ":
                for item in reversed(list(element.value)):
                    stack.append((item, depth + 1))
                continue

            if str(element.VR) in {"DA", "DT", "TM"}:
                _date_action(
                    element,
                    date_policy=date_policy,
                    date_shift_days=date_shift_days,
                    retain_times=retain_times,
                    counters=counters,
                )
                continue

            if str(element.VR) == "UI":
                if keyword in STRUCTURAL_UID_KEYWORDS:
                    counters["structural_uid_elements_preserved"] += 1
                elif _looks_instance_uid(keyword):
                    element.value = _map_uid_value(
                        element.value,
                        key=key,
                        scope=scope,
                        mapping=uid_mapping,
                    )
                    counters["uid_elements_remapped"] += 1
                else:
                    unresolved_uids[keyword] += 1
                continue

            if str(element.VR) in TEXT_VRS and action != "keep":
                unresolved_text[keyword] += 1

    # Never assert successful de-identification. These attributes are removed by
    # the starter profile and then set conservatively after processing.
    dataset.PatientIdentityRemoved = "NO"
    if "DeidentificationMethod" in dataset:
        del dataset.DeidentificationMethod
    if "DeidentificationMethodCodeSequence" in dataset:
        del dataset.DeidentificationMethodCodeSequence

    report = {
        "actions": counter_dict(counters),
        "burned_in_annotation": burned_in_status or "ABSENT",
        "date_policy": date_policy,
        "elements_examined": seen_elements,
        "expert_verification_required": True,
        "not_a_compliance_claim": True,
        "patient_identity_removed": "NO",
        "pixel_data_preserved": pixel_present,
        "private_policy": private_policy,
        "recognizable_visual_features": recognizable_status or "ABSENT",
        "residual_text_elements_by_keyword": counter_dict(unresolved_text),
        "unclassified_uid_elements_by_keyword": counter_dict(unresolved_uids),
        "uid_mappings": len(uid_mapping),
    }
    return report, uid_mapping


def _rebuild_file_meta(dataset: Any, *, original_transfer_syntax: Any) -> None:
    require_pydicom()
    from pydicom.dataset import FileMetaDataset
    from pydicom.uid import PYDICOM_IMPLEMENTATION_UID

    if not dataset.get("SOPClassUID") or not dataset.get("SOPInstanceUID"):
        raise ToolError("SOP Class and SOP Instance UIDs are required for safe output")
    file_meta = FileMetaDataset()
    file_meta.FileMetaInformationVersion = b"\x00\x01"
    file_meta.MediaStorageSOPClassUID = dataset.SOPClassUID
    file_meta.MediaStorageSOPInstanceUID = dataset.SOPInstanceUID
    file_meta.TransferSyntaxUID = original_transfer_syntax
    file_meta.ImplementationClassUID = PYDICOM_IMPLEMENTATION_UID
    dataset.file_meta = file_meta
    dataset.preamble = b"\x00" * 128


def process_file(args: argparse.Namespace) -> dict[str, Any]:
    max_input_bytes = parse_size(
        args.max_input_bytes,
        name="max_input_bytes",
        maximum=HARD_MAX_INPUT_BYTES,
    )
    max_output_bytes = parse_size(
        args.max_output_bytes,
        name="max_output_bytes",
        maximum=HARD_MAX_OUTPUT_BYTES,
    )
    max_elements = bounded_int(
        args.max_elements,
        name="max_elements",
        minimum=1,
        maximum=HARD_MAX_ELEMENTS,
    )
    source = checked_input(
        args.input,
        root=args.root,
        kind="file",
        max_bytes=max_input_bytes,
    )
    destination = checked_output(args.output, root=args.root, force=args.force)
    audit_path = checked_output(args.audit_report, root=args.root, force=args.force)
    key_path = checked_input(
        args.uid_key_file,
        root=args.root,
        kind="file",
        max_bytes=4 * 1024,
    )
    for candidate in (destination, audit_path):
        if paths_overlap(source, candidate):
            raise ToolError("input and output paths must be distinct")
        if paths_overlap(key_path, candidate):
            raise ToolError("UID key and output paths must be distinct")
    if paths_overlap(source, key_path):
        raise ToolError("DICOM input and UID key must be distinct")
    if destination == audit_path:
        raise ToolError("DICOM output and audit report must be distinct")

    mapping_path: Path | None = None
    if args.uid_map_output:
        if not args.acknowledge_sensitive_map:
            raise ToolError("UID map output requires --acknowledge-sensitive-map")
        mapping_path = checked_output(
            args.uid_map_output, root=args.root, force=args.force
        )
        if mapping_path in {destination, audit_path} or paths_overlap(
            source, mapping_path
        ):
            raise ToolError("UID map path must be distinct from all other paths")
        if paths_overlap(key_path, mapping_path):
            raise ToolError("UID map must not overwrite the UID key")

    scope = require_text(args.uid_scope, name="uid_scope", maximum=128)
    key = _load_key(key_path)
    profile = starter_profile()
    profile_source = "built-in"
    if args.profile_json:
        profile_path = checked_input(
            args.profile_json,
            root=args.root,
            kind="file",
            max_bytes=1 * 1024 * 1024,
        )
        if any(
            paths_overlap(profile_path, candidate)
            for candidate in (source, destination, audit_path, key_path)
        ):
            raise ToolError("action profile must use a distinct local file")
        if mapping_path is not None and paths_overlap(profile_path, mapping_path):
            raise ToolError("action profile and UID map paths must be distinct")
        profile = validate_profile(load_json(profile_path))
        profile_source = "local-json"
    if args.private_policy:
        profile["private_policy"] = args.private_policy
    if args.date_policy:
        profile["date_policy"] = args.date_policy
    if args.date_shift_days is not None:
        bounded_int(
            args.date_shift_days,
            name="date_shift_days",
            minimum=-365_000,
            maximum=365_000,
        )

    dataset = safe_dcmread(
        source,
        stop_before_pixels=False,
        force=False,
        defer_size=args.defer_size,
    )
    pydicom = require_pydicom()
    original_transfer_syntax = dataset.file_meta.get("TransferSyntaxUID")
    if original_transfer_syntax is None:
        raise ToolError("Transfer Syntax UID is required for safe output")

    transform_report, uid_mapping = transform_dataset(
        dataset,
        profile=profile,
        key=key,
        scope=scope,
        date_shift_days=args.date_shift_days,
        retain_times=args.retain_times,
        allow_private_retention=args.allow_private_retention,
        allow_date_retention=args.allow_date_retention,
        max_elements=max_elements,
    )
    _rebuild_file_meta(dataset, original_transfer_syntax=original_transfer_syntax)

    def writer(path: Path) -> None:
        pydicom.dcmwrite(
            path,
            dataset,
            enforce_file_format=True,
            overwrite=True,
        )

    def validator(path: Path) -> None:
        check = safe_dcmread(path, stop_before_pixels=True, force=False)
        if str(check.get("PatientIdentityRemoved", "")) != "NO":
            raise ToolError("output verification failed")
        if str(check.file_meta.get("MediaStorageSOPInstanceUID", "")) != str(
            check.get("SOPInstanceUID", "")
        ):
            raise ToolError("output file meta verification failed")

    atomic_generated_file(
        destination,
        writer=writer,
        validator=validator,
        force=args.force,
        max_bytes=max_output_bytes,
    )

    warnings = [
        "This output has not been established as de-identified or compliant.",
        "DICOM metadata and pixels may still contain PHI; expert review is required.",
        "Date/time actions can affect validity and longitudinal utility.",
    ]
    if transform_report["pixel_data_preserved"]:
        warnings.append(
            "Pixel data was not inspected or cleaned for burned-in annotations "
            "or recognizable visual features."
        )
    if transform_report["burned_in_annotation"] != "NO":
        warnings.append("Burned In Annotation is absent, unknown, or not NO.")
    if transform_report["unclassified_uid_elements_by_keyword"]:
        warnings.append("One or more UI elements were not classified for remapping.")
    if transform_report["residual_text_elements_by_keyword"]:
        warnings.append("One or more textual elements remain for profile review.")
    if profile["private_policy"] == "keep":
        warnings.append("Private elements were retained by explicit high-risk policy.")
    if profile["date_policy"] == "keep":
        warnings.append("Dates/times were retained by explicit high-risk policy.")

    audit = {
        "input_files": 1,
        "network_accessed": False,
        "ok": True,
        "original_preserved": True,
        "output_files": 1,
        "profile": {
            "name": profile["name"],
            "source": profile_source,
            "version": profile["version"],
        },
        "schema_version": SCHEMA_VERSION,
        "scope_sha256": sha256_text(scope),
        "tool": TOOL,
        "transform": transform_report,
        "uid_key_sha256": sha256_text(key.hex()),
        "uid_map_written": mapping_path is not None,
        "warnings": warnings,
    }
    atomic_write(audit_path, json_bytes(audit), force=args.force)
    if mapping_path is not None:
        mapping_document = {
            "entries": [
                {"original": original, "replacement": replacement}
                for original, replacement in sorted(uid_mapping.items())
            ],
            "schema_version": SCHEMA_VERSION,
            "scope_sha256": sha256_text(scope),
            "sensitive": True,
            "tool": TOOL,
        }
        atomic_write(mapping_path, json_bytes(mapping_document), force=args.force)
    return audit


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Create a bounded pseudonymized DICOM derivative. This is not a "
            "DICOM PS3.15, HIPAA, GDPR, or other compliance claim."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Local authorized data only. Originals are never modified. Metadata, private
elements, file names, overlays, structured content, and pixels may contain PHI.
The output requires profile-specific privacy and DICOM expert verification.
The UID key and optional map are re-identification secrets: keep them separate
from derivatives in approved encrypted/managed storage and never commit them.

Examples:
  python anonymize_dicom.py --generate-uid-key project.key
  python anonymize_dicom.py in.dcm out.dcm --uid-key-file project.key \\
    --uid-scope study-export-v1 --audit-report out.audit.json
  python anonymize_dicom.py in.dcm out.dcm --uid-key-file project.key \\
    --uid-scope study-export-v1 --audit-report out.audit.json \\
    --date-policy shift --date-shift-days 180
""",
    )
    parser.add_argument("input", nargs="?", help="Local source DICOM file")
    parser.add_argument("output", nargs="?", help="New local DICOM output file")
    parser.add_argument(
        "--root",
        default=".",
        help="Existing local root containing every input and output (default: .)",
    )
    parser.add_argument(
        "--generate-uid-key",
        metavar="PATH",
        help="Create a new private 32-byte key and exit; refuses overwrite",
    )
    parser.add_argument(
        "--uid-key-file",
        help="Local secret key used for deterministic scoped pseudonyms and UIDs",
    )
    parser.add_argument(
        "--uid-scope",
        help="Non-PHI scope label; the same key/scope gives consistent mappings",
    )
    parser.add_argument(
        "--profile-json",
        help="Optional bounded local JSON action profile merged over starter actions",
    )
    parser.add_argument(
        "--private-policy",
        choices=("remove", "reject", "keep"),
        help="Override profile private-element policy",
    )
    parser.add_argument(
        "--date-policy",
        choices=("empty", "shift", "keep"),
        help="Override profile DA/DT/TM policy",
    )
    parser.add_argument(
        "--date-shift-days",
        type=int,
        help="Fixed date shift for all DA/DT values; partial/invalid values are emptied",
    )
    parser.add_argument(
        "--retain-times",
        action="store_true",
        help="With date shifting, retain standalone TM values (explicit risk choice)",
    )
    parser.add_argument(
        "--allow-private-retention",
        action="store_true",
        help="Acknowledge that retained private elements may contain PHI",
    )
    parser.add_argument(
        "--allow-date-retention",
        action="store_true",
        help="Acknowledge that retained dates/times may be identifying",
    )
    parser.add_argument(
        "--audit-report",
        help="Required private JSON audit report path; contains no element values",
    )
    parser.add_argument(
        "--uid-map-output",
        help="Optional private JSON mapping; contains sensitive original UIDs",
    )
    parser.add_argument(
        "--acknowledge-sensitive-map",
        action="store_true",
        help="Required to write a UID map containing original identifiers",
    )
    parser.add_argument(
        "--defer-size",
        default="1 MiB",
        help="pydicom deferred-value threshold (default: 1 MiB)",
    )
    parser.add_argument(
        "--max-input-bytes",
        default=str(DEFAULT_MAX_INPUT_BYTES),
        help="Maximum source file size (integer or B/KiB/MiB/GiB)",
    )
    parser.add_argument(
        "--max-output-bytes",
        default=str(DEFAULT_MAX_OUTPUT_BYTES),
        help="Maximum generated DICOM size (integer or B/KiB/MiB/GiB)",
    )
    parser.add_argument(
        "--max-elements",
        type=int,
        default=DEFAULT_MAX_ELEMENTS,
        help=f"Maximum recursive data elements (default: {DEFAULT_MAX_ELEMENTS})",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing outputs, never the input",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.generate_uid_key:
            if args.input or args.output:
                raise ToolError("key generation does not accept input/output files")
            destination = checked_output(
                args.generate_uid_key, root=args.root, force=False
            )
            atomic_write(destination, secrets.token_bytes(32), force=False)
            emit_json(
                {
                    "key_bytes": 32,
                    "network_accessed": False,
                    "ok": True,
                    "permissions": "0600",
                    "tool": TOOL,
                }
            )
            return 0
        required = {
            "input": args.input,
            "output": args.output,
            "uid_key_file": args.uid_key_file,
            "uid_scope": args.uid_scope,
            "audit_report": args.audit_report,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise ToolError(f"missing required arguments: {', '.join(missing)}")
        audit = process_file(args)
        emit_json(audit)
        return 0
    except Exception as exc:  # noqa: BLE001 - sanitize unexpected library errors
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/deidentification_audit.py`

```python
#!/usr/bin/env python3
"""Audit DICOM metadata for bounded de-identification review signals."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from typing import Any

from _common import (
    DEFAULT_MAX_ELEMENTS,
    DEFAULT_MAX_FILES,
    DEFAULT_MAX_INPUT_BYTES,
    HARD_MAX_ELEMENTS,
    HARD_MAX_FILES,
    HARD_MAX_INPUT_BYTES,
    MAX_SEQUENCE_DEPTH,
    SCHEMA_VERSION,
    SENSITIVE_KEYWORDS,
    STRUCTURAL_UID_KEYWORDS,
    TEXT_VRS,
    UID_REMAP_KEYWORDS,
    ToolError,
    atomic_write,
    bounded_int,
    checked_input,
    checked_output,
    collect_local_files,
    counter_dict,
    element_tag,
    emit_json,
    fail_json,
    json_bytes,
    load_json,
    parse_size,
    paths_overlap,
    safe_dcmread,
    starter_profile,
    validate_profile,
)

TOOL = "deidentification_audit"
PIXEL_METADATA = {
    "BitsAllocated",
    "BitsStored",
    "Columns",
    "DoubleFloatPixelData",
    "FloatPixelData",
    "NumberOfFrames",
    "PhotometricInterpretation",
    "PixelData",
    "Rows",
    "SamplesPerPixel",
}
BULK_OR_CONTENT_KEYWORDS = {
    "AcquisitionContextSequence",
    "AudioSampleData",
    "ContentSequence",
    "EncapsulatedDocument",
    "GraphicAnnotationSequence",
    "IconImageSequence",
    "SpectroscopyData",
    "WaveformData",
}


def _has_value(element: Any) -> bool:
    value = element.value
    if value is None:
        return False
    if isinstance(value, (str, bytes)):
        return bool(value)
    try:
        return len(value) > 0
    except TypeError:
        return True


def audit_dataset(
    dataset: Any,
    *,
    profile: dict[str, Any],
    file_id: str,
    max_elements: int,
) -> dict[str, Any]:
    actions = profile["actions"]
    categories: Counter[str] = Counter()
    residual_keywords: Counter[str] = Counter()
    unclassified_text: Counter[str] = Counter()
    unclassified_uids: Counter[str] = Counter()
    stack: list[tuple[Any, int]] = [(dataset, 0)]
    elements = 0
    image_metadata_present = False
    while stack:
        current, depth = stack.pop()
        if depth > MAX_SEQUENCE_DEPTH:
            raise ToolError("sequence nesting exceeds the hard depth limit")
        for element in current:
            elements += 1
            if elements > max_elements:
                raise ToolError("data-element limit exceeded")
            keyword = element.keyword or element_tag(element)
            vr = str(element.VR)
            has_value = _has_value(element)

            if keyword in PIXEL_METADATA:
                image_metadata_present = True
            if keyword in BULK_OR_CONTENT_KEYWORDS:
                categories["bulk_or_structured_content_elements"] += 1
            if element.tag.is_private:
                categories["private_elements"] += 1
                if has_value:
                    categories["nonempty_private_elements"] += 1
            group = int(element.tag.group)
            if 0x5000 <= group <= 0x50FF or 0x6000 <= group <= 0x60FF:
                categories["curve_or_overlay_elements"] += 1

            action = actions.get(keyword, actions.get(element_tag(element)))
            if action in {"remove", "empty"} and has_value:
                residual_keywords[keyword] += 1
                categories["profile_action_residuals"] += 1
            elif action == "pseudonym" and has_value:
                categories["pseudonym_values_requiring_provenance_review"] += 1
            elif action == "keep" and has_value:
                categories["explicit_profile_retention"] += 1

            if vr == "SQ":
                for item in reversed(list(element.value)):
                    stack.append((item, depth + 1))
                continue
            if not has_value:
                continue
            if vr in {"DA", "DT", "TM"}:
                categories["nonempty_date_or_time_elements"] += 1
            if vr == "UI":
                if keyword in STRUCTURAL_UID_KEYWORDS:
                    categories["structural_uid_elements"] += 1
                elif keyword in UID_REMAP_KEYWORDS or keyword.endswith(
                    ("InstanceUID", "FrameOfReferenceUID")
                ):
                    categories["instance_uid_elements"] += 1
                else:
                    unclassified_uids[keyword] += 1
            if keyword in SENSITIVE_KEYWORDS:
                categories["known_sensitive_elements_present"] += 1
            elif vr in TEXT_VRS and keyword not in {"SpecificCharacterSet"}:
                unclassified_text[keyword] += 1

    burned_in = str(dataset.get("BurnedInAnnotation", "")).strip().upper()
    recognizable = str(dataset.get("RecognizableVisualFeatures", "")).strip().upper()
    identity_removed = str(dataset.get("PatientIdentityRemoved", "")).strip().upper()
    pixel_review_required = image_metadata_present
    high_risk_findings = (
        categories["nonempty_private_elements"]
        + categories["profile_action_residuals"]
        + categories["curve_or_overlay_elements"]
        + categories["bulk_or_structured_content_elements"]
        + len(unclassified_text)
        + len(unclassified_uids)
    )
    if image_metadata_present and burned_in != "NO":
        high_risk_findings += 1
    return {
        "burned_in_annotation": burned_in or "ABSENT",
        "categories": counter_dict(categories),
        "elements_examined": elements,
        "file_id": file_id,
        "high_risk_findings": high_risk_findings,
        "patient_identity_removed_claim": identity_removed or "ABSENT",
        "pixel_review_required": pixel_review_required,
        "profile_action_residuals_by_keyword": counter_dict(residual_keywords),
        "recognizable_visual_features": recognizable or "ABSENT",
        "review_passed": high_risk_findings == 0 and not pixel_review_required,
        "unclassified_text_by_keyword": counter_dict(unclassified_text),
        "unclassified_uids_by_keyword": counter_dict(unclassified_uids),
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    max_input_bytes = parse_size(
        args.max_input_bytes,
        name="max_input_bytes",
        maximum=HARD_MAX_INPUT_BYTES,
    )
    max_files = bounded_int(
        args.max_files,
        name="max_files",
        minimum=1,
        maximum=HARD_MAX_FILES,
    )
    max_elements = bounded_int(
        args.max_elements,
        name="max_elements",
        minimum=1,
        maximum=HARD_MAX_ELEMENTS,
    )
    source = checked_input(
        args.input,
        root=args.root,
        kind="any",
        max_bytes=max_input_bytes,
    )
    files = collect_local_files(
        source,
        max_files=max_files,
        max_bytes=max_input_bytes,
        recursive=args.recursive,
    )
    profile = starter_profile()
    profile_source = "built-in"
    if args.profile_json:
        profile_path = checked_input(
            args.profile_json,
            root=args.root,
            kind="file",
            max_bytes=1 * 1024 * 1024,
        )
        profile = validate_profile(load_json(profile_path))
        profile_source = "local-json"
    records: list[dict[str, Any]] = []
    parse_failures = 0
    for index, path in enumerate(files, start=1):
        try:
            dataset = safe_dcmread(
                path,
                stop_before_pixels=True,
                force=args.force_dicom_read,
            )
            records.append(
                audit_dataset(
                    dataset,
                    profile=profile,
                    file_id=f"file-{index:06d}",
                    max_elements=max_elements,
                )
            )
        except ToolError:
            parse_failures += 1
            records.append(
                {
                    "file_id": f"file-{index:06d}",
                    "high_risk_findings": 1,
                    "parse_failed": True,
                    "pixel_review_required": True,
                    "review_passed": False,
                }
            )
    category_totals: Counter[str] = Counter()
    for record in records:
        category_totals.update(record.get("categories", {}))
    review_failures = sum(not record["review_passed"] for record in records)
    return {
        "aggregate": {
            "categories": counter_dict(category_totals),
            "files_examined": len(records),
            "parse_failures": parse_failures,
            "pixel_review_files": sum(
                bool(record.get("pixel_review_required")) for record in records
            ),
            "review_failure_files": review_failures,
        },
        "file_names_emitted": False,
        "metadata_only": True,
        "network_accessed": False,
        "not_a_compliance_determination": True,
        "ok": bool(records),
        "profile": {
            "name": profile["name"],
            "source": profile_source,
            "version": profile["version"],
        },
        "records": records,
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL,
        "warnings": [
            "Attribute auditing cannot establish that an Information Object is de-identified.",
            "Patient Identity Removed=YES is not treated as proof.",
            "Pixels, recognizable visual features, graphics, overlays, structured content, private data, and external context require expert review.",
            "Profile and regulatory applicability are purpose, recipient, jurisdiction, and risk specific.",
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Audit bounded DICOM metadata for residual identifier categories; "
            "never claims de-identification or regulatory compliance."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Local authorized data only. This metadata-only audit never decompresses pixels.
It is one input to a context-specific expert de-identification review, not a
replacement for DICOM PS3.15 profile selection or re-identification risk analysis.

Examples:
  python deidentification_audit.py candidate.dcm
  python deidentification_audit.py export-dir --recursive --output audit.json
  python deidentification_audit.py candidate.dcm --profile-json site-profile.json
""",
    )
    parser.add_argument("input", help="Local DICOM file or directory")
    parser.add_argument("--root", default=".", help="Existing local I/O root")
    parser.add_argument(
        "--recursive", action="store_true", help="Recursively inspect directories"
    )
    parser.add_argument("--profile-json", help="Local bounded action-profile JSON")
    parser.add_argument("--output", "-o", help="Private JSON report path")
    parser.add_argument(
        "--force-dicom-read",
        action="store_true",
        help="Parse missing File Format headers; does not validate them",
    )
    parser.add_argument(
        "--fail-on-findings",
        action="store_true",
        help="Exit 1 when any file requires review",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=DEFAULT_MAX_FILES,
        help=f"Maximum files (default: {DEFAULT_MAX_FILES})",
    )
    parser.add_argument(
        "--max-elements",
        type=int,
        default=DEFAULT_MAX_ELEMENTS,
        help=f"Maximum elements per file (default: {DEFAULT_MAX_ELEMENTS})",
    )
    parser.add_argument(
        "--max-input-bytes",
        default=str(DEFAULT_MAX_INPUT_BYTES),
        help="Maximum bytes per input file",
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite an existing report only"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = build_report(args)
        if args.output:
            destination = checked_output(args.output, root=args.root, force=args.force)
            source = checked_input(
                args.input,
                root=args.root,
                kind="any",
                max_bytes=parse_size(
                    args.max_input_bytes,
                    name="max_input_bytes",
                    maximum=HARD_MAX_INPUT_BYTES,
                ),
            )
            if source.is_file() and paths_overlap(source, destination):
                raise ToolError("report must not overwrite its input")
            atomic_write(destination, json_bytes(report), force=args.force)
            emit_json(
                {
                    "ok": report["ok"],
                    "report_written": True,
                    "tool": TOOL,
                }
            )
        else:
            emit_json(report)
        findings = report["aggregate"]["review_failure_files"]
        if args.fail_on_findings and findings:
            return 1
        return 0 if report["ok"] else 1
    except Exception as exc:  # noqa: BLE001 - sanitize unexpected library errors
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/dicom_inventory.py`

```python
#!/usr/bin/env python3
"""Bounded metadata-only DICOM technical inventory and structural checks."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from typing import Any

from _common import (
    DEFAULT_MAX_DECOMPRESSED_BYTES,
    DEFAULT_MAX_FILES,
    DEFAULT_MAX_FRAMES,
    DEFAULT_MAX_INPUT_BYTES,
    HARD_MAX_DECOMPRESSED_BYTES,
    HARD_MAX_FILES,
    HARD_MAX_FRAMES,
    HARD_MAX_INPUT_BYTES,
    SCHEMA_VERSION,
    TECHNICAL_KEYWORDS,
    ToolError,
    atomic_write,
    bounded_int,
    checked_input,
    checked_output,
    collect_local_files,
    counter_dict,
    emit_json,
    fail_json,
    json_bytes,
    parse_size,
    paths_overlap,
    pixel_plan,
    require_pydicom,
    safe_dcmread,
    valid_uid,
)

TOOL = "dicom_inventory"
INVENTORY_TAGS = list(TECHNICAL_KEYWORDS) + [
    "SOPInstanceUID",
    "PatientIdentityRemoved",
]


def _issue(code: str, message: str, severity: str = "error") -> dict[str, str]:
    return {"code": code, "message": message, "severity": severity}


def inspect_dataset(
    dataset: Any,
    *,
    file_id: str,
    file_size: int,
    max_frames: int,
    max_decompressed_bytes: int,
    forced_read: bool,
) -> dict[str, Any]:
    pydicom = require_pydicom()
    issues: list[dict[str, str]] = []
    file_meta = dataset.file_meta
    try:
        pydicom.dataset.validate_file_meta(file_meta, enforce_standard=True)
    except Exception:  # noqa: BLE001 - any validation failure becomes a finding
        issues.append(
            _issue(
                "file_meta_invalid",
                "Required DICOM File Meta Information is missing, empty, or invalid.",
            )
        )

    transfer_value = str(file_meta.get("TransferSyntaxUID", ""))
    transfer = None
    if not valid_uid(transfer_value):
        issues.append(
            _issue(
                "transfer_syntax_invalid", "Transfer Syntax UID is absent or invalid."
            )
        )
    else:
        transfer = pydicom.uid.UID(transfer_value)

    sop_class = str(dataset.get("SOPClassUID", ""))
    sop_instance = str(dataset.get("SOPInstanceUID", ""))
    if not valid_uid(sop_class):
        issues.append(
            _issue("sop_class_invalid", "SOP Class UID is absent or invalid.")
        )
    if not valid_uid(sop_instance):
        issues.append(
            _issue("sop_instance_invalid", "SOP Instance UID is absent or invalid.")
        )
    media_class = str(file_meta.get("MediaStorageSOPClassUID", ""))
    media_instance = str(file_meta.get("MediaStorageSOPInstanceUID", ""))
    if sop_class and media_class and sop_class != media_class:
        issues.append(
            _issue(
                "media_sop_class_mismatch",
                "Media Storage SOP Class UID does not match the dataset SOP Class UID.",
            )
        )
    if sop_instance and media_instance and sop_instance != media_instance:
        issues.append(
            _issue(
                "media_sop_instance_mismatch",
                "Media Storage SOP Instance UID does not match the dataset SOP Instance UID.",
            )
        )

    image_plan: dict[str, Any] | None = None
    if "Rows" in dataset or "Columns" in dataset:
        try:
            image_plan = pixel_plan(
                dataset,
                max_frames=max_frames,
                max_decompressed_bytes=max_decompressed_bytes,
            )
            bits_allocated = image_plan["bits_allocated"]
            bits_stored = int(dataset.get("BitsStored", bits_allocated))
            high_bit = int(dataset.get("HighBit", bits_stored - 1))
            if bits_stored < 1 or bits_stored > bits_allocated:
                issues.append(
                    _issue(
                        "bits_stored_invalid",
                        "Bits Stored must be positive and no greater than Bits Allocated.",
                    )
                )
            if high_bit != bits_stored - 1:
                issues.append(
                    _issue(
                        "high_bit_unexpected",
                        "High Bit does not equal Bits Stored minus one.",
                        "warning",
                    )
                )
            representation = dataset.get("PixelRepresentation")
            if representation is None:
                issues.append(
                    _issue(
                        "pixel_representation_absent",
                        "Pixel Representation is absent; review whether integer or float pixel data is used.",
                        "warning",
                    )
                )
            elif int(representation) not in {0, 1}:
                issues.append(
                    _issue(
                        "pixel_representation_invalid",
                        "Pixel Representation must be 0 or 1 for integer Pixel Data.",
                    )
                )
            samples = image_plan["samples_per_pixel"]
            if samples > 1 and "PlanarConfiguration" not in dataset:
                issues.append(
                    _issue(
                        "planar_configuration_missing",
                        "Planar Configuration is required for multi-sample native pixel data.",
                        "warning",
                    )
                )
            if not dataset.get("PhotometricInterpretation"):
                issues.append(
                    _issue(
                        "photometric_interpretation_missing",
                        "Photometric Interpretation is absent.",
                    )
                )
        except ToolError as exc:
            issues.append(_issue("pixel_metadata_invalid", str(exc)))

    if forced_read:
        issues.append(
            _issue(
                "forced_read",
                "Dataset was parsed without requiring a DICOM File Format header.",
                "warning",
            )
        )
    errors = sum(issue["severity"] == "error" for issue in issues)
    warnings = sum(issue["severity"] == "warning" for issue in issues)
    return {
        "errors": errors,
        "file_id": file_id,
        "file_size_bytes": file_size,
        "forced_read": forced_read,
        "image": image_plan,
        "issues": issues,
        "modality": str(dataset.get("Modality", "UNSPECIFIED")),
        "ok": errors == 0,
        "patient_identity_removed_claim": str(
            dataset.get("PatientIdentityRemoved", "ABSENT")
        ).upper(),
        "photometric_interpretation": str(
            dataset.get("PhotometricInterpretation", "UNSPECIFIED")
        ),
        "sop_class": {
            "name": pydicom.uid.UID(sop_class).name if valid_uid(sop_class) else None,
            "uid": sop_class or None,
        },
        "transfer_syntax": {
            "compressed": bool(transfer.is_compressed) if transfer else None,
            "name": transfer.name if transfer else None,
            "uid": transfer_value or None,
        },
        "warnings": warnings,
    }


def inventory(args: argparse.Namespace) -> dict[str, Any]:
    max_input_bytes = parse_size(
        args.max_input_bytes,
        name="max_input_bytes",
        maximum=HARD_MAX_INPUT_BYTES,
    )
    max_decompressed_bytes = parse_size(
        args.max_decompressed_bytes,
        name="max_decompressed_bytes",
        maximum=HARD_MAX_DECOMPRESSED_BYTES,
    )
    max_files = bounded_int(
        args.max_files,
        name="max_files",
        minimum=1,
        maximum=HARD_MAX_FILES,
    )
    max_frames = bounded_int(
        args.max_frames,
        name="max_frames",
        minimum=1,
        maximum=HARD_MAX_FRAMES,
    )
    source = checked_input(
        args.input,
        root=args.root,
        kind="any",
        max_bytes=max_input_bytes,
    )
    files = collect_local_files(
        source,
        max_files=max_files,
        max_bytes=max_input_bytes,
        recursive=args.recursive,
    )
    records: list[dict[str, Any]] = []
    parse_failures = 0
    for index, path in enumerate(files, start=1):
        file_id = f"file-{index:06d}"
        try:
            dataset = safe_dcmread(
                path,
                stop_before_pixels=True,
                force=args.force_dicom_read,
                specific_tags=INVENTORY_TAGS,
            )
            records.append(
                inspect_dataset(
                    dataset,
                    file_id=file_id,
                    file_size=path.stat().st_size,
                    max_frames=max_frames,
                    max_decompressed_bytes=max_decompressed_bytes,
                    forced_read=args.force_dicom_read,
                )
            )
        except ToolError:
            parse_failures += 1
            records.append(
                {
                    "errors": 1,
                    "file_id": file_id,
                    "file_size_bytes": path.stat().st_size,
                    "issues": [
                        _issue(
                            "parse_failed",
                            "File could not be parsed as bounded DICOM metadata.",
                        )
                    ],
                    "ok": False,
                    "warnings": 0,
                }
            )
    issue_codes: Counter[str] = Counter()
    for record in records:
        for issue in record["issues"]:
            issue_codes[issue["code"]] += 1
    error_files = sum(not record["ok"] for record in records)
    return {
        "aggregate": {
            "error_files": error_files,
            "files_examined": len(records),
            "issue_codes": counter_dict(issue_codes),
            "parse_failures": parse_failures,
            "warning_files": sum(bool(record["warnings"]) for record in records),
        },
        "file_names_emitted": False,
        "metadata_only": True,
        "network_accessed": False,
        "ok": error_files == 0 and bool(records),
        "records": records,
        "schema_version": SCHEMA_VERSION,
        "technical_checks_only": True,
        "tool": TOOL,
        "warnings": [
            "No pixel data was loaded or decompressed.",
            "This is not complete IOD validation, clinical validation, or a diagnostic claim.",
            "Patient Identity Removed=YES, if present, is reported but not trusted as proof.",
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Perform bounded metadata-only DICOM File Format and image-pixel "
            "technical checks without printing PHI values."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Local authorized data only. Metadata and pixels may contain PHI. This tool does
not load pixels, validate every IOD rule, establish de-identification, or make
diagnostic claims.

Examples:
  python dicom_inventory.py image.dcm
  python dicom_inventory.py dicom-dir --recursive --output inventory.json
""",
    )
    parser.add_argument("input", help="Local DICOM file or directory")
    parser.add_argument("--root", default=".", help="Existing local I/O root")
    parser.add_argument(
        "--recursive", action="store_true", help="Recursively inspect directories"
    )
    parser.add_argument("--output", "-o", help="Private JSON report path")
    parser.add_argument(
        "--force-dicom-read",
        action="store_true",
        help="Parse missing File Format headers; records a warning",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=DEFAULT_MAX_FILES,
        help=f"Maximum files (default: {DEFAULT_MAX_FILES})",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=DEFAULT_MAX_FRAMES,
        help=f"Maximum declared frames (default: {DEFAULT_MAX_FRAMES})",
    )
    parser.add_argument(
        "--max-input-bytes",
        default=str(DEFAULT_MAX_INPUT_BYTES),
        help="Maximum bytes per input file",
    )
    parser.add_argument(
        "--max-decompressed-bytes",
        default=str(DEFAULT_MAX_DECOMPRESSED_BYTES),
        help="Maximum estimated full uncompressed pixel bytes",
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite an existing report only"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = inventory(args)
        if args.output:
            destination = checked_output(args.output, root=args.root, force=args.force)
            source = checked_input(
                args.input,
                root=args.root,
                kind="any",
                max_bytes=parse_size(
                    args.max_input_bytes,
                    name="max_input_bytes",
                    maximum=HARD_MAX_INPUT_BYTES,
                ),
            )
            if source.is_file() and paths_overlap(source, destination):
                raise ToolError("report must not overwrite its input")
            atomic_write(destination, json_bytes(report), force=args.force)
            emit_json(
                {
                    "ok": report["ok"],
                    "report_written": True,
                    "tool": TOOL,
                }
            )
        else:
            emit_json(report)
        return 0 if report["ok"] else 1
    except Exception as exc:  # noqa: BLE001 - sanitize unexpected library errors
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/dicom_to_image.py`

```python
#!/usr/bin/env python3
"""Render one bounded DICOM frame for non-diagnostic review."""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path
from typing import Any

from _common import (
    DEFAULT_MAX_DECOMPRESSED_BYTES,
    DEFAULT_MAX_INPUT_BYTES,
    DEFAULT_MAX_OUTPUT_BYTES,
    HARD_MAX_DECOMPRESSED_BYTES,
    HARD_MAX_INPUT_BYTES,
    HARD_MAX_OUTPUT_BYTES,
    SCHEMA_VERSION,
    ToolError,
    atomic_write,
    checked_input,
    checked_output,
    emit_json,
    fail_json,
    frame_count,
    parse_size,
    paths_overlap,
    pixel_plan,
    require_pixel_stack,
    safe_dcmread,
    safe_plugin_name,
)

TOOL = "dicom_to_image"
METADATA_TAGS = [
    "SOPClassUID",
    "Modality",
    "Rows",
    "Columns",
    "NumberOfFrames",
    "SamplesPerPixel",
    "PhotometricInterpretation",
    "PlanarConfiguration",
    "BitsAllocated",
    "BitsStored",
    "HighBit",
    "PixelRepresentation",
    "ModalityLUTSequence",
    "RescaleIntercept",
    "RescaleSlope",
    "RescaleType",
    "VOILUTSequence",
    "WindowCenter",
    "WindowWidth",
    "VOILUTFunction",
    "PresentationLUTShape",
    "RedPaletteColorLookupTableDescriptor",
    "GreenPaletteColorLookupTableDescriptor",
    "BluePaletteColorLookupTableDescriptor",
    "RedPaletteColorLookupTableData",
    "GreenPaletteColorLookupTableData",
    "BluePaletteColorLookupTableData",
    "SegmentedRedPaletteColorLookupTableData",
    "SegmentedGreenPaletteColorLookupTableData",
    "SegmentedBluePaletteColorLookupTableData",
    "ICCProfile",
    "BurnedInAnnotation",
    "RecognizableVisualFeatures",
]


def _infer_format(path: str, explicit: str | None) -> str:
    if explicit:
        return explicit
    suffix = Path(path).suffix.casefold()
    mapping = {
        ".png": "PNG",
        ".tif": "TIFF",
        ".tiff": "TIFF",
        ".jpg": "JPEG",
        ".jpeg": "JPEG",
    }
    if suffix not in mapping:
        raise ToolError("output extension must be .png, .tif, .tiff, .jpg, or .jpeg")
    return mapping[suffix]


def _normalize(array: Any, *, numpy: Any, bit_depth: int) -> tuple[Any, dict[str, Any]]:
    maximum = 255 if bit_depth == 8 else 65535
    dtype = numpy.uint8 if bit_depth == 8 else numpy.uint16
    work = numpy.asarray(array)
    finite = numpy.isfinite(work)
    finite_count = int(finite.sum())
    if finite_count == 0:
        raise ToolError("decoded frame contains no finite pixel values")
    finite_values = work[finite]
    low = float(finite_values.min())
    high = float(finite_values.max())
    converted = work.astype(numpy.float64, copy=True)
    converted[~finite] = low
    if high > low:
        converted = (converted - low) / (high - low)
    else:
        converted.fill(0)
    converted = numpy.clip(converted * maximum, 0, maximum).astype(dtype)
    return converted, {
        "finite_values": finite_count,
        "input_max": high,
        "input_min": low,
        "mapping": "per-frame linear min-max",
    }


def _apply_grayscale_transforms(
    array: Any,
    dataset: Any,
    *,
    modality_transform: str,
    voi: str,
    voi_index: int,
) -> tuple[Any, list[str]]:
    from pydicom.pixels import (
        apply_modality_lut,
        apply_voi,
        apply_voi_lut,
        apply_windowing,
    )

    applied: list[str] = []
    if modality_transform == "auto" and (
        "ModalityLUTSequence" in dataset
        or "RescaleSlope" in dataset
        or "RescaleIntercept" in dataset
    ):
        array = apply_modality_lut(array, dataset)
        applied.append("modality LUT/rescale")
    if voi == "none":
        return array, applied
    if voi == "auto":
        if "VOILUTSequence" in dataset or (
            "WindowCenter" in dataset and "WindowWidth" in dataset
        ):
            array = apply_voi_lut(array, dataset, index=voi_index)
            applied.append("VOI LUT/window")
        return array, applied
    if voi == "window":
        if "WindowCenter" not in dataset or "WindowWidth" not in dataset:
            raise ToolError("window VOI requested but Window Center/Width is absent")
        array = apply_windowing(array, dataset, index=voi_index)
        applied.append("window")
        return array, applied
    if "VOILUTSequence" not in dataset:
        raise ToolError("VOI LUT requested but VOI LUT Sequence is absent")
    array = apply_voi(array, dataset, index=voi_index)
    applied.append("VOI LUT")
    return array, applied


def render_frame(args: argparse.Namespace) -> dict[str, Any]:
    if not args.acknowledge_pixel_phi:
        raise ToolError(
            "conversion requires --acknowledge-pixel-phi because pixels may identify a person"
        )
    max_input_bytes = parse_size(
        args.max_input_bytes,
        name="max_input_bytes",
        maximum=HARD_MAX_INPUT_BYTES,
    )
    max_decompressed_bytes = parse_size(
        args.max_decompressed_bytes,
        name="max_decompressed_bytes",
        maximum=HARD_MAX_DECOMPRESSED_BYTES,
    )
    max_output_bytes = parse_size(
        args.max_output_bytes,
        name="max_output_bytes",
        maximum=HARD_MAX_OUTPUT_BYTES,
    )
    source = checked_input(
        args.input,
        root=args.root,
        kind="file",
        max_bytes=max_input_bytes,
    )
    destination = checked_output(args.output, root=args.root, force=args.force)
    if paths_overlap(source, destination):
        raise ToolError("image output must not overwrite its DICOM input")
    image_format = _infer_format(args.output, args.format)
    if image_format == "JPEG" and not args.allow_lossy_output:
        raise ToolError("JPEG output requires --allow-lossy-output")
    if image_format == "JPEG" and args.bit_depth != 8:
        raise ToolError("JPEG output supports only --bit-depth 8")

    metadata = safe_dcmread(
        source,
        stop_before_pixels=True,
        force=False,
        specific_tags=METADATA_TAGS,
    )
    frames, frame_warnings = frame_count(metadata)
    if not 0 <= args.frame < frames:
        raise ToolError("requested frame is outside the declared frame range")
    plan = pixel_plan(
        metadata,
        max_frames=max(frames, 1),
        max_decompressed_bytes=HARD_MAX_DECOMPRESSED_BYTES,
    )
    photometric = str(metadata.get("PhotometricInterpretation", ""))
    processing_samples = (
        3 if photometric == "PALETTE COLOR" else plan["samples_per_pixel"]
    )
    # Processing can require a float64 working copy in addition to the decoded
    # frame, masks, and output. Bound peak working memory conservatively.
    working_estimate = plan["bytes_per_frame"] + (
        plan["rows"] * plan["columns"] * processing_samples * 12
    )
    if working_estimate > max_decompressed_bytes:
        raise ToolError(
            "estimated one-frame working memory exceeds the configured limit"
        )

    _, numpy, Image = require_pixel_stack()
    from pydicom.pixels import apply_color_lut, pixel_array

    decoding_plugin = (
        safe_plugin_name(args.decoding_plugin) if args.decoding_plugin else ""
    )
    try:
        array = pixel_array(
            source,
            index=args.frame,
            raw=False,
            decoding_plugin=decoding_plugin,
        )
    except Exception as exc:
        raise ToolError(
            "selected frame could not be decoded with installed pixel plugins"
        ) from exc
    if int(array.nbytes) > max_decompressed_bytes:
        raise ToolError("decoded frame exceeds the configured byte limit")

    samples = int(metadata.get("SamplesPerPixel", 1))
    transforms: list[str] = []
    color_output = samples > 1 or photometric == "PALETTE COLOR"
    if photometric == "PALETTE COLOR":
        try:
            array = apply_color_lut(array, metadata)
        except Exception as exc:
            raise ToolError("palette color LUT could not be applied") from exc
        transforms.append("palette color LUT")
    elif not color_output:
        try:
            array, grayscale_transforms = _apply_grayscale_transforms(
                array,
                metadata,
                modality_transform=args.modality_transform,
                voi=args.voi,
                voi_index=args.voi_index,
            )
        except Exception as exc:
            if isinstance(exc, ToolError):
                raise
            raise ToolError(
                "requested grayscale transform could not be applied"
            ) from exc
        transforms.extend(grayscale_transforms)

    if color_output:
        if array.ndim != 3 or array.shape[-1] not in {3, 4}:
            raise ToolError("decoded color frame has an unexpected shape")
        if array.dtype == numpy.uint8 and bool(numpy.isfinite(array).all()):
            normalized = numpy.asarray(array)
            scale_report = {
                "finite_values": int(array.size),
                "input_max": int(array.max()),
                "input_min": int(array.min()),
                "mapping": "identity uint8",
            }
        else:
            normalized, scale_report = _normalize(array, numpy=numpy, bit_depth=8)
        image = Image.fromarray(normalized)
        if image_format == "JPEG" and image.mode == "RGBA":
            image = image.convert("RGB")
            transforms.append("alpha channel removed for JPEG")
        output_bit_depth = 8
        if photometric.startswith("YBR"):
            transforms.append("pydicom YCbCr-to-RGB decoding")
    else:
        if array.ndim != 2:
            raise ToolError("decoded grayscale frame has an unexpected shape")
        normalized, scale_report = _normalize(
            array, numpy=numpy, bit_depth=args.bit_depth
        )
        if photometric == "MONOCHROME1":
            maximum = 255 if args.bit_depth == 8 else 65535
            normalized = maximum - normalized
            transforms.append("MONOCHROME1 inversion")
        image = Image.fromarray(normalized)
        output_bit_depth = args.bit_depth

    buffer = io.BytesIO()
    save_options: dict[str, Any] = {}
    if image_format == "JPEG":
        save_options = {"quality": args.jpeg_quality, "subsampling": 0}
    try:
        image.save(buffer, format=image_format, **save_options)
    except Exception as exc:
        raise ToolError("rendered image could not be encoded") from exc
    payload = buffer.getvalue()
    atomic_write(
        destination,
        payload,
        force=args.force,
        max_bytes=max_output_bytes,
    )

    return {
        "burned_in_annotation": str(
            metadata.get("BurnedInAnnotation", "ABSENT")
        ).upper(),
        "color_output": color_output,
        "decoded_frame_bytes": int(array.nbytes),
        "diagnostic_use": False,
        "frame": args.frame,
        "frames_declared": frames,
        "image_format": image_format,
        "modality": str(metadata.get("Modality", "UNSPECIFIED")),
        "network_accessed": False,
        "ok": True,
        "original_preserved": True,
        "output_bit_depth": output_bit_depth,
        "output_bytes": len(payload),
        "photometric_interpretation": photometric,
        "recognizable_visual_features": str(
            metadata.get("RecognizableVisualFeatures", "ABSENT")
        ).upper(),
        "scale": scale_report,
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL,
        "transforms_applied_in_order": transforms,
        "warnings": [
            *frame_warnings,
            "Rendered output is for non-diagnostic review only.",
            "Per-frame min-max scaling is not quantitative and is not comparable across frames.",
            "Pixels may contain burned-in PHI or recognizable visual features.",
            "ICC/presentation-state behavior is not fully reproduced by this helper.",
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Render one bounded DICOM frame to PNG, TIFF, or explicit lossy JPEG "
            "for non-diagnostic review."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Local authorized data only. Pixel data may contain PHI, burned-in annotations,
or recognizable anatomy. This helper is not a diagnostic viewer and does not
establish clinical fidelity.

Examples:
  python dicom_to_image.py input.dcm frame.png --acknowledge-pixel-phi
  python dicom_to_image.py multi.dcm frame5.tiff --frame 5 \\
    --voi window --acknowledge-pixel-phi
  python dicom_to_image.py input.dcm frame.jpg --allow-lossy-output \\
    --acknowledge-pixel-phi
""",
    )
    parser.add_argument("input", help="Local DICOM input file")
    parser.add_argument("output", help="New .png, .tif/.tiff, or .jpg/.jpeg file")
    parser.add_argument("--root", default=".", help="Existing local I/O root")
    parser.add_argument("--format", choices=("PNG", "TIFF", "JPEG"))
    parser.add_argument("--frame", type=int, default=0, help="Zero-based frame index")
    parser.add_argument(
        "--modality-transform",
        choices=("auto", "none"),
        default="auto",
        help="Apply Modality LUT/rescale before VOI when present",
    )
    parser.add_argument(
        "--voi",
        choices=("auto", "none", "window", "lut"),
        default="auto",
        help="VOI policy after modality transformation",
    )
    parser.add_argument(
        "--voi-index",
        type=int,
        default=0,
        help="Index for multi-valued windows or VOI LUTs",
    )
    parser.add_argument(
        "--bit-depth",
        type=int,
        choices=(8, 16),
        default=8,
        help="Grayscale PNG/TIFF output depth (color and JPEG are 8-bit)",
    )
    parser.add_argument(
        "--decoding-plugin",
        default="",
        help="Optional installed pydicom decoding plugin name",
    )
    parser.add_argument(
        "--allow-lossy-output",
        action="store_true",
        help="Required for JPEG output",
    )
    parser.add_argument(
        "--jpeg-quality",
        type=int,
        choices=range(1, 96),
        default=95,
        metavar="1..95",
        help="JPEG quality when lossy output is explicitly enabled",
    )
    parser.add_argument(
        "--acknowledge-pixel-phi",
        action="store_true",
        help="Required acknowledgement that pixel data may identify a person",
    )
    parser.add_argument(
        "--max-input-bytes",
        default=str(DEFAULT_MAX_INPUT_BYTES),
        help="Maximum DICOM file bytes (integer or B/KiB/MiB/GiB)",
    )
    parser.add_argument(
        "--max-decompressed-bytes",
        default=str(DEFAULT_MAX_DECOMPRESSED_BYTES),
        help="Maximum estimated one-frame working bytes",
    )
    parser.add_argument(
        "--max-output-bytes",
        default=str(DEFAULT_MAX_OUTPUT_BYTES),
        help="Maximum encoded image bytes",
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite image output, never input"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.frame < 0 or args.voi_index < 0:
            raise ToolError("frame and VOI index must be non-negative")
        report = render_frame(args)
        emit_json(report)
        return 0
    except Exception as exc:  # noqa: BLE001 - sanitize unexpected library errors
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/extract_metadata.py`

```python
#!/usr/bin/env python3
"""Emit a redacted, allowlisted technical DICOM metadata inventory."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from typing import Any

from _common import (
    DEFAULT_MAX_FILES,
    DEFAULT_MAX_INPUT_BYTES,
    HARD_MAX_FILES,
    HARD_MAX_INPUT_BYTES,
    SCHEMA_VERSION,
    TECHNICAL_KEYWORDS,
    ToolError,
    atomic_write,
    bounded_int,
    checked_input,
    checked_output,
    collect_local_files,
    counter_dict,
    emit_json,
    fail_json,
    frame_count,
    json_bytes,
    parse_size,
    paths_overlap,
    require_pydicom,
    safe_dcmread,
)

TOOL = "extract_metadata"


def _uid_description(value: Any) -> dict[str, str] | None:
    if not value:
        return None
    pydicom = require_pydicom()
    uid = pydicom.uid.UID(str(value))
    return {"name": uid.name, "uid": str(uid)}


def _status(value: Any) -> str:
    text = str(value or "").strip().upper()
    if not text:
        return "ABSENT"
    if text in {"YES", "NO"}:
        return text
    return "OTHER"


def allowlisted_record(dataset: Any, *, file_id: str) -> dict[str, Any]:
    """Return only non-identifying technical fields from a metadata-only read."""

    pydicom = require_pydicom()
    transfer = dataset.file_meta.get("TransferSyntaxUID")
    transfer_info = _uid_description(transfer)
    sop_info = _uid_description(dataset.get("SOPClassUID"))
    frames, frame_warnings = frame_count(dataset)
    record: dict[str, Any] = {
        "bits_allocated": (
            int(dataset.BitsAllocated) if "BitsAllocated" in dataset else None
        ),
        "bits_stored": int(dataset.BitsStored) if "BitsStored" in dataset else None,
        "burned_in_annotation": _status(dataset.get("BurnedInAnnotation")),
        "columns": int(dataset.Columns) if "Columns" in dataset else None,
        "file_id": file_id,
        "frames": frames,
        "has_modality_transform": bool(
            "ModalityLUTSequence" in dataset
            or "RescaleSlope" in dataset
            or "RescaleIntercept" in dataset
        ),
        "has_voi_transform": bool(
            "VOILUTSequence" in dataset
            or "WindowCenter" in dataset
            or "WindowWidth" in dataset
        ),
        "high_bit": int(dataset.HighBit) if "HighBit" in dataset else None,
        "lossy_image_compression": _status(dataset.get("LossyImageCompression")),
        "modality": str(dataset.get("Modality", "UNSPECIFIED")),
        "photometric_interpretation": str(
            dataset.get("PhotometricInterpretation", "UNSPECIFIED")
        ),
        "pixel_representation": (
            int(dataset.PixelRepresentation)
            if "PixelRepresentation" in dataset
            else None
        ),
        "recognizable_visual_features": _status(
            dataset.get("RecognizableVisualFeatures")
        ),
        "rows": int(dataset.Rows) if "Rows" in dataset else None,
        "samples_per_pixel": (
            int(dataset.SamplesPerPixel) if "SamplesPerPixel" in dataset else None
        ),
        "sop_class": sop_info,
        "transfer_syntax": transfer_info,
        "warnings": frame_warnings,
    }
    if transfer_info is not None:
        record["transfer_syntax"]["compressed"] = bool(
            pydicom.uid.UID(transfer_info["uid"]).is_compressed
        )
    return record


def aggregate_records(
    records: list[dict[str, Any]], *, read_failures: int
) -> dict[str, Any]:
    modalities: Counter[str] = Counter()
    sop_classes: Counter[str] = Counter()
    transfer_syntaxes: Counter[str] = Counter()
    photometric: Counter[str] = Counter()
    burned_in: Counter[str] = Counter()
    recognizable: Counter[str] = Counter()
    compressed = 0
    image_like = 0
    total_frames = 0
    for record in records:
        modalities[record["modality"]] += 1
        photometric[record["photometric_interpretation"]] += 1
        burned_in[record["burned_in_annotation"]] += 1
        recognizable[record["recognizable_visual_features"]] += 1
        if record["sop_class"]:
            sop_classes[record["sop_class"]["name"]] += 1
        if record["transfer_syntax"]:
            transfer_syntaxes[record["transfer_syntax"]["name"]] += 1
            compressed += int(record["transfer_syntax"].get("compressed", False))
        if record["rows"] is not None and record["columns"] is not None:
            image_like += 1
        total_frames += record["frames"]
    return {
        "burned_in_annotation": counter_dict(burned_in),
        "compressed_files": compressed,
        "image_like_files": image_like,
        "modalities": counter_dict(modalities),
        "photometric_interpretations": counter_dict(photometric),
        "read_failures": read_failures,
        "recognizable_visual_features": counter_dict(recognizable),
        "sop_classes": counter_dict(sop_classes),
        "successful_files": len(records),
        "total_frames_declared": total_frames,
        "transfer_syntaxes": counter_dict(transfer_syntaxes),
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    max_bytes = parse_size(
        args.max_input_bytes,
        name="max_input_bytes",
        maximum=HARD_MAX_INPUT_BYTES,
    )
    max_files = bounded_int(
        args.max_files,
        name="max_files",
        minimum=1,
        maximum=HARD_MAX_FILES,
    )
    source = checked_input(
        args.input,
        root=args.root,
        kind="any",
        max_bytes=max_bytes,
    )
    files = collect_local_files(
        source,
        max_files=max_files,
        max_bytes=max_bytes,
        recursive=args.recursive,
    )
    records: list[dict[str, Any]] = []
    read_failures = 0
    tags = list(TECHNICAL_KEYWORDS) + ["ModalityLUTSequence", "VOILUTSequence"]
    for index, path in enumerate(files, start=1):
        try:
            dataset = safe_dcmread(
                path,
                stop_before_pixels=True,
                force=args.force_dicom_read,
                specific_tags=tags,
            )
            records.append(allowlisted_record(dataset, file_id=f"file-{index:06d}"))
        except ToolError:
            read_failures += 1
    aggregate = aggregate_records(records, read_failures=read_failures)
    report: dict[str, Any] = {
        "aggregate": aggregate,
        "allowlist_only": True,
        "file_names_emitted": False,
        "full_metadata_dump_supported": False,
        "network_accessed": False,
        "ok": bool(records),
        "phi_values_emitted": False,
        "schema_version": SCHEMA_VERSION,
        "technical_inventory_only": True,
        "tool": TOOL,
        "warnings": [
            "DICOM metadata and pixels may contain PHI.",
            "This report omits patient, study, series, instance, date, and free-text identifiers.",
            "Technical inventory is not DICOM conformance or diagnostic validation.",
        ],
    }
    if args.per_file:
        report["records"] = records
    return report


def render_text(report: dict[str, Any]) -> str:
    aggregate = report["aggregate"]
    lines = [
        "Redacted DICOM technical inventory",
        f"Successful files: {aggregate['successful_files']}",
        f"Read failures: {aggregate['read_failures']}",
        f"Image-like files: {aggregate['image_like_files']}",
        f"Compressed files: {aggregate['compressed_files']}",
        f"Declared frames: {aggregate['total_frames_declared']}",
        "No file names, patient/study/series/instance identifiers, dates, or free text emitted.",
        "Not a DICOM conformance or diagnostic report.",
    ]
    for heading, key in (
        ("Modalities", "modalities"),
        ("SOP classes", "sop_classes"),
        ("Transfer syntaxes", "transfer_syntaxes"),
    ):
        lines.append(f"{heading}:")
        values = aggregate[key]
        if not values:
            lines.append("  (none)")
        for name, count in values.items():
            lines.append(f"  {name}: {count}")
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Create a redacted allowlisted technical DICOM inventory; never "
            "prints a full metadata dump or known PHI fields."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Local authorized data only. DICOM metadata and pixels may contain PHI.
The default is aggregate JSON with no file names or per-instance identifiers.

Examples:
  python extract_metadata.py image.dcm
  python extract_metadata.py dicom-dir --recursive --output inventory.json
  python extract_metadata.py image.dcm --per-file --format text
""",
    )
    parser.add_argument("input", help="Local DICOM file or directory")
    parser.add_argument("--root", default=".", help="Existing local I/O root")
    parser.add_argument(
        "--recursive", action="store_true", help="Recursively inspect a directory"
    )
    parser.add_argument(
        "--per-file",
        action="store_true",
        help="Include allowlisted records keyed by synthetic file IDs",
    )
    parser.add_argument(
        "--format", choices=("json", "text"), default="json", help="Output format"
    )
    parser.add_argument("--output", "-o", help="Private local report file")
    parser.add_argument(
        "--force-dicom-read",
        action="store_true",
        help="Parse datasets lacking a File Format header; does not validate them",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=DEFAULT_MAX_FILES,
        help=f"Maximum files to inspect (default: {DEFAULT_MAX_FILES})",
    )
    parser.add_argument(
        "--max-input-bytes",
        default=str(DEFAULT_MAX_INPUT_BYTES),
        help="Maximum bytes per input file (integer or B/KiB/MiB/GiB)",
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite an existing report only"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = build_report(args)
        if args.format == "json":
            payload = json_bytes(report)
        else:
            payload = render_text(report).encode("utf-8")
        if args.output:
            destination = checked_output(args.output, root=args.root, force=args.force)
            source = checked_input(
                args.input,
                root=args.root,
                kind="any",
                max_bytes=parse_size(
                    args.max_input_bytes,
                    name="max_input_bytes",
                    maximum=HARD_MAX_INPUT_BYTES,
                ),
            )
            if source.is_file() and paths_overlap(source, destination):
                raise ToolError("report must not overwrite its input")
            atomic_write(destination, payload, force=args.force)
            emit_json(
                {
                    "network_accessed": False,
                    "ok": report["ok"],
                    "report_written": True,
                    "tool": TOOL,
                }
            )
        else:
            sys.stdout.buffer.write(payload)
        return 0 if report["ok"] else 1
    except Exception as exc:  # noqa: BLE001 - sanitize unexpected library errors
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/pixel_frame_planner.py`

```python
#!/usr/bin/env python3
"""Plan bounded DICOM frame decoding from metadata without loading pixels."""

from __future__ import annotations

import argparse
import re
import sys
from typing import Any

from _common import (
    DEFAULT_MAX_DECOMPRESSED_BYTES,
    DEFAULT_MAX_FRAMES,
    DEFAULT_MAX_INPUT_BYTES,
    HARD_MAX_DECOMPRESSED_BYTES,
    HARD_MAX_FRAMES,
    HARD_MAX_INPUT_BYTES,
    SCHEMA_VERSION,
    ToolError,
    atomic_write,
    bounded_int,
    checked_input,
    checked_output,
    emit_json,
    fail_json,
    json_bytes,
    parse_size,
    paths_overlap,
    pixel_plan,
    require_pydicom,
    safe_dcmread,
    valid_uid,
)

TOOL = "pixel_frame_planner"
FRAME_TOKEN = re.compile(r"^(\d+)(?:-(\d+))?$")
PIXEL_TAGS = [
    "Modality",
    "Rows",
    "Columns",
    "NumberOfFrames",
    "SamplesPerPixel",
    "PhotometricInterpretation",
    "PlanarConfiguration",
    "BitsAllocated",
    "BitsStored",
    "HighBit",
    "PixelRepresentation",
    "ModalityLUTSequence",
    "RescaleIntercept",
    "RescaleSlope",
    "RescaleType",
    "VOILUTSequence",
    "WindowCenter",
    "WindowWidth",
    "VOILUTFunction",
    "ICCProfile",
    "BurnedInAnnotation",
    "RecognizableVisualFeatures",
]


def parse_frame_selection(
    specification: str, *, total_frames: int, max_selected: int
) -> list[int]:
    if specification.strip().casefold() == "all":
        if total_frames > max_selected:
            raise ToolError("'all' exceeds the selected-frame limit")
        return list(range(total_frames))
    selected: set[int] = set()
    for token in specification.split(","):
        token = token.strip()
        match = FRAME_TOKEN.fullmatch(token)
        if not match:
            raise ToolError(
                "frames must use comma-separated indices or inclusive ranges"
            )
        start = int(match.group(1))
        stop = int(match.group(2) or start)
        if stop < start:
            raise ToolError("frame ranges must be ascending")
        if stop >= total_frames:
            raise ToolError("selected frame is outside the declared range")
        if stop - start + 1 > max_selected:
            raise ToolError("one frame range exceeds the selected-frame limit")
        selected.update(range(start, stop + 1))
        if len(selected) > max_selected:
            raise ToolError("selected-frame limit exceeded")
    if not selected:
        raise ToolError("at least one frame must be selected")
    return sorted(selected)


def plan(args: argparse.Namespace) -> dict[str, Any]:
    max_input_bytes = parse_size(
        args.max_input_bytes,
        name="max_input_bytes",
        maximum=HARD_MAX_INPUT_BYTES,
    )
    max_decompressed_bytes = parse_size(
        args.max_decompressed_bytes,
        name="max_decompressed_bytes",
        maximum=HARD_MAX_DECOMPRESSED_BYTES,
    )
    max_frames = bounded_int(
        args.max_frames,
        name="max_frames",
        minimum=1,
        maximum=HARD_MAX_FRAMES,
    )
    max_selected = bounded_int(
        args.max_selected_frames,
        name="max_selected_frames",
        minimum=1,
        maximum=100_000,
    )
    source = checked_input(
        args.input,
        root=args.root,
        kind="file",
        max_bytes=max_input_bytes,
    )
    dataset = safe_dcmread(
        source,
        stop_before_pixels=True,
        force=False,
        specific_tags=PIXEL_TAGS,
    )
    metadata_plan = pixel_plan(
        dataset,
        max_frames=max_frames,
        max_decompressed_bytes=max_decompressed_bytes,
    )
    selected = parse_frame_selection(
        args.frames,
        total_frames=metadata_plan["frames"],
        max_selected=max_selected,
    )
    selected_bytes = metadata_plan["bytes_per_frame"] * len(selected)
    if selected_bytes > max_decompressed_bytes:
        raise ToolError("selected decoded frames exceed the configured byte limit")

    pydicom = require_pydicom()
    transfer_value = str(dataset.file_meta.get("TransferSyntaxUID", ""))
    if not valid_uid(transfer_value):
        raise ToolError("Transfer Syntax UID is absent or invalid")
    transfer = pydicom.uid.UID(transfer_value)
    try:
        transfer_compressed = bool(transfer.is_compressed)
    except ValueError as exc:
        raise ToolError("UID is not recognized as a transfer syntax") from exc
    photometric = str(dataset.get("PhotometricInterpretation", ""))
    samples = metadata_plan["samples_per_pixel"]
    one_frame_shape = (
        [metadata_plan["rows"], metadata_plan["columns"]]
        if samples == 1
        else [metadata_plan["rows"], metadata_plan["columns"], samples]
    )
    transforms: list[str] = []
    if (
        "ModalityLUTSequence" in dataset
        or "RescaleSlope" in dataset
        or "RescaleIntercept" in dataset
    ):
        transforms.append("optional modality LUT/rescale")
    if "VOILUTSequence" in dataset or (
        "WindowCenter" in dataset and "WindowWidth" in dataset
    ):
        transforms.append("optional VOI LUT/window after modality transform")
    if photometric.startswith("YBR"):
        transforms.append("default pydicom YCbCr-to-RGB conversion unless raw=True")
    if photometric == "PALETTE COLOR":
        transforms.append("palette color LUT required for RGB rendering")
    if photometric == "MONOCHROME1":
        transforms.append("presentation inversion may be required")

    return {
        "burned_in_annotation": str(
            dataset.get("BurnedInAnnotation", "ABSENT")
        ).upper(),
        "decode_plan": {
            "all_frames_shape": metadata_plan["shape"],
            "bytes_per_frame_estimate": metadata_plan["bytes_per_frame"],
            "frame_indices": selected,
            "one_frame_shape": one_frame_shape,
            "selected_decoded_bytes_estimate": selected_bytes,
            "use_iter_pixels": len(selected) > 1,
            "use_pixel_array_index": len(selected) == 1,
        },
        "metadata": {
            "bits_allocated": metadata_plan["bits_allocated"],
            "columns": metadata_plan["columns"],
            "frames": metadata_plan["frames"],
            "modality": str(dataset.get("Modality", "UNSPECIFIED")),
            "photometric_interpretation": photometric,
            "rows": metadata_plan["rows"],
            "samples_per_pixel": samples,
            "transfer_syntax": {
                "compressed": transfer_compressed,
                "name": transfer.name,
                "uid": str(transfer),
            },
        },
        "network_accessed": False,
        "ok": True,
        "pixel_data_loaded": False,
        "recognizable_visual_features": str(
            dataset.get("RecognizableVisualFeatures", "ABSENT")
        ).upper(),
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL,
        "transforms_in_semantic_order": transforms,
        "warnings": [
            *metadata_plan["warnings"],
            "Estimates use metadata and do not prove that the codestream matches it.",
            "Pixel decoding can expose PHI and requires independent correctness checks.",
            "Frame rendering is non-diagnostic unless validated in an appropriate system.",
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Plan bounded DICOM pixel frame access, shapes, byte limits, and "
            "display transforms from metadata without decoding pixels."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pixel_frame_planner.py image.dcm
  python pixel_frame_planner.py multi.dcm --frames 0,2-4
  python pixel_frame_planner.py multi.dcm --frames all --max-selected-frames 20

Metadata can be inconsistent with compressed codestreams. This is a resource
and semantics plan, not diagnostic or pixel-correctness validation.
""",
    )
    parser.add_argument("input", help="Local DICOM input file")
    parser.add_argument("--root", default=".", help="Existing local I/O root")
    parser.add_argument(
        "--frames",
        default="0",
        help="Comma-separated zero-based indices/ranges, or 'all' (default: 0)",
    )
    parser.add_argument("--output", "-o", help="Private JSON plan path")
    parser.add_argument(
        "--max-frames",
        type=int,
        default=DEFAULT_MAX_FRAMES,
        help=f"Maximum declared frames (default: {DEFAULT_MAX_FRAMES})",
    )
    parser.add_argument(
        "--max-selected-frames",
        type=int,
        default=100,
        help="Maximum selected frames (default: 100)",
    )
    parser.add_argument(
        "--max-input-bytes",
        default=str(DEFAULT_MAX_INPUT_BYTES),
        help="Maximum DICOM input bytes",
    )
    parser.add_argument(
        "--max-decompressed-bytes",
        default=str(DEFAULT_MAX_DECOMPRESSED_BYTES),
        help="Maximum estimated decoded bytes",
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite an existing plan only"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = plan(args)
        if args.output:
            destination = checked_output(args.output, root=args.root, force=args.force)
            source = checked_input(
                args.input,
                root=args.root,
                kind="file",
                max_bytes=parse_size(
                    args.max_input_bytes,
                    name="max_input_bytes",
                    maximum=HARD_MAX_INPUT_BYTES,
                ),
            )
            if paths_overlap(source, destination):
                raise ToolError("plan must not overwrite its input")
            atomic_write(destination, json_bytes(report), force=args.force)
            emit_json({"ok": True, "plan_written": True, "tool": TOOL})
        else:
            emit_json(report)
        return 0
    except Exception as exc:  # noqa: BLE001 - sanitize unexpected library errors
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/transfer_syntax_inspector.py`

```python
#!/usr/bin/env python3
"""Inspect installed pydicom transfer-syntax decoder/encoder capabilities."""

from __future__ import annotations

import argparse
import importlib.metadata
import sys
from pathlib import Path
from typing import Any

from _common import (
    DEFAULT_MAX_INPUT_BYTES,
    HARD_MAX_INPUT_BYTES,
    SCHEMA_VERSION,
    ToolError,
    atomic_write,
    checked_input,
    checked_output,
    emit_json,
    fail_json,
    json_bytes,
    parse_size,
    paths_overlap,
    require_pydicom,
    safe_dcmread,
    valid_uid,
)

TOOL = "transfer_syntax_inspector"
KNOWN_TRANSFER_SYNTAXES = (
    "1.2.840.10008.1.2",
    "1.2.840.10008.1.2.1",
    "1.2.840.10008.1.2.1.99",
    "1.2.840.10008.1.2.2",
    "1.2.840.10008.1.2.4.50",
    "1.2.840.10008.1.2.4.51",
    "1.2.840.10008.1.2.4.57",
    "1.2.840.10008.1.2.4.70",
    "1.2.840.10008.1.2.4.80",
    "1.2.840.10008.1.2.4.81",
    "1.2.840.10008.1.2.4.90",
    "1.2.840.10008.1.2.4.91",
    "1.2.840.10008.1.2.4.201",
    "1.2.840.10008.1.2.4.202",
    "1.2.840.10008.1.2.4.203",
    "1.2.840.10008.1.2.5",
)
PACKAGES = (
    "pydicom",
    "numpy",
    "Pillow",
    "pylibjpeg",
    "pylibjpeg-libjpeg",
    "pylibjpeg-openjpeg",
    "pylibjpeg-rle",
    "pyjpegls",
    "python-gdcm",
)


def _package_versions() -> dict[str, str | None]:
    versions: dict[str, str | None] = {}
    for package in PACKAGES:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
    return versions


def _codec_capability(uid_value: str) -> dict[str, Any]:
    pydicom = require_pydicom()
    from pydicom.pixels import get_decoder, get_encoder

    uid = pydicom.uid.UID(uid_value)
    try:
        compressed: bool | None = bool(uid.is_compressed)
        implicit_vr: bool | None = bool(uid.is_implicit_VR)
        little_endian: bool | None = bool(uid.is_little_endian)
    except ValueError:
        compressed = None
        implicit_vr = None
        little_endian = None
    record: dict[str, Any] = {
        "compressed": compressed,
        "decoder": {
            "available": False,
            "available_plugins": [],
            "implemented": False,
            "missing_dependencies": [],
        },
        "encoder": {
            "available": False,
            "available_plugins": [],
            "implemented": False,
            "missing_dependencies": [],
        },
        "implicit_vr": implicit_vr,
        "little_endian": little_endian,
        "name": uid.name,
        "retired": uid_value == "1.2.840.10008.1.2.2",
        "uid": uid_value,
    }
    try:
        decoder = get_decoder(uid)
        record["decoder"] = {
            "available": bool(decoder.is_available),
            "available_plugins": list(decoder.available_plugins),
            "implemented": True,
            "missing_dependencies": list(decoder.missing_dependencies),
        }
    except (NotImplementedError, ValueError):
        pass
    try:
        encoder = get_encoder(uid)
        record["encoder"] = {
            "available": bool(encoder.is_available),
            "available_plugins": list(encoder.available_plugins),
            "implemented": True,
            "missing_dependencies": list(encoder.missing_dependencies),
        }
    except (NotImplementedError, ValueError):
        pass
    return record


def inspect(args: argparse.Namespace) -> dict[str, Any]:
    requested = list(args.uid or [])
    selected_uid: str | None = None
    source: Path | None = None
    if args.input:
        max_bytes = parse_size(
            args.max_input_bytes,
            name="max_input_bytes",
            maximum=HARD_MAX_INPUT_BYTES,
        )
        source = checked_input(
            args.input,
            root=args.root,
            kind="file",
            max_bytes=max_bytes,
        )
        dataset = safe_dcmread(source, stop_before_pixels=True, force=False)
        selected_uid = str(dataset.file_meta.get("TransferSyntaxUID", ""))
        if not valid_uid(selected_uid):
            raise ToolError("input Transfer Syntax UID is absent or invalid")
        requested.append(selected_uid)
    if not requested:
        requested.extend(KNOWN_TRANSFER_SYNTAXES)
    unique: list[str] = []
    for value in requested:
        if not valid_uid(value):
            raise ToolError("each --uid must be a valid numeric DICOM UID")
        if value not in unique:
            unique.append(value)
    if len(unique) > 256:
        raise ToolError("at most 256 transfer syntaxes may be inspected")
    records = [_codec_capability(value) for value in unique]
    return {
        "capability_scope": (
            "Installed plugin discovery only; image-specific bit depth, color, "
            "platform, and codestream constraints still apply."
        ),
        "input_selected_uid": selected_uid,
        "network_accessed": False,
        "ok": True,
        "package_versions": _package_versions(),
        "pixel_data_loaded": False,
        "records": records,
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL,
        "warnings": [
            "An available plugin is not proof that a particular image will decode correctly.",
            "Verify decoded pixels independently before scientific or clinical use.",
            "Compression can change SOP Instance UID and image metadata; review the pydicom API behavior.",
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect pydicom 3.0.2 decoder/encoder implementation and installed "
            "plugin availability without loading pixel data."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python transfer_syntax_inspector.py
  python transfer_syntax_inspector.py --input image.dcm
  python transfer_syntax_inspector.py --uid 1.2.840.10008.1.2.4.90

Availability is a deployment preflight, not a pixel-correctness guarantee.
""",
    )
    parser.add_argument("--input", help="Optional local DICOM file")
    parser.add_argument(
        "--uid",
        action="append",
        help="Transfer Syntax UID to inspect; repeat as needed",
    )
    parser.add_argument("--root", default=".", help="Existing local I/O root")
    parser.add_argument("--output", "-o", help="Private JSON report path")
    parser.add_argument(
        "--max-input-bytes",
        default=str(DEFAULT_MAX_INPUT_BYTES),
        help="Maximum optional DICOM input bytes",
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite an existing report only"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = inspect(args)
        if args.output:
            destination = checked_output(args.output, root=args.root, force=args.force)
            if args.input:
                source = checked_input(
                    args.input,
                    root=args.root,
                    kind="file",
                    max_bytes=parse_size(
                        args.max_input_bytes,
                        name="max_input_bytes",
                        maximum=HARD_MAX_INPUT_BYTES,
                    ),
                )
                if paths_overlap(source, destination):
                    raise ToolError("report must not overwrite its input")
            atomic_write(destination, json_bytes(report), force=args.force)
            emit_json({"ok": True, "report_written": True, "tool": TOOL})
        else:
            emit_json(report)
        return 0
    except Exception as exc:  # noqa: BLE001 - sanitize unexpected library errors
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/uid_mapping_validator.py`

```python
#!/usr/bin/env python3
"""Validate bounded DICOM UID mapping consistency without printing UIDs."""

from __future__ import annotations

import argparse
import os
import stat
import sys
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from _common import (
    MAX_JSON_BYTES,
    SCHEMA_VERSION,
    ToolError,
    atomic_write,
    bounded_int,
    checked_input,
    checked_output,
    counter_dict,
    derive_uid,
    emit_json,
    fail_json,
    json_bytes,
    load_json,
    paths_overlap,
    require_text,
    sha256_text,
    valid_uid,
)

TOOL = "uid_mapping_validator"
STANDARD_ROOT = "1.2.840.10008"


def _load_key(path: Path) -> bytes:
    info = path.stat()
    if os.name != "nt":
        if stat.S_IMODE(info.st_mode) & 0o077:
            raise ToolError("UID key permissions must deny group and other access")
        if hasattr(os, "getuid") and info.st_uid != os.getuid():
            raise ToolError("UID key must be owned by the current user")
    payload = path.read_bytes()
    if len(payload) == 64:
        try:
            payload = bytes.fromhex(payload.decode("ascii"))
        except (UnicodeError, ValueError):
            pass
    if len(payload) < 32:
        raise ToolError("UID key must contain at least 32 bytes")
    return payload[:128]


def validate_mapping(
    document: Any,
    *,
    max_entries: int,
    require_2_25: bool,
    key: bytes | None = None,
    scope: str | None = None,
) -> dict[str, Any]:
    if not isinstance(document, Mapping):
        raise ToolError("mapping document must be a JSON object")
    allowed = {"entries", "schema_version", "scope_sha256", "sensitive", "tool"}
    unknown = sorted(set(document) - allowed)
    if unknown:
        raise ToolError(f"mapping document has unsupported keys: {', '.join(unknown)}")
    entries = document.get("entries")
    if not isinstance(entries, list):
        raise ToolError("mapping entries must be a JSON array")
    bounded_int(
        len(entries),
        name="mapping entry count",
        minimum=0,
        maximum=max_entries,
    )
    if (key is None) != (scope is None):
        raise ToolError("deterministic verification requires both key and scope")
    if scope is not None:
        expected_scope_hash = sha256_text(scope)
        stored_scope_hash = document.get("scope_sha256")
        if stored_scope_hash and stored_scope_hash != expected_scope_hash:
            raise ToolError("mapping scope digest does not match the supplied scope")

    errors: Counter[str] = Counter()
    originals: dict[str, str] = {}
    replacements: dict[str, str] = {}
    for entry in entries:
        if not isinstance(entry, Mapping) or set(entry) != {
            "original",
            "replacement",
        }:
            errors["entry_schema_invalid"] += 1
            continue
        original = entry.get("original")
        replacement = entry.get("replacement")
        if not valid_uid(original):
            errors["original_uid_invalid"] += 1
            continue
        if not valid_uid(replacement):
            errors["replacement_uid_invalid"] += 1
            continue
        if original == replacement:
            errors["unchanged_uid"] += 1
        if original == STANDARD_ROOT or original.startswith(STANDARD_ROOT + "."):
            errors["standard_uid_mapped"] += 1
        if require_2_25 and not replacement.startswith("2.25."):
            errors["replacement_not_2_25"] += 1
        previous = originals.get(original)
        if previous is not None and previous != replacement:
            errors["one_original_to_multiple_replacements"] += 1
        originals[original] = replacement
        previous_original = replacements.get(replacement)
        if previous_original is not None and previous_original != original:
            errors["replacement_collision"] += 1
        replacements[replacement] = original
        if key is not None and scope is not None:
            expected = derive_uid(original, key=key, scope=scope)
            if replacement != expected:
                errors["deterministic_mapping_mismatch"] += 1
    return {
        "deterministic_mapping_verified": key is not None,
        "duplicate_entries": len(entries) - len(originals),
        "entries": len(entries),
        "error_codes": counter_dict(errors),
        "errors": sum(errors.values()),
        "network_accessed": False,
        "ok": not errors,
        "original_uids_emitted": False,
        "replacement_uids_emitted": False,
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL,
        "unique_originals": len(originals),
        "unique_replacements": len(replacements),
        "warnings": [
            "UID maps contain identifiers and must be stored as sensitive data.",
            "Mapping consistency does not establish de-identification or referential completeness.",
            "Structural UIDs such as SOP Class and Transfer Syntax UIDs must not be remapped.",
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate UID syntax, one-to-one mapping, collisions, standard-UID "
            "protection, and optional keyed deterministic derivation."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
The mapping file is sensitive because it contains original identifiers. This
tool emits aggregate findings only and performs no network access.

Examples:
  python uid_mapping_validator.py uid-map.json
  python uid_mapping_validator.py uid-map.json --uid-key-file project.key \\
    --uid-scope study-export-v1
""",
    )
    parser.add_argument("mapping", help="Local sensitive UID mapping JSON")
    parser.add_argument("--root", default=".", help="Existing local I/O root")
    parser.add_argument("--uid-key-file", help="Optional local deterministic key")
    parser.add_argument("--uid-scope", help="Scope paired with --uid-key-file")
    parser.add_argument(
        "--allow-non-2-25",
        action="store_true",
        help="Allow valid replacement UIDs outside the 2.25 UUID-derived root",
    )
    parser.add_argument(
        "--max-entries",
        type=int,
        default=100_000,
        help="Maximum mapping entries (default: 100000)",
    )
    parser.add_argument("--output", "-o", help="Private aggregate JSON report")
    parser.add_argument(
        "--force", action="store_true", help="Overwrite an existing report only"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        max_entries = bounded_int(
            args.max_entries,
            name="max_entries",
            minimum=1,
            maximum=1_000_000,
        )
        mapping_path = checked_input(
            args.mapping,
            root=args.root,
            kind="file",
            max_bytes=MAX_JSON_BYTES,
        )
        key: bytes | None = None
        scope: str | None = None
        if args.uid_key_file or args.uid_scope:
            if not args.uid_key_file or not args.uid_scope:
                raise ToolError("--uid-key-file and --uid-scope must be used together")
            key_path = checked_input(
                args.uid_key_file,
                root=args.root,
                kind="file",
                max_bytes=4 * 1024,
            )
            key = _load_key(key_path)
            scope = require_text(args.uid_scope, name="uid_scope", maximum=128)
        report = validate_mapping(
            load_json(mapping_path),
            max_entries=max_entries,
            require_2_25=not args.allow_non_2_25,
            key=key,
            scope=scope,
        )
        if args.output:
            destination = checked_output(args.output, root=args.root, force=args.force)
            if paths_overlap(mapping_path, destination):
                raise ToolError("report must not overwrite the sensitive mapping")
            atomic_write(destination, json_bytes(report), force=args.force)
            emit_json(
                {
                    "ok": report["ok"],
                    "report_written": True,
                    "tool": TOOL,
                }
            )
        else:
            emit_json(report)
        return 0 if report["ok"] else 1
    except Exception as exc:  # noqa: BLE001 - sanitize unexpected library errors
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
```
