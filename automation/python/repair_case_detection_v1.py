#!/usr/bin/env python3
"""RepairCase Detection v1 from the AI-readable staging layer.

Input:
  data/processed/ai/1405/operational_records.csv

Outputs:
  data/processed/repair_cases/v1/repair_case_candidates.csv
  data/processed/repair_cases/v1/record_to_repair_case.csv
  data/processed/repair_cases/v1/review_queue.csv
  data/processed/repair_cases/v1/multi_case_mold_summary.csv
  data/processed/repair_cases/v1/index.json

Rules in v1:
  HIGH:
    MoldCodeNorm + RequestLetterNoNorm (both nonblank) define one proposed RepairCase.
  REVIEW:
    MoldCodeNorm present but RequestLetterNoNorm blank -> no automatic Case assignment.
  NON-REPAIR:
    Only mold + repair-like records are included in this detection layer.

This is a test/candidate engine, not final business logic.
"""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "data" / "processed" / "ai" / "1405" / "operational_records.csv"
OUTPUT = ROOT / "data" / "processed" / "repair_cases" / "v1"


def clean(value: str | None) -> str:
    if value is None:
        return ""
    text = str(value)
    text = text.replace("\u200c", " ").replace("\ufeff", "")
    text = text.translate(str.maketrans(
        "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
        "01234567890123456789",
    ))
    return re.sub(r"\s+", " ", text).strip()


def date_key(value: str) -> tuple:
    text = clean(value)
    m = re.match(r"^(\d{4})/(\d{1,2})/(\d{1,2})$", text)
    if not m:
        return (9999, 99, 99)
    return tuple(map(int, m.groups()))


def repair_like(row: dict) -> bool:
    return row.get("AssetType") == "قالب" and "تعمیر" in clean(row.get("WorkTypeNorm") or row.get("WorkType"))


def read_rows() -> list[dict]:
    if not INPUT.exists():
        raise FileNotFoundError(INPUT)
    with INPUT.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    rows = [r for r in read_rows() if repair_like(r)]

    # Stable order for sequence assignment within each mold.
    rows.sort(key=lambda r: (
        clean(r.get("MoldCodeNorm")),
        date_key(r.get("WorkDate", "")),
        clean(r.get("SourceSheet")),
        int(clean(r.get("SourceRowNumber")) or 0),
    ))

    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    review_rows: list[dict] = []

    for r in rows:
        mold = clean(r.get("MoldCodeNorm"))
        req = clean(r.get("RequestLetterNoNorm"))
        if mold and req:
            groups[(mold, req)].append(r)
        elif mold:
            review_rows.append(r)

    # Assign stable case IDs in deterministic mold/date order.
    sorted_groups = sorted(
        groups.items(),
        key=lambda item: (
            item[0][0],
            min(date_key(x.get("WorkDate", "")) for x in item[1]),
            item[0][1],
        ),
    )

    case_id_by_key: dict[tuple[str, str], str] = {}
    sequence_by_mold: dict[str, int] = defaultdict(int)
    candidate_rows: list[dict] = []
    mapping_rows: list[dict] = []

    for (mold, req), group in sorted_groups:
        sequence_by_mold[mold] += 1
        seq = sequence_by_mold[mold]
        case_id = f"RC-1405-{len(case_id_by_key) + 1:04d}"
        case_id_by_key[(mold, req)] = case_id

        worked_hours = 0.0
        dates = []
        failures = []
        for r in group:
            try:
                worked_hours += float(clean(r.get("WorkedHours") or 0) or 0)
            except ValueError:
                pass
            if clean(r.get("WorkDate")):
                dates.append(r["WorkDate"])
            failure = clean(r.get("FailureDescriptionRaw"))
            if failure and failure not in failures:
                failures.append(failure)

            mapping_rows.append({
                "RecordKey": clean(r.get("RecordKey")),
                "SourceSheet": clean(r.get("SourceSheet")),
                "SourceRowNumber": clean(r.get("SourceRowNumber")),
                "RecordID": clean(r.get("RecordID")),
                "MoldCode": clean(r.get("MoldCode")),
                "MoldCodeNorm": mold,
                "RequestLetterNo": clean(r.get("RequestLetterNo")),
                "RequestLetterNoNorm": req,
                "ProposedRepairCaseID": case_id,
                "RepairSequenceNo": seq,
                "DetectionBasis": "MoldCodeNorm + RequestLetterNoNorm",
                "Confidence": "HIGH",
            })

        candidate_rows.append({
            "RepairCaseID": case_id,
            "MoldCode": clean(group[0].get("MoldCode")),
            "MoldCodeNorm": mold,
            "MoldName": clean(group[0].get("AssetName")),
            "RequestLetterNo": clean(group[0].get("RequestLetterNo")),
            "RepairSequenceNo": seq,
            "CaseStartDate": min(dates, key=date_key) if dates else "",
            "CaseLastWorkDate": max(dates, key=date_key) if dates else "",
            "RecordCount": len(group),
            "TotalWorkedHours": round(worked_hours, 2),
            "FailureExamples": " | ".join(failures[:5]),
            "DetectionBasis": "MoldCodeNorm + RequestLetterNoNorm",
            "Confidence": "HIGH",
        })

    # Review queue: mold repair records without a request number.
    review_export = []
    for r in review_rows:
        review_export.append({
            "RecordKey": clean(r.get("RecordKey")),
            "SourceSheet": clean(r.get("SourceSheet")),
            "SourceRowNumber": clean(r.get("SourceRowNumber")),
            "RecordID": clean(r.get("RecordID")),
            "MoldCode": clean(r.get("MoldCode")),
            "MoldCodeNorm": clean(r.get("MoldCodeNorm")),
            "RequestLetterNo": "",
            "WorkDate": clean(r.get("WorkDate")),
            "FailureDescriptionRaw": clean(r.get("FailureDescriptionRaw")),
            "WorkedHours": clean(r.get("WorkedHours")),
            "ReviewReason": "F009 RequestLetterNo is blank; automatic RepairCase assignment deferred",
        })

    # Multi-case mold summary.
    by_mold: dict[str, list[dict]] = defaultdict(list)
    for r in candidate_rows:
        by_mold[r["MoldCodeNorm"]].append(r)

    multi_rows = []
    for mold, cases in sorted(by_mold.items()):
        if len(cases) < 2:
            continue
        multi_rows.append({
            "MoldCode": cases[0]["MoldCode"],
            "MoldCodeNorm": mold,
            "MoldName": cases[0]["MoldName"],
            "ProposedRepairCaseCount": len(cases),
            "RepairCaseIDs": " | ".join(c["RepairCaseID"] for c in cases),
            "RequestLetterNos": " | ".join(c["RequestLetterNo"] for c in cases),
            "FirstCaseDate": min(
                (c["CaseStartDate"] for c in cases if c["CaseStartDate"]),
                key=date_key,
                default="",
            ),
            "LastCaseDate": max(
                (c["CaseLastWorkDate"] for c in cases if c["CaseLastWorkDate"]),
                key=date_key,
                default="",
            ),
        })

    write_csv(
        OUTPUT / "repair_case_candidates.csv",
        candidate_rows,
        [
            "RepairCaseID", "MoldCode", "MoldCodeNorm", "MoldName",
            "RequestLetterNo", "RepairSequenceNo", "CaseStartDate",
            "CaseLastWorkDate", "RecordCount", "TotalWorkedHours",
            "FailureExamples", "DetectionBasis", "Confidence",
        ],
    )

    write_csv(
        OUTPUT / "record_to_repair_case.csv",
        mapping_rows,
        [
            "RecordKey", "SourceSheet", "SourceRowNumber", "RecordID",
            "MoldCode", "MoldCodeNorm", "RequestLetterNo",
            "RequestLetterNoNorm", "ProposedRepairCaseID",
            "RepairSequenceNo", "DetectionBasis", "Confidence",
        ],
    )

    write_csv(
        OUTPUT / "review_queue.csv",
        review_export,
        [
            "RecordKey", "SourceSheet", "SourceRowNumber", "RecordID",
            "MoldCode", "MoldCodeNorm", "RequestLetterNo", "WorkDate",
            "FailureDescriptionRaw", "WorkedHours", "ReviewReason",
        ],
    )

    write_csv(
        OUTPUT / "multi_case_mold_summary.csv",
        multi_rows,
        [
            "MoldCode", "MoldCodeNorm", "MoldName",
            "ProposedRepairCaseCount", "RepairCaseIDs",
            "RequestLetterNos", "FirstCaseDate", "LastCaseDate",
        ],
    )

    summary = {
        "version": "repair-case-detection-v1",
        "source": str(INPUT.relative_to(ROOT)).replace("\\", "/"),
        "generated_at_utc": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "repair_like_record_count": len(rows),
        "proposed_repair_case_count": len(candidate_rows),
        "high_confidence_record_assignments": len(mapping_rows),
        "records_in_review_queue": len(review_export),
        "molds_with_multiple_proposed_cases": len(multi_rows),
        "logic": {
            "same_mold_same_request": "same proposed RepairCase",
            "same_mold_different_nonblank_request": "new proposed RepairCase",
            "same_mold_blank_request": "REVIEW; no automatic assignment",
        },
        "status": "TEST / CANDIDATE ONLY",
    }

    (OUTPUT / "index.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
