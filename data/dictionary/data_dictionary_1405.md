# Data Dictionary — 1405.xlsx

> **Mold Shop Management System — Data Management Foundation**

## 1. Document Control

| Item | Value |
|---|---|
| Source File | `data/source/1405.xlsx` |
| Version | **0.1** |
| Status | **Draft — Needs Validation** |
| Owner | Fouad Alizadeh |
| Domain | Mold Shop / Production Planning / Maintenance |
| Target Platforms | Python + Power BI + future SQL Server |
| Data Grain | One operational work/record entry |

---

## 2. Purpose

This Data Dictionary defines the initial meaning, standard name, expected data type, business role, validation rules, and analytical role of the operational fields used in `1405.xlsx`.

Version **0.1** is intentionally a controlled draft. It establishes the target terminology and governance framework but does **not** claim that every field has been verified against every worksheet in the source workbook.

The objective is to create a stable semantic layer before Python processing, Power Query, Power BI, MDR integration, and future SQL Server migration.

---

## 3. Data Dictionary Status Definitions

| Status | Meaning |
|---|---|
| **Draft** | Initial definition; not yet fully validated |
| **Needs Validation** | Must be checked against the actual workbook/business process |
| **Confirmed** | Verified against the source workbook and business process |
| **Derived** | Calculated from one or more source fields |
| **Optional** | May legitimately be blank |
| **Deprecated** | Existing source field should not be used in the target model |

---

## 4. Standard Naming Convention

The analytical model uses English **snake_case** field names.

Examples:

`work_date`  
`work_hours`  
`mold_code`  
`request_no`

Rules:

1. Preserve the original Persian Excel field name for traceability.
2. Use English standard names in processed datasets and analytical models.
3. Business identifiers must remain **Text**.
4. Do not convert codes to numeric types merely because they contain digits.
5. Use explicit date and duration fields.
6. Keep source fields separate from derived analytical fields.
7. Technical audit fields should be added by the ETL layer, not by modifying the raw workbook.

---

## 5. Initial Field Dictionary

> The following fields represent the currently known operational structure. **All fields remain Needs Validation in v0.1 until the complete workbook is inspected.**

| # | Source Field | Standard Field | Data Type | Required | Business Definition | Business Rule / Validation | Power BI Role | Status |
|---:|---|---|---|---|---|---|---|---|
| 1 | قالب / قطعه / دستگاه | `item_type` | Text / Category | Yes | نوع موضوع کاری: قالب، قطعه یا دستگاه | Controlled vocabulary | Dimension | Needs Validation |
| 2 | نوع تعمیر | `activity_type` | Text / Category | Yes | نوع فعالیت یا تعمیر انجام‌شده | Controlled vocabulary | Dimension | Needs Validation |
| 3 | تعمیرکار | `technician` | Text | No | فرد یا تیم انجام‌دهنده کار | Standardize names; trim spaces | Dimension | Needs Validation |
| 4 | واحد درخواست کننده | `requesting_department` | Text | No | واحد سازمانی درخواست‌کننده کار | Standardize department names | Dimension | Needs Validation |
| 5 | زیرگروه | `asset_subgroup` | Text / Category | No | زیرگروه موضوع کاری | Controlled vocabulary where applicable | Dimension | Needs Validation |
| 6 | کد قالب | `mold_code` | Text | No | شناسه یا کد قالب | Preserve leading zeros and alphanumeric codes | Dimension / Key | Needs Validation |
| 7 | شماره نامه درخواست | `request_no` | Text | No | شماره درخواست/نامه مرتبط با کار | Preserve as text; validate uniqueness | Dimension / Key | Needs Validation |
| 8 | تاریخ | `work_date` | Date | Yes | تاریخ انجام/ثبت فعالیت | Must become a true date in processed data | Date | Needs Validation |
| 9 | ساعت کاری | `work_time` | Time / Text | No | ساعت یا بازه زمانی ثبت‌شده | Exact source format must be verified | Attribute | Needs Validation |
| 10 | مقدار دقیقه کار شده | `work_minutes` | Decimal / Integer | No | مدت کار انجام‌شده بر حسب دقیقه | Must be >= 0 | Measure | Needs Validation |
| 11 | مقدار ساعت کار شده | `work_hours` | Decimal | Yes* | مدت کار انجام‌شده بر حسب ساعت | Must be >= 0; preferred reporting measure | Measure | Needs Validation |

\* Required for the target reporting model where available. If unavailable or invalid, it may be derived from `work_minutes / 60`, while the original source value remains preserved.

---

## 6. Initial Activity Classification

The current draft controlled vocabulary is:

| Standard Value | Description |
|---|---|
| ساخت قالب | Mold manufacturing |
| تعمیر قالب | Mold repair |
| ساخت قطعه | Part manufacturing |
| تعمیر قطعه | Part repair |
| ساخت دستگاه | Machine manufacturing |
| تعمیر دستگاه | Machine repair |

**Important:** These values are a draft business vocabulary. Any additional value found in `1405.xlsx` must be reviewed before Version 1.0 is approved.

---

## 7. Initial Item Classification

| Standard Value | Description |
|---|---|
| قالب | Mold |
| قطعه | Part |
| دستگاه | Machine |

The field remains categorical even when the related identifier contains numbers.

---

## 8. Core Business Rules

### 8.1 Work Date

Standard field: `work_date`

The processed dataset must contain a real date value.

Validation must determine:

- Source date format
- Whether the source uses Jalali dates
- Jalali-to-Gregorian conversion requirements
- Invalid dates
- Blank dates
- Duplicate records by business keys and date

A dedicated Date dimension is recommended for Power BI.

### 8.2 Work Hours

Standard field: `work_hours`

For management reporting, `work_hours` is the primary duration measure.

Where both source fields are available:

`work_hours ≈ work_minutes / 60`

Differences between the two values must be flagged rather than silently overwritten.

### 8.3 Mold Code

Standard field: `mold_code`

Mold codes must be stored as **Text**.

Possible patterns include:

- `M-125`
- `00125`
- Other alphanumeric identifiers

The actual patterns must be confirmed from the workbook.

### 8.4 Request Number

Standard field: `request_no`

Request numbers are business identifiers, not quantities.

Therefore:

- Store as Text.
- Preserve leading zeros.
- Do not aggregate.
- Validate duplicates.
- Determine whether uniqueness is global or contextual.

---

## 9. Data Quality Rules

The future Python / Power Query validation layer should check at minimum:

### Completeness

- Required fields are not blank.
- Work dates are present for operational records.
- Request numbers are available where the process requires a formal request.

### Validity

- `work_hours >= 0`
- `work_minutes >= 0`
- Dates are valid.
- Text identifiers are not silently converted to numbers.

### Consistency

Where both duration fields exist:

`work_minutes / 60 ≈ work_hours`

Significant differences should be flagged for review.

### Standardization

- Technician names use one standard spelling.
- Requesting department names are standardized.
- Activity types use controlled vocabulary.
- Item types use controlled vocabulary.
- Mold codes use consistent representation.

### Uniqueness

Potential business-key combinations should be investigated, for example:

`request_no + mold_code + work_date`

The final business key must be determined from the actual source data and workflow.

---

## 10. Recommended Technical Audit Fields

The raw workbook should remain unchanged.

The processing pipeline may add:

| Field | Purpose |
|---|---|
| `record_id` | Technical unique identifier |
| `source_file` | Source-file traceability |
| `source_sheet` | Original worksheet traceability |
| `source_row` | Original row traceability |
| `processed_at` | ETL processing timestamp |
| `data_quality_status` | Validation result |
| `data_quality_note` | Explanation of validation issues |

These fields are **derived by the processing layer**, not source fields.

---

## 11. Recommended Canonical Output Schema

The first standardized dataset is expected to use:

```text
record_id
item_type
activity_type
technician
requesting_department
asset_subgroup
mold_code
request_no
work_date
work_time
work_minutes
work_hours
source_file
source_sheet
source_row
processed_at
data_quality_status
data_quality_note
```

This schema is provisional until the complete source workbook is validated.

---

## 12. Power BI Semantic Mapping

### Dimensions

Potential dimensions:

- Date
- Item Type
- Activity Type
- Mold
- Request
- Technician
- Requesting Department
- Asset Subgroup
- Work Time / Shift

### Measures

Potential measures:

- Total Work Hours
- Total Work Minutes
- Request Count
- Activity Count
- Project Count
- Hours by Activity
- Hours by Item Type
- Hours by Technician
- Hours by Department
- Hours by Month
- Hours by Mold Code

Formal DAX definitions should be created only after the source schema is validated.

---

## 13. MDR Integration

The Data Dictionary is designed to support the future MDR structure.

Potential relationships:

| Data Field | Future MDR Role |
|---|---|
| `request_no` | Request / MDR identifier |
| `mold_code` | Mold master reference |
| `item_type` | Mold / Part / Machine classification |
| `activity_type` | Activity / repair classification |
| `work_date` | Activity date |
| `technician` | Responsible resource |

The detailed MDR schema will be maintained separately under:

`mdr/`

---

## 14. ETL / Data Pipeline

Target architecture:

```text
Excel Source
    │
    ▼
Source Validation
    │
    ▼
Python / Power Query
    │
    ├── Type Conversion
    ├── Cleaning
    ├── Standardization
    ├── Validation
    └── Traceability
    │
    ▼
Processed Dataset
    │
    ├──────────────► Power BI
    │
    ├──────────────► Management Reports
    │
    └──────────────► Future SQL Server
```

---

## 15. Data Governance

### Raw Layer

`data/source/`

Original files are source evidence and should not be modified by transformation processes.

### Processed Layer

`data/processed/`

Contains cleaned and standardized datasets generated by the processing pipeline.

### Dictionary Layer

`data/dictionary/`

Contains business definitions, field mappings, data types, validation rules, and controlled vocabularies.

### Reporting Layer

`powerbi/` and `reports/`

Dashboards and management reports should consume standardized data.

---

## 16. Source Preservation Rules

1. Never overwrite the original `1405.xlsx` during transformation.
2. Generate processed outputs separately.
3. Preserve original Persian field names.
4. Record transformation rules.
5. Preserve source sheet and row traceability.
6. Use Git history to document dictionary changes.
7. Do not treat a processed dataset as the original source.

---

## 17. Version 0.1 Validation Checklist

Before Version 1.0 is approved:

- [ ] Inspect every worksheet in `1405.xlsx`.
- [ ] Extract every actual source column.
- [ ] Verify exact header names.
- [ ] Verify column positions.
- [ ] Identify duplicate headers.
- [ ] Identify merged cells and their impact.
- [ ] Identify helper / blank columns.
- [ ] Verify actual data types.
- [ ] Verify date format and calendar system.
- [ ] Verify Jalali/Gregorian handling.
- [ ] Verify the authoritative work-hours field.
- [ ] Verify the relationship between minutes and hours.
- [ ] Verify request-number structure.
- [ ] Verify mold-code structure.
- [ ] Extract actual activity values.
- [ ] Extract actual item-type values.
- [ ] Standardize technician values.
- [ ] Standardize requesting departments.
- [ ] Identify business keys.
- [ ] Identify nullable fields.
- [ ] Define Power BI dimensions.
- [ ] Define Power BI measures.
- [ ] Review MDR relationships.
- [ ] Freeze the Version 1.0 canonical schema.

---

## 18. Version History

| Version | Date | Status | Change |
|---|---|---|---|
| 0.1 | 2026-09-20 | Draft | Initial professional Data Dictionary and governance structure |
| 1.0 | TBD | Planned | Complete validation against `1405.xlsx` |
| 1.1 | TBD | Planned | Minor compatible improvements |
| 2.0 | TBD | Planned | Enhanced analytical / SQL / Power BI model |

---

## 19. Next Development Steps

1. Inspect the complete `1405.xlsx` workbook.
2. Extract the actual schema from all relevant sheets.
3. Compare the actual schema with this draft.
4. Mark every field as Confirmed / Derived / Optional / Deprecated / Needs Validation.
5. Finalize controlled vocabularies.
6. Define business keys and relationships.
7. Upgrade this document to Version 1.0.
8. Build the standardized processed dataset.
9. Build the Power BI semantic model.
10. Integrate the MDR structure.

---

## 20. Document Ownership

**Project:** Mold Shop Management System  
**Document:** Data Dictionary — 1405.xlsx  
**Version:** 0.1  
**Owner:** Fouad Alizadeh  
**Domain:** Production Planning • Mold Shop • MDR • Power BI • Data Analytics

> **Important:** Version 0.1 is a controlled draft. It establishes the project's initial terminology and governance framework and must be validated against the actual source workbook before being treated as the production schema.
