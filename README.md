# Mold Shop Management System

> Production - Mold Repair - MDR - Power BI - Data Analytics

A professional data management, document control, and reporting system for Mold Shop operations.

---

## Project Objectives

- Centralize Mold Shop operational data
- Standardize Excel source files
- Establish a professional MDR (Master Document Register)
- Prepare structured datasets for Power BI
- Automate data processing and reporting
- Support weekly, monthly, and management reporting
- Create a scalable foundation for future SQL Server and Python integration

---

## Repository Structure

```text
mold-shop-management/
│
├── data/
│   ├── source/          Original Excel source files
│   ├── processed/       Processed CSV / JSON datasets
│   └── dictionary/      Data Dictionary
│
├── mdr/
│   ├── documents/       MDR documents
│   ├── templates/       MDR templates
│   └── status/          Document tracking
│
├── powerbi/
│   ├── reports/         Power BI reports
│   └── metadata/        Power BI metadata
│
├── automation/
│   ├── python/          Python scripts
│   └── scripts/         PowerShell scripts
│
├── reports/
│   ├── weekly/
│   ├── monthly/
│   └── management/
│
├── docs/
│   ├── process/
│   ├── technical/
│   └── training/
│
└── .github/
    └── workflows/
```

---

## Data Pipeline

```text
Excel Source Files
        │
        ▼
Python Data Processing
        │
        ▼
Standardized CSV / JSON
        │
        ▼
Power BI
        │
        ▼
Management Reports
```

---

## Main Data Source

`data/source/1405.xlsx`

---

## Core Project Areas

- Mold Manufacturing
- Mold Repair
- Part Manufacturing
- Part Repair
- Machine Manufacturing
- Machine Repair
- MDR (Master Document Register)
- Production Planning
- Data Analysis
- Power BI Reporting

---

## Technology Stack

| Technology | Purpose |
|------------|---------|
| Microsoft Excel | Primary operational data source |
| Python | Data processing & automation |
| Power BI | Dashboards & analytics |
| Git | Version control |
| GitHub | Collaboration & repository management |
| PowerShell | Automation scripts |
| SQL Server (Future) | Centralized database |

---

## Project Status

**Current Phase:** Repository Architecture & Data Management Foundation

- **Repository:** `mold-shop-management`
- **Main Branch:** `main`
- **Architecture Commit:** `573aa6d`

---

## Data Governance

The `data/source/` directory contains the original Excel source files.

### Rules

1. Preserve original files without modification.
2. Generate processed datasets inside `data/processed/`.
3. Maintain field definitions in `data/dictionary/`.
4. Store MDR documents and templates inside the `mdr/` directory.
5. Keep Power BI reports independent from raw source files.

---

## Future Development Roadmap

- [ ] Automated Excel data processing
- [ ] Standardized Data Dictionary
- [ ] Professional MDR implementation
- [ ] Power BI semantic data model
- [ ] Automated weekly & monthly reporting
- [ ] Python desktop reporting application
- [ ] GitHub Actions CI/CD automation
- [ ] SQL Server integration
- [ ] Advanced production & maintenance analytics

---

## Author

**Fouad Alizadeh**

Production Planning • Mold Shop • MDR • Power BI • Data Analytics

---

*Mold Shop Management System — Professional Data & Reporting Infrastructure*
