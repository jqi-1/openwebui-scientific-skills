---
name: imaging-data-commons
description: Query and download public cancer imaging data from NCI Imaging Data Commons. Invoke for any question about IDC collections, cancer imaging datasets, DICOM data access, radiology (CT, MR, PET) or pathology AI training sets, metadata queries, visualization, or license checks — even when the user doesn't explicitly mention "IDC". No authentication required.
---

# Imaging Data Commons

## Overview

Query and download public cancer imaging data from the National Cancer Institute Imaging Data Commons (IDC). No authentication required for data access.

**Expected network access:** IDC metadata is reachable three ways — a local DuckDB index shipped with the `idc-index` Python package (no network), or the hosted IDC service over MCP or REST (`api.imaging.datacommons.cancer.gov`, no authentication). File downloads use public GCS (`storage.googleapis.com`) and AWS S3 (`s3.amazonaws.com`) — no authentication required. DICOMweb access uses either the public IDC proxy (`proxy.imaging.datacommons.cancer.gov`, no auth) or the Google Cloud Healthcare API (`healthcare.googleapis.com`, requires GCP authentication). Optional BigQuery queries (`bigquery.googleapis.com`) also require GCP authentication. No credentials or environment variables are accessed by this skill.

**Current IDC Data Version: v24** (always verify — see *Best Practices*)

**Choose the access path first.** There is no single default: the cheapest correct path depends
on the session and the task.

1. **Session already has the IDC MCP server?** Route discovery and metadata there — see *IDC
   MCP Server*.
2. **Otherwise, is `idc-index` installed?** Run `python scripts/check_version.py`. If it passes,
   use `idc-index` for everything.
3. **Not installed, and the task is read-only metadata** — counts, attribute values, collection
   lookups, SQL under 10 000 rows, licenses, citations, viewer URLs? **Use the REST API over
   `curl`; do not install anything.** Installing costs ~77 MB of packaged index data plus
   pandas, pyarrow, and duckdb, which a metadata question does not need. See *Data Access
   Options*.
4. **Not installed, and the task needs more than metadata** — downloading files, pandas or
   plotting, pydicom/SimpleITK, pathology tiling, results past 10 000 rows, or a version-pinned
   script the user re-runs? Install `idc-index`: `check_version.py` exits non-zero and prints
   the exact install command for the running interpreter. Prefer a virtual environment, then
   restart Python.

`idc-index` ([GitHub](https://github.com/imagingdatacommons/idc-index)) is still the most
capable path and the only one that moves image bytes; the rule is just not to pay for it before
the task calls for it. `check_version.py` never installs anything itself — it also flags a newer
`idc-index` or skill release when one exists.

**Setup for the `idc-index` path:**

```python
from idc_index import IDCClient
client = IDCClient()

# Verify IDC data version (should be "v24")
print(f"IDC data version: {client.get_idc_version()}")
```

**Core workflow:** query metadata with `client.sql_query()` → download with
`client.download_from_selection()` → visualize with `client.get_viewer_URL()`. Python examples
below assume this `client`; *Data Access Options* has the REST equivalents. For current data
scale, run the summary query in `references/sql_patterns.md` or `GET /v3/stats`.

## IDC MCP Server

IDC operates a hosted MCP server at `https://api.imaging.datacommons.cancer.gov/mcp`
(streamable HTTP, no authentication). Where it is available it complements — it does not
replace — the `idc-index` workflow below.

**Identify it** by the MCP resource `idc://guide`, or by three or more of the tool names
`build_cohort`, `get_cohort_urls`, `list_analysis_results`, and `get_idc_version`. Generic
names such as `run_sql` are not evidence on their own. If identification is ambiguous, use
`idc-index`.

**If this session has the server**, treat it as authoritative for discovery and metadata —
IDC version, counts, attribute values, cohort building, metadata SQL — and follow the
server's own instructions rather than re-deriving them from this file. Its data version is
whatever the server reports: call `get_idc_version` instead of relying on the version pinned
in this file.

Return here for what the server does not do: downloading files, local pandas/notebook
analysis, DICOMweb, BigQuery, digital pathology tiling, and reproducible scripts. Hand off by
passing SeriesInstanceUIDs from the server to `client.download_from_selection(...)`, and run
`scripts/check_version.py` at that point.

**If it is not available**, the identical service is reachable with no configuration as a REST
API at `https://api.imaging.datacommons.cancer.gov/v3` — use it for read-only metadata rather
than installing `idc-index`, per the routing gate in *Overview*. Suggest connecting the MCP
server at most once, only for repeated interactive discovery, and never change the user's
configuration yourself.

See `references/mcp_guide.md` for the tool inventory, handoff patterns, and per-host notes.

## When to Use This Skill

- Finding publicly available radiology (CT, MR, PET) or pathology (slide microscopy) images
- Selecting image subsets by cancer type, modality, anatomical site, or other metadata
- Downloading DICOM data from IDC
- Checking data licenses before use in research or commercial applications
- Visualizing medical images in a browser without local DICOM viewer software

## Quick Navigation

Inline below: the MCP/REST routing rules, the IDC data model, the index tables and how they
join, the core API patterns (query, download, visualize, license, cite), best practices, and
troubleshooting.

**Reference Guides (load on demand):**

| Guide | When to Load |
|-------|--------------|
| `index_tables_guide.md` | Complex JOINs, schema discovery, DataFrame access |
| `use_cases.md` | End-to-end workflows: training datasets, batch downloads, DICOM reading with pydicom/SimpleITK, pipeline integration |
| `sql_patterns.md` | Quick SQL patterns for filter discovery, annotations, size estimation |
| `clinical_data_guide.md` | Clinical/tabular data, imaging+clinical joins, value mapping |
| `licensing_and_citation.md` | Commercial-use questions, mixed-license cohorts, citation formats |
| `cloud_storage_guide.md` | Direct S3/GCS access, versioning, UUID mapping |
| `dicomweb_guide.md` | DICOMweb endpoints, PACS integration |
| `digital_pathology_guide.md` | Slide microscopy (SM), annotations (ANN), pathology workflows |
| `bigquery_guide.md` | Full DICOM metadata, private elements (requires GCP) |
| `cli_guide.md` | Command-line tools (`idc download`, manifest files) |
| `parquet_access_guide.md` | Direct Parquet queries via GCS (no idc-index install needed) |
| `mcp_guide.md` | Hosted IDC MCP server: tool inventory, identification, handoff to `idc-index` |
| `rest_api_guide.md` | Hosted IDC REST API: endpoints, filter syntax, SQL over HTTP, manifests |

## IDC Data Model

IDC adds two grouping levels above the standard DICOM hierarchy (Patient → Study → Series → Instance):

- **collection_id**: Groups patients by disease, modality, or research focus (e.g., `tcga_luad`, `nlst`). A patient belongs to exactly one collection.
- **analysis_result_id**: Identifies derived objects (segmentations, annotations, radiomics features) across one or more original collections. Use it to find AI-generated or expert annotations, while `collection_id` finds original imaging data (which may itself include deposited annotations).

**Key identifiers for queries:**
| Identifier | Scope | Use for |
|------------|-------|---------|
| `collection_id` | Dataset grouping | Filtering by project/study |
| `PatientID` | Patient | Grouping images by patient |
| `StudyInstanceUID` | DICOM study | Grouping of related series, visualization |
| `SeriesInstanceUID` | DICOM series | Grouping of related series, visualization |

## Index Tables

The `idc-index` package provides multiple metadata index tables, accessible via SQL or as pandas DataFrames. The REST API exposes the same tables through `GET /tables` and `POST /sql`.

**Important:** `client.indices_overview` is the authoritative source for current table descriptions, available columns, and their types — query it when writing SQL or exploring data structure. It also answers "which table contains column X"; see `references/index_tables_guide.md` for that search pattern and full schema discovery.

### Available Tables

Always call `client.fetch_index("table_name")` before querying any index table — it is safe and idempotent for all tables, including those loaded automatically at startup.

| Family | Tables | Granularity |
|--------|--------|-------------|
| Core | `index` (primary metadata for all current data), `collections_index`, `analysis_results_index` | series / collection / analysis result |
| Modality acquisition parameters | `ct_index`, `mr_index`, `pt_index`, `contrast_index` | 1 row = 1 series of that modality |
| Derived objects | `seg_index`, `rtstruct_index`, `ann_index`, `ann_group_index` | 1 row = 1 series (or annotation group) |
| Microscopy | `sm_index`, `sm_instance_index` | 1 row = 1 SM series / instance |
| Geometry, clinical, history | `volume_geometry_index`, `clinical_index`, `version_metadata_index`, `prior_versions_index` | see guide |

`references/index_tables_guide.md` has the full inventory with each table's columns and
contents — load it when you need to know what a specialized table actually holds.

**`prior_versions_index` is for reproducibility only.** It contains series permanently *removed*
from IDC, with zero overlap with `index`. Use it only to reproduce work against a prior IDC
version. Do NOT use it for version history or "what's new" questions — those use
`series_init_idc_version` / `series_revised_idc_version` in the main `index` table, which are
not equivalent to this table's `min_idc_version` / `max_idc_version`.

### Joining Tables

**`SeriesInstanceUID` is the universal join key** for all series-level specialized tables: `sm_index`, `sm_instance_index`, `seg_index`, `ann_index`, `ann_group_index`, `contrast_index`, `volume_geometry_index`, `rtstruct_index`, `ct_index`, `mr_index`, `pt_index`. Always join these to `index` on `SeriesInstanceUID`. The exceptions below use different column names.

| Join Column | Tables | Use Case |
|-------------|--------|----------|
| `collection_id` | index, prior_versions_index, collections_index, clinical_index | Link series to collection metadata or clinical data |
| `analysis_result_id` | index, analysis_results_index | Link series to analysis result metadata (annotations, segmentations) |
| `source_DOI` | index, analysis_results_index | Link by publication DOI |
| `segmented_SeriesInstanceUID` | seg_index → index | Link segmentation to its source image series (`seg_index.segmented_SeriesInstanceUID = index.SeriesInstanceUID`) |
| `referenced_SeriesInstanceUID` | ann_index → index, rtstruct_index → index | Link annotation or RTSTRUCT to its source image series |

**Note:** `subjects`, `updated`, and `description` appear in multiple tables but have different meanings (counts vs identifiers, different update contexts). Joining `prior_versions_index` to `index` on `SeriesInstanceUID` always returns zero rows — see the warning above.

For detailed join examples, schema discovery patterns, key columns reference, and DataFrame access, see `references/index_tables_guide.md`.

### Clinical Data Access

Clinical (non-imaging) attributes — staging, demographics, therapy — live in per-collection
tables. `client.fetch_index("clinical_index")` loads the dictionary mapping columns to
collections; `client.get_clinical_table(name)` returns one table as a DataFrame.

See `references/clinical_data_guide.md` for the discovery workflow, coded-value mapping, and
joining clinical data with imaging.

## Data Access Options

| Method | Auth | Best For | Reference |
|--------|------|----------|-----------|
| `idc-index` | No | Downloads, pandas analysis, unbounded queries — the most capable path | This document |
| IDC MCP server | No | Discovery, cohort building, metadata when the session already has it | `mcp_guide.md` |
| IDC REST API | No | Metadata with no install, from any language or shell — the default when `idc-index` is absent | `rest_api_guide.md` |
| Direct Parquet (GCS) | No | Version-pinned queries, or results past the REST row cap | `parquet_access_guide.md` |
| Cloud storage (S3/GCS) | No | Direct file access, bulk transfer, custom pipelines | `cloud_storage_guide.md` |
| DICOMweb via IDC proxy | No | Tool and PACS integration; daily quota, so testing and moderate use | `dicomweb_guide.md` |
| DICOMweb via Google Healthcare | Yes (GCP) | The same DICOMweb API at production volume, without the proxy quota | `dicomweb_guide.md` |
| SlicerIDCBrowser | No | 3D visualization and analysis in 3D Slicer | https://github.com/ImagingDataCommons/SlicerIDCBrowser |
| BigQuery | Yes (GCP) | Full DICOM metadata, private elements, SR measurements — last resort | `bigquery_guide.md` |

**The IDC Portal (https://portal.imaging.datacommons.cancer.gov/) is interactive only** —
browser-based exploration, manual cohort selection, and download. Unlike every option above it
has no programmatic interface, so point a user there to browse or click through data
themselves; never use it as a step in a script or workflow.

**REST API — the no-install metadata path**

`https://api.imaging.datacommons.cancer.gov/v3`, no authentication: discovery, cohort counts and
manifests, read-only SQL, clinical tables, viewer URLs, licenses, citations. It is the same
service as the MCP server over plain HTTP, so it needs no configuration. It never moves image
bytes — switch to `idc-index` to download, to get a DataFrame, or for results past 10 000 rows.

```bash
B=https://api.imaging.datacommons.cancer.gov/v3
curl -s $B/version   # idc_version, idc_index_data_version, api_version
curl -s $B/stats     # collections, patients, studies, series, instances, size_TB
curl -s "$B/attributes/Modality/values?limit=5"   # real filter values, with counts
curl -s $B/sql -H 'content-type: application/json' \
  -d '{"sql":"SELECT collection_id, COUNT(*) n FROM index GROUP BY 1 ORDER BY n DESC LIMIT 3"}'
curl -s $B/cohort/counts -H 'content-type: application/json' \
  -d '{"filters":{"terms":{"collection_id":["rider_pilot"]}}}'
```

**The filter object always goes under `filters`** — on `cohort/counts`, `cohort/manifest`,
`cohort/manifest.txt`, `licenses`, and `citations` alike. A bare filter or an unrecognized key is
a 422 naming the fix; an unfiltered series-enumerating request is a 400, not the whole archive.
Every filtered response echoes `filters_applied` and `warnings` — read them, because they name
any predicate the server dropped. A zero count with empty `warnings` therefore means the filter
matched nothing, not that a value was miscased; miscasing produces a warning that says so.

`POST /sql` takes one read-only `SELECT`/`WITH` over the tables `idc-index` exposes plus
`clinical.<table>`; `max_rows` defaults to 5 000, caps at 10 000, and `truncated` flags clipping.
`GET /attributes` lists the 19 filterable attributes — clinical values, segmented anatomy, and
acquisition parameters are not among them and need SQL. There is no rate limit or quota. **Use
v3 only:** V1 and V2 are superseded and scheduled for shutdown, so port any `/v1/`- or
`Modality_btw`-style example a user brings rather than extending it.

Both sides build on `idc-index-data`, so compare the API's `idc_index_data_version` against local
`idc_index_data.__version__` before mixing them: the **major is the IDC data release** (`24.x.y`
serves `v24`), so differing minor/patch means the series are identical. If the API is a whole
release ahead, `idc-index` **cannot download the extra series** — it silently skips what its own
index does not list — so either upgrade it (run `scripts/check_version.py` for the right command)
or transfer directly from the bucket with `s5cmd --no-sign-request`.

See `references/rest_api_guide.md` for the endpoint reference, filter grounding, limits, and the
manifest-based download flow.

**Cloud storage organization**

All DICOM files live in public buckets mirrored between AWS S3 and GCS, organized by CRDC UUIDs
(not DICOM UIDs) to support versioning, as `<crdc_series_uuid>/<crdc_instance_uuid>.dcm`. Access
is free (no egress fees) via AWS CLI, gsutil, or s5cmd with anonymous access; use the
`series_aws_url` column for S3 URLs. Note that `idc-open-data-cr` / `idc-open-cr` (~4% of data)
is commercial-use restricted (CC BY-NC). See `references/cloud_storage_guide.md` for the full
bucket list and UUID mapping.

**DICOMweb access**

IDC data is available via DICOMweb (Google Cloud Healthcare API) for PACS integration and
DICOMweb-compatible tools: a public proxy (no auth, daily quota) for testing and moderate
queries, or Google Healthcare (GCP auth) for production volumes. See
`references/dicomweb_guide.md`.

**Direct Parquet access**

The idc-index metadata tables are also published as Parquet on a public GCS bucket
(`idc-index-data-artifacts`), queryable with DuckDB or pandas. This needs DuckDB installed
and cannot reach the per-collection clinical tables, so prefer REST `/sql` for ad-hoc metadata;
choose Parquet to pin a data version or for results past the REST row cap. See
`references/parquet_access_guide.md`.

## Core Capabilities

The patterns below are the ones that go wrong when recalled from memory rather than checked.
Worked examples for each area live in the reference guides named inline.

### 1. Discovery — enumerate values before filtering on them

Filtering on a guessed `Modality` or `BodyPartExamined` string is the most common cause of an
empty result set. Enumerate first:

```python
modalities = client.sql_query("""
    SELECT DISTINCT Modality, COUNT(*) as series_count
    FROM index
    GROUP BY Modality
    ORDER BY series_count DESC
""")
print(modalities)
```

The same pattern works for any filter column, optionally narrowed by another —
`BodyPartExamined` within a `Modality`, `Manufacturer`, `collection_id`. On the REST path this
grounding is a single call — `GET /attributes/{attr}/values` returns values with counts — and the
cohort endpoints report a miscased value in `warnings` rather than as an empty result.

Two indices carry curated collection-level metadata the primary `index` does not, both
requiring `client.fetch_index(...)` first: `collections_index` (cancer types, tumor locations,
species, subject counts) and `analysis_results_index` (derived datasets — AI segmentations,
expert annotations, radiomics — with their source collections and modalities).

**Cancer type lives in `collections_index.cancer_types`, not in `index`** — filtering by
cancer type requires a join:

```python
client.fetch_index("collections_index")
results = client.sql_query("""
    SELECT i.collection_id, i.PatientID, i.SeriesInstanceUID, i.Modality
    FROM index i
    JOIN collections_index c ON i.collection_id = c.collection_id
    WHERE c.cancer_types LIKE '%Breast%'
      AND i.Modality = 'MR'
    LIMIT 20
""")
```

`client.sql_query()` returns a pandas DataFrame. Confirm column names with
`client.get_index_schema('index')` or `client.indices_overview` before writing a query rather
than assuming them.

See `references/sql_patterns.md` for filter-value discovery, annotation and segmentation
queries, size estimation, clinical linking, and version tracking ("what's new in vX" — use
`series_init_idc_version` / `series_revised_idc_version` in `index`, never
`prior_versions_index`).

### 2. Downloading DICOM files

**The two download methods take their first two arguments in opposite order.** This is the
most common source of broken IDC code — check it rather than recalling it:

| Method | First arg | Second arg | Use when |
|--------|-----------|------------|----------|
| `download_from_selection` | `downloadDir` (required) | filter kwargs (optional) | Filtering by collection, patient, study, or series |
| `download_dicom_series` | `seriesInstanceUID` (required) | `downloadDir` (required) | Downloading specific series by UID only |

**`download_from_selection` takes filter keyword arguments, NOT a DataFrame.** The name
"from_selection" refers to filtering the IDC index by criteria — not to accepting a pandas
DataFrame. To download query results, extract the UIDs into a list first:

```python
# Step 1: Query for series UIDs
series_df = client.sql_query("""
    SELECT SeriesInstanceUID
    FROM index
    WHERE Modality = 'CT'
      AND BodyPartExamined = 'CHEST'
      AND collection_id = 'nlst'
    LIMIT 5
""")

# Step 2: Extract UIDs as a list from the DataFrame
uids = list(series_df['SeriesInstanceUID'].values)

# Step 3: Pass the list to download_from_selection (NOT the DataFrame itself)
client.download_from_selection(
    downloadDir="./data/lung_ct",
    seriesInstanceUID=uids       # list of strings, not a DataFrame
)

# Alternative: download_dicom_series has seriesInstanceUID as FIRST arg (different order!)
client.download_dicom_series(
    seriesInstanceUID=uids,      # FIRST arg here
    downloadDir="./data/lung_ct"
)

# Whole collection: downloadDir is still the FIRST positional argument
client.download_from_selection(downloadDir="./data/rider", collection_id="rider_pilot")
```

Both methods default to AWS; pass `source_bucket_location="gcs"` to pull from Google Storage.

**Downloaded files are named `<crdc_instance_uuid>.dcm`, not by SOPInstanceUID.** The DICOM
UIDs are preserved inside the file metadata, not in the filename. Use the `crdc_instance_uuid`
column to map files back to the series they came from.

`idc download <collection|series-uid|manifest> --download-dir ./data` does the same from a
shell. See `references/cli_guide.md` for the `dirTemplate` hierarchy options (Python default:
`%collection_id/%PatientID/%StudyInstanceUID/%Modality_%SeriesInstanceUID`; `dirTemplate=""`
flattens), manifest downloads with resume, and dry-run size estimation.

### 3. Visualizing IDC images

```python
viewer_url = client.get_viewer_URL(seriesInstanceUID=uid)        # one series
viewer_url = client.get_viewer_URL(studyInstanceUID=study_uid)   # all series in a study
```

Returns a browser URL — nothing is downloaded. The method selects OHIF v3 for radiology or
SLIM for slide microscopy automatically. Viewing by study is useful when a single DICOM Study
holds several Series (T1, T2, and DWI from one MRI session).

### 4. Licenses and citations — obligations, not optional steps

IDC data carries license terms and attribution requirements that follow it into any downstream
publication or product, and neither is inferable from the pixel data. **Check the license
before use, and generate citations for whatever you download.**

```python
# License breakdown for a selection
licenses = client.sql_query("""
    SELECT DISTINCT collection_id, license_short_name,
           COUNT(DISTINCT SeriesInstanceUID) as series_count
    FROM index GROUP BY collection_id, license_short_name
""")

# Citations for the same selection you downloaded (APA by default)
for citation in client.citations_from_selection(collection_id="rider_pilot"):
    print(citation)
```

About 97% of IDC data is CC BY (commercial use allowed with attribution) and about 3% is
CC BY-NC (non-commercial only). **Licenses attach to series, not collections** — 39 of 176
collections carry more than one — so check the selection you actually intend to use, and note
that the most restrictive term governs a mixed cohort.

Both tasks are available from all three access paths, so stay on whichever one the session is
already using: `idc-index` as above, `POST /v3/licenses` and `POST /v3/citations` over REST,
or the `get_licenses` and `get_citations` MCP tools. See
`references/licensing_and_citation.md` for the full license inventory, all three routes, the
citation formats (APA, BibTeX, CSL JSON, RDF Turtle), and what to include when publishing.

### 5. Reaching past the index

Pick the access path with the routing gate in *Overview*; *Data Access Options* above is the
full routing table.

Before reaching for BigQuery (which needs a billing-enabled GCP account), check whether a
specialized index table already has the column you want: search `client.indices_overview`,
then `client.fetch_index(...)` and query locally for free. BigQuery is required only for
private DICOM elements, per-segment anatomy (`segmentations`), and pre-extracted SR
measurements (`quantitative_measurements`, `qualitative_measurements`) — these have no
idc-index equivalent.

## Best Practices

- **Check schema before writing queries** — Use `client.get_index_schema('index')` (reads cached metadata, no SQL executed) or `client.indices_overview` to see all available columns and their descriptions. The version-tracking columns `series_init_idc_version` and `series_revised_idc_version` in the main `index` table directly answer "what's new / when was this added" questions without touching `prior_versions_index`.
- **Never use web search for IDC data content questions** - Always query the IDC index directly, via `client.sql_query()` locally or `POST /v3/sql` over HTTP. Web sources (release notes, blog posts, documentation pages) are frequently out of date and will produce incorrect answers. The index is the authoritative source; use it even when web search is available.
- **Verify the IDC data version at the start of a session** - `client.get_idc_version()`, `GET /v3/version`, or the MCP `get_idc_version` tool, depending on the path in use (currently v24). For a stale local index, run `scripts/check_version.py` and use the upgrade command it prints
- **Check licenses and generate citations** - Query `license_short_name` and respect CC BY vs CC BY-NC terms; use `citations_from_selection()` to produce citations from `source_DOI` for publications
- **Explore small, then commit** - Use `LIMIT` (or a low `max_rows`) while exploring, and check collection size before downloading — some collections are terabytes. See `references/cli_guide.md`
- **Keep downloads reproducible** - Organize with `dirTemplate` (e.g. `%collection_id/%PatientID/%Modality`) and save the Series UIDs or manifest behind any dataset you build

## Troubleshooting

**Issue: `ModuleNotFoundError: No module named 'idc_index'`**
- **Cause:** idc-index package not installed
- **Solution:** If the task is read-only metadata, do not install it — use the REST API instead (*Data Access Options*). Otherwise run `scripts/check_version.py` and use the install command it prints, which targets the running interpreter and pins the vetted version. For data analysis also add pandas, numpy, and pydicom (tested with pandas>=1.5, numpy>=1.23, pydicom>=2.3)

**Issue: Download fails with connection timeout**
- **Cause:** Network instability or large download size
- **Solution:** Download in smaller batches (10-20 series); see `references/cli_guide.md` for
  `--use-s5cmd-sync` resume and retry guidance

**Issue: `BigQuery quota exceeded` or billing errors**
- **Cause:** BigQuery requires billing-enabled GCP project
- **Solution:** Use idc-index mini-index for simple queries (no billing required), or see `references/bigquery_guide.md` for cost optimization tips

**Issue: Series UID not found or no data returned**
- **Cause:** Typo in UID, data not in the current IDC version, or wrong field name
- **Solution:** Test with `LIMIT 5` first, check field names against `client.indices_overview`,
  and confirm the series is in the current version (some old data is deprecated)

**Issue: Column not found in `index` table (e.g., `SliceThickness`, `PixelSpacing`, `KVP`, `EchoTime`, `InjectedDose`)**
- **Cause:** The `index` table contains series-level metadata only; modality-specific acquisition and reconstruction parameters live in dedicated tables (`ct_index`, `mr_index`, `pt_index`)
- **Solution:** Search `client.indices_overview` for the column to find its table — the loop is under *Finding which table contains a column* in `references/index_tables_guide.md` — then fetch and join on `SeriesInstanceUID`:
  ```python
  client.fetch_index("ct_index")
  result = client.sql_query("""
      SELECT i.SeriesInstanceUID, i.Modality, c.SliceThickness, c.KVP, c.PixelSpacing_row_mm
      FROM index i
      JOIN ct_index c USING (SeriesInstanceUID)
      WHERE i.collection_id = 'your_collection'
  """)
  ```

**Issue: Downloaded DICOM files won't open**
- **Cause:** Corrupted download, or an object type the viewer does not handle — SEG, RTSTRUCT,
  SR, and slide microscopy all need specialized tools
- **Solution:** Check `Modality` and `SOPClassUID` first, validate with
  `pydicom.dcmread(file, force=True)`, try another viewer (3D Slicer, QuPath for pathology),
  then re-download

## Resources

Reference guides and their decision triggers are listed in *Quick Navigation* above.

- **IDC Portal**: https://portal.imaging.datacommons.cancer.gov/explore/
- **Documentation**: https://learn.canceridc.dev/ — **Tutorials**: https://github.com/ImagingDataCommons/IDC-Tutorials
- **User Forum**: https://discourse.canceridc.dev/ — **idc-index**: https://github.com/ImagingDataCommons/idc-index
- **[indices_reference](https://idc-index.readthedocs.io/en/latest/indices_reference.html)** — external index-table docs (may be ahead of the installed version)
- **Citation**: Fedorov, A., et al. "National Cancer Institute Imaging Data Commons: Toward Transparency, Reproducibility, and Scalability in Imaging Artificial Intelligence." RadioGraphics 43.12 (2023). https://doi.org/10.1148/rg.230180
- **Skill updates**: [releases page](https://github.com/ImagingDataCommons/imaging-data-commons-skill/releases); watch the repository (Watch → Custom → Releases)

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/imaging-data-commons/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/bigquery_guide.md`

# BigQuery Guide for IDC

**Tested with:** `bigquery-public-data.idc_current` and idc-index 0.12.5 (IDC data version v24)

For most queries and downloads, use `idc-index` (see main SKILL.md). This guide covers BigQuery for advanced use cases requiring full DICOM metadata or complex joins.

## Prerequisites

**Requirements:**
1. Google account
2. Google Cloud project with billing enabled (first 1 TB/month free)
3. `google-cloud-bigquery` Python package or BigQuery console access

**Authentication setup:**
```bash
# Install Google Cloud SDK, then:
gcloud auth application-default login
```

## When to Use BigQuery

Use BigQuery instead of `idc-index` when you need:
- Full DICOM metadata (all 4000+ tags, not just the ~50 in idc-index)
- Complex joins across clinical data tables
- DICOM sequence attributes (nested structures)
- Queries on fields not in the idc-index mini-index
- Private DICOM elements (vendor-specific tags in OtherElements column)
- **Per-segment detail from DICOM Segmentation objects** — `idc-index` `seg_index` gives series-level metadata, but not individual segment anatomy codes; use `segmentations` BigQuery table to query by structure name
- **Quantitative measurements from DICOM SR** — radiomics features (volume, diameter, shape descriptors) without downloading and parsing SR files; no idc-index equivalent
- **Qualitative measurements from DICOM SR** — coded evaluations (malignancy rating, texture, margin) without parsing SR files; no idc-index equivalent

## Accessing IDC in BigQuery

### Dataset Structure

All IDC tables are in the `bigquery-public-data` BigQuery project.

**Current version (recommended for exploration):**
- `bigquery-public-data.idc_current.*`
- `bigquery-public-data.idc_current_clinical.*`

**Versioned datasets (recommended for reproducibility):**

- `bigquery-public-data.idc_v{IDC version}.*`
- `bigquery-public-data.idc_v{IDC version}_clinical.*`

Always use versioned datasets for reproducible research!

## Key Tables

### dicom_all
Primary table joining complete DICOM metadata with IDC-specific columns (collection_id, gcs_url, license). Contains all DICOM tags from `dicom_metadata` plus collection and administrative metadata. See [dicom_all.sql](https://github.com/ImagingDataCommons/etl_flow/blob/master/bq/generate_tables_and_views/derived_tables/BQ_Table_Building/derived_data_views/sql/dicom_all.sql) for the exact derivation.

```sql
SELECT 
  collection_id,
  PatientID,
  StudyInstanceUID, 
  SeriesInstanceUID,
  Modality,
  BodyPartExamined,
  SeriesDescription,
  gcs_url,
  license_short_name
FROM `bigquery-public-data.idc_current.dicom_all`
WHERE Modality = 'CT'
  AND BodyPartExamined = 'CHEST'
LIMIT 10
```

### Derived Tables

These tables are derived from DICOM objects (Segmentation and Structured Report) and have **no equivalent in idc-index**. Use them to query per-segment anatomy, radiomics features, and qualitative assessments without downloading DICOM files.

**segmentations** — one row per segment within a DICOM SEG object. Lets you search by anatomical structure name or DICOM coded concept. The `idc-index` `seg_index` gives series-level metadata; this table gives per-segment detail.

**measurement_groups** — one row per SR TID1500 measurement group. The parent grouping for quantitative and qualitative measurements; links measurements to segmentations and source images.

**quantitative_measurements** — one row per numeric measurement within an SR TID1500 group. Contains radiomics features (volume, diameter, shape descriptors, texture) extracted from DICOM SR without downloading or parsing SR files.

**qualitative_measurements** — one row per coded evaluation within an SR TID1500 group. Contains assessed findings (malignancy likelihood, texture, margin type) using coded concept values.

See the [Derived Tables: Detailed Documentation](#derived-tables-detailed-documentation) section below for schemas, column descriptions, and query examples.

### Collection Metadata

**original_collections_metadata** - Collection-level descriptions

```sql
SELECT
  collection_id,
  CancerTypes,
  TumorLocations,
  Subjects,
  src.source_doi,
  src.ImageTypes,
  src.license.license_short_name
FROM `bigquery-public-data.idc_current.original_collections_metadata`,
UNNEST(Sources) AS src
WHERE CancerTypes LIKE '%Lung%'
```

## Common Query Patterns

### Find Collections by Criteria

```sql
SELECT 
  collection_id,
  COUNT(DISTINCT PatientID) as patient_count,
  COUNT(DISTINCT SeriesInstanceUID) as series_count,
  ARRAY_AGG(DISTINCT Modality) as modalities
FROM `bigquery-public-data.idc_current.dicom_all`
WHERE BodyPartExamined LIKE '%BRAIN%'
GROUP BY collection_id
HAVING patient_count > 50
ORDER BY patient_count DESC
```

### Get Download URLs

```sql
SELECT
  SeriesInstanceUID,
  gcs_url
FROM `bigquery-public-data.idc_current.dicom_all`
WHERE collection_id = 'rider_pilot'
  AND Modality = 'CT'
```

### Find Studies with Multiple Modalities

```sql
SELECT
  StudyInstanceUID,
  ARRAY_AGG(DISTINCT Modality) as modalities,
  COUNT(DISTINCT SeriesInstanceUID) as series_count
FROM `bigquery-public-data.idc_current.dicom_all`
GROUP BY StudyInstanceUID
HAVING ARRAY_LENGTH(ARRAY_AGG(DISTINCT Modality)) > 1
LIMIT 100
```

### License Filtering

```sql
SELECT
  collection_id,
  license_short_name,
  COUNT(*) as instance_count
FROM `bigquery-public-data.idc_current.dicom_all`
WHERE license_short_name = 'CC BY 4.0'
GROUP BY collection_id, license_short_name
```

### Find Segmentations with Source Images

```sql
SELECT
  src.collection_id,
  seg.SeriesInstanceUID as seg_series,
  seg.SegmentedPropertyType,
  src.SeriesInstanceUID as source_series,
  src.Modality as source_modality
FROM `bigquery-public-data.idc_current.segmentations` seg
JOIN `bigquery-public-data.idc_current.dicom_all` src
  ON seg.segmented_SeriesInstanceUID = src.SeriesInstanceUID
WHERE src.collection_id = 'qin_prostate_repeatability'
LIMIT 10
```

## Derived Tables: Detailed Documentation

### segmentations

One row per segment within a DICOM Segmentation (SEG) object. Unlike `idc-index` `seg_index` (one row per SEG series), this table exposes each labeled region individually so you can search by anatomical structure or finding type.

**Key columns:**

| Column | Type | Description |
|--------|------|-------------|
| `SeriesInstanceUID` | STRING | SEG series UID |
| `SOPInstanceUID` | STRING | SEG instance UID |
| `PatientID` | STRING | Patient identifier |
| `StudyInstanceUID` | STRING | Study UID |
| `SegmentNumber` | INTEGER | Segment index within the SEG (starting from 1) |
| `SegmentedPropertyCategory` | RECORD | Coded category (e.g., "Anatomical Structure", "Morphologically Altered Structure") |
| `SegmentedPropertyType` | RECORD | Specific structure (e.g., "Liver", "Kidney", "Neoplasm") |
| `AnatomicRegion` | RECORD | Optional anatomic region modifier |
| `SegmentAlgorithmType` | STRING | AUTOMATIC, SEMIAUTOMATIC, or MANUAL |
| `SegmentAlgorithmName` | STRING (REPEATED) | Algorithm name array (e.g., ["TotalSegmentator"]) |
| `TrackingUID` | STRING | Links segment to SR measurements |
| `TrackingID` | STRING | Human-readable tracking label |
| `segmented_SeriesInstanceUID` | STRING | Source image series UID — join to `dicom_all` to get collection/modality |
| `viewer_url` | STRING | Direct IDC viewer link for the SEG |

`SegmentedPropertyCategory` and `SegmentedPropertyType` are RECORD types with sub-fields `CodeValue`, `CodingSchemeDesignator`, and `CodeMeaning`. Use `.CodeMeaning` for human-readable filtering.

**idc-index gap:** `seg_index` in idc-index has `total_segments`, `AlgorithmName`, and aggregated codes, but does not expose individual segment anatomy per row. Use this BigQuery table when you need to find SEG series that contain a specific structure (e.g., all series with a "Liver" segment).

**Discover what structures are segmented across IDC:**

```sql
SELECT
  SegmentedPropertyCategory.CodeMeaning AS category,
  SegmentedPropertyType.CodeMeaning AS structure,
  SegmentAlgorithmType,
  COUNT(DISTINCT SeriesInstanceUID) AS seg_series_count
FROM `bigquery-public-data.idc_current.segmentations`
GROUP BY 1, 2, 3
ORDER BY seg_series_count DESC
LIMIT 20
```

**Find all SEG series containing a specific structure, with source image context:**

```sql
SELECT
  seg.SeriesInstanceUID AS seg_series,
  seg.SegmentNumber,
  seg.SegmentedPropertyType.CodeMeaning AS structure,
  seg.SegmentAlgorithmType,
  seg.SegmentAlgorithmName,
  img.collection_id,
  img.PatientID,
  img.Modality,
  seg.viewer_url
FROM `bigquery-public-data.idc_current.segmentations` seg
JOIN `bigquery-public-data.idc_current.dicom_all` img
  ON seg.segmented_SeriesInstanceUID = img.SeriesInstanceUID
WHERE seg.SegmentedPropertyType.CodeMeaning = 'Liver'
  AND seg.SegmentAlgorithmType = 'AUTOMATIC'
LIMIT 20
```

**Find all segment types present in a collection:**

```sql
SELECT
  seg.SegmentedPropertyType.CodeMeaning AS structure,
  seg.SegmentAlgorithmType,
  COUNT(DISTINCT seg.SeriesInstanceUID) AS seg_series_count
FROM `bigquery-public-data.idc_current.segmentations` seg
JOIN `bigquery-public-data.idc_current.dicom_all` img
  ON seg.segmented_SeriesInstanceUID = img.SeriesInstanceUID
WHERE img.collection_id = 'nlst'
GROUP BY 1, 2
ORDER BY seg_series_count DESC
```

**Link segments to SR measurements using TrackingUID:**

```sql
-- Find segments that have corresponding SR measurements
SELECT
  seg.SeriesInstanceUID AS seg_series,
  seg.SegmentNumber,
  seg.SegmentedPropertyType.CodeMeaning AS structure,
  qm.Quantity.CodeMeaning AS measurement,
  ROUND(CAST(qm.Value AS FLOAT64), 2) AS value,
  qm.Units.CodeMeaning AS units
FROM `bigquery-public-data.idc_current.segmentations` seg
JOIN `bigquery-public-data.idc_current.quantitative_measurements` qm
  ON seg.SeriesInstanceUID = qm.segmentationSeriesUID
  AND seg.SegmentNumber = qm.segmentationSegmentNumber
WHERE seg.SegmentedPropertyType.CodeMeaning = 'Neoplasm'
  AND qm.Quantity.CodeMeaning = 'Volume from Voxel Summation'
LIMIT 10
```

---

### quantitative_measurements

One row per numeric measurement in a DICOM SR TID1500 Measurement Report. Contains radiomics features (shape, intensity, texture) and clinical measurements (volume, diameter, SUV). These measurements are pre-extracted from SR — no download or DICOM parsing needed.

**No idc-index equivalent.** This table is only accessible via BigQuery.

**Key columns:**

| Column | Type | Description |
|--------|------|-------------|
| `SOPInstanceUID` | STRING | SR instance UID |
| `SeriesInstanceUID` | STRING | SR series UID — join to `dicom_all` for collection/modality |
| `SeriesDescription` | STRING | SR series description (e.g., "TotalSegmentator(v1.5.6) shape Measurements") |
| `PatientID` | STRING | Patient identifier |
| `measurementGroup_number` | INTEGER | Group index within the SR (0-based); join key with `measurement_groups` and `qualitative_measurements` |
| `Quantity` | RECORD | What was measured — `CodeValue`, `CodingSchemeDesignator`, `CodeMeaning` (e.g., "Volume from Voxel Summation") |
| `Value` | NUMERIC | The numeric measurement value |
| `Units` | RECORD | Units — `CodeMeaning` (e.g., "cubic millimeter", "no units", "Hounsfield Unit") |
| `derivationModifier` | RECORD | How the value was derived (e.g., "Mean", "Minimum", "Maximum") |
| `lateralityModifier` | RECORD | Laterality qualifier |
| `finding` | RECORD | What finding was measured — `CodeMeaning` (e.g., "Nodule", "Organ", "Anatomical Structure") |
| `findingSite` | RECORD | Where the finding is — `CodeMeaning` (e.g., "Liver", "Esophagus", "Lung") |
| `trackingIdentifier` | STRING | Human-readable tracking label (e.g., "Nodule 1", "Measurements group 26") |
| `trackingUniqueIdentifier` | STRING | Tracking UID — links back to `segmentations.TrackingUID` |
| `segmentationInstanceUID` | STRING | SOPInstanceUID of the referenced SEG object |
| `segmentationSeriesUID` | STRING | SeriesInstanceUID of the referenced SEG object |
| `segmentationSegmentNumber` | INTEGER | Segment number within the SEG — join to `segmentations.SegmentNumber` |
| `sourceSegmentedSeriesUID` | STRING | Source image series — join to `dicom_all.SeriesInstanceUID` |

**Discover available measurement types:**

```sql
SELECT
  Quantity.CodeMeaning AS measurement,
  Units.CodeMeaning AS units,
  COUNT(*) AS measurement_count,
  COUNT(DISTINCT SeriesInstanceUID) AS sr_series_count
FROM `bigquery-public-data.idc_current.quantitative_measurements`
GROUP BY 1, 2
ORDER BY measurement_count DESC
LIMIT 20
```

**Query measurements for a specific structure (e.g., liver volume across collections):**

```sql
SELECT
  qm.PatientID,
  ROUND(CAST(qm.Value AS FLOAT64) / 1000, 1) AS volume_cm3,
  img.collection_id,
  qm.segmentationSeriesUID
FROM `bigquery-public-data.idc_current.quantitative_measurements` qm
JOIN `bigquery-public-data.idc_current.dicom_all` img
  ON qm.sourceSegmentedSeriesUID = img.SeriesInstanceUID
WHERE qm.Quantity.CodeMeaning = 'Volume from Voxel Summation'
  AND qm.findingSite.CodeMeaning = 'Liver'
ORDER BY volume_cm3 DESC
LIMIT 20
```

**Retrieve all measurements for a specific patient and finding:**

```sql
SELECT
  qm.measurementGroup_number,
  qm.finding.CodeMeaning AS finding,
  qm.findingSite.CodeMeaning AS finding_site,
  qm.lateralityModifier.CodeMeaning AS laterality,
  qm.Quantity.CodeMeaning AS feature,
  ROUND(CAST(qm.Value AS FLOAT64), 3) AS value,
  qm.Units.CodeMeaning AS units
FROM `bigquery-public-data.idc_current.quantitative_measurements` qm
WHERE qm.PatientID = 'LIDC-IDRI-0001'
  AND qm.finding.CodeMeaning = 'Nodule'
ORDER BY qm.measurementGroup_number, qm.Quantity.CodeMeaning
```

---

### qualitative_measurements

One row per coded evaluation in a DICOM SR TID1500 Measurement Report. Instead of numeric values, these record assessed characteristics using coded concept pairs (e.g., Quantity="Malignancy", Value="4 out of 5 (Moderately Suspicious for Cancer)").

**No idc-index equivalent.** This table is only accessible via BigQuery.

**Key columns:**

| Column | Type | Description |
|--------|------|-------------|
| `SOPInstanceUID` | STRING | SR instance UID |
| `SeriesInstanceUID` | STRING | SR series UID — join to `dicom_all` for collection/modality |
| `PatientID` | STRING | Patient identifier |
| `measurementGroup_number` | INTEGER | Group index within the SR — join key with `quantitative_measurements` |
| `Quantity` | RECORD | What was assessed — `CodeMeaning` (e.g., "Malignancy", "Calcification", "Texture") |
| `Value` | RECORD | The coded answer — `CodeMeaning` (e.g., "4 out of 5 (Moderately Suspicious for Cancer)") |
| `finding` | RECORD | What finding was assessed — `CodeMeaning` (e.g., "Nodule") |
| `findingSite` | RECORD | Anatomic site — `CodeMeaning` (e.g., "Lung") |
| `trackingIdentifier` | STRING | Human-readable tracking label |
| `segmentationInstanceUID` | STRING | SOPInstanceUID of the referenced SEG object |
| `segmentationSeriesUID` | STRING | SeriesInstanceUID of the referenced SEG object |
| `segmentationSegmentNumber` | INTEGER | Segment number within the referenced SEG |
| `sourceSegmentedSeriesUID` | STRING | Source image series — join to `dicom_all.SeriesInstanceUID` |

**Discover available qualitative features and their values:**

```sql
SELECT
  Quantity.CodeMeaning AS feature,
  Value.CodeMeaning AS assessed_value,
  finding.CodeMeaning AS finding,
  COUNT(*) AS count
FROM `bigquery-public-data.idc_current.qualitative_measurements`
GROUP BY 1, 2, 3
ORDER BY count DESC
LIMIT 20
```

**Find all nodules with a specific malignancy rating:**

```sql
SELECT
  qm.PatientID,
  qm.trackingIdentifier AS nodule_id,
  qm.Value.CodeMeaning AS malignancy_rating,
  img.collection_id
FROM `bigquery-public-data.idc_current.qualitative_measurements` qm
JOIN `bigquery-public-data.idc_current.dicom_all` img
  ON qm.SeriesInstanceUID = img.SeriesInstanceUID
WHERE qm.Quantity.CodeMeaning = 'Malignancy'
  AND qm.Value.CodeMeaning LIKE '%Suspicious%'
ORDER BY qm.PatientID
LIMIT 20
```

---

### measurement_groups

The parent table for TID1500 measurement groups. Each row represents one measurement group within an SR, with references to the segmentation and source image but without the individual measurement values. Use this table when you need to enumerate groups or check what was tracked, without pulling all measurement values.

**Key columns:** `SOPInstanceUID`, `SeriesInstanceUID`, `PatientID`, `measurementGroup_number`, `trackingIdentifier`, `trackingUniqueIdentifier`, `finding`, `findingSite`, `segmentationInstanceUID`, `segmentationSeriesUID`, `segmentationSegmentNumber`, `sourceSegmentedSeriesUID`, `contentSequence` (raw SR content sequence).

In most workflows, join `quantitative_measurements` and `qualitative_measurements` directly using `SOPInstanceUID` + `measurementGroup_number` rather than going through `measurement_groups`.

---

### Combining quantitative and qualitative measurements

The primary use case requiring both tables: correlate numeric features (volume, diameter) with coded assessments (malignancy, texture) for the same finding. Join on `SOPInstanceUID` + `measurementGroup_number`.

**Example: LIDC-IDRI lung nodule analysis — malignancy rating with volume and diameter:**

```sql
SELECT
  qual.PatientID,
  qual.trackingIdentifier AS nodule_id,
  qual.Value.CodeMeaning AS malignancy_rating,
  ROUND(CAST(vol.Value AS FLOAT64), 1) AS volume_mm3,
  ROUND(CAST(diam.Value AS FLOAT64), 1) AS diameter_mm
FROM `bigquery-public-data.idc_current.qualitative_measurements` qual
JOIN `bigquery-public-data.idc_current.quantitative_measurements` vol
  ON qual.SOPInstanceUID = vol.SOPInstanceUID
  AND qual.measurementGroup_number = vol.measurementGroup_number
JOIN `bigquery-public-data.idc_current.quantitative_measurements` diam
  ON qual.SOPInstanceUID = diam.SOPInstanceUID
  AND qual.measurementGroup_number = diam.measurementGroup_number
WHERE qual.Quantity.CodeMeaning = 'Malignancy'
  AND vol.Quantity.CodeMeaning = 'Volume'
  AND diam.Quantity.CodeMeaning = 'Diameter'
ORDER BY qual.PatientID, qual.trackingIdentifier
LIMIT 20
```

**Joining all three derived tables to get full segment context:**

```sql
SELECT
  seg.SegmentedPropertyType.CodeMeaning AS structure,
  qual.Quantity.CodeMeaning AS qualitative_feature,
  qual.Value.CodeMeaning AS qualitative_value,
  qm.Quantity.CodeMeaning AS quantitative_feature,
  ROUND(CAST(qm.Value AS FLOAT64), 3) AS numeric_value,
  qm.Units.CodeMeaning AS units,
  img.collection_id
FROM `bigquery-public-data.idc_current.segmentations` seg
JOIN `bigquery-public-data.idc_current.qualitative_measurements` qual
  ON seg.SeriesInstanceUID = qual.segmentationSeriesUID
  AND seg.SegmentNumber = qual.segmentationSegmentNumber
JOIN `bigquery-public-data.idc_current.quantitative_measurements` qm
  ON qual.SOPInstanceUID = qm.SOPInstanceUID
  AND qual.measurementGroup_number = qm.measurementGroup_number
JOIN `bigquery-public-data.idc_current.dicom_all` img
  ON seg.segmented_SeriesInstanceUID = img.SeriesInstanceUID
WHERE seg.SegmentedPropertyType.CodeMeaning = 'Neoplasm'
LIMIT 10
```

## Private DICOM Elements

Private DICOM elements are vendor-specific attributes not defined in the DICOM standard. They often contain essential acquisition parameters (like diffusion b-values, gradient directions, or scanner-specific settings) that are critical for image interpretation and analysis.

### Understanding Private Elements

**How private elements work:**
- Private elements use odd-numbered group numbers (e.g., 0019, 0043, 2001)
- Each vendor reserves blocks of 256 elements using Private Creator identifiers at positions (gggg,0010-00FF)
- For example, GE uses Private Creator "GEMS_PARM_01" at (0043,0010) to reserve elements (0043,1000-10FF)

**Standard vs. private tags:** Some parameters exist in both forms:
| Parameter | Standard Tag | GE | Siemens | Philips |
|-----------|--------------|-----|---------|---------|
| Diffusion b-value | (0018,9087) | (0043,1039) | (0019,100C) | (2001,1003) |
| Private Creator | - | GEMS_PARM_01 | SIEMENS CSA HEADER | Philips Imaging |

Older scanners typically populate only private tags; newer scanners may use standard tags. Always check both.

**Challenges with private elements:**
- Require manufacturer DICOM Conformance Statements to interpret
- Tag meanings can change between software versions
- May be removed during de-identification for HIPAA compliance
- Value encoding varies (string vs. numeric, different units)

### Accessing Private Elements in BigQuery

Private elements are stored in the `OtherElements` column of `dicom_all` as an array of structs with `Tag` and `Data` fields.

**Tag notation:** DICOM notation (0043,1039) becomes BigQuery format `Tag_00431039`.

### Private Element Query Patterns

#### Discover Available Private Tags

List all non-empty private tags for a collection:

```sql
SELECT
  other_elements.Tag,
  COUNT(*) AS instance_count,
  ARRAY_AGG(DISTINCT other_elements.Data[SAFE_OFFSET(0)] IGNORE NULLS LIMIT 5) AS sample_values
FROM `bigquery-public-data.idc_current.dicom_all`,
  UNNEST(OtherElements) AS other_elements
WHERE collection_id = 'qin_prostate_repeatability'
  AND Modality = 'MR'
  AND ARRAY_LENGTH(other_elements.Data) > 0
  AND other_elements.Data[SAFE_OFFSET(0)] IS NOT NULL
  AND other_elements.Data[SAFE_OFFSET(0)] != ''
GROUP BY other_elements.Tag
ORDER BY instance_count DESC
```

For a specific series:

```sql
SELECT
  other_elements.Tag,
  ARRAY_AGG(DISTINCT other_elements.Data[SAFE_OFFSET(0)] IGNORE NULLS) AS values
FROM `bigquery-public-data.idc_current.dicom_all`,
  UNNEST(OtherElements) AS other_elements
WHERE SeriesInstanceUID = '1.3.6.1.4.1.14519.5.2.1.7311.5101.206828891270520544417996275680'
  AND ARRAY_LENGTH(other_elements.Data) > 0
  AND other_elements.Data[SAFE_OFFSET(0)] IS NOT NULL
  AND other_elements.Data[SAFE_OFFSET(0)] != ''
GROUP BY other_elements.Tag
```

To identify the Private Creator for a tag, look for the reservation element in the same group. For example, if you find `Tag_00431039`, the Private Creator is at `Tag_00430010` (the tag that reserves block 10xx in group 0043).

#### Identify Equipment Manufacturer

Determine what equipment produced the data to find the correct DICOM Conformance Statement:

```sql
SELECT DISTINCT Manufacturer, ManufacturerModelName
FROM `bigquery-public-data.idc_current.dicom_all`
WHERE collection_id = 'qin_prostate_repeatability'
  AND Modality = 'MR'
```

#### Access Private Element Values

Use `UNNEST` to access individual private elements:

```sql
SELECT
  SeriesInstanceUID,
  SeriesDescription,
  other_elements.Data[SAFE_OFFSET(0)] AS b_value
FROM `bigquery-public-data.idc_current.dicom_all`,
  UNNEST(OtherElements) AS other_elements
WHERE collection_id = 'qin_prostate_repeatability'
  AND other_elements.Tag = 'Tag_00431039'
LIMIT 10
```

#### Aggregate Values by Series

Collect all unique values across slices in a series:

```sql
SELECT
  SeriesInstanceUID,
  ANY_VALUE(SeriesDescription) AS SeriesDescription,
  ARRAY_AGG(DISTINCT other_elements.Data[SAFE_OFFSET(0)]) AS b_values
FROM `bigquery-public-data.idc_current.dicom_all`,
  UNNEST(OtherElements) AS other_elements
WHERE collection_id = 'qin_prostate_repeatability'
  AND other_elements.Tag = 'Tag_00431039'
GROUP BY SeriesInstanceUID
```

#### Combine Standard and Private Filters

Filter using both standard DICOM attributes and private element values:

```sql
SELECT
  PatientID,
  SeriesInstanceUID,
  ANY_VALUE(SeriesDescription) AS SeriesDescription,
  ARRAY_AGG(DISTINCT other_elements.Data[SAFE_OFFSET(0)]) AS b_values,
  COUNT(DISTINCT SOPInstanceUID) AS n_slices
FROM `bigquery-public-data.idc_current.dicom_all`,
  UNNEST(OtherElements) AS other_elements
WHERE collection_id = 'qin_prostate_repeatability'
  AND Modality = 'MR'
  AND other_elements.Tag = 'Tag_00431039'
  AND ImageType[SAFE_OFFSET(0)] = 'ORIGINAL'
  AND other_elements.Data[SAFE_OFFSET(0)] = '1400'
GROUP BY PatientID, SeriesInstanceUID
ORDER BY PatientID
```

#### Cross-Collection Analysis

Survey usage of a private tag across all IDC collections:

```sql
SELECT
  collection_id,
  ARRAY_TO_STRING(ARRAY_AGG(DISTINCT other_elements.Data[SAFE_OFFSET(0)] IGNORE NULLS), ', ') AS values_found,
  ARRAY_AGG(DISTINCT Manufacturer IGNORE NULLS) AS manufacturers
FROM `bigquery-public-data.idc_current.dicom_all`,
  UNNEST(OtherElements) AS other_elements
WHERE other_elements.Tag = 'Tag_00431039'
  AND other_elements.Data[SAFE_OFFSET(0)] IS NOT NULL
  AND other_elements.Data[SAFE_OFFSET(0)] != ''
GROUP BY collection_id
ORDER BY collection_id
```

### Workflow: Finding and Using Private Tags

1. **Discover available private tags** in your collection using the discovery query above
2. **Identify the manufacturer** to know which conformance statement to consult
3. **Find the DICOM Conformance Statement** from the manufacturer's website (see Resources below)
4. **Search the conformance statement** for the parameter you need (e.g., "b_value", "gradient") to understand what each tag contains
5. **Convert tag to BigQuery format:** (gggg,eeee) → `Tag_ggggeeee`
6. **Query and verify** results visually in the IDC Viewer

### Data Quality Notes

- Some collections show unrealistic values (e.g., b-value "1000000600") indicating encoding issues or different conventions
- IDC data is de-identified; private tags containing PHI may have been removed or modified
- The same tag may have different meanings across software versions
- Always verify query results visually using the [IDC Viewer](https://viewer.imaging.datacommons.cancer.gov/) before large-scale analysis

### Private Element Resources

**Manufacturer DICOM Conformance Statements:**
- [GE Healthcare MR](https://www.gehealthcare.com/products/interoperability/dicom/magnetic-resonance-imaging-dicom-conformance-statements)
- [Siemens MR](https://www.siemens-healthineers.com/services/it-standards/dicom-conformance-statements-magnetic-resonance)
- [Siemens CT](https://www.siemens-healthineers.com/services/it-standards/dicom-conformance-statements-computed-tomography)

**DICOM Standard:**
- [Part 5 Section 7.8 - Private Data Elements](https://dicom.nema.org/medical/dicom/current/output/chtml/part05/sect_7.8.html)
- [Part 15 Appendix E - De-identification Profiles](https://dicom.nema.org/medical/dicom/current/output/chtml/part15/chapter_e.html)

**Community Resources:**
- [NAMIC Wiki: DWI/DTI DICOM](https://web.archive.org/web/20260520044207/https://www.na-mic.org/wiki/NAMIC_Wiki:DTI:DICOM_for_DWI_and_DTI) - comprehensive vendor comparison for diffusion imaging (archived; original NA-MIC wiki retired)
- [StandardizeBValue](https://github.com/nslay/StandardizeBValue) - tool to extract vendor b-values to standard tags

## Using Query Results with idc-index

Combine BigQuery for complex queries with idc-index for downloads (no GCP auth needed for downloads):

```python
from google.cloud import bigquery
from idc_index import IDCClient

# Initialize BigQuery client
# Requires: the Python google-cloud-bigquery package
# Auth: gcloud auth application-default login
# Project: needed for billing even on public datasets (free tier applies)
bq_client = bigquery.Client(project="your-gcp-project-id")

# Query for series with specific criteria
query = """
SELECT DISTINCT SeriesInstanceUID
FROM `bigquery-public-data.idc_current.dicom_all`
WHERE collection_id = 'tcga_luad'
  AND Modality = 'CT'
  AND Manufacturer = 'GE MEDICAL SYSTEMS'
LIMIT 100
"""

df = bq_client.query(query).to_dataframe()
print(f"Found {len(df)} GE CT series")

# Download with idc-index (no GCP auth required)
idc_client = IDCClient()
idc_client.download_from_selection(
    seriesInstanceUID=list(df['SeriesInstanceUID'].values),
    downloadDir="./tcga_luad_thin_ct"
)
```

## Cost and Optimization

**Pricing:** $5 per TB scanned (first 1 TB/month free). Most users stay within free tier.

**Minimize data scanned:**
- Select only needed columns (not `SELECT *`)
- Filter early with `WHERE` clauses
- Use `LIMIT` when testing
- Use `dicom_all` instead of `dicom_metadata` when possible (smaller)
- Preview queries in BQ console (free, shows bytes to scan)

**Check cost before running:**
```python
query_job = client.query(query, job_config=bigquery.QueryJobConfig(dry_run=True))
print(f"Query will scan {query_job.total_bytes_processed / 1e9:.2f} GB")
```

**Use materialized tables:** IDC provides both views (`table_name_view`) and materialized tables (`table_name`). Always use the materialized tables (faster, lower cost).

## Clinical Data

Clinical data is in separate datasets with collection-specific tables. All clinical data available via `idc-index` is also available in BigQuery, with the same content and structure. Use BigQuery when you need complex cross-collection queries or joins that aren't possible with the local `idc-index` tables.

**Datasets:**
- `bigquery-public-data.idc_current_clinical` - current release (for exploration)
- `bigquery-public-data.idc_v{version}_clinical` - versioned datasets (for reproducibility)

Currently there are ~130 clinical tables representing ~70 collections. Not all collections have clinical data (started in IDC v11).

### Clinical Table Naming

Most collections use a single table: `<collection_id>_clinical`

**Exception:** ACRIN collections use multiple tables for different data types (e.g., `acrin_6698_A0`, `acrin_6698_A1`, etc.).

### Metadata Tables

Two metadata tables help navigate clinical data:

**table_metadata** - Collection-level information:
```sql
SELECT
  collection_id,
  table_name,
  table_description
FROM `bigquery-public-data.idc_current_clinical.table_metadata`
WHERE collection_id = 'nlst'
```

**column_metadata** - Attribute-level details with value mappings:
```sql
SELECT
  collection_id,
  table_name,
  column,
  column_label,
  data_type,
  values
FROM `bigquery-public-data.idc_current_clinical.column_metadata`
WHERE collection_id = 'nlst'
  AND column_label LIKE '%stage%'
```

The `values` field contains observed attribute values with their descriptions (same as in `idc-index` clinical_index).

### Common Clinical Queries

**List available clinical tables:**
```sql
SELECT table_name
FROM `bigquery-public-data.idc_current_clinical.INFORMATION_SCHEMA.TABLES`
WHERE table_name NOT IN ('table_metadata', 'column_metadata')
```

**Find collections with specific clinical attributes:**
```sql
SELECT DISTINCT collection_id, table_name, column, column_label
FROM `bigquery-public-data.idc_current_clinical.column_metadata`
WHERE LOWER(column_label) LIKE '%chemotherapy%'
```

**Query clinical data for a collection:**
```sql
-- Example: NLST cancer staging data
SELECT
  dicom_patient_id,
  clinical_stag,
  path_stag,
  de_stag
FROM `bigquery-public-data.idc_current_clinical.nlst_canc`
WHERE clinical_stag IS NOT NULL
LIMIT 10
```

**Join clinical with imaging data:**
```sql
SELECT
  d.PatientID,
  d.StudyInstanceUID,
  d.Modality,
  c.clinical_stag,
  c.path_stag
FROM `bigquery-public-data.idc_current.dicom_all` d
JOIN `bigquery-public-data.idc_current_clinical.nlst_canc` c
  ON d.PatientID = c.dicom_patient_id
WHERE d.collection_id = 'nlst'
  AND d.Modality = 'CT'
  AND c.clinical_stag = '400'  -- Stage IV
LIMIT 20
```

**Cross-collection clinical search:**
```sql
-- Find all collections with staging information
SELECT
  cm.collection_id,
  cm.table_name,
  cm.column,
  cm.column_label
FROM `bigquery-public-data.idc_current_clinical.column_metadata` cm
WHERE LOWER(cm.column_label) LIKE '%stage%'
ORDER BY cm.collection_id
```

### Key Column: dicom_patient_id

Every clinical table includes `dicom_patient_id`, which matches the DICOM `PatientID` attribute in imaging tables. This is the join key between clinical and imaging data.

**Note:** Clinical table schemas vary significantly by collection. Always check available columns first:
```sql
SELECT column_name, data_type
FROM `bigquery-public-data.idc_current_clinical.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'nlst_canc'
```

See `references/clinical_data_guide.md` for detailed workflows using `idc-index`, which provides the same clinical data without requiring BigQuery authentication.

## Important Notes

- Tables are read-only (public dataset)
- Schema changes between IDC versions
- Use versioned datasets for reproducibility
- Some DICOM sequences >15 levels deep are not extracted
- Very large sequences (>1MB) may be truncated
- Always check data license before use

## Common Errors

**Issue: Billing must be enabled**
- Cause: BigQuery requires a billing-enabled GCP project
- Solution: Enable billing in Google Cloud Console or use idc-index mini-index instead

**Issue: Query exceeds resource limits**
- Cause: Query scans too much data or is too complex
- Solution: Add more specific WHERE filters, use LIMIT, break into smaller queries

**Issue: Column not found**
- Cause: Field name typo or not in selected table
- Solution: Check table schema first with `INFORMATION_SCHEMA.COLUMNS`

**Issue: Permission denied**
- Cause: Not authenticated to Google Cloud
- Solution: Run `gcloud auth application-default login` or set GOOGLE_APPLICATION_CREDENTIALS

## Resources

- [Understanding the BigQuery DICOM schema](https://docs.cloud.google.com/healthcare-api/docs/how-tos/dicom-bigquery-schema)
- [BigQuery Query Syntax](https://docs.cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax)
- [Kaggle Intro to SQL](https://www.kaggle.com/learn/intro-to-sql)
- [Sample BigQuery queries of IDC data](https://github.com/ImagingDataCommons/idc-bigquery-cookbook)

### `references/cli_guide.md`

# idc-index Command Line Interface Guide

The `idc-index` package provides command-line tools for downloading DICOM data from the NCI Imaging Data Commons without writing Python code.

## Installation

Needs `idc-index` installed — run `python scripts/check_version.py`, which reports the installed
version and prints the install command for the interpreter you are running.

After installation, the `idc` command is available in your terminal.

## Available Commands

| Command | Purpose |
|---------|---------|
| `idc download` | General-purpose download with auto-detection of input type |
| `idc download-from-manifest` | Download from manifest file with validation and progress tracking |
| `idc download-from-selection` | Filter-based download with multiple criteria |

---

## idc download

General-purpose download command that intelligently interprets input. It determines whether the input corresponds to a manifest file path or a list of identifiers (collection_id, PatientID, StudyInstanceUID, SeriesInstanceUID, crdc_series_uuid).

### Usage

```bash
# Download entire collection
idc download rider_pilot --download-dir ./data

# Download specific series by UID
idc download "1.3.6.1.4.1.9328.50.1.69736" --download-dir ./data

# Download multiple items (comma-separated)
idc download "tcga_luad,tcga_lusc" --download-dir ./data

# Download from manifest file (auto-detected by file extension)
idc download manifest.txt --download-dir ./data
```

### Options

| Option | Description |
|--------|-------------|
| `--download-dir` | Destination directory (default: current directory) |
| `--dir-template` | Directory hierarchy template (default: `%collection_id/%PatientID/%StudyInstanceUID/%Modality_%SeriesInstanceUID`) |
| `--log-level` | Verbosity: debug, info, warning, error, critical |

### Directory Template Variables

The same templates apply in Python, where the argument is `dirTemplate=` rather than the
`--dir-template` flag. The default is
`%collection_id/%PatientID/%StudyInstanceUID/%Modality_%SeriesInstanceUID`:

```python
# Simplified hierarchy (omit StudyInstanceUID level)
client.download_from_selection(
    downloadDir="./data",
    collection_id="tcga_luad",
    dirTemplate="%collection_id/%PatientID/%Modality"
)
# Results in: ./data/tcga_luad/TCGA-05-4244/CT/

# dirTemplate="" disables the hierarchy, writing every file straight into downloadDir
```

Use these variables in `--dir-template` to organize downloads:

- `%collection_id` - Collection identifier
- `%PatientID` - Patient identifier
- `%StudyInstanceUID` - Study UID
- `%SeriesInstanceUID` - Series UID
- `%Modality` - Imaging modality (CT, MR, PT, etc.)

**Examples:**

```bash
# Flat structure (all files in one directory)
idc download rider_pilot --download-dir ./data --dir-template ""

# Simplified hierarchy
idc download rider_pilot --download-dir ./data --dir-template "%collection_id/%PatientID/%Modality"
```

---

## idc download-from-manifest

Specialized for downloading from manifest files with built-in validation, progress tracking, and resume capability.

### Usage

```bash
# Basic download from manifest
idc download-from-manifest --manifest-file cohort.txt --download-dir ./data

# With progress bar and validation
idc download-from-manifest --manifest-file cohort.txt --download-dir ./data --show-progress-bar

# Resume interrupted download with s5cmd sync
idc download-from-manifest --manifest-file cohort.txt --download-dir ./data --use-s5cmd-sync
```

### Options

| Option | Description |
|--------|-------------|
| `--manifest-file` | **Required.** Path to manifest file containing S3 URLs |
| `--download-dir` | **Required.** Destination directory |
| `--validate-manifest` | Validate manifest before download (enabled by default) |
| `--show-progress-bar` | Display download progress |
| `--use-s5cmd-sync` | Enable resumable downloads - skips already-downloaded files |
| `--quiet` | Suppress subprocess output |
| `--dir-template` | Directory hierarchy template |
| `--log-level` | Logging verbosity |

### Manifest File Format

Manifest files contain S3 URLs, one per line:

```
s3://idc-open-data/cb09464a-c5cc-4428-9339-d7fa87cfe837/*
s3://idc-open-data/88f3990d-bdef-49cd-9b2b-4787767240f2/*
```

**How to get a manifest file:**

1. **IDC Portal**: Export cohort selection as manifest
2. **Python query**: Generate from SQL results

```python
from idc_index import IDCClient

client = IDCClient()
results = client.sql_query("""
    SELECT series_aws_url
    FROM index
    WHERE collection_id = 'rider_pilot' AND Modality = 'CT'
""")

with open('ct_manifest.txt', 'w') as f:
    for url in results['series_aws_url']:
        f.write(url + '\n')
```

---

## idc download-from-selection

Download data using filter criteria. Filters are applied sequentially.

### Usage

```bash
# Download by collection
idc download-from-selection --collection-id rider_pilot --download-dir ./data

# Download specific series
idc download-from-selection --series-instance-uid "1.3.6.1.4.1.9328.50.1.69736" --download-dir ./data

# Multiple filters
idc download-from-selection --collection-id nlst --patient-id "100004" --download-dir ./data

# Dry run - see what would be downloaded without actually downloading
idc download-from-selection --collection-id tcga_luad --dry-run --download-dir ./data
```

### Options

| Option | Description |
|--------|-------------|
| `--download-dir` | **Required.** Destination directory |
| `--collection-id` | Filter by collection identifier |
| `--patient-id` | Filter by patient identifier |
| `--study-instance-uid` | Filter by study UID |
| `--series-instance-uid` | Filter by series UID |
| `--crdc-series-uuid` | Filter by CRDC UUID |
| `--dry-run` | Calculate cohort size without downloading |
| `--show-progress-bar` | Display download progress |
| `--use-s5cmd-sync` | Enable resumable downloads |
| `--dir-template` | Directory hierarchy template |

### Dry Run for Size Estimation

Use `--dry-run` to estimate download size before committing:

```bash
idc download-from-selection --collection-id nlst --dry-run --download-dir ./data
```

This shows:
- Number of series matching filters
- Total download size
- No files are downloaded

---

## Common Workflows

### 1. Download Small Collection for Testing

```bash
# rider_pilot is ~1GB - good for testing
idc download rider_pilot --download-dir ./test_data
```

### 2. Large Dataset with Progress and Resume

```bash
# Use s5cmd sync for large downloads - can resume if interrupted
idc download-from-selection \
    --collection-id nlst \
    --download-dir ./nlst_data \
    --show-progress-bar \
    --use-s5cmd-sync
```

### 3. Estimate Size Before Download

```bash
# Check size first
idc download-from-selection --collection-id tcga_luad --dry-run --download-dir ./data

# Then download if size is acceptable
idc download-from-selection --collection-id tcga_luad --download-dir ./data
```

### 4. Download Specific Modality via Python + CLI

```python
# First, query for series UIDs in Python
from idc_index import IDCClient

client = IDCClient()
results = client.sql_query("""
    SELECT SeriesInstanceUID
    FROM index
    WHERE collection_id = 'nlst'
      AND Modality = 'CT'
      AND BodyPartExamined = 'CHEST'
    LIMIT 50
""")

# Save to manifest
results['SeriesInstanceUID'].to_csv('my_series.csv', index=False, header=False)
```

```bash
# Then download via CLI
idc download my_series.csv --download-dir ./lung_ct
```

---

## Built-in Safety Features

The CLI includes several safety features:

- **Disk space checking**: Verifies sufficient space before starting downloads
- **Manifest validation**: Validates manifest file format by default
- **Progress tracking**: Optional progress bar for monitoring large downloads
- **Resume capability**: Use `--use-s5cmd-sync` to continue interrupted downloads

---

## Troubleshooting

### Download Interrupted

Use `--use-s5cmd-sync` to resume:

```bash
idc download-from-manifest --manifest-file cohort.txt --download-dir ./data --use-s5cmd-sync
```

### Connection Timeout

For unstable networks, download in smaller batches using Python to generate multiple manifests, then download sequentially.

---

## See Also

- [idc-index Documentation](https://idc-index.readthedocs.io/)
- [IDC Portal](https://portal.imaging.datacommons.cancer.gov/) - Interactive cohort building
- [IDC Tutorials](https://github.com/ImagingDataCommons/IDC-Tutorials)

### `references/clinical_data_guide.md`

# Clinical Data Guide for IDC

**Tested with:** idc-index 0.12.5 (IDC data version v24)

Clinical data (demographics, diagnoses, therapies, lab tests, staging) accompanies many IDC imaging collections. This guide covers how to discover, access, and integrate clinical data with imaging data using `idc-index`.

## When to Use This Guide

Use this guide when you need to:
- Find what clinical metadata is available for a collection
- Filter patients by clinical criteria (e.g., cancer stage, treatment history)
- Join clinical attributes with imaging data for cohort selection
- Understand and decode coded values in clinical tables

For basic clinical data access, see the "Clinical Data Access" section in the main SKILL.md. This guide provides detailed workflows and advanced patterns.

## Prerequisites

Needs `idc-index` installed — run `python scripts/check_version.py`, which reports the installed
version and prints the install command for the interpreter you are running.

No BigQuery credentials required - clinical data is packaged with `idc-index`.

## Understanding Clinical Data in IDC

### What is Clinical Data?

Clinical data refers to non-imaging information that accompanies medical images:
- Patient demographics (age, sex, race)
- Clinical history (diagnoses, surgeries, therapies)
- Lab tests and pathology results
- Cancer staging (clinical and pathological)
- Treatment outcomes

### Data Organization

Clinical data in IDC comes from collection-specific spreadsheets provided by data submitters. IDC parses these into queryable tables accessible via `idc-index`.

**Important characteristics:**
- Clinical data is **not harmonized** across collections (terms and formats vary)
- Not all collections have clinical data (check availability first)
- All data is **anonymized** - `dicom_patient_id` links to imaging

### The clinical_index Table

The `clinical_index` serves as a dictionary/catalog of all available clinical data:

| Column | Purpose | Use For |
|--------|---------|---------|
| `collection_id` | Collection identifier | Filtering by collection |
| `table_name` | Full BigQuery table reference | BigQuery queries (if needed) |
| `short_table_name` | Short name | `get_clinical_table()` method |
| `column` | Column name in table | Selecting data columns |
| `column_label` | Human-readable description | Searching for concepts |
| `values` | Observed attribute values for the column | Interpreting coded values |

### The `values` Column

The `values` column contains an array of observed attribute values for the column defined in the `column` field. Each entry has:
- **option_code**: The actual value observed in that column
- **option_description**: Human-readable description of that value (from data dictionary if available, otherwise `None`)

For ACRIN collections, value descriptions come from provided data dictionaries. For other collections, they are derived from inspection of the actual data values.

**Note:** For columns with >20 unique values, the `values` array is left empty (`[]`) for simplicity.

## Core Workflow

### Step 1: Fetch Clinical Index

```python
from idc_index import IDCClient

client = IDCClient()
client.fetch_index('clinical_index')

# View available columns
print(client.clinical_index.columns.tolist())
```

### Step 2: Discover Available Clinical Data

```python
# List all collections with clinical data
collections_with_clinical = client.clinical_index["collection_id"].unique().tolist()
print(f"{len(collections_with_clinical)} collections have clinical data")

# Find clinical attributes for a specific collection
nlst_columns = client.clinical_index[client.clinical_index['collection_id']=='nlst']
nlst_columns[['short_table_name', 'column', 'column_label', 'values']]
```

### Step 3: Search for Specific Attributes

```python
# Search by keyword in column_label (case-insensitive)
stage_attrs = client.clinical_index[
    client.clinical_index["column_label"].str.contains("[Ss]tage", na=False)
]
stage_attrs[["collection_id", "short_table_name", "column", "column_label"]]
```

### Step 4: Load Clinical Table

```python
# Load table using short_table_name
nlst_canc_df = client.get_clinical_table("nlst_canc")

# Examine structure
print(f"Rows: {len(nlst_canc_df)}, Columns: {len(nlst_canc_df.columns)}")
nlst_canc_df.head()
```

### Step 5: Map Coded Values to Descriptions

Many clinical attributes use coded values. The `values` column in `clinical_index` contains an array of observed values with their descriptions (when available).

```python
# Get the clinical_index rows for NLST
nlst_clinical_columns = client.clinical_index[client.clinical_index['collection_id']=='nlst']

# Get observed values for a specific column
# Filter to the row for 'clinical_stag' and extract the values array
clinical_stag_values = nlst_clinical_columns[
    nlst_clinical_columns['column']=='clinical_stag'
]['values'].values[0]

# View the observed values and their descriptions
print(clinical_stag_values)
# Output: array([{'option_code': '.M', 'option_description': 'Missing'},
#                {'option_code': '110', 'option_description': 'Stage IA'},
#                {'option_code': '120', 'option_description': 'Stage IB'}, ...])

# Create mapping dictionary from codes to descriptions
mapping_dict = {item['option_code']: item['option_description'] for item in clinical_stag_values}

# Apply to DataFrame - convert column to string first for consistent matching
nlst_canc_df['clinical_stag_meaning'] = nlst_canc_df['clinical_stag'].astype(str).map(mapping_dict)
```

### Step 6: Join with Imaging Data

The `dicom_patient_id` column links clinical data to imaging. It matches the `PatientID` column in the imaging index.

```python
# Pandas merge approach
import pandas as pd

# Get NLST CT imaging data
nlst_imaging = client.index[(client.index['collection_id']=='nlst') & (client.index['Modality']=='CT')]

# Join with clinical data
merged = pd.merge(
    nlst_imaging[['PatientID', 'StudyInstanceUID']].drop_duplicates(),
    nlst_canc_df[['dicom_patient_id', 'clinical_stag', 'clinical_stag_meaning']],
    left_on='PatientID',
    right_on='dicom_patient_id',
    how='inner'
)
```

```python
# SQL join approach
# Clinical tables loaded via get_clinical_table() are not automatically
# registered in DuckDB. Register the DataFrame manually before joining.
nlst_canc_df = client.get_clinical_table("nlst_canc")
client._duckdb_conn.register("nlst_canc", nlst_canc_df)

query = """
SELECT
  index.PatientID,
  index.StudyInstanceUID,
  index.Modality,
  nlst_canc.clinical_stag
FROM index
JOIN nlst_canc ON index.PatientID = nlst_canc.dicom_patient_id
WHERE index.collection_id = 'nlst' AND index.Modality = 'CT'
"""
results = client.sql_query(query)
```

## Common Use Cases

### Use Case 1: Select Patients by Cancer Stage

```python
from idc_index import IDCClient
import pandas as pd

client = IDCClient()
client.fetch_index('clinical_index')

# Load clinical table
nlst_canc = client.get_clinical_table("nlst_canc")

# Select Stage IV patients (code '400')
stage_iv_patients = nlst_canc[nlst_canc['clinical_stag'] == '400']['dicom_patient_id']

# Get CT imaging studies for these patients
stage_iv_studies = pd.merge(
    client.index[(client.index['collection_id']=='nlst') & (client.index['Modality']=='CT')],
    stage_iv_patients,
    left_on='PatientID',
    right_on='dicom_patient_id',
    how='inner'
)['StudyInstanceUID'].drop_duplicates()

print(f"Found {len(stage_iv_studies)} CT studies for Stage IV patients")
```

### Use Case 2: Find Collections with Specific Clinical Attributes

```python
# Find collections with chemotherapy information
chemo_collections = client.clinical_index[
    client.clinical_index["column_label"].str.contains("[Cc]hemotherapy", na=False)
]["collection_id"].unique()

print(f"Collections with chemotherapy data: {list(chemo_collections)}")
```

### Use Case 3: Examine Observed Values for a Clinical Attribute

```python
# Find what values have been observed for a specific attribute
chemotherapy_rows = client.clinical_index[
    (client.clinical_index["collection_id"] == "hcc_tace_seg") &
    (client.clinical_index["column"] == "chemotherapy")
]

# Get the observed values array
values_list = chemotherapy_rows["values"].tolist()
print(values_list)
# Output: [[{'option_code': 'Cisplastin', 'option_description': None},
#           {'option_code': 'Cisplatin, Mitomycin-C', 'option_description': None}, ...]]
```

### Use Case 4: Generate Viewer URLs for Selected Patients

```python
import random

# Get studies for a sample Stage IV patient
sample_patient = stage_iv_patients.iloc[0]
studies = client.index[client.index['PatientID'] == sample_patient]['StudyInstanceUID'].unique()

# Generate viewer URL
if len(studies) > 0:
    viewer_url = client.get_viewer_URL(studyInstanceUID=studies[0])
    print(viewer_url)
```

## Key Concepts

### column vs column_label

- **column**: Use for selecting data from tables (programmatic access)
- **column_label**: Use for searching/understanding what data means (human-readable)

Some collections (like `c4kc_kits`) have identical column and column_label. Others (like ACRIN collections) have cryptic column names but descriptive labels.

### option_code vs option_description

The `values` array contains observed attribute values:
- **option_code**: The actual value observed in the column (what you filter on)
- **option_description**: Human-readable description (from data dictionary if available, otherwise `None`)

### dicom_patient_id

Every clinical table includes `dicom_patient_id`, which matches the `PatientID` column in the imaging index. This is the key for joining clinical and imaging data.

## Troubleshooting

### Issue: Clinical table not found

**Cause:** Using wrong table name or table doesn't exist for collection

**Solution:** Query clinical_index first to find available tables:
```python
client.clinical_index[client.clinical_index['collection_id']=='your_collection']['short_table_name'].unique()
```

### Issue: Empty values array

**Cause:** The `values` array is left empty when a column has >20 unique values

**Solution:** Load the clinical table and examine unique values directly:
```python
clinical_df = client.get_clinical_table("table_name")
clinical_df['column_name'].unique()
```

### Issue: Coded values not in mapping

**Cause:** Some values may be missing from the dictionary (e.g., empty strings, special codes like `.M` for missing)

**Solution:** Handle unmapped values gracefully:
```python
df['meaning'] = df['code'].astype(str).map(mapping_dict).fillna('Unknown/Missing')
```

### Issue: No matching patients when joining

**Cause:** Clinical data may include patients without images, or vice versa

**Solution:** Verify patient overlap before joining:
```python
imaging_patients = set(client.index[client.index['collection_id']=='nlst']['PatientID'].unique())
clinical_patients = set(clinical_df['dicom_patient_id'].unique())
overlap = imaging_patients & clinical_patients
print(f"Patients with both imaging and clinical data: {len(overlap)}")
```

## Resources

**IDC Documentation:**
- [Clinical data organization](https://learn.canceridc.dev/data/organization-of-data/clinical) - How clinical data is organized in IDC
- [Clinical data dashboard](https://datastudio.google.com/u/0/reporting/04cf5976-4ea0-4fee-a749-8bfd162f2e87/page/p_s7mk6eybqc) - Visual summary of available clinical data
- [idc-index clinical_index documentation](https://idc-index.readthedocs.io/en/latest/column_descriptions.html#clinical-index)

**Related Guides:**
- `bigquery_guide.md` - Advanced clinical queries via BigQuery
- Main SKILL.md - Core IDC workflows

**IDC Tutorials:**
- [clinical_data_intro.ipynb](https://github.com/ImagingDataCommons/IDC-Tutorials/blob/master/notebooks/advanced_topics/clinical_data_intro.ipynb)
- [exploring_clinical_data.ipynb](https://github.com/ImagingDataCommons/IDC-Tutorials/blob/master/notebooks/getting_started/exploring_clinical_data.ipynb)
- [nlst_clinical_data.ipynb](https://github.com/ImagingDataCommons/IDC-Tutorials/blob/master/notebooks/collections_demos/nlst_clinical_data.ipynb)

### `references/cloud_storage_guide.md`

# Cloud Storage Guide for IDC

IDC maintains all DICOM files in public cloud storage buckets mirrored between Google Cloud Storage (GCS) and AWS S3. This guide covers bucket organization, file structure, access methods, and versioning.

## When to Use Direct Cloud Storage Access

Use direct bucket access when you need:
- Maximum download performance with parallel transfers
- Integration with cloud-native workflows (e.g., running analysis on cloud VMs)
- Programmatic access from tools like s5cmd or gsutil
- Access to specific file versions for reproducibility

For most use cases, `idc-index` is simpler and recommended -— it uses s5cmd internally to download from these same S3 buckets, handling the UUID lookups automatically. Use direct cloud storage when you need raw file access, custom parallelization, or are building cloud-native pipelines.

## Storage Buckets

IDC organizes data across multiple buckets based on licensing and content type. All buckets are mirrored between AWS and GCS with identical content and file paths.

### Bucket Summary

| Purpose | AWS S3 Bucket | GCS Bucket | License | Content |
|---------|---------------|------------|---------|---------|
| Primary data | `idc-open-data` | `idc-open-data` | No commercial restriction | >90% of IDC data |
| Head scans | `idc-open-data-two` | `idc-open-idc1` | No commercial restriction | Collections potentially containing head imaging |
| Commercial-restricted | `idc-open-data-cr` | `idc-open-cr` | Commercial use restricted (CC BY-NC) | ~4% of data |

**Notes:**
- All AWS buckets are in AWS region `us-east-1`
- Prior to IDC v19, GCS used `public-datasets-idc` (now superseded by `idc-open-data`)
- The head scans bucket exists for potential future policy changes regarding facial imaging data
- **Important** Use `idc-index` to get license information - do not rely on bucket name! 

### Why Multiple Buckets?

1. **Licensing separation**: Data with commercial-use restrictions (CC BY-NC) is isolated in `idc-open-data-cr` / `idc-open-cr` to prevent accidental commercial use
2. **Head scan handling**: Collections labeled by TCIA as potentially containing head scans are in separate buckets (`idc-open-data-two` / `idc-open-idc1`) for potential future policy compliance
3. **Historical reasons**: The bucket structure evolved as IDC grew and partnered with different cloud programs

## File Organization Within Buckets

Files are organized by CRDC UUIDs, not DICOM UIDs. This enables versioning while maintaining consistent paths across cloud providers.

### Directory Structure

```
<bucket>/
└── <crdc_series_uuid>/
    ├── <crdc_instance_uuid_1>.dcm
    ├── <crdc_instance_uuid_2>.dcm
    └── ...
```

**Example path:**
```
s3://idc-open-data/7a6b2389-53c6-4c5b-b07f-6d1ed4a3eed9/0d73f84e-70ae-4eeb-96a0-1c613b5d9229.dcm
```

- `7a6b2389-53c6-4c5b-b07f-6d1ed4a3eed9` = series UUID (folder)
- `0d73f84e-70ae-4eeb-96a0-1c613b5d9229.dcm` = instance UUID (file)

### CRDC UUIDs vs DICOM UIDs

| Identifier Type | Format | Changes When | Use For |
|-----------------|--------|--------------|---------|
| DICOM UID (e.g., SeriesInstanceUID) | Numeric (e.g., `1.3.6.1.4...`) | Never (included in DICOM metadata) | Clinical identification, DICOMweb queries |
| CRDC UUID (e.g., crdc_series_uuid) | UUID (e.g., `e127d258-37c2-...`) | Content changes | File paths, versioning, reproducibility |

**Key insight:** A single DICOM SeriesInstanceUID may have multiple CRDC series UUIDs across IDC versions if the series content changed (instances added/removed, metadata corrected). The CRDC UUID uniquely identifies a specific version of the data.

### Mapping DICOM UIDs to File Paths

Use `idc-index` to get file URLs from DICOM identifiers:

```python
from idc_index import IDCClient

client = IDCClient()

# Get all file URLs for a series
series_uid = "1.3.6.1.4.1.14519.5.2.1.6450.9002.217441095430480124587725641302"
urls = client.get_series_file_URLs(seriesInstanceUID=series_uid)

for url in urls[:3]:
    print(url)
# Returns S3 URLs like: s3://idc-open-data/<crdc_series_uuid>/<crdc_instance_uuid>.dcm
```

Or query the index directly for URL columns:

```python
# Get series-level URL (points to folder)
result = client.sql_query("""
    SELECT SeriesInstanceUID, series_aws_url
    FROM index
    WHERE collection_id = 'rider_pilot' AND Modality = 'CT'
    LIMIT 3
""")

print(result[['SeriesInstanceUID', 'series_aws_url']])
```

**Available URL column in index:**
- `series_aws_url`: S3 URL to series folder (e.g., `s3://idc-open-data/uuid/*`)

GCS URLs follow the same path structure—replace `s3://` with `gs://` (e.g., `gs://idc-open-data/uuid/*`). When using `idc-index` download methods, GCS access is handled internally.

## Accessing Cloud Storage

All IDC buckets support free egress (no download fees) through partnerships with AWS Open Data and Google Public Data programs. No authentication required.

### AWS S3 Access

**Using AWS CLI (no account required):**
```bash
# List bucket contents
aws s3 ls --no-sign-request s3://idc-open-data/

# List files in a series folder
aws s3 ls --no-sign-request s3://idc-open-data/7a6b2389-53c6-4c5b-b07f-6d1ed4a3eed9/

# Download a single file
aws s3 cp --no-sign-request \
    s3://idc-open-data/7a6b2389-53c6-4c5b-b07f-6d1ed4a3eed9/0d73f84e-70ae-4eeb-96a0-1c613b5d9229.dcm \
    ./local_file.dcm

# Download entire series folder
aws s3 cp --no-sign-request --recursive \
    s3://idc-open-data/7a6b2389-53c6-4c5b-b07f-6d1ed4a3eed9/ \
    ./series_folder/
```

**Using s5cmd (faster for bulk downloads):**
```bash
# Install s5cmd
# macOS: brew install s5cmd
# Linux: download from https://github.com/peak/s5cmd/releases

# Download specific series
s5cmd --no-sign-request cp 's3://idc-open-data/7a6b2389-53c6-4c5b-b07f-6d1ed4a3eed9/*' ./local_folder/

# Download from manifest file
s5cmd --no-sign-request run manifest.txt
```

**s5cmd manifest format:** The `s5cmd run` command expects one s5cmd command per line, not just URLs:
```
cp s3://idc-open-data/uuid1/instance1.dcm ./local_folder/
cp s3://idc-open-data/uuid1/instance2.dcm ./local_folder/
cp s3://idc-open-data/uuid2/instance3.dcm ./local_folder/
```

IDC Portal exports manifests in this format. When creating manifests programmatically, use `idc-index` download methods (which handle this internally) rather than constructing manifests manually.

### GCS Access

**Using gsutil:**
```bash
# List bucket contents
gsutil ls gs://idc-open-data/

# Download a series folder
gsutil -m cp -r gs://idc-open-data/7a6b2389-53c6-4c5b-b07f-6d1ed4a3eed9/ ./local_folder/
```

**Using gcloud storage (newer CLI):**
```bash
gcloud storage cp -r gs://idc-open-data/7a6b2389-53c6-4c5b-b07f-6d1ed4a3eed9/ ./local_folder/
```

### Python Direct Access

```python
import s3fs
import gcsfs
from idc_index import IDCClient

# First, get a file URL from idc-index
client = IDCClient()
result = client.sql_query("""
    SELECT series_aws_url
    FROM index
    WHERE collection_id = 'rider_pilot' AND Modality = 'CT'
    LIMIT 1
""")
# series_aws_url is like: s3://idc-open-data/<uuid>/*
series_url = result['series_aws_url'].iloc[0]
series_path = series_url.replace('s3://', '').rstrip('/*')  # e.g., "idc-open-data/<uuid>"

# AWS S3 access
s3 = s3fs.S3FileSystem(anon=True)
files = s3.ls(series_path)
with s3.open(files[0], 'rb') as f:
    data = f.read()

# GCS access (same path structure as AWS)
gcs = gcsfs.GCSFileSystem(token='anon')
files = gcs.ls(series_path)
with gcs.open(files[0], 'rb') as f:
    data = f.read()
```

## Versioning and Reproducibility

IDC releases new data versions every 2-4 months. The versioning system ensures reproducibility by preserving all historical data.

### How Versioning Works

1. **Snapshots**: Each IDC version (v1, v2, ..., v24, etc.) represents a complete snapshot of all data at release time
2. **UUID-based**: When data changes, new CRDC UUIDs are assigned; old UUIDs remain accessible
3. **Cumulative buckets**: All versions coexist in the same buckets—old series folders

**Version change scenarios:**
| Change Type | DICOM UID | CRDC UUID | Effect |
|-------------|-----------|-----------|--------|
| New series added | New | New | New folder in bucket |
| Instance added to series | Same | New series UUID | New folder, instances may be duplicated |
| Metadata corrected | Same or new | New | New folder with updated files |
| Series removed | N/A | N/A | Old folder remains, not in current index |

**Data removal caveat:** In rare circumstances (e.g., data owner request, PHI incident), data may be removed from IDC entirely, including from all historical versions.

**BigQuery versioned datasets (metadata only, not file storage):**

For querying version-specific metadata, BigQuery provides versioned tables. See `bigquery_guide.md` for details.
- `bigquery-public-data.idc_current` — alias to latest version
- `bigquery-public-data.idc_v24` — specific version (replace 24 with desired version)

### Reproducing a Previous Analysis

The simplest way to ensure reproducibility is to save the `crdc_series_uuid` values of the data you use at analysis time:

```python
from idc_index import IDCClient
import json

client = IDCClient()

# Select data for your analysis
selection = client.sql_query("""
    SELECT crdc_series_uuid
    FROM index
    WHERE collection_id = 'tcga_luad'
      AND Modality = 'CT'
    LIMIT 10
""")
series_uuids = list(selection['crdc_series_uuid'])

# Download the data
client.download_from_selection(seriesInstanceUID=series_uuids, downloadDir="./data")

# Save a manifest for reproducibility
manifest = {
    "crdc_series_uuids": series_uuids,
    "download_date": "2024-01-15",
    "idc_version": client.get_idc_version(),
    "description": "CT scans for lung cancer analysis"
}
with open("analysis_manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)

# Later, reproduce the exact dataset:
with open("analysis_manifest.json") as f:
    manifest = json.load(f)
client.download_from_selection(
    seriesInstanceUID=manifest["crdc_series_uuids"],
    downloadDir="./reproduced_data"
)
```

Since `crdc_series_uuid` identifies an immutable version of each series, saving these UUIDs guarantees you can retrieve the exact same files later.

## Relationship Between Buckets, Versions, and Other Access Methods

### Data Coverage Comparison

| Access Method | Buckets Included | Coverage | Versions |
|---------------|------------------|----------|----------|
| Direct bucket access | All 3 buckets | 100% | All historical |
| `idc-index` download | All 3 buckets | 100% | Current + prior_versions_index |
| IDC Portal | All 3 buckets | 100% | Current only |
| DICOMweb public proxy | All 3 buckets | 100% | Current only |
| Google Healthcare DICOM | `idc-open-data` only | ~96% | Current only |

**Important:** The Google Healthcare API DICOM store only replicates data from `idc-open-data`. Data in `idc-open-data-two` and `idc-open-data-cr` (approximately 4% of total) is not available via Google Healthcare DICOMweb endpoint.

## Best Practices

- **Use `idc-index` for discovery**: Query metadata first, then access buckets with known UUIDs
- **Download defaults to AWS buckets**: request GCS if needed
- **Save manifests**: Store the `series_aws_url` or `crdc_series_uuid` values for reproducibility
- **Check licenses**: Query `license_short_name` before commercial use; CC-NC data requires non-commercial use
- **Use current version unless reproducing**: The `index` table has current data; use `prior_versions_index` only for exact reproducibility

## Troubleshooting

### Issue: "Access Denied" when accessing buckets
- **Cause:** Using signed requests or wrong bucket name
- **Solution:** Use `--no-sign-request` flag with AWS CLI, or `anon=True` with Python libraries

### Issue: File not found at expected path
- **Cause:** Using DICOM UID instead of CRDC UUID, or data changed in newer version
- **Solution:** Query `idc-index` for current `series_aws_url`, or check `prior_versions_index` for historical paths

### Issue: Downloaded files don't match expected series
- **Cause:** Series was revised in a newer IDC version
- **Solution:** Use `prior_versions_index` to find the exact version you need; compare `crdc_series_uuid` values

### Issue: Some data missing from Google Healthcare DICOMweb
- **Cause:** Google Healthcare only mirrors `idc-open-data` bucket (~96% of data)
- **Solution:** Use IDC public proxy for 100% coverage, or access buckets directly

## Resources

**IDC Documentation:**
- [Files and metadata](https://learn.canceridc.dev/data/organization-of-data/files-and-metadata) - Bucket organization details
- [Data versioning](https://learn.canceridc.dev/data/data-versioning) - Versioning scheme explanation
- [Resolving GUIDs and UUIDs](https://learn.canceridc.dev/data/organization-of-data/guids-and-uuids) - CRDC UUID documentation
- [Direct loading from cloud](https://learn.canceridc.dev/data/downloading-data/direct-loading) - Python examples for cloud access

**AWS Resources:**
- [NCI IDC on AWS Open Data Registry](https://registry.opendata.aws/nci-imaging-data-commons/) - Bucket ARNs and access info
- [s5cmd](https://github.com/peak/s5cmd) - High-performance S3 client (used internally by idc-index)
- [AWS CLI S3 commands](https://docs.aws.amazon.com/cli/latest/reference/s3/) - Standard AWS command-line interface
- [Boto3 S3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html) - AWS SDK for Python

**Google Cloud Resources:**
- [gsutil tool](https://cloud.google.com/storage/docs/gsutil) - Google Cloud Storage command-line tool
- [gcloud storage commands](https://cloud.google.com/sdk/gcloud/reference/storage) - Modern GCS CLI (recommended over gsutil)
- [Google Cloud Storage Python client](https://cloud.google.com/python/docs/reference/storage/latest) - GCS SDK for Python

**Related Guides:**
- `dicomweb_guide.md` - DICOMweb API access (alternative to direct bucket access)
- `bigquery_guide.md` - Advanced metadata queries including versioned datasets

### `references/dicomweb_guide.md`

# DICOMweb Guide for IDC

IDC provides DICOMweb access through Google Cloud Healthcare API DICOM stores. This guide covers the implementation specifics and usage patterns.

## When to Use DICOMweb

Use DICOMweb when you need:
- Integration with PACS systems or DICOMweb-compatible tools
- Streaming metadata without downloading full files
- Building custom viewers or web applications
- Using existing DICOMweb client libraries (OHIF, dicomweb-client, etc.)

For most use cases, `idc-index` is simpler and recommended. Use DICOMweb when you specifically need the DICOMweb protocol.

## Endpoints

### Public Proxy (No Authentication)

```
https://proxy.imaging.datacommons.cancer.gov/current/viewer-only-no-downloads-see-tinyurl-dot-com-slash-3j3d9jyp/dicomWeb
```

- **100% data coverage** - Contains all IDC data from all storage buckets
- Points to the latest IDC version automatically
- **Updates immediately** on new IDC releases
- Per-IP daily quota (suitable for testing and moderate use)
- No authentication required
- Read-only access
- Note: "viewer-only-no-downloads" in URL is legacy naming with no functional meaning

### Google Healthcare API (Requires Authentication)

```
https://healthcare.googleapis.com/v1/projects/nci-idc-data/locations/us-central1/datasets/idc/dicomStores/idc-store-v{VERSION}/dicomWeb
```

Replace `{VERSION}` with the IDC release number. To find the current version:

```python
from idc_index import IDCClient
client = IDCClient()
print(client.get_idc_version())  # e.g., "v24" for current version
```

- **~96% data coverage** - Only replicates data from `idc-open-data` bucket (missing ~4% from other buckets)
- **Updates 1-2 weeks after** IDC releases
- Requires authentication and provides higher quotas
- Better performance (no proxy routing)
- Each release gets a new versioned store

See [Content Coverage Differences](#content-coverage-differences) and [Authentication](#authentication-for-google-healthcare-api) sections below.

## Content Coverage Differences

**Important:** The two DICOMweb endpoints have different data coverage. The IDC public proxy contains MORE data than the authenticated Google Healthcare endpoint.

### Coverage Summary

| Endpoint | Coverage | Missing Data |
|----------|----------|--------------|
| **IDC Public Proxy** | 100% | None |
| **Google Healthcare API** | ~96% | ~4% (two buckets not replicated) |

### What's Missing from Google Healthcare?

The Google Healthcare DICOM store **only replicates data from the `idc-open-data` S3 bucket**. It does not include data from two additional buckets:

- `idc-open-data-cr`
- `idc-open-data-two`

These missing buckets typically contain several thousand series each, representing approximately 4% of total IDC data. The exact counts vary by IDC version.

See `cloud_storage_guide.md` for details on bucket organization, file structure, and direct access methods.

### Update Timing

- **IDC Public Proxy**: Updates immediately when new IDC versions are released
- **Google Healthcare**: Updates 1-2 weeks after each new IDC version release

Between releases, both endpoints remain current. The 1-2 week delay only occurs during the transition period after a new IDC version is published.

**Warning from IDC documentation:** *"Google-hosted DICOM store may not contain the latest version of IDC data!"* - Check during the weeks following a new release.

### Choosing the Right Endpoint

**Use IDC Public Proxy when:**
- You need complete data coverage (100%)
- You need the absolute latest data immediately after a new version release
- You don't want to set up GCP authentication
- Your usage fits within per-IP quotas (can request increases via support@canceridc.dev)
- You're accessing slide microscopy images frame-by-frame

**Use Google Healthcare API when:**
- The ~4% missing data doesn't affect your use case
- You need higher quotas for heavy usage
- You want better performance (direct access, no proxy routing)

### Checking Your Data Availability

Before choosing an endpoint, verify whether your data might be in the missing buckets:

```python
from idc_index import IDCClient

client = IDCClient()

# Check which buckets contain your collection's data
results = client.sql_query("""
    SELECT series_aws_url, COUNT(*) as series_count
    FROM index
    WHERE collection_id = 'your_collection_id'
    GROUP BY series_aws_url
""")

print(results)

# Look for URLs containing 'idc-open-data-cr' or 'idc-open-data-two'
# If present, that data won't be available in Google Healthcare endpoint
```

## Implementation Details

IDC DICOMweb is provided through Google Cloud Healthcare API DICOM stores. The implementation follows DICOM PS3.18 Web Services with specific characteristics documented in the [Google Healthcare DICOM conformance statement](https://docs.cloud.google.com/healthcare-api/docs/dicom).

### Supported Operations

| Service | Description | Supported |
|---------|-------------|-----------|
| QIDO-RS | Search for DICOM objects | Yes |
| WADO-RS | Retrieve DICOM objects and metadata | Yes |
| STOW-RS | Store DICOM objects | No (IDC is read-only) |

**Not supported:** URI Service, Worklist Service, Non-Patient Instance Service, Capabilities Transactions

### Searchable DICOM Tags (QIDO-RS)

The implementation supports a limited set of searchable tags:

| Level | Searchable Tags |
|-------|-----------------|
| Study | StudyInstanceUID, PatientName, PatientID, AccessionNumber, ReferringPhysicianName, StudyDate |
| Series | All study tags + SeriesInstanceUID, Modality |
| Instance | All series tags + SOPInstanceUID |

**Important:** Only exact matching is supported, except for:
- StudyDate: supports range queries
- PatientName: supports fuzzy matching

### Query Limitations

- Maximum results: 5,000 for studies/series searches; 50,000 for instances
- Maximum offset: 1,000,000
- DICOM sequence tags larger than ~1 MB are not returned in metadata (BulkDataURI provided instead)

## Code Examples

All examples use the public proxy endpoint. For authenticated access to Google Healthcare, see the [authentication section](#authentication-for-google-healthcare-api).

### Finding UIDs with idc-index

Use `idc-index` to discover data, then use DICOMweb for metadata access:

```python
from idc_index import IDCClient

client = IDCClient()

# Find studies of interest
results = client.sql_query("""
    SELECT StudyInstanceUID, SeriesInstanceUID, PatientID, Modality
    FROM index
    WHERE collection_id = 'tcga_luad' AND Modality = 'CT'
    LIMIT 5
""")

# Use these UIDs with DICOMweb
study_uid = results.iloc[0]['StudyInstanceUID']
series_uid = results.iloc[0]['SeriesInstanceUID']
print(f"Study: {study_uid}")
print(f"Series: {series_uid}")
```

### QIDO-RS: Search by UID

```python
import requests

base_url = "https://proxy.imaging.datacommons.cancer.gov/current/viewer-only-no-downloads-see-tinyurl-dot-com-slash-3j3d9jyp/dicomWeb"

# Search for a specific study
study_uid = "1.3.6.1.4.1.14519.5.2.1.6450.9002.307623500513044641407722230440"
response = requests.get(
    f"{base_url}/studies",
    params={"StudyInstanceUID": study_uid},
    headers={"Accept": "application/dicom+json"}
)

if response.status_code == 200:
    studies = response.json()
    print(f"Found {len(studies)} study")
```

### QIDO-RS: List Series in a Study

```python
import requests

base_url = "https://proxy.imaging.datacommons.cancer.gov/current/viewer-only-no-downloads-see-tinyurl-dot-com-slash-3j3d9jyp/dicomWeb"
study_uid = "1.3.6.1.4.1.14519.5.2.1.6450.9002.307623500513044641407722230440"

response = requests.get(
    f"{base_url}/studies/{study_uid}/series",
    headers={"Accept": "application/dicom+json"}
)

if response.status_code == 200:
    series_list = response.json()
    for series in series_list:
        # DICOM tags are returned as hex codes
        series_uid = series.get("0020000E", {}).get("Value", [None])[0]
        modality = series.get("00080060", {}).get("Value", [None])[0]
        description = series.get("0008103E", {}).get("Value", [""])[0]
        print(f"{modality}: {description}")
```

### QIDO-RS: List Instances in a Series

```python
import requests

base_url = "https://proxy.imaging.datacommons.cancer.gov/current/viewer-only-no-downloads-see-tinyurl-dot-com-slash-3j3d9jyp/dicomWeb"
study_uid = "1.3.6.1.4.1.14519.5.2.1.6450.9002.307623500513044641407722230440"
series_uid = "1.3.6.1.4.1.14519.5.2.1.6450.9002.217441095430480124587725641302"

response = requests.get(
    f"{base_url}/studies/{study_uid}/series/{series_uid}/instances",
    params={"limit": 10},
    headers={"Accept": "application/dicom+json"}
)

if response.status_code == 200:
    instances = response.json()
    print(f"Found {len(instances)} instances")
    for inst in instances[:3]:
        sop_uid = inst.get("00080018", {}).get("Value", [None])[0]
        print(f"  SOPInstanceUID: {sop_uid}")
```

### WADO-RS: Retrieve Series Metadata

```python
import requests

base_url = "https://proxy.imaging.datacommons.cancer.gov/current/viewer-only-no-downloads-see-tinyurl-dot-com-slash-3j3d9jyp/dicomWeb"
study_uid = "1.3.6.1.4.1.14519.5.2.1.6450.9002.307623500513044641407722230440"
series_uid = "1.3.6.1.4.1.14519.5.2.1.6450.9002.217441095430480124587725641302"

response = requests.get(
    f"{base_url}/studies/{study_uid}/series/{series_uid}/metadata",
    headers={"Accept": "application/dicom+json"}
)

if response.status_code == 200:
    instances = response.json()
    print(f"Retrieved metadata for {len(instances)} instances")

    # Extract image dimensions from first instance
    if instances:
        inst = instances[0]
        rows = inst.get("00280010", {}).get("Value", [None])[0]
        cols = inst.get("00280011", {}).get("Value", [None])[0]
        print(f"Image dimensions: {rows} x {cols}")
```

### Combined Workflow: idc-index Discovery + DICOMweb Metadata

```python
from idc_index import IDCClient
import requests

# Use idc-index for efficient discovery
idc = IDCClient()
results = idc.sql_query("""
    SELECT StudyInstanceUID, SeriesInstanceUID, Modality, SeriesDescription
    FROM index
    WHERE collection_id = 'nlst' AND Modality = 'CT'
    LIMIT 1
""")

study_uid = results.iloc[0]['StudyInstanceUID']
series_uid = results.iloc[0]['SeriesInstanceUID']
print(f"Found: {results.iloc[0]['SeriesDescription']}")

# Use DICOMweb to stream metadata without downloading files
base_url = "https://proxy.imaging.datacommons.cancer.gov/current/viewer-only-no-downloads-see-tinyurl-dot-com-slash-3j3d9jyp/dicomWeb"

response = requests.get(
    f"{base_url}/studies/{study_uid}/series/{series_uid}/metadata",
    headers={"Accept": "application/dicom+json"}
)

if response.status_code == 200:
    metadata = response.json()
    print(f"Retrieved metadata for {len(metadata)} instances without downloading files")
```

## Common DICOM Tags Reference

DICOMweb returns tags as hexadecimal codes. Common tags:

| Tag | Name | Description |
|-----|------|-------------|
| 00080018 | SOPInstanceUID | Unique instance identifier |
| 00080020 | StudyDate | Date study was performed |
| 00080060 | Modality | Imaging modality (CT, MR, PT, etc.) |
| 0008103E | SeriesDescription | Description of series |
| 00100020 | PatientID | Patient identifier |
| 0020000D | StudyInstanceUID | Unique study identifier |
| 0020000E | SeriesInstanceUID | Unique series identifier |
| 00280010 | Rows | Image height in pixels |
| 00280011 | Columns | Image width in pixels |

## Authentication for Google Healthcare API

To use the Google Healthcare endpoint with higher quotas:

```python
from google.auth import default
from google.auth.transport.requests import Request
import requests

# Get credentials (requires gcloud auth)
credentials, project = default()
credentials.refresh(Request())

# Build authenticated request
base_url = "https://healthcare.googleapis.com/v1/projects/nci-idc-data/locations/us-central1/datasets/idc/dicomStores/idc-store-v24/dicomWeb"

response = requests.get(
    f"{base_url}/studies",
    params={"limit": 5},
    headers={
        "Authorization": f"Bearer {credentials.token}",
        "Accept": "application/dicom+json"
    }
)
```

**Prerequisites:**
1. Google Cloud SDK installed (`gcloud`)
2. Authenticated: `gcloud auth application-default login`
3. Account has access to public Google Cloud datasets

## Troubleshooting

### Issue: 400 Bad Request on search queries
- **Cause:** Using unsupported search parameters. The implementation only supports specific DICOM tags for filtering.
- **Solution:** Use UID-based queries (StudyInstanceUID, SeriesInstanceUID). For filtering by Modality or other attributes, use `idc-index` to discover UIDs first, then query DICOMweb with specific UIDs.

### Issue: 403 Forbidden on Google Healthcare endpoint
- **Cause:** Missing authentication or insufficient permissions
- **Solution:** Run `gcloud auth application-default login` and ensure your account has access

### Issue: 429 Too Many Requests
- **Cause:** Rate limit exceeded
- **Solution:** Add delays between requests, reduce `limit` values, or use authenticated endpoint for higher quotas

### Issue: 204 No Content for valid UIDs
- **Cause:** UID may be from an older IDC version not in current data, or data is in buckets not replicated by Google Healthcare
- **Solution:**
  - Verify UID exists using `idc-index` query first
  - Check if data is in `idc-open-data-cr` or `idc-open-data-two` buckets (not available in Google Healthcare endpoint)
  - Switch to IDC public proxy for 100% coverage
  - During new version releases, Google Healthcare may lag 1-2 weeks behind

### Issue: Large metadata responses slow to parse
- **Cause:** Series with many instances returns large JSON
- **Solution:** Use `limit` parameter on instance queries, or query specific instances by SOPInstanceUID

### Issue: Response missing expected attributes
- **Cause:** DICOM sequences larger than ~1 MB are excluded from metadata responses
- **Solution:** Retrieve the full DICOM instance using WADO-RS instance retrieval if you need all attributes

## Resources

**IDC Documentation:**
- [IDC DICOM Stores](https://learn.canceridc.dev/data/organization-of-data/dicom-stores) - Data coverage and bucket details
- [IDC DICOMweb Access](https://learn.canceridc.dev/data/downloading-data/dicomweb-access) - Endpoint usage and differences
- [IDC Proxy Policy](https://learn.canceridc.dev/portal/proxy-policy) - Quota policies and usage restrictions
- [IDC User Guide](https://learn.canceridc.dev/) - Complete documentation

**DICOMweb Standards and Tools:**
- [Google Healthcare DICOM Conformance Statement](https://docs.cloud.google.com/healthcare-api/docs/dicom)
- [DICOMweb Standard](https://www.dicomstandard.org/using/dicomweb)
- [dicomweb-client Python library](https://dicomweb-client.readthedocs.io/)

**Related Guides:**
- `cloud_storage_guide.md` - Direct bucket access, file organization, CRDC UUIDs, and versioning
- `bigquery_guide.md` - Advanced metadata queries with full DICOM attributes

### `references/digital_pathology_guide.md`

# Digital Pathology Guide for IDC

**Tested with:** idc-index 0.12.5 (IDC data version v24)

For general IDC queries and downloads, use `idc-index` (see main SKILL.md). This guide covers slide microscopy (SM) imaging, microscopy bulk simple annotations (ANN), and segmentations (SEG) in the context of digital pathology in IDC.

## Index Tables for Digital Pathology

Five specialized index tables provide curated metadata without needing BigQuery:

| Table | Row Granularity | Description |
|-------|-----------------|-------------|
| `sm_index` | 1 row = 1 SM series | Slide Microscopy series metadata: container/slide ID, tissue type, anatomic structure, diagnosis, lens power, pixel spacing, image dimensions |
| `sm_instance_index` | 1 row = 1 SM instance | Instance-level (SOPInstanceUID) metadata for individual slide images |
| `seg_index` | 1 row = 1 SEG series | DICOM Segmentation metadata: algorithm, segment count, reference to source series. Used for both radiology and pathology — filter by source Modality to find pathology-specific segmentations |
| `ann_index` | 1 row = 1 ANN series | Microscopy Bulk Simple Annotations series metadata; includes `referenced_SeriesInstanceUID` linking to the annotated slide |
| `ann_group_index` | 1 row = 1 annotation group | Annotation group details: `AnnotationGroupLabel`, `GraphicType`, `NumberOfAnnotations`, `AlgorithmName`, property codes |

All require `client.fetch_index("table_name")` before querying. Use `client.indices_overview` to inspect column schemas programmatically.

## Slide Microscopy Queries

### Basic SM metadata

```python
from idc_index import IDCClient
client = IDCClient()

# sm_index has detailed metadata; join with index for collection_id
client.fetch_index("sm_index")
client.sql_query("""
    SELECT i.collection_id, COUNT(*) as slides,
           MIN(s.min_PixelSpacing_2sf) as min_resolution
    FROM sm_index s
    JOIN index i ON s.SeriesInstanceUID = i.SeriesInstanceUID
    GROUP BY i.collection_id
    ORDER BY slides DESC
""")
```

### Find SM series with specific properties

```python
# Find high-resolution slides with specific objective lens power
client.fetch_index("sm_index")
client.sql_query("""
    SELECT
        i.collection_id,
        i.PatientID,
        s.ObjectiveLensPower,
        s.min_PixelSpacing_2sf
    FROM sm_index s
    JOIN index i ON s.SeriesInstanceUID = i.SeriesInstanceUID
    WHERE s.ObjectiveLensPower >= 40
    ORDER BY s.min_PixelSpacing_2sf
    LIMIT 20
""")
```

### Filter by specimen preparation

The `sm_index` includes staining, embedding, and fixative metadata. These columns are **arrays** (e.g., `[hematoxylin stain, water soluble eosin stain]` for H&E) — use `array_to_string()` with `LIKE` or `list_contains()` to filter.

```python
# Find H&E-stained slides in a collection
client.fetch_index("sm_index")
client.sql_query("""
    SELECT
        i.PatientID,
        s.staining_usingSubstance_CodeMeaning as staining,
        s.embeddingMedium_CodeMeaning as embedding,
        s.tissueFixative_CodeMeaning as fixative
    FROM sm_index s
    JOIN index i ON s.SeriesInstanceUID = i.SeriesInstanceUID
    WHERE i.collection_id = 'tcga_brca'
      AND array_to_string(s.staining_usingSubstance_CodeMeaning, ', ') LIKE '%hematoxylin%'
    LIMIT 10
""")
```

```python
# Compare FFPE vs frozen slides across collections
client.sql_query("""
    SELECT
        i.collection_id,
        s.embeddingMedium_CodeMeaning as embedding,
        COUNT(*) as slide_count
    FROM sm_index s
    JOIN index i ON s.SeriesInstanceUID = i.SeriesInstanceUID
    GROUP BY i.collection_id, embedding
    ORDER BY i.collection_id, slide_count DESC
""")
```

## Identifying Tumor vs Normal Slides

The `sm_index` table provides two ways to identify tissue type:

| Column | Use Case |
|--------|----------|
| `primaryAnatomicStructureModifier_CodeMeaning` | Structured tissue type from DICOM specimen metadata (e.g., `Neoplasm, Primary`, `Normal`, `Tumor`, `Neoplasm, Metastatic`). Works across all collections with SM data. |
| `ContainerIdentifier` | Slide/container identifier. For TCGA collections, contains the [TCGA barcode](https://docs.gdc.cancer.gov/Encyclopedia/pages/TCGA_Barcode/) where the [sample type code](https://gdc.cancer.gov/resources-tcga-users/tcga-code-tables/sample-type-codes) (positions 14-15) encodes tissue origin: `01`-`09` = tumor, `10`-`19` = normal. |

### Using structured tissue type metadata

```python
from idc_index import IDCClient
client = IDCClient()
client.fetch_index("sm_index")

# Discover tissue type values across all SM data
client.sql_query("""
    SELECT
        s.primaryAnatomicStructureModifier_CodeMeaning as tissue_type,
        COUNT(*) as slide_count
    FROM sm_index s
    WHERE s.primaryAnatomicStructureModifier_CodeMeaning IS NOT NULL
    GROUP BY tissue_type
    ORDER BY slide_count DESC
""")
```

#### Example: Tumor vs normal slides in TCGA-BRCA

```python
# Tissue type breakdown for TCGA-BRCA
client.sql_query("""
    SELECT
        s.primaryAnatomicStructureModifier_CodeMeaning as tissue_type,
        COUNT(*) as slide_count,
        COUNT(DISTINCT i.PatientID) as patient_count
    FROM sm_index s
    JOIN index i ON s.SeriesInstanceUID = i.SeriesInstanceUID
    WHERE i.collection_id = 'tcga_brca'
    GROUP BY tissue_type
    ORDER BY slide_count DESC
""")
# Returns: Neoplasm, Primary (2704 slides), Normal (399 slides)
```

### Using TCGA barcode (TCGA collections only)

For TCGA collections, `ContainerIdentifier` contains the slide barcode (e.g., `TCGA-E9-A3X8-01A-03-TSC`). Extract the sample type code to classify tissue:

```python
# Parse sample type from TCGA barcode
client.sql_query("""
    SELECT
        SUBSTRING(SPLIT_PART(s.ContainerIdentifier, '-', 4), 1, 2) as sample_type_code,
        s.primaryAnatomicStructureModifier_CodeMeaning as tissue_type,
        COUNT(*) as slide_count
    FROM sm_index s
    JOIN index i ON s.SeriesInstanceUID = i.SeriesInstanceUID
    WHERE i.collection_id = 'tcga_brca'
    GROUP BY sample_type_code, tissue_type
    ORDER BY sample_type_code
""")
# Returns: 01 → Neoplasm, Primary (2704), 06 → None (8), 11 → Normal (399)
```

The barcode approach catches cases where structured metadata is NULL (e.g., `06` = Metastatic slides have `primaryAnatomicStructureModifier_CodeMeaning` = NULL in TCGA-BRCA).

## Annotation Queries (ANN)

DICOM Microscopy Bulk Simple Annotations (Modality = 'ANN') are annotations **on** slide microscopy images. They appear in `ann_index` (series-level) and `ann_group_index` (group-level detail). Each ANN series references the slide it annotates via `referenced_SeriesInstanceUID`.

### Basic annotation discovery

```python
# Find annotation series and their referenced images
client.fetch_index("ann_index")
client.fetch_index("ann_group_index")

client.sql_query("""
    SELECT
        a.SeriesInstanceUID as ann_series,
        a.AnnotationCoordinateType,
        a.referenced_SeriesInstanceUID as source_series
    FROM ann_index a
    LIMIT 10
""")
```

### Annotation group statistics

```python
# Get annotation group details (graphic types, counts, algorithms)
client.sql_query("""
    SELECT
        GraphicType,
        SUM(NumberOfAnnotations) as total_annotations,
        COUNT(*) as group_count
    FROM ann_group_index
    GROUP BY GraphicType
    ORDER BY total_annotations DESC
""")
```

### Find annotations with source slide context

```python
# Find annotations with their source slide microscopy context
client.sql_query("""
    SELECT
        i.collection_id,
        g.GraphicType,
        g.AnnotationPropertyType_CodeMeaning,
        g.AlgorithmName,
        g.NumberOfAnnotations
    FROM ann_group_index g
    JOIN ann_index a ON g.SeriesInstanceUID = a.SeriesInstanceUID
    JOIN index i ON a.referenced_SeriesInstanceUID = i.SeriesInstanceUID
    WHERE g.AlgorithmName IS NOT NULL
    LIMIT 10
""")
```

## Segmentations on Slide Microscopy

DICOM Segmentations (Modality = 'SEG') are used for both radiology (e.g., organ segmentations on CT) and pathology (e.g., tissue region segmentations on whole slide images). Use `seg_index.segmented_SeriesInstanceUID` to find the source series, then filter by source Modality to isolate pathology segmentations.

```python
# Find segmentations whose source is a slide microscopy image
client.fetch_index("seg_index")
client.fetch_index("sm_index")
client.sql_query("""
    SELECT
        seg.SeriesInstanceUID as seg_series,
        seg.AlgorithmName,
        seg.total_segments,
        src.collection_id,
        src.Modality as source_modality
    FROM seg_index seg
    JOIN index src ON seg.segmented_SeriesInstanceUID = src.SeriesInstanceUID
    WHERE src.Modality = 'SM'
    LIMIT 20
""")
```

## Finding Pre-Computed Analysis Results

IDC hosts derived datasets (nuclei segmentations, TIL maps, AI annotations) identified by `analysis_result_id` in the main `index` table. Use `analysis_results_index` to discover what's available for pathology.

```python
from idc_index import IDCClient
client = IDCClient()
client.fetch_index("analysis_results_index")

# Find analysis results that include pathology annotations or segmentations
client.sql_query("""
    SELECT
        ar.analysis_result_id,
        ar.analysis_result_title,
        ar.modalities,
        ar.subjects,
        ar.collections
    FROM analysis_results_index ar
    WHERE ar.modalities LIKE '%ANN%' OR ar.modalities LIKE '%SEG%'
    ORDER BY ar.subjects DESC
""")
```

### Find analysis results for a specific slide

```python
# Find all derived data (annotations, segmentations) for TCGA-BRCA slides
client.fetch_index("ann_index")
client.sql_query("""
    SELECT
        i.analysis_result_id,
        i.PatientID,
        a.referenced_SeriesInstanceUID as source_slide,
        g.AnnotationGroupLabel,
        g.NumberOfAnnotations,
        g.AlgorithmName
    FROM ann_group_index g
    JOIN ann_index a ON g.SeriesInstanceUID = a.SeriesInstanceUID
    JOIN index i ON a.SeriesInstanceUID = i.SeriesInstanceUID
    WHERE i.collection_id = 'tcga_brca'
    LIMIT 10
""")
```

Annotation objects can also contain per-annotation **measurements** (e.g., nucleus area, eccentricity) stored within the DICOM file. These are not in the index tables — extract them after download using [highdicom](https://github.com/ImagingDataCommons/highdicom) (`ann.get_annotation_groups()`, `group.get_measurements()`). See the [microscopy_dicom_ann_intro](https://github.com/ImagingDataCommons/IDC-Tutorials/blob/master/notebooks/pathomics/microscopy_dicom_ann_intro.ipynb) tutorial for a worked example including spatial analysis and cellularity computation.

## Filter by AnnotationGroupLabel

`AnnotationGroupLabel` is the most direct column for finding annotation groups by name or semantic content. Use `LIKE` with wildcards for text search.

### Simple label filtering

```python
# Find annotation groups by label (e.g., groups mentioning "blast")
client.fetch_index("ann_group_index")
client.sql_query("""
    SELECT
        g.SeriesInstanceUID,
        g.AnnotationGroupLabel,
        g.GraphicType,
        g.NumberOfAnnotations,
        g.AlgorithmName
    FROM ann_group_index g
    WHERE LOWER(g.AnnotationGroupLabel) LIKE '%blast%'
    ORDER BY g.NumberOfAnnotations DESC
""")
```

### Label filtering with collection context

```python
# Find annotation groups matching a label within a specific collection
client.fetch_index("ann_index")
client.fetch_index("ann_group_index")
client.sql_query("""
    SELECT
        i.collection_id,
        g.AnnotationGroupLabel,
        g.GraphicType,
        g.NumberOfAnnotations,
        g.AnnotationPropertyType_CodeMeaning
    FROM ann_group_index g
    JOIN ann_index a ON g.SeriesInstanceUID = a.SeriesInstanceUID
    JOIN index i ON a.SeriesInstanceUID = i.SeriesInstanceUID
    WHERE i.collection_id = 'your_collection_id'
      AND LOWER(g.AnnotationGroupLabel) LIKE '%keyword%'
    ORDER BY g.NumberOfAnnotations DESC
""")
```

## Annotations on Slide Microscopy (SM + ANN Cross-Reference)

When looking for annotations related to slide microscopy data, use both SM and ANN tables together. The `ann_index.referenced_SeriesInstanceUID` links each annotation series to its source slide.

```python
# Find slide microscopy images and their annotations in a collection
client.fetch_index("sm_index")
client.fetch_index("ann_index")
client.fetch_index("ann_group_index")
client.sql_query("""
    SELECT
        i.collection_id,
        s.ObjectiveLensPower,
        g.AnnotationGroupLabel,
        g.NumberOfAnnotations,
        g.GraphicType
    FROM ann_group_index g
    JOIN ann_index a ON g.SeriesInstanceUID = a.SeriesInstanceUID
    JOIN sm_index s ON a.referenced_SeriesInstanceUID = s.SeriesInstanceUID
    JOIN index i ON a.SeriesInstanceUID = i.SeriesInstanceUID
    WHERE i.collection_id = 'your_collection_id'
    ORDER BY g.NumberOfAnnotations DESC
""")
```

## Join Patterns

### SM join (slide microscopy details with collection context)

```python
client.fetch_index("sm_index")
result = client.sql_query("""
    SELECT i.collection_id, i.PatientID, s.ObjectiveLensPower, s.min_PixelSpacing_2sf
    FROM index i
    JOIN sm_index s ON i.SeriesInstanceUID = s.SeriesInstanceUID
    LIMIT 10
""")
```

### ANN join (annotation groups with collection context)

```python
client.fetch_index("ann_index")
client.fetch_index("ann_group_index")
result = client.sql_query("""
    SELECT
        i.collection_id,
        g.AnnotationGroupLabel,
        g.GraphicType,
        g.NumberOfAnnotations,
        a.referenced_SeriesInstanceUID as source_series
    FROM ann_group_index g
    JOIN ann_index a ON g.SeriesInstanceUID = a.SeriesInstanceUID
    JOIN index i ON a.SeriesInstanceUID = i.SeriesInstanceUID
    LIMIT 10
""")
```

## Related Tools

The following tools work with DICOM format for digital pathology workflows:

**Python Libraries:**
- [highdicom](https://github.com/ImagingDataCommons/highdicom) - High-level DICOM abstractions for Python. Create and read DICOM Segmentations (SEG), Structured Reports (SR), and parametric maps for pathology and radiology. Developed by IDC.
- [wsidicom](https://github.com/imi-bigpicture/wsidicom) - Python package for reading DICOM WSI datasets. Parses metadata into easy-to-use dataclasses for whole slide image analysis.
- [TIA-Toolbox](https://github.com/TissueImageAnalytics/tiatoolbox) - End-to-end computational pathology library with DICOM support via `DICOMWSIReader`. Provides tile extraction, feature extraction, and pretrained deep learning models.
- [EZ-WSI-DICOMweb](https://github.com/GoogleCloudPlatform/EZ-WSI-DICOMweb) - Extract image patches from DICOM whole slide images via DICOMweb. Designed for AI/ML workflows with cloud DICOM stores.

**Viewers:**
- [Slim](https://github.com/ImagingDataCommons/slim) - Web-based DICOM slide microscopy viewer and annotation tool. Supports brightfield and multiplexed immunofluorescence imaging via DICOMweb. Developed by IDC.
- [QuPath](https://qupath.github.io/) - Cross-platform open source software for whole slide image analysis. Supports DICOM WSI via Bio-Formats and OpenSlide (v0.4.0+).

**Conversion:**
- [dicom_wsi](https://github.com/Steven-N-Hart/dicom_wsi) - Python implementation for converting proprietary WSI formats to DICOM-compliant files.

### `references/index_tables_guide.md`

# Index Tables Guide for IDC

**Tested with:** idc-index 0.12.5 (IDC data version v24)

This guide covers the structure and access patterns for IDC index tables: programmatic schema discovery, DataFrame access, and join column references. For the overview of available tables and their purposes, see the "Index Tables" section in the main SKILL.md.

**Complete index table documentation:** https://idc-index.readthedocs.io/en/latest/indices_reference.html

## When to Use This Guide

Load this guide when you need to:
- Discover table schemas and column types programmatically
- Access index tables as pandas DataFrames (not via SQL)
- Understand key columns and join relationships between tables

For SQL query examples (filter discovery, finding annotations, size estimation), see `references/sql_patterns.md`.

## Prerequisites

Needs `idc-index` installed — run `python scripts/check_version.py`, which reports the installed
version and prints the install command for the interpreter you are running.

## Available Tables

`SKILL.md` carries a compact map of the table families. This is the full inventory with row
granularity and contents. Always call `client.fetch_index("table_name")` before querying any
of them — it is safe and idempotent for all tables, including those loaded automatically at
startup.

| Table | Row Granularity | Description |
|-------|-----------------|-------------|
| `index` | 1 row = 1 DICOM series | Primary metadata for all current IDC data |
| `version_metadata_index` | 1 row = 1 IDC release version | IDC version release timestamps; join on `idc_version` to correlate series with their release date |
| `collections_index` | 1 row = 1 collection | Collection-level metadata and descriptions |
| `analysis_results_index` | 1 row = 1 analysis result collection | Metadata about derived datasets (annotations, segmentations) |
| `clinical_index` | 1 row = 1 (collection, table, column) triple | Dictionary mapping clinical data table columns to collections |
| `sm_index` | 1 row = 1 slide microscopy series | Slide Microscopy (pathology) series metadata |
| `sm_instance_index` | 1 row = 1 slide microscopy instance | Instance-level (SOPInstanceUID) metadata for slide microscopy |
| `seg_index` | 1 row = 1 DICOM Segmentation series | Segmentation metadata: algorithm, segment count, reference to source image series |
| `ann_index` | 1 row = 1 DICOM ANN series | Microscopy Bulk Simple Annotations series metadata; references annotated image series |
| `ann_group_index` | 1 row = 1 annotation group | Detailed annotation group metadata: graphic type, annotation count, property codes, algorithm |
| `contrast_index` | 1 row = 1 series with contrast info | Contrast agent metadata: agent name, ingredient, administration route (CT, MR, PT, XA, RF) |
| `volume_geometry_index` | 1 row = 1 CT/MR/PT series | 3D volume geometry validation for single-frame CT, MR, and PT series; boolean checks for orientation, spacing, dimensions, and slice positions; composite `regularly_spaced_3d_volume` flag |
| `rtstruct_index` | 1 row = 1 RTSTRUCT series | RT Structure Set metadata: total ROI count, ROI names, generation algorithms, interpreted types, and the referenced image series UID |
| `ct_index` | 1 row = 1 CT series | CT acquisition/reconstruction parameters: pixel spacing, slice thickness, kVp, convolution kernel, tube current (min/max for dose-modulated), exposure, spiral pitch, scan options |
| `mr_index` | 1 row = 1 MR series | MR acquisition/sequence parameters: field strength, scanning sequence, TE (array for multi-echo), TR, flip angle, DiffusionBValue (array for DWI), pixel bandwidth, receive coil, number of temporal positions |
| `pt_index` | 1 row = 1 PET series | PET acquisition/reconstruction/radiopharmaceutical parameters: series type, units, decay/scatter/attenuation correction, reconstruction method, radionuclide, injected dose, frame duration (array for dynamic PET) |
| `prior_versions_index` | 1 row = 1 DICOM series | **Reproducibility only.** Contains series permanently removed from IDC (all `max_idc_version` < current version; zero overlap with `index`). Use ONLY when a user explicitly needs to reproduce work from a prior IDC version using data no longer in the current release. Do NOT use for version history or "what's new" questions — those use `series_init_idc_version`/`series_revised_idc_version` in the main `index` table. Column names `min_idc_version`/`max_idc_version` here are NOT equivalent to `series_init_idc_version`/`series_revised_idc_version` in `index`. |

## Accessing Index Tables

### Via SQL (recommended for filtering/aggregation)

```python
from idc_index import IDCClient
client = IDCClient()

# Query the primary index (always available)
results = client.sql_query("SELECT * FROM index WHERE Modality = 'CT' LIMIT 10")

# Fetch and query additional indices
client.fetch_index("collections_index")
collections = client.sql_query("SELECT collection_id, cancer_types, tumor_locations FROM collections_index")

client.fetch_index("analysis_results_index")
analysis = client.sql_query("SELECT * FROM analysis_results_index LIMIT 5")
```

### As pandas DataFrames (direct access)

```python
# Primary index (always available after client initialization)
df = client.index

# Fetch and access on-demand indices
client.fetch_index("sm_index")
sm_df = client.sm_index
```

## Discovering Table Schemas

The `indices_overview` dictionary contains complete schema information for all tables. **Always consult this when writing queries or exploring data structure.**

**DICOM attribute mapping:** Many columns are populated directly from DICOM attributes in the source files. The column description in the schema indicates when a column corresponds to a DICOM attribute (e.g., "DICOM Modality attribute" or references a DICOM tag). This allows leveraging DICOM knowledge when querying — standard DICOM attribute names like `PatientID`, `StudyInstanceUID`, `Modality`, `BodyPartExamined` work as expected.

```python
from idc_index import IDCClient
client = IDCClient()

# List all available indices with descriptions
for name, info in client.indices_overview.items():
    print(f"\n{name}:")
    print(f"  Installed: {info['installed']}")
    print(f"  Description: {info['description']}")

# Get complete schema for a specific index (columns, types, descriptions)
schema = client.indices_overview["index"]["schema"]
print(f"\nTable: {schema['table_description']}")
print("\nColumns:")
for col in schema['columns']:
    desc = col.get('description', 'No description')
    # Description indicates if column is from DICOM attribute
    print(f"  {col['name']} ({col['type']}): {desc}")

# Find columns that are DICOM attributes (check description for "DICOM" reference)
dicom_cols = [c['name'] for c in schema['columns'] if 'DICOM' in c.get('description', '').upper()]
print(f"\nDICOM-sourced columns: {dicom_cols}")
```

**Alternative: use `get_index_schema()` method:**
```python
schema = client.get_index_schema("index")
# Returns same schema dict: {'table_description': ..., 'columns': [...]}
```

### Finding which table contains a column

The most common schema question is "where does `SliceThickness` live?" — the primary `index`
holds series-level metadata only, so modality-specific acquisition parameters are in dedicated
tables. Search the overview rather than guessing; neither call fetches anything:

```python
# Find which table(s) contain a specific column (no fetch required)
target = "SliceThickness"
for table_name, info in client.indices_overview.items():
    if any(c["name"] == target for c in info["schema"]["columns"]):
        print(f"'{target}' is in: {table_name}")
# → 'SliceThickness' is in: ct_index

# List all columns in a table from the schema (no fetch required)
ct_cols = [c["name"] for c in client.indices_overview["ct_index"]["schema"]["columns"]]
print("ct_index columns:", ct_cols)
# → ['SeriesInstanceUID', 'PixelSpacing_row_mm', 'PixelSpacing_col_mm', 'Rows',
#    'Columns', 'SliceThickness', 'KVP', 'ConvolutionKernel', ...]
```

Then `client.fetch_index("ct_index")` and join to `index` on `SeriesInstanceUID`.

## Key Columns Reference

Most common columns in the primary `index` table (use `indices_overview` for complete list and descriptions):

| Column | Type | DICOM | Description |
|--------|------|-------|-------------|
| `collection_id` | STRING | No | IDC collection identifier |
| `analysis_result_id` | STRING | No | If applicable, indicates what analysis results collection given series is part of |
| `source_DOI` | STRING | No | DOI linking to dataset details; use for learning more about the content and for attribution (see citations below) |
| `PatientID` | STRING | Yes | Patient identifier |
| `StudyInstanceUID` | STRING | Yes | DICOM Study UID |
| `SeriesInstanceUID` | STRING | Yes | DICOM Series UID — use for downloads/viewing |
| `Modality` | STRING | Yes | Imaging modality (CT, MR, PT, SM, SEG, ANN, RTSTRUCT, etc.) |
| `BodyPartExamined` | STRING | Yes | Anatomical region |
| `SeriesDescription` | STRING | Yes | Description of the series |
| `Manufacturer` | STRING | Yes | Equipment manufacturer |
| `StudyDate` | STRING | Yes | Date study was performed |
| `PatientSex` | STRING | Yes | Patient sex |
| `PatientAge` | STRING | Yes | Patient age at time of study |
| `license_short_name` | STRING | No | License type (CC BY 4.0, CC BY-NC 4.0, etc.) |
| `series_size_MB` | FLOAT | No | Size of series in megabytes |
| `instanceCount` | INTEGER | No | Number of DICOM instances in series |
| `SOPClassUID` | STRING | Yes | DICOM SOP Class UID (identifies the object/service class, e.g., CT Image Storage) |
| `TransferSyntaxUID` | STRING | Yes | DICOM Transfer Syntax UID (encoding/compression method) |

**DICOM = Yes**: Column value extracted from the DICOM attribute with the same name. Refer to the [DICOM standard](https://dicom.nema.org/medical/dicom/current/output/chtml/part06/chapter_6.html) for numeric tag mappings. Use standard DICOM knowledge for expected values and formats.

## Join Column Reference

Use this table to identify join columns between index tables. Always call `client.fetch_index("table_name")` before using a table in SQL.

| Table A | Table B | Join Condition |
|---------|---------|----------------|
| `index` | `collections_index` | `index.collection_id = collections_index.collection_id` |
| `index` | `sm_index` | `index.SeriesInstanceUID = sm_index.SeriesInstanceUID` |
| `index` | `seg_index` | `index.SeriesInstanceUID = seg_index.segmented_SeriesInstanceUID` |
| `index` | `ann_index` | `index.SeriesInstanceUID = ann_index.SeriesInstanceUID` |
| `ann_index` | `ann_group_index` | `ann_index.SeriesInstanceUID = ann_group_index.SeriesInstanceUID` |
| `index` | `clinical_index` | `index.collection_id = clinical_index.collection_id` (then filter by patient) |
| `index` | `contrast_index` | `index.SeriesInstanceUID = contrast_index.SeriesInstanceUID` |
| `index` | `volume_geometry_index` | `index.SeriesInstanceUID = volume_geometry_index.SeriesInstanceUID` |
| `index` | `rtstruct_index` | `index.SeriesInstanceUID = rtstruct_index.SeriesInstanceUID` |
| `rtstruct_index` | `index` (source images) | `rtstruct_index.referenced_SeriesInstanceUID = index.SeriesInstanceUID` |
| `index` | `ct_index` | `index.SeriesInstanceUID = ct_index.SeriesInstanceUID` |
| `index` | `mr_index` | `index.SeriesInstanceUID = mr_index.SeriesInstanceUID` |
| `index` | `pt_index` | `index.SeriesInstanceUID = pt_index.SeriesInstanceUID` |

For complete query examples using these joins, see `references/sql_patterns.md`.

## Troubleshooting

**Issue:** Column not found in table
- **Cause:** Column name misspelled or doesn't exist in that table
- **Solution:** Use `client.indices_overview["table_name"]["schema"]["columns"]` to list available columns

**Issue:** DataFrame access returns None
- **Cause:** Index not fetched or property name incorrect
- **Solution:** Fetch first with `client.fetch_index()`, then access via property matching the index name

## Resources

- Complete index table documentation: https://idc-index.readthedocs.io/en/latest/indices_reference.html
- `references/sql_patterns.md` for query examples using these tables
- `references/clinical_data_guide.md` for clinical data workflows
- `references/digital_pathology_guide.md` for pathology-specific indices

### `references/licensing_and_citation.md`

# Licensing and Citation Guide for IDC

## When to Use This Guide

Load this guide when:
- A user asks whether IDC data can be used commercially, redistributed, or included in a product
- You are assembling a cohort that mixes collections and need to know which terms govern it
- A user is publishing results and needs formatted citations (APA, BibTeX, CSL JSON, RDF Turtle)
- You need the parameters or output formats for citation generation

The obligation summary — check the license, generate citations — lives in `SKILL.md`. This
guide holds the detail behind it.

**These are the two IDC tasks least tied to any one access path.** Licenses and citations are
available identically from `idc-index`, the REST API, and the hosted MCP server. Use whichever
route the session is already on rather than installing Python to answer a licensing question,
or dropping out of an MCP session to run a script.

| Task | `idc-index` (Python) | REST API | MCP server |
|------|----------------------|----------|------------|
| License breakdown for a selection | `sql_query` on `license_short_name` | `POST /v3/licenses` | `get_licenses` |
| Citations for a selection | `citations_from_selection()` | `POST /v3/citations` | `get_citations` |

Route-specific detail lives in `references/rest_api_guide.md` (endpoint reference, filter
syntax, and the body-shape pitfall that makes a mis-shaped filter return all of IDC) and
`references/mcp_guide.md` (tool inventory). The license semantics below apply to all three.

## Licenses in IDC

Every DICOM file in IDC is tagged with its license in the file metadata, and every row in the
`index` table carries a `license_short_name` column. There is no single IDC-wide license.

| License | Share of data | Commercial use | Attribution required |
|---------|---------------|----------------|----------------------|
| CC BY 4.0 | 74.7% | Yes | Yes |
| CC BY 3.0 | 22.1% | Yes | Yes |
| CC BY-NC 4.0 | 2.1% | **No** | Yes |
| CC BY-NC 3.0 | 0.8% | **No** | Yes |
| NLM Terms and Conditions | 0.3% | Read the terms | Yes |

About 97% of IDC data by size permits commercial reuse; just under 3% is non-commercial. Treat
any `license_short_name` that is not a recognizable Creative Commons string as custom, and
report the exact value to the user rather than assuming it permits reuse.

**Licenses attach to individual series, not to whole collections.** 39 of IDC's 176 collections
carry more than one license — analysis results and original images within one collection can
differ, as can series from different sources. Never conclude that a collection is
commercially usable from one series, or from the collection's headline license: group by
`license_short_name` over the exact selection you intend to use.

**When a cohort mixes licenses, the most restrictive term governs the combined dataset.** If a
selection contains any CC BY-NC series, either drop those series or tell the user the whole
derived dataset is non-commercial.

Commercially restricted data is also physically separated in cloud storage: the
`idc-open-data-cr` (AWS) / `idc-open-cr` (GCS) buckets hold the CC BY-NC collections. See
`references/cloud_storage_guide.md` for bucket details.

## Checking licenses

### Via `idc-index`

```python
from idc_index import IDCClient
client = IDCClient()

# Licenses across all collections
licenses = client.sql_query("""
    SELECT DISTINCT
      collection_id,
      license_short_name,
      COUNT(DISTINCT SeriesInstanceUID) as series_count
    FROM index
    GROUP BY collection_id, license_short_name
    ORDER BY collection_id
""")
print(licenses)
```

```python
# Licenses present in one specific cohort — run this before handing a dataset to a user
cohort_licenses = client.sql_query("""
    SELECT license_short_name, COUNT(DISTINCT SeriesInstanceUID) as series_count
    FROM index
    WHERE Modality = 'MR' AND BodyPartExamined = 'BREAST'
    GROUP BY license_short_name
""")
print(cohort_licenses)
```

```python
# Commercial-safe subset: exclude non-commercial collections outright
commercial_ok = client.sql_query("""
    SELECT collection_id, SeriesInstanceUID
    FROM index
    WHERE Modality = 'CT'
      AND license_short_name NOT LIKE '%NC%'
    LIMIT 20
""")
```

### Via the REST API

`POST /v3/licenses` takes the filter object **directly** (not wrapped in a `filters` key) and
returns the per-license breakdown with series counts and sizes:

```bash
B=https://api.imaging.datacommons.cancer.gov/v3
curl -s $B/licenses \
  -H 'content-type: application/json' \
  -d '{"terms": {"Modality": ["MR"], "BodyPartExamined": ["BREAST"]}}'
```

Response shape: `licenses[{license_short_name, series, size_TB}]`. A collection's licenses are
also included in `GET /v3/collections/{id}`.

### Via the MCP server

Call `get_licenses` with the same selection you built with `build_cohort`. The result carries
the same per-license breakdown; the CC BY vs CC BY-NC distinction above applies unchanged.

## Citations and attribution

The `source_DOI` column links to the publications describing how each dataset was generated.
All three routes turn a selection into formatted citations that satisfy the attribution
requirement common to every IDC license.

Generate citations from the *same* selection you downloaded, not from the collection as a
whole — a five-series subset of a collection that spans several source publications should
cite only the publications it actually draws on.

### Via `idc-index`

```python
# Citations for a collection (APA is the default format)
citations = client.citations_from_selection(collection_id="rider_pilot")
for citation in citations:
    print(citation)
```

```python
# Citations for a specific set of series — matches what you actually downloaded
results = client.sql_query("""
    SELECT SeriesInstanceUID FROM index
    WHERE collection_id = 'tcga_luad' LIMIT 5
""")
citations = client.citations_from_selection(
    seriesInstanceUID=list(results['SeriesInstanceUID'].values)
)
```

```python
# BibTeX, for LaTeX manuscripts
bibtex_citations = client.citations_from_selection(
    collection_id="tcga_luad",
    citation_format=IDCClient.CITATION_FORMAT_BIBTEX
)
```

`citations_from_selection()` takes the same selection filters as the download methods —
`collection_id`, `patientId`, `studyInstanceUID`, `seriesInstanceUID` — plus `citation_format`.

### Via the REST API

`POST /v3/citations` **wraps** the filter in a `filters` key (unlike `/v3/licenses` — this
asymmetry is the single most common REST mistake; see `references/rest_api_guide.md`):

```bash
curl -s $B/citations \
  -H 'content-type: application/json' \
  -d '{"filters": {"terms": {"collection_id": ["rider_pilot"]}}, "citation_format": "bibtex"}'
```

The response separates the per-dataset `citations[]` from `idc_acknowledgment` (the IDC paper)
and `recommendation`. Include both parts — see *What to include when publishing* below.

### Via the MCP server

Call `get_citations` for a selection. It returns the per-dataset citations plus the IDC paper
to acknowledge IDC itself, matching the REST response.

### Citation formats

| `idc-index` constant | REST / MCP `citation_format` | Output |
|----------------------|------------------------------|--------|
| `IDCClient.CITATION_FORMAT_APA` | `apa` (default) | APA string |
| `IDCClient.CITATION_FORMAT_BIBTEX` | `bibtex` | BibTeX entry, for LaTeX |
| `IDCClient.CITATION_FORMAT_JSON` | `csl-json` | CSL JSON |
| `IDCClient.CITATION_FORMAT_TURTLE` | `turtle` | RDF Turtle |

## What to include when publishing

1. **The dataset citations** for every collection or series set used.
2. **The IDC data version** — `client.get_idc_version()`, `GET /v3/version`, or the MCP
   `get_idc_version` tool. IDC releases are versioned and series are added and revised between
   them, so the version is what makes the selection reproducible.
3. **The IDC platform citation**, to acknowledge IDC itself. The REST and MCP routes return
   this as `idc_acknowledgment`; when using `idc-index`, add it yourself:

   > Fedorov, A., et al. "National Cancer Institute Imaging Data Commons: Toward Transparency,
   > Reproducibility, and Scalability in Imaging Artificial Intelligence." *RadioGraphics* 43.12
   > (2023). https://doi.org/10.1148/rg.230180

4. **The series manifest** — save the `SeriesInstanceUID` list alongside the analysis so the
   exact cohort can be rebuilt.

## Troubleshooting

### Issue: Fewer citations returned than collections selected

- **Cause:** Citations are derived from `source_DOI`, and several collections can share one
  DOI, so a multi-collection selection may legitimately produce a shorter list.
- **Solution:** Query `SELECT DISTINCT collection_id, source_DOI FROM index WHERE ...` to see
  the mapping directly.

### Issue: `POST /v3/citations` returns citations for all of IDC

- **Cause:** The filter was passed directly instead of wrapped in `filters`. `/v3/licenses`
  takes the filter directly; `/v3/citations` wraps it. A mis-shaped body is not an error — it
  is treated as an empty filter.
- **Solution:** Check the response counts against a `POST /v3/cohort/counts` for the same
  selection. See `references/rest_api_guide.md`.

## Resources

- **IDC Portal** — https://portal.imaging.datacommons.cancer.gov/
- **IDC data licensing documentation** — https://learn.canceridc.dev/data/licensing
- **`references/rest_api_guide.md`** — `/v3/licenses` and `/v3/citations` endpoint reference
- **`references/mcp_guide.md`** — `get_licenses` and `get_citations` tool inventory
- **`references/cloud_storage_guide.md`** — bucket separation for commercially restricted data

### `references/mcp_guide.md`

# IDC MCP Server Guide

IDC operates a hosted [Model Context Protocol](https://modelcontextprotocol.io/) server that
exposes IDC discovery and metadata as agent tools. This guide covers how to recognize it, how
to divide work between it and `idc-index`, and what to hand off across that boundary.

The server is optional. Everything in `SKILL.md` works without it.

## Endpoint

| Property | Value |
|----------|-------|
| URL | `https://api.imaging.datacommons.cancer.gov/mcp` |
| Transport | Streamable HTTP (`streamable-http`, sometimes spelled `http`) |
| Authentication | None |
| Server identity | `IDC (Imaging Data Commons)` |

## Identifying the server

Tool names and resource URIs are defined by the server, so they are the same on every host.
Use them, not host-specific naming conventions, to decide whether the server is present.

**Strongest signal — resource URIs.** The server publishes two resources under an `idc://`
scheme:

| URI | Content |
|-----|---------|
| `idc://guide` | Data model and recommended workflow (Markdown) |
| `idc://tables` | Tables available to `run_sql`, with descriptions and column counts (JSON) |

If the host can enumerate MCP resources, a resource with URI `idc://guide` identifies the
server unambiguously.

**Fallback — tool-name fingerprint.** Require three or more of `build_cohort`,
`get_cohort_urls`, `list_analysis_results`, and `get_idc_version`. Do not treat `run_sql`,
`get_stats`, `list_tables`, or `get_citations` as evidence on their own; those names are
generic enough that another server could expose them.

**This is disambiguation, not authentication.** No runtime check can prove the server on the
other end is operated by NCI — a hostile server could serve `idc://guide` and name its tools
anything. The trust anchor is the URL the user configured plus TLS, which is established when
the server is added, not when the skill runs. That is sufficient for routing: the check only
has to distinguish IDC from the user's other installed servers.

**Fail soft.** If identification is ambiguous, or a tool call fails, fall back rather than
reporting an error — to the REST API (`rest_api_guide.md`) for read-only metadata, which is the
same service with no configuration, or to `idc-index` when it is already installed or the task
needs downloads or local analysis. Tool names may change as the server matures.

## Tool inventory

Verified against server version `3.0.0b3`. Treat this as a snapshot, not a contract — call
the server's own listing rather than assuming this list is current.

| Group | Tools |
|-------|-------|
| Version and scale | `get_idc_version`, `get_stats` |
| Collections | `list_collections`, `get_collection`, `list_analysis_results` |
| Attribute grounding | `list_attributes`, `get_attribute_values` |
| Cohorts | `build_cohort`, `get_cohort_urls` |
| SQL | `list_tables`, `get_table_schema`, `run_sql` |
| Clinical data | `list_clinical_tables`, `get_clinical_table_schema`, `get_clinical_table` |
| Attribution | `get_citations`, `get_licenses` |
| Visualization | `get_viewer_url` |

The server ships its own usage instructions, which most hosts inject automatically. Follow
those instructions for tool sequencing (ground with `list_attributes` /
`get_attribute_values` before filtering; check `list_tables` before writing SQL). Do not
re-derive that workflow from `SKILL.md` — the two would drift apart on the server's next
release.

**Cohort results report their own filters.** `build_cohort` and `get_cohort_urls` require at
least one filter predicate and fail cleanly without one, rather than returning the whole archive;
results echo the filters actually applied along with warnings for any predicate that was dropped
or any value whose casing did not match. Read those warnings before reporting a count — a zero
with no warning means the filter matched nothing, which is a real answer. Same contract as the
REST endpoints they wrap; see `rest_api_guide.md`.

## Division of labor

The server and `idc-index` overlap on metadata queries and diverge everywhere else.

| Task | Use |
|------|-----|
| IDC data version, collection and series counts | Server (`get_idc_version`, `get_stats`) |
| Valid filter values before building a query | Server (`get_attribute_values`) |
| Cohort selection by attribute filters | Server (`build_cohort`) |
| One-off metadata SQL, answer consumed as prose | Server (`run_sql`) |
| Metadata SQL whose result feeds local Python | `idc-index` (`client.sql_query`) |
| Downloading DICOM files | `idc-index` (`client.download_from_selection`) |
| pandas / notebook analysis, plotting | `idc-index` |
| Reading pixel data (pydicom, SimpleITK) | `idc-index` + local files |
| DICOMweb, BigQuery, direct S3/GCS, Parquet | `idc-index` and the relevant reference guide |
| Digital pathology tiling and annotation workflows | `idc-index` + `digital_pathology_guide.md` |
| Reproducible scripts a user will re-run | `idc-index` (a script outlives the session) |

Two rules resolve the overlap:

- **Prefer the server for discovery.** It is hosted against a current IDC release, so it does
  not depend on the `idc-index` version pinned in `SKILL.md`.
- **Prefer `idc-index` when the result must become a Python object.** Round-tripping a
  DataFrame through tool output wastes context and loses types.

## Handing off from the server to `idc-index`

The boundary artifact is a list of `SeriesInstanceUID` values.

```python
# UIDs obtained from the MCP server's build_cohort / run_sql output
series_uids = [
    "1.3.6.1.4.1.14519.5.2.1.7009.2403.334240657131972136850343327463",
    # ...
]

from idc_index import IDCClient
client = IDCClient()

# Confirm size before downloading — the server reports size_TB, but re-check locally
sizes = client.sql_query(f"""
    SELECT COUNT(*) AS series, SUM(series_size_MB)/1000 AS size_GB
    FROM index
    WHERE SeriesInstanceUID IN ({','.join(f"'{u}'" for u in series_uids)})
""")
print(sizes)

client.download_from_selection(
    downloadDir="./data",
    seriesInstanceUID=series_uids,       # a list, not a DataFrame
    dirTemplate="%collection_id/%PatientID/%Modality",
)
```

Run `python scripts/check_version.py` before the first `idc-index` call in a session, even if
discovery happened server-side — the two components version independently.

`get_cohort_urls` also returns ready-made `idc` CLI commands. Those are the better handoff
when the user wants a shell command they can re-run outside the session; see
`references/cli_guide.md`.

Going the other direction, `idc-index` results are already local, so there is rarely a reason
to send them back to the server.

## Version authority

When the server is present, it is the authority on the IDC data version: call
`get_idc_version` rather than quoting the `idc-data-version` value in the `SKILL.md`
frontmatter, which records the release the skill was last verified against.

If the server and a locally installed `idc-index` report different versions, say so and name
both. The mismatch is real — the hosted server tracks IDC releases independently of the user's
installed package — and it changes which answers about "what's new" are correct.

## Host-specific notes

Everything above is portable. The items below are not, and apply only to specific agent
environments.

### Claude Code

- **Tool naming.** MCP tools are exposed as `mcp__<server>__<tool>`, where `<server>` is the
  configured server name with every character outside `A-Za-z0-9_-` replaced by `_`. A CLI
  install named `idc` yields `mcp__idc__build_cohort`; a claude.ai connector named
  `IDC MCP prod` yields `mcp__claude_ai_IDC_MCP_prod__build_cohort`.
- **Enumerating resources.** `ListMcpResourcesTool` returns each resource with a `server`
  field, which is how to find the `idc://guide` resource and the owning server name in one
  call.
- **Adding the server.**
  `claude mcp add --transport http idc https://api.imaging.datacommons.cancer.gov/mcp`
- **Permission rules.** Allow rules need a literal, glob-free server segment: `mcp__idc__*`
  works, `mcp__*` does not. Connector installs need their own
  `mcp__claude_ai_<name>__*` rule, so the rule differs by install path.
- **Detecting via the CLI does not work.** `claude mcp list` reads only file-based
  configuration (`~/.claude.json`, `.mcp.json`). It reports "No MCP servers configured" for a
  claude.ai connector that is connected and working in the same session, so it cannot be used
  as a presence check.

### Other hosts

Any agent that supports MCP over streamable HTTP can use the server. Consult that agent's
documentation for how servers are registered and how tool names are namespaced; the endpoint
URL and the absence of authentication are all the configuration it needs.

### `references/parquet_access_guide.md`

# Direct Parquet Access Guide for IDC

**Tested with:** idc-index-data 24.2.2 (IDC data version v24), DuckDB 1.5

All idc-index metadata tables are published as Parquet files to a public GCS bucket with unrestricted CORS access. This enables metadata queries with DuckDB or pandas without installing idc-index.

**Limitation:** download helpers (`download_from_selection()`), viewer URLs (`get_viewer_URL()`), and citation generation require the idc-index client and are not available from raw Parquet files.

**This is not the first no-install option to reach for.** It still needs DuckDB installed, and the per-collection clinical tables are not published here — only the `clinical_index` dictionary. For ad-hoc metadata with nothing installed, the REST API (`rest_api_guide.md`) needs no install at all and reaches `clinical.<table>` through `POST /sql`.

## When to Use This Guide

Load this guide when you need to:
- Pin queries to a specific IDC data version (see *Pinning to a Specific Version* below) rather than whatever the hosted API currently serves
- Return more rows than the REST `/sql` ceiling of 10 000
- Run heavy or repeated local DuckDB analysis without driving the hosted API
- Query IDC metadata where DuckDB is available but idc-index is not

For downloads, viewer URLs, and citations, use idc-index as documented in the main SKILL.md.

## URL Pattern

```
https://storage.googleapis.com/idc-index-data-artifacts/current/release_artifacts/{filename}.parquet
```

`current/` always resolves to the latest data release. To pin to a specific version, replace `current` with the data version number (e.g., `23.10.1`).

## Available Files

| File | Approximate Size | Description |
|------|-----------------|-------------|
| `idc_index.parquet` | ~70 MB | Primary index (all DICOM series metadata) |
| `volume_geometry_index.parquet` | ~5 MB | 3D geometry validation for CT/MR/PT series |
| `rtstruct_index.parquet` | ~2 MB | RT Structure Set ROI metadata |
| `seg_index.parquet` | ~6 MB | DICOM Segmentation cross-references |
| `sm_index.parquet` | ~2 MB | Slide microscopy series metadata |
| `contrast_index.parquet` | ~1 MB | Contrast agent metadata |
| `ann_index.parquet` | ~0.2 MB | Microscopy annotation series metadata |
| `ann_group_index.parquet` | ~0.5 MB | Annotation group metadata |
| `collections_index.parquet` | — | Collection-level metadata |
| `analysis_results_index.parquet` | — | Derived dataset metadata |
| `clinical_index.parquet` | ~0.2 MB | Clinical data column dictionary |
| `ct_index.parquet` | — | CT acquisition/reconstruction parameters |
| `mr_index.parquet` | — | MR sequence/acquisition parameters |
| `pt_index.parquet` | — | PET acquisition/radiopharmaceutical parameters |
| `prior_versions_index.parquet` | — | Series from previous IDC releases |

**Note:** the main index file is named `idc_index.parquet`, not `index.parquet`. Reference it with an alias in SQL queries (e.g., `FROM read_parquet(...) AS index`).

## Prerequisites

Install the Python `duckdb` package, using whatever installer manages the environment you are
running in.

DuckDB reads Parquet directly from HTTPS URLs using HTTP range requests — no GCS client library or authentication required.

## Basic Queries

```python
import duckdb

BASE = "https://storage.googleapis.com/idc-index-data-artifacts/current/release_artifacts"

# Discover modalities and series counts
duckdb.sql(f"""
    SELECT Modality, COUNT(*) as series_count, ROUND(SUM(series_size_MB)/1000, 1) as size_GB
    FROM read_parquet('{BASE}/idc_index.parquet')
    GROUP BY Modality
    ORDER BY series_count DESC
""").df()

# Collections with CT data, ordered by size
duckdb.sql(f"""
    SELECT collection_id,
           COUNT(DISTINCT PatientID) as patients,
           COUNT(*) as series,
           ROUND(SUM(series_size_MB)/1000, 1) as size_GB
    FROM read_parquet('{BASE}/idc_index.parquet')
    WHERE Modality = 'CT'
    GROUP BY collection_id
    ORDER BY size_GB DESC
    LIMIT 10
""").df()
```

## Volume Geometry Validation

`volume_geometry_index` covers single-frame CT, MR, and PT series. Each row has boolean checks for orientation, spacing, dimensions, and slice positions, plus a composite `regularly_spaced_3d_volume` flag.

```python
import duckdb

BASE = "https://storage.googleapis.com/idc-index-data-artifacts/current/release_artifacts"

# CT series that form a valid 3D volume (can be loaded without resampling)
duckdb.sql(f"""
    SELECT i.collection_id, i.SeriesInstanceUID, i.BodyPartExamined,
           v.obliquity_degrees, v.regularly_spaced_3d_volume
    FROM read_parquet('{BASE}/idc_index.parquet') i
    JOIN read_parquet('{BASE}/volume_geometry_index.parquet') v
        ON i.SeriesInstanceUID = v.SeriesInstanceUID
    WHERE i.Modality = 'CT'
      AND v.regularly_spaced_3d_volume = TRUE
    LIMIT 10
""").df()

# Fraction of 3D-valid series per collection and modality
duckdb.sql(f"""
    SELECT i.collection_id, i.Modality,
           COUNT(*) as total,
           SUM(CASE WHEN v.regularly_spaced_3d_volume THEN 1 ELSE 0 END) as valid_3d,
           ROUND(100.0 * SUM(CASE WHEN v.regularly_spaced_3d_volume THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_valid
    FROM read_parquet('{BASE}/idc_index.parquet') i
    JOIN read_parquet('{BASE}/volume_geometry_index.parquet') v
        ON i.SeriesInstanceUID = v.SeriesInstanceUID
    WHERE i.Modality IN ('CT', 'MR', 'PT')
    GROUP BY i.collection_id, i.Modality
    ORDER BY total DESC
    LIMIT 10
""").df()
```

Key columns in `volume_geometry_index`:

| Column | Type | Description |
|--------|------|-------------|
| `SeriesInstanceUID` | STRING | Join key |
| `single_orientation` | BOOLEAN | All instances share the same ImageOrientationPatient |
| `orthogonal_orientation` | BOOLEAN | Orientation direction cosines are orthogonal |
| `unique_slice_positions` | BOOLEAN | No duplicate or overlapping slices |
| `consistent_pixel_spacing` | BOOLEAN | All instances share the same PixelSpacing |
| `consistent_image_dimensions` | BOOLEAN | All instances share the same Rows and Columns |
| `uniform_slice_spacing` | BOOLEAN | Spacing between consecutive slices is constant |
| `obliquity_degrees` | FLOAT | Angle between slice normal and nearest cardinal axis (0 = pure axial/sagittal/coronal) |
| `regularly_spaced_3d_volume` | BOOLEAN | Composite: TRUE if all checks pass |

## RT Structure Sets

`rtstruct_index` has one row per RTSTRUCT series with aggregated ROI metadata.

```python
import duckdb

BASE = "https://storage.googleapis.com/idc-index-data-artifacts/current/release_artifacts"

# RTSTRUCT series with ROI details
duckdb.sql(f"""
    SELECT i.collection_id, i.SeriesInstanceUID,
           r.total_rois, r.ROINames, r.RTROIInterpretedTypes,
           r.referenced_SeriesInstanceUID
    FROM read_parquet('{BASE}/idc_index.parquet') i
    JOIN read_parquet('{BASE}/rtstruct_index.parquet') r
        ON i.SeriesInstanceUID = r.SeriesInstanceUID
    WHERE i.Modality = 'RTSTRUCT'
    LIMIT 5
""").df()

# Collections with the most RTSTRUCT series
duckdb.sql(f"""
    SELECT i.collection_id,
           COUNT(*) as rtstruct_series,
           ROUND(AVG(r.total_rois), 1) as avg_rois_per_struct
    FROM read_parquet('{BASE}/idc_index.parquet') i
    JOIN read_parquet('{BASE}/rtstruct_index.parquet') r
        ON i.SeriesInstanceUID = r.SeriesInstanceUID
    GROUP BY i.collection_id
    ORDER BY rtstruct_series DESC
    LIMIT 10
""").df()
```

Key columns in `rtstruct_index`:

| Column | Type | Description |
|--------|------|-------------|
| `SeriesInstanceUID` | STRING | Join key (the RTSTRUCT series) |
| `total_rois` | INTEGER | Number of ROIs in the structure set |
| `ROINames` | STRING (array) | Distinct ROI names (e.g., `["GTV", "Heart", "PTV"]`) |
| `ROIGenerationAlgorithms` | STRING (array) | Distinct generation algorithms (e.g., `["AUTOMATIC", "MANUAL"]`) |
| `RTROIInterpretedTypes` | STRING (array) | Distinct ROI types (e.g., `["GTV", "ORGAN", "PTV"]`) |
| `referenced_SeriesInstanceUID` | STRING | SeriesInstanceUID of the referenced source image series |

## Pinning to a Specific Version

```python
import duckdb

# Use a specific data release instead of 'current'
VERSION = "23.10.1"
BASE = f"https://storage.googleapis.com/idc-index-data-artifacts/{VERSION}/release_artifacts"

duckdb.sql(f"SELECT COUNT(*) FROM read_parquet('{BASE}/idc_index.parquet')").df()
```

## Resources

- idc-index-data releases: https://github.com/ImagingDataCommons/idc-index-data/releases
- idc-index documentation: https://idc-index.readthedocs.io/
- IDC Portal: https://portal.imaging.datacommons.cancer.gov/

### `references/rest_api_guide.md`

# IDC REST API Guide

**Tested with:** API `3.0.0b3` (build `0640860`), IDC data version v24, `idc_index_data_version` 24.2.2

IDC operates a hosted REST API that exposes discovery, cohort building, metadata SQL, and
download manifests over plain HTTP. No authentication, account, or credentials are required —
every example on this page can be run from any terminal with `curl`.

The API and the [MCP server](mcp_guide.md) are the same service behind two transports: the MCP
tools wrap these endpoints. Both are hosted against a current IDC release, independently of the
`idc-index` version installed locally.

## When to Use This Guide

Load this guide when you need to:
- Query IDC from a language or environment with no `idc-index` install (shell, R, Java, JS, a
  notebook without pip access)
- Build cohorts and manifests over HTTP for a pipeline or web application
- Run metadata SQL against a current IDC release without downloading local index files
- Hand a user copy-pasteable `curl` commands they can run anywhere

For downloads, pandas/notebook analysis, reading pixel data, DICOMweb, BigQuery, or digital
pathology tiling, use `idc-index` as documented in `SKILL.md`. The API never moves image bytes:
it returns public `s3://` URLs and manifests, and the transfer happens directly from cloud
storage to the client.

**Choosing among the three interfaces:**

| Situation | Use |
|-----------|-----|
| Session already has the hosted MCP server | MCP tools (`mcp_guide.md`) — same data, no HTTP plumbing |
| `idc-index` already installed, results feed pandas / downloads | `idc-index` (`SKILL.md`) |
| `idc-index` **not** installed and the task is read-only metadata | This REST API — do not install to answer a metadata question |
| No Python, or a non-Python client, or shell commands the user re-runs | This REST API |
| Installed `idc-index` is a whole IDC data release behind and cannot be upgraded here | REST API for the query, **direct bucket transfer** may be needed for the download — `idc-index` cannot fetch what its index does not list |

Being hosted, the API always serves a current IDC release — but so does an up-to-date
`idc-index`. "I want the newest data" is not on its own a reason to prefer the API: the normal
fix for a stale local index is to upgrade it. Reach for the API on version grounds only when
upgrading is not an option in that environment. Avoiding the install *is* a reason, though: the
packaged index data is ~77 MB before pandas, pyarrow, and duckdb, which a metadata question does
not need.

## Endpoint and Versioning

| Property | Value |
|----------|-------|
| Base URL | `https://api.imaging.datacommons.cancer.gov/v3` |
| Authentication | None |
| Content type | `application/json` (request and response), except `cohort/manifest.txt` → `text/plain` |
| Interactive docs | https://api.imaging.datacommons.cancer.gov/v3/docs (Swagger UI) |
| OpenAPI spec | https://api.imaging.datacommons.cancer.gov/v3/openapi.json |
| Source | https://github.com/ImagingDataCommons/IDC-REST-MCP |

**v3 is in beta.** The contract may still change before the final `3.0.0` release, so verify the
running build rather than assuming the values in this guide:

```bash
curl -s https://api.imaging.datacommons.cancer.gov/v3/version
# {"idc_version":"v24","idc_index_data_version":"24.2.2","api_version":"3.0.0b3","build":"0640860"}
```

`idc_version` is the IDC data release the API serves and is the authority when the API is in
use — prefer it over the `idc-data-version` pinned in the `SKILL.md` frontmatter, which records
the release the skill was last verified against.

### Checking the API against a local idc-index

The API and `idc-index` are built on the same `idc-index-data` package, and both report its
version, so consistency is an exact check rather than a guess:

| Side | Data release (coarse) | `idc-index-data` version (exact) |
|------|-----------------------|----------------------------------|
| API | `GET /v3/version` → `idc_version` | `GET /v3/version` → `idc_index_data_version` |
| Local | `IDCClient().get_idc_version()` | `idc_index_data.__version__` |

```python
import idc_index_data
import requests

api = requests.get("https://api.imaging.datacommons.cancer.gov/v3/version", timeout=30).json()
api_version, local_version = api["idc_index_data_version"], idc_index_data.__version__

if api_version.split(".")[0] != local_version.split(".")[0]:
    print(f"Different IDC data release: API {api_version}, local {local_version} — upgrade")
elif api_version != local_version:
    print(f"Same data release, different index build: API {api_version}, local {local_version}")
    # → Same data release, different index build: API 24.2.2, local 24.2.0
```

**The major is the IDC data release; the rest is the index build.** `idc-index-data` `24.x.y`
serves IDC `v24` — 24.0.0 shipped with the v24 release, and 24.1.0 / 24.2.x are later builds of
the *same* release. What differs between them is the index itself (added tables and columns,
corrected metadata), never which series IDC contains.

So read a mismatch by its position:

| Difference | Means | Consequence |
|------------|-------|-------------|
| Major (24.x.y vs 25.x.y) | Different IDC data release | Series added, revised, or removed. Counts legitimately differ, and `idc-index` **cannot download** what its index does not list |
| Minor or patch (24.2.0 vs 24.2.2) | Same data release, different index build | Same series everywhere; downloads are unaffected. A metadata query can still differ if it touches a column that was added or corrected |

Comparing `idc_version` alone cannot make this distinction in the other direction either — the
`vNN` label is exactly the major, so matching `v24` on both sides tells you the release agrees
but says nothing about the index build.

When the two disagree, say so and name both versions, then reconcile rather than mixing
results: upgrading `idc-index` brings the local side to the newer `idc-index-data`, and
`python scripts/check_version.py` reports whether an upgrade is available and prints the
command for the interpreter you are running. Do not present API-derived and locally-derived counts side by side as if they came
from one index.

**A major behind also breaks downloads.** `idc-index` resolves every `s3://` URL it is given
against its *own* index, so a manifest built from a newer IDC data release can name series it
has never heard of — see *When the local index is a data release behind the API* under
**Getting the Data**.

### Use v3 only — V1 and V2 are being retired

**Do not write new code against the V1 or V2 IDC APIs, and do not follow V1/V2 examples found
in older tutorials, notebooks, blog posts, or forum answers.** Both are superseded by v3 and
are scheduled to be deprecated and shut down; code written against them will stop working. If
a user brings V1 or V2 code, say so and port it to v3 rather than extending it.

Two signals that a snippet is V1/V2 rather than v3, both of which will fail against `/v3`:

- a base URL other than `https://api.imaging.datacommons.cancer.gov/v3` (for example a
  `/v1/` or `/v2/` path segment)
- per-attribute filter suffixes such as `Modality_btw` or `_lt` / `_gt`, instead of v3's
  separate `terms` and `ranges` objects

V1/V2 documentation survives only in the [IDC docs archive](https://learn.canceridc.dev/archive/archive)
for historical reference. Treat it as read-only history, not as a source of working examples.

## The Query Surfaces

The endpoints group into five surfaces that build on each other:

| Surface | Answers | Endpoints |
|---------|---------|-----------|
| Discovery | What exists? What can I filter on? | `GET /version`, `/stats`, `/collections`, `/collections/{id}`, `/analysis_results`, `/attributes`, `/attributes/{attr}/values` |
| Cohort | How big is my selection, and what's in it? | `POST /cohort/counts`, `POST /cohort/manifest` |
| Retrieval | Give me the download links | `POST /cohort/manifest.txt` |
| SQL | Anything relational or aggregate | `GET /tables`, `GET /tables/{table}`, `POST /sql` |
| Side tools | View / cite / license-check a cohort | `GET /viewer-url`, `POST /citations`, `POST /licenses` |

Discovery supplies the vocabulary (attribute names and their valid values) that the cohort
filters consume. SQL is the escape hatch for questions structured filters cannot express.

Clinical data has its own discovery endpoints (`GET /clinical/tables`,
`/clinical/tables/{table}`, `/clinical/tables/{table}/rows`) and is filtered or joined through
SQL against the `clinical` schema.

## Endpoint Reference

All paths are relative to `https://api.imaging.datacommons.cancer.gov/v3`.

| Method & path | Purpose | Key response fields |
|---------------|---------|---------------------|
| `GET /version` | IDC data release + API build | `idc_version`, `idc_index_data_version`, `api_version`, `build` |
| `GET /stats` | Headline totals | `collections`, `patients`, `studies`, `series`, `instances`, `size_TB` |
| `GET /collections` | List collections (JSON array) | `collection_id`, `collection_name`, `cancer_types`, `tumor_locations`, `species`, `subjects`, `description` |
| `GET /collections/{id}` | Collection detail | the above plus `patients`, `studies`, `series`, `instances`, `size_TB`, `modalities[]`, `licenses[]` |
| `GET /analysis_results` | Derived datasets (JSON array) | `analysis_result_id`, `analysis_result_title`, `source_DOI`, `subjects`, `collections`, `modalities`, `license_short_name` |
| `GET /attributes` | Filterable attributes | `name`, `table`, `data_type`, `kind` (`term` \| `range`), `categorical`, `description` |
| `GET /attributes/{attr}/values?limit=` | Distinct values with counts | `attribute`, `values[{value,count}]`, `truncated`, `note` |
| `GET /tables` | Tables available to SQL | `tables[{name,description,column_count}]` |
| `GET /tables/{table}` | Column schema | `name`, `description`, `columns[{name,type,description}]` |
| `GET /clinical/tables?collection_id=` | Clinical tables, optionally one collection | `tables[{table_name,sql_path,collection_id,column_count}]` |
| `GET /clinical/tables/{table}` | Clinical columns + labels | `name`, `columns[{name,type,description}]` |
| `GET /clinical/tables/{table}/rows?max_rows=` | Clinical rows (capped) | `columns`, `rows`, `row_count`, `truncated`, `max_rows` |
| `POST /cohort/counts` | Distinct counts for a filter (cheap) | `patients`, `studies`, `series`, `instances`, `size_TB` |
| `POST /cohort/manifest` | Counts + page of series + download payload | `counts`, `page`, `page_size`, `returned`, `total_series`, `series[]`, `download` |
| `POST /cohort/manifest.txt` | Full manifest as `text/plain` | one `s3://…/*` URL per line |
| `POST /sql` | Guarded read-only SQL (DuckDB) | `columns`, `rows`, `row_count`, `truncated`, `max_rows` |
| `GET /viewer-url` | OHIF / Slim viewer link | `viewer_url`, `viewer`, `study_instance_uid`, `series_instance_uid` |
| `POST /citations` | Citations for a cohort | `format`, `citations[]`, `idc_acknowledgment`, `recommendation` |
| `POST /licenses` | License breakdown for a cohort | `licenses[{license_short_name,series,size_TB}]` |

`GET /health` and `GET /v3` (API root) also exist for liveness checks.

## Filter Syntax

Cohort filters are shared by `cohort/counts`, `cohort/manifest`, `cohort/manifest.txt`,
`licenses`, and `citations`. **The filter object always goes under a `filters` key**, on every one
of them. It has two parts:

- **`terms`** — `{attribute: [values]}` for equality/membership. Values are **OR**'d within an
  attribute and **AND**'d across attributes.
- **`ranges`** — `{attribute: {"gte": x, "lte": y}}` for numeric and date attributes. Either
  bound may be omitted for an open-ended range.

```json
{
  "filters": {
    "terms": {"Modality": ["CT"], "collection_id": ["nlst"]},
    "ranges": {"instanceCount": {"gte": 100, "lte": 200}}
  }
}
```

Filters operate only on the `index` table's filterable attributes — 19 of them as of `3.0.0b3`:

| Kind | Attributes |
|------|------------|
| `term` | `collection_id`, `analysis_result_id`, `PatientID`, `StudyInstanceUID`, `SeriesInstanceUID`, `Modality`, `BodyPartExamined`, `Manufacturer`, `ManufacturerModelName`, `PatientSex`, `sop_class_name`, `license_short_name`, `source_DOI` |
| `range` | `instanceCount`, `series_size_MB`, `series_init_idc_version`, `series_revised_idc_version`, `StudyDate`, `SeriesDate` |

`SeriesInstanceUID`, `StudyInstanceUID`, and `PatientID` being filterable is what makes the
side tools work at any granularity — the licenses or citations for a single series are just a
one-value filter.

Anything outside this list — clinical values, segmented anatomy, per-modality acquisition
parameters — is not filterable here; use the SQL surface instead.

**Ground values before filtering.** Call `GET /attributes` for what is filterable and whether
it is a term or a range, then `GET /attributes/{attr}/values` for real values and their casing —
values are matched case-sensitively.

### The server reports what it filtered on

Every filtered response echoes `filters_applied` and `warnings`, and misuse is refused rather
than ignored. Together these make a result self-describing, so you do not have to sanity-check a
count against a number you happen to remember.

| Mistake | Response |
|---------|----------|
| Bare filter object, no `filters` key | `422` naming the correct shape |
| Unrecognized key at any depth (`term` for `terms`, a range bound spelled `min`) | `422` pointing at the key |
| Unknown filter attribute, or a range attribute used as a term | `400` naming the discovery call |
| Unfiltered `cohort/manifest` or `manifest.txt` | `400` — it will not enumerate the whole archive |
| Unfiltered `cohort/counts` or `licenses` | `200` plus an explicit "ENTIRE IDC archive" warning |
| A predicate that constrains nothing (`{"collection_id": []}`, `{"instanceCount": {}}`) | `200`, and `warnings` names the ignored predicate |
| Miscased value (`mr` for `MR`) | `200`, zero counts, and a warning naming the casing that exists |

```bash
curl -s $B/cohort/counts -H 'content-type: application/json' \
  -d '{"filters": {"terms": {"collection_id": ["rider_pilot"]}}}'
# {"patients":8,"studies":154,"series":774,"instances":21111,"size_TB":0.011,
#  "filters_applied":{"terms":{"collection_id":["rider_pilot"]},"ranges":{}},"warnings":[]}
```

**Read `warnings` before reporting any count.** A zero count with `warnings: []` means the filter
applied and matched nothing — that is a real answer. A zero count *with* a casing warning means
the filter was wrong. And `filters_applied` covers the case no shape check can: a request
carrying one good predicate plus one that constrains nothing returns a perfectly plausible
number, and only `warnings` reveals the dropped half.

`cohort/manifest.txt` returns `text/plain` and so cannot carry these fields; there the
required-predicate `400` does the same job, appending the ignored-predicate reason to its message.

## Worked Examples

### Discovery

```bash
B=https://api.imaging.datacommons.cancer.gov/v3

curl -s $B/version                      # data release + API build
curl -s $B/stats                        # headline totals
curl -s $B/collections                  # all 176 collections
curl -s $B/collections/rider_pilot      # one collection: counts, modalities, licenses
curl -s $B/analysis_results             # derived datasets (segmentations, annotations)
curl -s $B/attributes                   # what can be filtered, and how
curl -s "$B/attributes/Modality/values?limit=10"
```

### Cohort building

Check size first — `counts` is cheap and answers "is this download sane?":

```bash
curl -s $B/cohort/counts \
  -H 'content-type: application/json' \
  -d '{"filters": {"terms": {"Modality": ["MR"], "BodyPartExamined": ["BREAST"]}}}'
# {"patients":3718,"studies":5689,"series":47986,"instances":6493262,"size_TB":2.421,
#  "filters_applied":{...},"warnings":[]}
```

Then request a page of series plus the download payload — same filter, same `filters` key.

```bash
curl -s $B/cohort/manifest \
  -H 'content-type: application/json' \
  -d '{"filters": {"terms": {"Modality": ["MR"], "BodyPartExamined": ["BREAST"]}},
       "page": 0, "page_size": 3}'
```

Each `series[]` row carries `collection_id`, `PatientID`, `StudyInstanceUID`,
`SeriesInstanceUID`, `Modality`, `SeriesDescription`, `instanceCount`, `series_size_MB`,
`aws_bucket`, `crdc_series_uuid`, and `series_aws_url`. Set `"include_rows": false` to get
counts and the download payload without the rows.

### SQL

```bash
curl -s $B/sql \
  -H 'content-type: application/json' \
  -d '{"sql": "SELECT Modality, count(*) n FROM index GROUP BY 1 ORDER BY n DESC", "max_rows": 20}'
```

### Viewer, licenses, citations

```bash
curl -s "$B/viewer-url?study_instance_uid=1.3.6.1.4.1.14519.5.2.1.7695.4164.129908397467389975396031099306"

curl -s $B/licenses \
  -H 'content-type: application/json' \
  -d '{"filters": {"terms": {"collection_id": ["rider_pilot"]}}}'

curl -s $B/citations \
  -H 'content-type: application/json' \
  -d '{"filters": {"terms": {"collection_id": ["rider_pilot"]}}, "citation_format": "bibtex"}'
```

`viewer-url` takes `series_instance_uid` or `study_instance_uid` (and an optional `viewer`
override); it picks OHIF v3 for radiology and Slim for slide microscopy automatically.

`citation_format` is one of `apa` (default), `bibtex`, `csl-json`, `turtle`. The response
separates the per-dataset `citations[]` from `idc_acknowledgment`, the IDC paper — include
both when publishing.

### Python client

```python
import requests

BASE = "https://api.imaging.datacommons.cancer.gov/v3"
session = requests.Session()

def get(path, **params):
    r = session.get(f"{BASE}{path}", params=params, timeout=60)
    r.raise_for_status()
    return r.json()

def post(path, payload):
    r = session.post(f"{BASE}{path}", json=payload, timeout=120)
    r.raise_for_status()
    return r.json()

# 1. Confirm which IDC release the API is serving
print(get("/version")["idc_version"])

# 2. Ground the filter values before using them
modalities = {v["value"] for v in get("/attributes/Modality/values", limit=1000)["values"]}
assert "MR" in modalities

# 3. Size the cohort, then page through it — the filter always goes under `filters`
filters = {"terms": {"collection_id": ["rider_pilot"], "Modality": ["CT"]}}
counts = post("/cohort/counts", {"filters": filters})
assert not counts["warnings"], counts["warnings"]   # nothing was silently dropped
print(counts)

manifest = post("/cohort/manifest", {"filters": filters, "page": 0, "page_size": 100})
uids = [row["SeriesInstanceUID"] for row in manifest["series"]]

# 4. Hand off to idc-index for the download (see "Handing Off to idc-index" below)
```

Error responses raise through `raise_for_status()`; read `r.json()["error"]["message"]` for the
reason before retrying.

## The SQL Surface

`POST /sql` runs read-only DuckDB SQL against the same tables `idc-index` exposes locally.
Ground the schema with `GET /tables` and `GET /tables/{table}` — do not guess table or column
names.

**Guardrails** (verified against `3.0.0b3`):

- Only single read-only `SELECT` / `WITH … SELECT` statements are accepted. Anything else is
  rejected with `{"error": {"code": "invalid_query", "message": "Only read-only SELECT (or WITH ... SELECT) statements are allowed."}}` and HTTP 400.
- A server row cap and per-query timeout apply. `max_rows` defaults to **5000** and is clamped
  to **10000**; results carry `truncated: true` when the cap was hit, and echo the `max_rows`
  actually applied.
- Invalid SQL returns DuckDB's own error text, including its "Candidate bindings" suggestions —
  useful for fixing a misspelled column without another schema round-trip.

**Tables reachable from SQL** are the `index` table plus the specialized indices documented in
`SKILL.md` (`collections_index`, `analysis_results_index`, `version_metadata_index`,
`prior_versions_index`, `seg_index`, `ann_index`, `ann_group_index`, `rtstruct_index`,
`ct_index`, `mr_index`, `pt_index`, `sm_index`, `sm_instance_index`, `contrast_index`,
`volume_geometry_index`, `clinical_index`). Join them to `index` on `SeriesInstanceUID`, except
where `SKILL.md` documents a different key (`segmented_SeriesInstanceUID`,
`referenced_SeriesInstanceUID`, `collection_id`, `analysis_result_id`).

The SQL patterns in `references/sql_patterns.md` are written for `client.sql_query()` but the
SQL itself transfers unchanged — send it as the `sql` field.

**Array columns:** columns typed `STRING[]` (e.g. `SegmentedPropertyType_CodeMeanings`) hold a
list per row. Match with `list_contains(col, 'value')`, not `=` or `LIKE`:

```bash
curl -s $B/sql -H 'content-type: application/json' -d '{
  "sql": "SELECT i.collection_id, count(DISTINCT i.SeriesInstanceUID) AS slides FROM index i JOIN seg_index seg ON seg.segmented_SeriesInstanceUID = i.SeriesInstanceUID WHERE i.Modality = '\''SM'\'' AND list_contains(seg.SegmentedPropertyType_CodeMeanings, '\''Nucleus'\'') GROUP BY 1 ORDER BY slides DESC",
  "max_rows": 20}'
```

**A SQL result can be a manifest.** Selecting `series_aws_url` gives download URLs directly,
and unlike `cohort/manifest.txt` you can carry extra columns alongside them — a per-row
`license_short_name`, for instance, which the plain manifest does not include:

```sql
SELECT SeriesInstanceUID, license_short_name, series_aws_url
FROM index WHERE collection_id = 'rider_pilot'
```

For bulk series, still prefer `cohort/manifest.txt` — it is not subject to the SQL row cap.

### Clinical data

Clinical data comes in two layers:

- **`clinical_index`** — a data dictionary, one row per (collection, table, column) with a
  human-readable `column_label` and coded `values`. It is an ordinary SQL table and joins to
  `index` on `collection_id`.
- **Per-collection clinical tables** (e.g. `nlst_canc`) — the actual rows. There are ~150, so
  they are kept out of `GET /tables` and discovered through the `/clinical/tables` endpoints
  instead. In SQL they live under a separate schema and are addressed as `clinical.<table>`.

Clinical tables join to imaging on **`dicom_patient_id = index.PatientID`**, not on a series
UID. Clinical data is not harmonized across collections — table and column names vary, so
always discover before querying.

```bash
curl -s "$B/clinical/tables?collection_id=nlst"            # which tables this collection has
curl -s $B/clinical/tables/nlst_canc                       # columns + labels
curl -s "$B/clinical/tables/nlst_canc/rows?max_rows=100"   # rows, capped

curl -s $B/sql -H 'content-type: application/json' -d '{
  "sql": "SELECT count(DISTINCT i.PatientID) AS patients FROM index i JOIN clinical.nlst_canc c ON c.dicom_patient_id = i.PatientID WHERE i.collection_id = '\''nlst'\'' AND i.Modality = '\''CT'\'' AND c.clinical_stag = '\''400'\''"}'
```

See `references/clinical_data_guide.md` for value mapping and the wider clinical data model.

## Getting the Data

The API returns manifests; a client moves the bytes. Every URL points at public AWS S3 or GCS
buckets and needs no credentials.

```bash
# save the full manifest
curl -s $B/cohort/manifest.txt \
  -H 'content-type: application/json' \
  -d '{"filters": {"terms": {"collection_id": ["rider_pilot"]}}}' > idc_manifest.txt

# download it (needs idc-index installed)
idc download-from-manifest idc_manifest.txt --download-dir ./idc-data
```

For a filter that is a single `collection_id`, the `download` payload of `cohort/manifest`
emits the simpler `idc download <collection_id> --download-dir ./idc-data` form.

### When the local index is a data release behind the API

This applies when the two `idc-index-data` **majors** differ — the API serving `25.x.y` against
a local `24.x.y`, say. A newer build of the same release (24.2.2 vs 24.2.0) covers the same
series, so manifests from it resolve locally and downloads are unaffected.

`idc download-from-manifest` does not simply hand the URLs to a transfer client: it extracts
each `crdc_series_uuid` from the manifest and joins it against the **local** index (then
against `prior_versions_index`) to compute sizes and build the output hierarchy. A manifest
produced by an API serving a newer IDC data release can therefore contain series the local
index has never heard of.

Those rows are **not** downloaded, and the command does not fail — it logs, then continues
with the rest:

```
The total of N copy commands are not recognized as referencing any associated series in the
main index. ... they may correspond to files available in a release of IDC different from v24
used in this version of idc-index.
...
The corresponding files could not be downloaded.
```

The result is a partial download that otherwise looks successful. `download_from_selection(seriesInstanceUID=…)`
has the same blind spot from the other direction: it filters the local index, so UIDs it does
not contain are silently dropped from the selection.

**Fix it one of two ways:**

1. **Upgrade** — upgrade `idc-index` (`python scripts/check_version.py` prints the command),
   then re-run. This is the right answer
   whenever it is possible; it restores the hierarchy, size checks, and progress reporting.
2. **Bypass the index** — transfer directly from the bucket. The manifest URLs are
   self-contained (`s3://<bucket>/<crdc_series_uuid>/*`), so no index is needed at all:

```bash
# one directory per series, named by crdc_series_uuid
awk -F/ '{print "cp " $0 " ./idc-data/" $4 "/"}' idc_manifest.txt > s5cmd_commands.txt
s5cmd --no-sign-request run s5cmd_commands.txt

# for source=gcs manifests, add the GCS endpoint
s5cmd --no-sign-request --endpoint-url https://storage.googleapis.com run s5cmd_commands.txt
```

`s5cmd run` expects one *command* per line, which is why the bare URLs are rewritten as `cp`
commands; drop the `$4` segment to land every file flat in `./idc-data/`. `aws s3 cp
--no-sign-request --recursive` works the same way per URL.

What you give up by bypassing `idc-index` is convenience, not data: files are laid out under
CRDC UUIDs instead of `%collection_id/%PatientID/%Modality`, and there is no local size or
disk-space check — so read `size_TB` from `cohort/counts` first. See
`references/cloud_storage_guide.md` for bucket layout, `aws`/`gsutil` equivalents, and
UUID-to-DICOM-UID mapping.

**`source`: `aws` (default) vs `gcs`.** Both return `s3://` URLs — GCS is reached through its
S3-compatible endpoint, never a `gs://` URL. That is why `idc download-from-manifest` only
recognizes `s3://` lines. Driving `s5cmd` yourself, use `--no-sign-request`, and for
`source=gcs` add `--endpoint-url https://storage.googleapis.com`.

IDC is ~99 TB across 176 collections. Always report `series` and `size_TB` from
`cohort/counts` and confirm with the user before starting a broad download.

## Limits, Defaults, and Errors

Measured against `3.0.0b3`. Values above a cap are silently clamped — the response echoes the
value actually used (`max_rows`, `page_size`), so read it back rather than assuming the request
was honored.

| Endpoint | Parameter | Default | Cap |
|----------|-----------|---------|-----|
| `GET /attributes/{attr}/values` | `limit` | 100 | 10000 |
| `POST /sql` | `max_rows` | 5000 | 10000 |
| `GET /clinical/tables/{table}/rows` | `max_rows` | 5000 | 100000 |
| `POST /cohort/manifest` | `page_size` | 100 | 5000 |
| `POST /cohort/manifest` | `page` | 0 | — |
| `POST /cohort/manifest` | `include_rows` | `true` | — |
| `POST /cohort/manifest.txt` | `limit` | 100000 | — |
| `POST /cohort/manifest.txt` | `source` | `aws` | — |
| `POST /citations` | `citation_format` | `apa` | — |

`cohort/manifest.txt` is the surface that is not *row*-capped the way `/sql` is — it returned all
774 lines for `rider_pilot` with no `limit` set, and enumerates up to 100 000 series. That is why
bulk series belong there rather than in a `/sql` dump.

There is **no per-caller rate limit or quota** and no `429`. What is bounded is the individual
request: a 30 s SQL statement timeout, 4 GB query memory, and the caps above. A burst is absorbed
by autoscaling and surfaces as slower responses or a `503` — back off and retry rather than
treating it as permanent. For sustained heavy metadata access, query the `idc-index` Parquet files
(`references/parquet_access_guide.md`) or BigQuery instead of driving this API hard.

Size-capped responses carry a `truncated` boolean: `false` means the result is complete, `true`
means raise the limit or aggregate/narrow instead. Explore narrow, then widen.

Errors come in two shapes. Semantic problems are HTTP 400 with a uniform body:

```json
{"error": {"code": "invalid_query", "message": "Unknown or non-term filter attribute: 'NotAnAttribute'. Use list_attributes to see valid attributes."}}
```

Request-shape problems are HTTP 422 with FastAPI's `detail[]` array, which names the offending
key — a bare filter object, an unrecognized key, or a misspelled range bound all land here. Both
kinds are actionable: an unknown attribute names the discovery call to make, and a bad column name
carries DuckDB's candidate bindings. Read the message and fix the request rather than retrying it
unchanged.

What does **not** produce an error is a filter that is valid but empty or over-broad. Those return
HTTP 200 with a `warnings` entry saying so — see *The server reports what it filtered on*. Read
`warnings`; do not infer from the count alone.

## Handing Off to idc-index

The boundary artifact is a list of `SeriesInstanceUID` values (or a saved `manifest.txt`).

```python
# UIDs from a cohort/manifest or /sql response
series_uids = [row["SeriesInstanceUID"] for row in manifest["series"]]

from idc_index import IDCClient
client = IDCClient()

client.download_from_selection(
    downloadDir="./data",
    seriesInstanceUID=series_uids,        # a list, not a DataFrame
    dirTemplate="%collection_id/%PatientID/%Modality",
)
```

Run `python scripts/check_version.py` before the first `idc-index` call in a session, even when
discovery happened over the API — the two version independently. Compare
`idc_index_data_version` on both sides first (see *Checking the API against a local
idc-index*).

**This handoff is only valid while the two are on the same IDC data release** — the same
`idc-index-data` major. `idc-index` can only download series its own index lists, so when the
API is a release ahead, UIDs and manifest URLs it returned may resolve to nothing locally:
`download_from_selection` silently drops them and `download-from-manifest` logs them as
unrecognized and skips them. Do not report that as "no data": name both versions, then either
upgrade `idc-index` or download straight from the bucket, as described in *When the local index
is a data release behind the API*.

## What the API Does Not Cover

- **Image bytes.** The API returns URLs and manifests only; files transfer from S3/GCS.
- **Pixel data access and DICOMweb.** Use `references/dicomweb_guide.md`.
- **Full DICOM metadata, per-segment detail, SR quantitative/qualitative measurements, private
  DICOM elements.** Still BigQuery-only — see `references/bigquery_guide.md`.
- **Writes.** The service is read-only by construction; there are no POST endpoints that mutate
  state, and the SQL connection rejects anything but `SELECT`.
- **Local analysis.** DataFrames, plotting, pydicom/SimpleITK, pathology tiling all stay with
  `idc-index`.

## Related Documentation

- IDC REST API docs: https://learn.canceridc.dev/rest-api/api
- Swagger UI: https://api.imaging.datacommons.cancer.gov/v3/docs
- API and MCP server source: https://github.com/ImagingDataCommons/IDC-REST-MCP
- `references/mcp_guide.md` — the same capabilities as agent tools
- `references/sql_patterns.md` — SQL that transfers unchanged to `POST /sql`
- `references/cli_guide.md` — `idc download-from-manifest` and the rest of the CLI

### `references/sql_patterns.md`

# SQL Query Patterns for IDC

**Tested with:** idc-index 0.12.5 (IDC data version v24)

Quick reference for common SQL query patterns when working with IDC data. For detailed examples with context, see the "Core Capabilities" section in the main SKILL.md.

## When to Use This Guide

Load this guide when you need quick-reference SQL patterns for:
- Discovering available filter values (modalities, body parts, manufacturers)
- Finding annotations and segmentations across collections
- Querying slide microscopy and annotation data
- Estimating download sizes before download
- Linking imaging data to clinical data
- Filtering by 3D volume geometry validity (volume_geometry_index)
- Finding RT Structure Set series and ROI metadata (rtstruct_index)
- Filtering by CT/MR/PET acquisition parameters (ct_index, mr_index, pt_index)

For table schemas, DataFrame access, and join column references, see `references/index_tables_guide.md`.

## Prerequisites

Needs `idc-index` installed — run `python scripts/check_version.py`, which reports the installed
version and prints the install command for the interpreter you are running.

```python
from idc_index import IDCClient
client = IDCClient()
```

## Overall Data Scale

Counts and total size across all of IDC — useful for orienting a user, and for sanity-checking
that the index loaded the release you expect:

```python
stats = client.sql_query("""
    SELECT
        COUNT(DISTINCT collection_id) as collections,
        COUNT(DISTINCT analysis_result_id) as analysis_results,
        COUNT(DISTINCT PatientID) as patients,
        COUNT(DISTINCT StudyInstanceUID) as studies,
        COUNT(DISTINCT SeriesInstanceUID) as series,
        SUM(instanceCount) as instances,
        SUM(series_size_MB)/1000000 as size_TB
    FROM index
""")
print(stats)
```

### Per-collection breakdown

```python
# Get summary statistics from primary index
collections_summary = client.sql_query("""
    SELECT collection_id,
           COUNT(DISTINCT PatientID) as patients,
           COUNT(DISTINCT SeriesInstanceUID) as series,
           SUM(series_size_MB) as size_mb
    FROM index
    GROUP BY collection_id
    ORDER BY patients DESC
""")
```

For richer per-collection metadata — cancer types, tumor locations, species, supporting data —
query `collections_index` instead; for derived datasets, `analysis_results_index`. Both need
`client.fetch_index(...)` first:

```python
client.fetch_index("collections_index")
collections_info = client.sql_query("""
    SELECT collection_id, cancer_types, tumor_locations, species, subjects, supporting_data
    FROM collections_index
""")

client.fetch_index("analysis_results_index")
analysis_info = client.sql_query("""
    SELECT analysis_result_id, analysis_result_title, subjects, collections, modalities
    FROM analysis_results_index
""")
```

## Discover Available Filter Values

```python
# What modalities exist?
client.sql_query("SELECT DISTINCT Modality FROM index")

# What body parts for a specific modality?
client.sql_query("""
    SELECT DISTINCT BodyPartExamined, COUNT(*) as n
    FROM index WHERE Modality = 'CT' AND BodyPartExamined IS NOT NULL
    GROUP BY BodyPartExamined ORDER BY n DESC
""")

# What manufacturers for MR?
client.sql_query("""
    SELECT DISTINCT Manufacturer, COUNT(*) as n
    FROM index WHERE Modality = 'MR'
    GROUP BY Manufacturer ORDER BY n DESC
""")
```

## Find Annotations and Segmentations

**Note:** Not all image-derived objects belong to analysis result collections. Some annotations are deposited alongside original images. Use DICOM Modality or SOPClassUID to find all derived objects regardless of collection type.

```python
# Find ALL segmentations and structure sets by DICOM Modality
# SEG = DICOM Segmentation, RTSTRUCT = Radiotherapy Structure Set
client.sql_query("""
    SELECT collection_id, Modality, COUNT(*) as series_count
    FROM index
    WHERE Modality IN ('SEG', 'RTSTRUCT')
    GROUP BY collection_id, Modality
    ORDER BY series_count DESC
""")

# Find segmentations for a specific collection (includes non-analysis-result items)
client.sql_query("""
    SELECT SeriesInstanceUID, SeriesDescription, analysis_result_id
    FROM index
    WHERE collection_id = 'tcga_luad' AND Modality = 'SEG'
""")

# List analysis result collections (curated derived datasets)
client.fetch_index("analysis_results_index")
client.sql_query("""
    SELECT analysis_result_id, analysis_result_title, collections, modalities
    FROM analysis_results_index
""")

# Find analysis results for a specific source collection
client.sql_query("""
    SELECT analysis_result_id, analysis_result_title
    FROM analysis_results_index
    WHERE Collections LIKE '%tcga_luad%'
""")

# Use seg_index for detailed DICOM Segmentation metadata
client.fetch_index("seg_index")

# Get segmentation statistics by algorithm
client.sql_query("""
    SELECT AlgorithmName, AlgorithmType, COUNT(*) as seg_count
    FROM seg_index
    WHERE AlgorithmName IS NOT NULL
    GROUP BY AlgorithmName, AlgorithmType
    ORDER BY seg_count DESC
    LIMIT 10
""")

# Find segmentations for specific source images (e.g., chest CT)
client.sql_query("""
    SELECT
        s.SeriesInstanceUID as seg_series,
        s.AlgorithmName,
        s.total_segments,
        s.segmented_SeriesInstanceUID as source_series
    FROM seg_index s
    JOIN index src ON s.segmented_SeriesInstanceUID = src.SeriesInstanceUID
    WHERE src.Modality = 'CT' AND src.BodyPartExamined = 'CHEST'
    LIMIT 10
""")

# Find TotalSegmentator results with source image context
client.sql_query("""
    SELECT
        seg_info.collection_id,
        COUNT(DISTINCT s.SeriesInstanceUID) as seg_count,
        SUM(s.total_segments) as total_segments
    FROM seg_index s
    JOIN index seg_info ON s.SeriesInstanceUID = seg_info.SeriesInstanceUID
    WHERE s.AlgorithmName LIKE '%TotalSegmentator%'
    GROUP BY seg_info.collection_id
    ORDER BY seg_count DESC
""")

# Use ann_index and ann_group_index for Microscopy Bulk Simple Annotations
# ann_group_index has AnnotationGroupLabel, GraphicType, NumberOfAnnotations, AlgorithmName
client.fetch_index("ann_index")
client.fetch_index("ann_group_index")
client.sql_query("""
    SELECT g.AnnotationGroupLabel, g.GraphicType, g.NumberOfAnnotations, i.collection_id
    FROM ann_group_index g
    JOIN ann_index a ON g.SeriesInstanceUID = a.SeriesInstanceUID
    JOIN index i ON a.SeriesInstanceUID = i.SeriesInstanceUID
    WHERE g.AlgorithmName IS NOT NULL
    LIMIT 10
""")
# See references/digital_pathology_guide.md for AnnotationGroupLabel filtering, SM+ANN joins, and more
```

## Query Slide Microscopy and Annotation Data

Use `sm_index` for slide microscopy metadata and `ann_index`/`ann_group_index` for annotations on slides (DICOM ANN objects). Filter annotation groups by `AnnotationGroupLabel` to find annotations by name.

```python
client.fetch_index("sm_index")
client.fetch_index("ann_index")
client.fetch_index("ann_group_index")

# Example: find annotation groups by label within a collection
client.sql_query("""
    SELECT g.AnnotationGroupLabel, g.GraphicType, g.NumberOfAnnotations
    FROM ann_group_index g
    JOIN index i ON g.SeriesInstanceUID = i.SeriesInstanceUID
    WHERE i.collection_id = 'your_collection_id'
      AND LOWER(g.AnnotationGroupLabel) LIKE '%keyword%'
""")
```

See `references/digital_pathology_guide.md` for SM queries, ANN filtering patterns, SM+ANN cross-references, and join examples.

## Estimate Download Size

```python
# Size for specific criteria
client.sql_query("""
    SELECT SUM(series_size_MB) as total_mb, COUNT(*) as series_count
    FROM index
    WHERE collection_id = 'nlst' AND Modality = 'CT'
""")
```

## Link to Clinical Data

```python
client.fetch_index("clinical_index")

# Find collections with clinical data and their tables
client.sql_query("""
    SELECT collection_id, table_name, COUNT(DISTINCT column_label) as columns
    FROM clinical_index
    GROUP BY collection_id, table_name
    ORDER BY collection_id
""")
```

See `references/clinical_data_guide.md` for complete patterns including value mapping and patient cohort selection.

## Version Tracking — "What's New in IDC vX?"

Use `series_init_idc_version` and `series_revised_idc_version` in the main `index` table. Do NOT
use `prior_versions_index` for this — it contains only removed series.

```python
VERSION = 24  # Replace with target version

# Series added for the first time in vVERSION
client.sql_query(f"""
    SELECT collection_id,
           COUNT(DISTINCT SeriesInstanceUID) as new_series,
           ROUND(SUM(series_size_MB)/1000, 2) as size_GB
    FROM index
    WHERE series_init_idc_version = {VERSION}
    GROUP BY collection_id
    ORDER BY new_series DESC
""")

# Series revised (updated content) in vVERSION but originally added earlier
client.sql_query(f"""
    SELECT collection_id,
           COUNT(DISTINCT SeriesInstanceUID) as revised_series
    FROM index
    WHERE series_revised_idc_version = {VERSION}
      AND series_init_idc_version < {VERSION}
    GROUP BY collection_id
    ORDER BY revised_series DESC
""")

# When was each collection first added to IDC?
client.fetch_index("version_metadata_index")
client.sql_query("""
    WITH first_versions AS (
        SELECT collection_id, MIN(series_init_idc_version) as first_version
        FROM index
        GROUP BY collection_id
    )
    SELECT f.collection_id, f.first_version, v.version_timestamp as first_release_date
    FROM first_versions f
    JOIN version_metadata_index v ON f.first_version = v.idc_version
    ORDER BY f.first_version DESC
""")
```

## Troubleshooting

**Issue:** Query returns error "table not found"
- **Cause:** Index not fetched before query
- **Solution:** Call `client.fetch_index("table_name")` before using tables other than the primary `index`

**Issue:** LIKE pattern not matching expected results
- **Cause:** Case sensitivity or whitespace
- **Solution:** Use `LOWER(column)` for case-insensitive matching, `TRIM()` for whitespace

**Issue:** JOIN returns fewer rows than expected
- **Cause:** NULL values in join columns or no matching records
- **Solution:** Use `LEFT JOIN` to include rows without matches, check for NULLs with `IS NOT NULL`

## Volume Geometry Validation

`volume_geometry_index` covers single-frame CT, MR, and PT series. Fetch it before querying.

```python
client.fetch_index("volume_geometry_index")

# Series that form a regularly-spaced 3D volume (no resampling needed)
client.sql_query("""
    SELECT i.collection_id, i.SeriesInstanceUID, i.BodyPartExamined,
           v.obliquity_degrees
    FROM index i
    JOIN volume_geometry_index v ON i.SeriesInstanceUID = v.SeriesInstanceUID
    WHERE i.Modality = 'CT'
      AND v.regularly_spaced_3d_volume = TRUE
    LIMIT 10
""")

# Fraction of 3D-valid CT per collection
client.sql_query("""
    SELECT i.collection_id,
           COUNT(*) as total_ct,
           SUM(CASE WHEN v.regularly_spaced_3d_volume THEN 1 ELSE 0 END) as valid_3d,
           ROUND(100.0 * SUM(CASE WHEN v.regularly_spaced_3d_volume THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_valid
    FROM index i
    JOIN volume_geometry_index v ON i.SeriesInstanceUID = v.SeriesInstanceUID
    WHERE i.Modality = 'CT'
    GROUP BY i.collection_id
    ORDER BY total_ct DESC
    LIMIT 10
""")
```

Key columns: `regularly_spaced_3d_volume` (composite flag), `obliquity_degrees` (0 = pure axial/sagittal/coronal), plus individual boolean checks: `single_orientation`, `orthogonal_orientation`, `unique_slice_positions`, `consistent_pixel_spacing`, `consistent_image_dimensions`, `uniform_slice_spacing`.

## RT Structure Sets

`rtstruct_index` has one row per RTSTRUCT series. Array columns (`ROINames`, `ROIGenerationAlgorithms`, `RTROIInterpretedTypes`) are stored as strings.

```python
client.fetch_index("rtstruct_index")

# RTSTRUCT series with ROI counts and names
client.sql_query("""
    SELECT i.collection_id, i.SeriesInstanceUID,
           r.total_rois, r.ROINames, r.RTROIInterpretedTypes,
           r.referenced_SeriesInstanceUID
    FROM index i
    JOIN rtstruct_index r ON i.SeriesInstanceUID = r.SeriesInstanceUID
    LIMIT 10
""")

# Collections with the most RTSTRUCT series
client.sql_query("""
    SELECT i.collection_id,
           COUNT(*) as rtstruct_series,
           ROUND(AVG(r.total_rois), 1) as avg_rois
    FROM index i
    JOIN rtstruct_index r ON i.SeriesInstanceUID = r.SeriesInstanceUID
    GROUP BY i.collection_id
    ORDER BY rtstruct_series DESC
    LIMIT 10
""")

# Find source CT series for a given RTSTRUCT
client.sql_query("""
    SELECT r.SeriesInstanceUID as rtstruct_uid,
           r.total_rois, r.ROINames,
           src.SeriesInstanceUID as source_ct_uid,
           src.collection_id, src.BodyPartExamined
    FROM rtstruct_index r
    JOIN index src ON r.referenced_SeriesInstanceUID = src.SeriesInstanceUID
    LIMIT 10
""")
```

## Modality Acquisition Parameters

`ct_index`, `mr_index`, and `pt_index` (added in idc-index 0.12.3) expose acquisition and reconstruction parameters for CT, MR, and PET series. All join on `SeriesInstanceUID`. Dose-modulated CT acquisitions have `_min`/`_max` columns for tube current, exposure, and exposure time.

```python
client.fetch_index("ct_index")
client.fetch_index("mr_index")
client.fetch_index("pt_index")

# CT: thin-slice series (≤2mm) with standard reconstruction
client.sql_query("""
    SELECT i.collection_id, i.SeriesInstanceUID, i.BodyPartExamined,
           c.SliceThickness, c.ConvolutionKernel, c.KVP
    FROM index i
    JOIN ct_index c ON i.SeriesInstanceUID = c.SeriesInstanceUID
    WHERE c.SliceThickness <= 2.0
      AND c.ConvolutionKernel IS NOT NULL
    LIMIT 10
""")

# CT: dose-modulated acquisitions (tube current varies across slices)
client.sql_query("""
    SELECT i.collection_id, c.SeriesInstanceUID,
           c.XRayTubeCurrent_min, c.XRayTubeCurrent_max, c.SliceThickness
    FROM ct_index c
    JOIN index i ON c.SeriesInstanceUID = i.SeriesInstanceUID
    WHERE c.XRayTubeCurrent_min != c.XRayTubeCurrent_max
    LIMIT 10
""")

# MR: DWI series (have non-null DiffusionBValue) at 3T
client.sql_query("""
    SELECT i.collection_id, i.SeriesInstanceUID, i.SeriesDescription,
           m.MagneticFieldStrength, m.DiffusionBValue
    FROM index i
    JOIN mr_index m ON i.SeriesInstanceUID = m.SeriesInstanceUID
    WHERE m.DiffusionBValue IS NOT NULL
      AND m.MagneticFieldStrength >= 2.9
    LIMIT 10
""")

# MR: multi-echo series (EchoTime stored as array with multiple values)
client.sql_query("""
    SELECT i.collection_id, i.SeriesInstanceUID,
           m.EchoTime, m.EchoTrainLength, m.ScanningSequence
    FROM index i
    JOIN mr_index m ON i.SeriesInstanceUID = m.SeriesInstanceUID
    WHERE m.EchoTrainLength > 1
    LIMIT 10
""")

# PET: FDG studies with specific reconstruction method
client.sql_query("""
    SELECT i.collection_id, i.SeriesInstanceUID,
           p.RadionuclideCodeMeaning, p.ReconstructionMethod,
           p.Units, p.DecayCorrection
    FROM index i
    JOIN pt_index p ON i.SeriesInstanceUID = p.SeriesInstanceUID
    WHERE p.RadionuclideCodeMeaning LIKE '%fluorodeoxyglucose%'
    LIMIT 10
""")

# PET: dynamic acquisitions (ActualFrameDuration is array with multiple values)
client.sql_query("""
    SELECT i.collection_id, i.SeriesInstanceUID,
           p.NumberOfTimeSlices, p.ActualFrameDuration
    FROM index i
    JOIN pt_index p ON i.SeriesInstanceUID = p.SeriesInstanceUID
    WHERE p.NumberOfTimeSlices > 1
    LIMIT 10
""")
```

Key columns by table (use `client.indices_overview["ct_index"]["schema"]` for the full list):
- **ct_index**: `SliceThickness`, `KVP`, `ConvolutionKernel`, `SpiralPitchFactor`, `XRayTubeCurrent_min/max`, `Exposure_min/max`, `PixelSpacing_row_mm/col_mm`, `Rows`, `Columns`
- **mr_index**: `MagneticFieldStrength`, `ScanningSequence`, `SequenceVariant`, `MRAcquisitionType`, `EchoTime` (array), `RepetitionTime`, `FlipAngle`, `DiffusionBValue` (array), `NumberOfTemporalPositions`, `ReceiveCoilName`
- **pt_index**: `RadionuclideCodeMeaning`, `Radiopharmaceutical`, `RadionuclideTotalDose`, `ReconstructionMethod`, `DecayCorrection`, `AttenuationCorrectionMethod`, `ActualFrameDuration` (array), `NumberOfTimeSlices`

## Resources

- `references/index_tables_guide.md` for table schemas, DataFrame access, and join column references
- `references/clinical_data_guide.md` for clinical data patterns and value mapping
- `references/digital_pathology_guide.md` for pathology-specific queries
- `references/bigquery_guide.md` for advanced queries requiring full DICOM metadata
- `references/parquet_access_guide.md` for direct Parquet queries without installing idc-index

### `references/use_cases.md`

# Common Use Cases for IDC

**Tested with:** idc-index 0.12.5 (IDC data version v24)

This guide provides complete end-to-end workflow examples for common IDC use cases. Each use case demonstrates the full workflow from query to download with best practices.

## When to Use This Guide

Load this guide when you need:
- Complete end-to-end workflow examples for training dataset creation
- Patterns for multi-step data selection and download workflows
- Examples of license-aware data handling for commercial use
- Visualization workflows for data preview before download

For core API patterns (query, download, visualize, citations), see the "Core Capabilities" section in the main SKILL.md.

## Prerequisites

Needs `idc-index` installed — run `python scripts/check_version.py`, which reports the installed
version and prints the install command for the interpreter you are running.

## Use Case 1: Find and Download Lung CT Scans for Deep Learning

**Objective:** Build training dataset of lung CT scans from NLST collection

**Steps:**
```python
from idc_index import IDCClient

client = IDCClient()

# 1. Query for lung CT scans with specific criteria
query = """
SELECT
  PatientID,
  SeriesInstanceUID,
  SeriesDescription
FROM index
WHERE collection_id = 'nlst'
  AND Modality = 'CT'
  AND BodyPartExamined = 'CHEST'
  AND license_short_name = 'CC BY 4.0'
ORDER BY PatientID
LIMIT 100
"""

results = client.sql_query(query)
print(f"Found {len(results)} series from {results['PatientID'].nunique()} patients")

# 2. Download data organized by patient
client.download_from_selection(
    seriesInstanceUID=list(results['SeriesInstanceUID'].values),
    downloadDir="./training_data",
    dirTemplate="%collection_id/%PatientID/%SeriesInstanceUID"
)

# 3. Save manifest for reproducibility
results.to_csv('training_manifest.csv', index=False)
```

## Use Case 2: Query Brain MRI by Manufacturer for Quality Study

**Objective:** Compare image quality across different MRI scanner manufacturers

**Steps:**
```python
from idc_index import IDCClient
import pandas as pd

client = IDCClient()

# Query for brain MRI grouped by manufacturer
query = """
SELECT
  Manufacturer,
  ManufacturerModelName,
  COUNT(DISTINCT SeriesInstanceUID) as num_series,
  COUNT(DISTINCT PatientID) as num_patients
FROM index
WHERE Modality = 'MR'
  AND BodyPartExamined LIKE '%BRAIN%'
GROUP BY Manufacturer, ManufacturerModelName
HAVING num_series >= 10
ORDER BY num_series DESC
"""

manufacturers = client.sql_query(query)
print(manufacturers)

# Download sample from each manufacturer for comparison
for _, row in manufacturers.head(3).iterrows():
    mfr = row['Manufacturer']
    model = row['ManufacturerModelName']

    query = f"""
    SELECT SeriesInstanceUID
    FROM index
    WHERE Manufacturer = '{mfr}'
      AND ManufacturerModelName = '{model}'
      AND Modality = 'MR'
      AND BodyPartExamined LIKE '%BRAIN%'
    LIMIT 5
    """

    series = client.sql_query(query)
    client.download_from_selection(
        seriesInstanceUID=list(series['SeriesInstanceUID'].values),
        downloadDir=f"./quality_study/{mfr.replace(' ', '_')}"
    )
```

## Use Case 3: Visualize Series Without Downloading

**Objective:** Preview imaging data before committing to download

```python
from idc_index import IDCClient
import webbrowser

client = IDCClient()

series_list = client.sql_query("""
    SELECT SeriesInstanceUID, PatientID, SeriesDescription
    FROM index
    WHERE collection_id = 'acrin_nsclc_fdg_pet' AND Modality = 'PT'
    LIMIT 10
""")

# Preview each in browser
for _, row in series_list.iterrows():
    viewer_url = client.get_viewer_URL(seriesInstanceUID=row['SeriesInstanceUID'])
    print(f"Patient {row['PatientID']}: {row['SeriesDescription']}")
    print(f"  View at: {viewer_url}")
    # webbrowser.open(viewer_url)  # Uncomment to open automatically
```

For additional visualization options, see the [IDC Portal getting started guide](https://learn.canceridc.dev/portal/getting-started) or [SlicerIDCBrowser](https://github.com/ImagingDataCommons/SlicerIDCBrowser) for 3D Slicer integration.

## Use Case 4: License-Aware Batch Download for Commercial Use

**Objective:** Download only CC-BY licensed data suitable for commercial applications

**Steps:**
```python
from idc_index import IDCClient

client = IDCClient()

# Query ONLY for CC BY licensed data (allows commercial use with attribution)
query = """
SELECT
  SeriesInstanceUID,
  collection_id,
  PatientID,
  Modality
FROM index
WHERE license_short_name LIKE 'CC BY%'
  AND license_short_name NOT LIKE '%NC%'
  AND Modality IN ('CT', 'MR')
  AND BodyPartExamined IN ('CHEST', 'BRAIN', 'ABDOMEN')
LIMIT 200
"""

cc_by_data = client.sql_query(query)

print(f"Found {len(cc_by_data)} CC BY licensed series")
print(f"Collections: {cc_by_data['collection_id'].unique()}")

# Download with license verification
client.download_from_selection(
    seriesInstanceUID=list(cc_by_data['SeriesInstanceUID'].values),
    downloadDir="./commercial_dataset",
    dirTemplate="%collection_id/%Modality/%PatientID/%SeriesInstanceUID"
)

# Save license information
cc_by_data.to_csv('commercial_dataset_manifest_CC-BY_ONLY.csv', index=False)
```

## Use Case 5: Batch Download with Filtering

**Objective:** Download a large filtered dataset in batches to avoid timeouts

**Steps:**
```python
from idc_index import IDCClient
import pandas as pd

client = IDCClient()

# Find chest CT scans from GE scanners with a permissive license
query = """
SELECT
  SeriesInstanceUID,
  PatientID,
  collection_id,
  ManufacturerModelName
FROM index
WHERE Modality = 'CT'
  AND BodyPartExamined = 'CHEST'
  AND Manufacturer = 'GE MEDICAL SYSTEMS'
  AND license_short_name = 'CC BY 4.0'
LIMIT 100
"""

results = client.sql_query(query)

# Save manifest for reproducibility
results.to_csv('lung_ct_manifest.csv', index=False)

# Download in batches to avoid timeout
batch_size = 10
for i in range(0, len(results), batch_size):
    batch = results.iloc[i:i+batch_size]
    client.download_from_selection(
        seriesInstanceUID=list(batch['SeriesInstanceUID'].values),
        downloadDir=f"./data/batch_{i//batch_size}"
    )
```

## Use Case 6: Integration with Analysis Pipelines

**Objective:** Load downloaded DICOM files into Python for processing

**Read individual DICOM files with pydicom:**
```python
import pydicom
import os

series_dir = "./data/rider/rider_pilot/RIDER-1007893286/CT_1.3.6.1..."

dicom_files = [os.path.join(series_dir, f) for f in os.listdir(series_dir)
               if f.endswith('.dcm')]

ds = pydicom.dcmread(dicom_files[0])
print(f"Patient ID: {ds.PatientID}")
print(f"Modality: {ds.Modality}")
print(f"Image shape: {ds.pixel_array.shape}")
```

**Build 3D volume from CT series:**
```python
import pydicom
import numpy as np
from pathlib import Path

def load_ct_series(series_path):
    files = sorted(Path(series_path).glob('*.dcm'))
    slices = [pydicom.dcmread(str(f)) for f in files]
    slices.sort(key=lambda x: float(x.ImagePositionPatient[2]))
    volume = np.stack([s.pixel_array for s in slices])
    return volume, slices[0]

volume, metadata = load_ct_series("./data/lung_ct/series_dir")
print(f"Volume shape: {volume.shape}")  # (z, y, x)
```

**Load DICOM series with SimpleITK (recommended for correct geometry):**
```python
import SimpleITK as sitk

series_path = "./data/ct_series"
reader = sitk.ImageSeriesReader()
dicom_names = reader.GetGDCMSeriesFileNames(series_path)
reader.SetFileNames(dicom_names)
image = reader.Execute()

smoothed = sitk.CurvatureFlow(image1=image, timeStep=0.125, numberOfIterations=5)
sitk.WriteImage(smoothed, "processed_volume.nii.gz")
```

## Resources

- Main SKILL.md for core API patterns (query, download, visualize)
- `references/clinical_data_guide.md` for clinical data integration workflows
- `references/sql_patterns.md` for additional SQL query patterns
- `references/index_tables_guide.md` for complex join patterns

### `scripts/check_version.py`

```python
#!/usr/bin/env python3
"""Check the idc-index package and this skill for required/available updates.

Run FIRST at the start of an IDC session:  python scripts/check_version.py

- Verifies that idc-index is installed and at least MIN_VERSION. It never
  installs or upgrades anything itself: if the requirement is not met it prints
  the command to run — targeting the interpreter that ran this script, via uv
  when uv is available — and exits non-zero, leaving the choice of Python
  environment to the caller.
- Notifies (only) when a newer idc-index (PyPI) or skill release (GitHub) is
  available. Network checks are best-effort and silently skipped offline.

Keep MIN_VERSION and SKILL_VERSION in sync with the SKILL.md frontmatter.
"""
import re
import shutil
import sys

MIN_VERSION = "0.12.5"   # keep in sync with metadata.idc-index in SKILL.md
SKILL_VERSION = "1.8.1"  # keep in sync with metadata.version in SKILL.md
REPO = "ImagingDataCommons/imaging-data-commons-skill"

_LEADING_DIGITS = re.compile(r"\d+")


def parse_version(v):
    """Numeric 3-tuple for comparison (string comparison misorders multi-digit parts).

    Tolerates pre-release and suffixed tags by taking the leading digits of each
    component: "0.13.0rc1" and "v1.7.0-beta" parse as (0, 13, 0) and (1, 7, 0)
    rather than raising. A pre-release therefore compares equal to its base
    release, which keeps the update notices conservative instead of advertising
    unreleased versions.
    """
    parts = []
    for part in v.lstrip("v").split(".")[:3]:
        match = _LEADING_DIGITS.match(part)
        parts.append(int(match.group()) if match else 0)
    return tuple(parts + [0] * (3 - len(parts)))


def fetch_json(url, *keys):
    """Best-effort JSON fetch, drilling into nested keys; None if unreachable."""
    import json
    import urllib.request
    try:
        data = json.load(urllib.request.urlopen(url, timeout=5))
        for key in keys:
            data = data[key]
        return data
    except Exception:
        return None


def install_commands(spec, upgrade=False):
    """Install commands for the interpreter running this script, preferred first.

    `-m pip` is always offered: every standard interpreter ships it, and naming the
    interpreter explicitly keeps the install out of whatever other environment a bare
    `pip` on PATH would resolve to. `uv` is offered ahead of it when it is on PATH, with
    `--python` for the same reason — otherwise `uv pip install` targets the active
    virtual environment, which is not necessarily this one.

    Neither form overrides the PEP 668 guard on an externally managed interpreter. Both
    refuse there, which is the intended outcome, not a gap to work around.
    """
    flag = "--upgrade " if upgrade else ""
    commands = [f"{sys.executable} -m pip install {flag}'{spec}'"]
    if shutil.which("uv"):
        commands.insert(0, f"uv pip install --python {sys.executable} {flag}'{spec}'")
    return commands


def print_install_instructions(spec):
    """Print how to install `spec` — this script never modifies the environment."""
    print("\nInstall the vetted version with:\n")
    for command in install_commands(spec):
        print(f"    {command}")
    print()
    print("Use a virtual environment where you can; on an externally managed system Python")
    print("(PEP 668) the install is refused until you use a virtual environment or `--user`.")
    print("Re-run this script once the install finishes.")


def check_minimum():
    """Check the installed idc-index against MIN_VERSION.

    Returns the installed version string, or None if idc-index is missing or
    older than MIN_VERSION — in which case install instructions are printed and
    the caller should not proceed until they have been followed.
    """
    try:
        import idc_index
    except ImportError:
        print(f"idc-index is not installed; this skill requires {MIN_VERSION} or newer.")
        print_install_instructions(f"idc-index=={MIN_VERSION}")
        return None

    installed = idc_index.__version__
    if parse_version(installed) < parse_version(MIN_VERSION):
        print(f"idc-index {installed} is below the pinned minimum {MIN_VERSION}.")
        print_install_instructions(f"idc-index=={MIN_VERSION}")
        return None

    print(f"idc-index {installed} meets pinned minimum ({MIN_VERSION})")
    return installed


def notify_updates(installed):
    """Print notices when newer idc-index or skill versions are available."""
    if installed:
        pkg = fetch_json("https://pypi.org/pypi/idc-index/json", "info", "version")
        if pkg and parse_version(pkg) > parse_version(installed):
            print(f"ℹ️ idc-index {pkg} available — to update: "
                  f"{install_commands('idc-index', upgrade=True)[0]}")

    tag = fetch_json(f"https://api.github.com/repos/{REPO}/releases/latest", "tag_name")
    if tag and parse_version(tag) > parse_version(SKILL_VERSION):
        print(f"ℹ️ Skill {tag.lstrip('v')} available (you have {SKILL_VERSION}): "
              f"https://github.com/{REPO}/releases/latest")


def main():
    """Exit 0 when the pinned minimum is installed, 1 when the caller must install it."""
    installed = check_minimum()
    notify_updates(installed)
    return 0 if installed else 1


if __name__ == "__main__":
    sys.exit(main())
```
