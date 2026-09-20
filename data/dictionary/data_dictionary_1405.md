# Data Dictionary — 1405.xlsx

> Mold Shop Management System — Data Management Foundation

## 1. Document Control

| Item | Value |
|---|---|
| Source File | `data/source/1405.xlsx` |
| Version | 0.1 |
| Status | Draft — Initial Standardization |
| Owner | Fouad Alizadeh |
| Domain | Mold Shop / Production Planning / Maintenance |
| Target | Python + Power BI + future SQL Server |
| Primary Language | Persian |
| Data Grain | One operational work/record entry |

---

## 2. Purpose

This Data Dictionary defines the meaning, expected type, business role, and standardization rules of the operational fields used in `1405.xlsx`.

The objective is to create a stable semantic layer before data processing with Python and visualization in Power BI.

---

## 3. Core Business Fields

| # | Source Field | Standard Field Name | Data Type | Business Meaning | Required | Standardization Rule |
|---|---|---|---|---|---|---|
| 1 | قالب / قطعه / دستگاه | asset_type | Text / Category | نوع موضوع کاری: قالب، قطعه یا دستگاه | Yes | Controlled vocabulary |
| 2 | نوع تعمیر | activity_type | Text / Category | نوع فعالیت انجام‌شده | Yes | Controlled vocabulary |
| 3 | تعمیرکار | technician | Text | نام فرد/تیم انجام‌دهنده کار | No | Trim spaces; preserve Persian names |
| 4 | واحد درخواست کننده | requesting_department | Text | واحد سازمانی درخواست‌کننده کار | No | Standard department names |
| 5 | زیرگروه | asset_subgroup | Text / Category | زیرگروه موضوع کاری | No | Controlled vocabulary where possible |
| 6 | کد قالب | mold_code | Text | شناسه/کد قالب | No | Treat as text; never convert to number |
| 7 | شماره نامه درخواست | request_no | Text | شماره درخواست/نامه مرتبط با کار | No | Treat as text; preserve leading zeros |
| 8 | تاریخ | work_date | Date | تاریخ انجام/ثبت فعالیت | Yes | Convert to a true date field |
| 9 | ساعت کاری | work_shift | Text / Category | شیفت یا بازه کاری ثبت‌شده | No | Standardize shift labels |
| 10 | مقدار دقیقه کار شده | worked_minutes | Decimal / Integer | مدت کار انجام‌شده بر حسب دقیقه | No | Numeric; reject non-numeric values |
| 11 | مقدار ساعت کار شده | worked_hours | Decimal | مدت کار انجام‌شده بر حسب ساعت | Yes* | Numeric; preferred measure for reporting |

\* If `worked_hours` is unavailable or invalid, it may be calculated from `worked_minutes / 60`, but the original source value must be preserved.

---

## 4. Activity Classification

The initial controlled vocabulary for `activity_type` is:

| Standard Value | Description |
|---|---|
| ساخت قالب | Mold manufacturing |
| تعمیر قالب | Mold repair |
| ساخت قطعه | Part manufacturing |
| تعمیر قطعه | Part repair |
| ساخت دستگاه | Machine manufacturing |
| تعمیر دستگاه | Machine repair |

Any additional source value must be documented before being added to the controlled vocabulary.

---

## 5. Asset Classification

The initial controlled vocabulary for `asset_type` is:

| Standard Value | Description |
|---|---|
| قالب | Mold |
| قطعه | Part |
| دستگاه | Machine |

The field must remain categorical even when the source contains numeric-looking identifiers.

---

## 6. Data Type Standards

### Text

- Preserve Persian characters.
- Remove leading/trailing spaces.
- Do not silently change business identifiers.
- Codes and request numbers must remain text.

### Dates

- `work_date` must become a real date type in the processed dataset.
- Jalali dates must be explicitly identified and converted through a controlled conversion step when required.
- The original source representation should remain available during processing.

### Numeric Measures

- `worked_minutes` is measured in minutes.
- `worked_hours` is measured in hours.
- Decimal values are allowed for hours.
- Blank, text, negative, or impossible values must be flagged during validation rather than silently corrected.

---

## 7. Business Keys and Identifiers

The following fields may participate in record identification and analysis:

- `mold_code`
- `request_no`
- `asset_type`
- `asset_subgroup`
- `work_date`

No single field should currently be assumed to be a globally unique primary key.

A future processed dataset should receive a technical record identifier such as:

`record_id`

This identifier should be generated during processing and must not replace the original business identifiers.

---

## 8. Data Quality Rules

The Python validation layer should check at minimum:

1. Missing required fields.
2. Invalid dates.
3. Invalid numeric values.
4. Negative worked time.
5. Worked hours/minutes inconsistency.
6. Duplicate records.
7. Unrecognized activity types.
8. Unrecognized asset types.
9. Leading/trailing whitespace.
10. Inconsistent spelling of departments, technicians, and categories.
11. Numeric identifiers incorrectly stored as numbers.
12. Records with an activity but no measurable work time.

---

## 9. Recommended Standard Output Schema

The first processed dataset should use these canonical fields:

```text
record_id
asset_type
activity_type
technician
requesting_department
asset_subgroup
mold_code
request_no
work_date
work_shift
worked_minutes
worked_hours
source_file
source_sheet
source_row
```

The final three technical fields are added by the processing pipeline for traceability and auditability.

---

## 10. Power BI Semantic Mapping

| Data Dictionary Field | Power BI Role |
|---|---|
| record_id | Technical identifier |
| asset_type | Dimension |
| activity_type | Dimension |
| technician | Dimension |
| requesting_department | Dimension |
| asset_subgroup | Dimension |
| mold_code | Dimension / Identifier |
| request_no | Dimension / Identifier |
| work_date | Date dimension relationship |
| work_shift | Dimension |
| worked_minutes | Measure |
| worked_hours | Primary measure |
| source_file | Audit field |
| source_sheet | Audit field |
| source_row | Audit field |

Recommended first measures:

- Total Requests
- Total Worked Hours
- Total Worked Minutes
- Hours by Activity
- Hours by Asset Type
- Hours by Technician
- Hours by Department
- Hours by Month
- Hours by Mold Code

---

## 11. Data Governance

### Raw Layer

`data/source/`

Original files are immutable source evidence.

### Processed Layer

`data/processed/`

Cleaned and standardized outputs generated by Python.

### Dictionary Layer

`data/dictionary/`

Business definitions, field mappings, data types, validation rules, and controlled vocabularies.

### Reporting Layer

`powerbi/` and `reports/`

Dashboards and management reports must use processed/standardized data rather than directly modifying raw source files.

---

## 12. Versioning

Changes to field meaning, field names, controlled vocabularies, or transformation rules must update the Data Dictionary version.

Suggested versions:

- 0.x — Draft / discovery
- 1.0 — First approved production schema
- 1.x — Backward-compatible additions
- 2.0 — Breaking schema changes

---

## 13. Next Validation Step

Before Python processing is finalized, the following must be verified against every relevant sheet in `1405.xlsx`:

- Exact sheet names
- Exact header names
- Column positions
- Actual date format
- Actual hour/minute formats
- Blank/null patterns
- Duplicate patterns
- Additional fields not yet included in this initial dictionary

Only after this validation should the canonical processed dataset be frozen.

---

**Document:** Data Dictionary — 1405.xlsx  
**Project:** Mold Shop Management System  
**Status:** Draft v0.1
