#!/usr/bin/env python3
"""Build a review queue for mold-repair records with missing MoldCode.

Input:
  data/processed/ai/1405/operational_records.csv

Selection:
  AssetType == 'قالب'
  WorkTypeNorm contains 'تعمیر'
  MoldCodeNorm is blank

The queue is review-only. No MoldCode is inferred from MoldName, ProductTechnicalNo,
MachineCode, PartCode, RequestLetterNo, or any other field.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "data" / "processed" / "ai" / "1405" / "operational_records.csv"
OUTPUT = ROOT / "data" / "processed" / "repair_cases" / "v1"


def clean(value: str | None) -> str:
    return "" if value is None else str(value).strip()


def read_rows() -> list[dict]:
    with INPUT.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    if not INPUT.exists():
        raise FileNotFoundError(INPUT)

    source_rows = read_rows()
    selected = [
        r for r in source_rows
        if clean(r.get("AssetType")) == "قالب"
        and "تعمیر" in clean(r.get("WorkTypeNorm") or r.get("WorkType"))
        and not clean(r.get("MoldCodeNorm"))
    ]

    selected.sort(key=lambda r: (
        clean(r.get("WorkDate")),
        clean(r.get("SourceSheet")),
        int(clean(r.get("SourceRowNumber")) or 0),
    ))

    fields = [
        "ReviewID",
        "RecordKey",
        "SourceSheet",
        "SourceRowNumber",
        "RecordID",
        "AssetName",
        "WorkType",
        "RequestLetterNo",
        "FailureDescriptionRaw",
        "OperationDescriptionRaw",
        "RelatedMachineCode",
        "MachineName",
        "PartName",
        "PartCode",
        "WorkDate",
        "WorkedHours",
        "ProcessStatus",
        "RepairDeliveryOrProductionStartDate",
        "MoldDeliveryToProductionDate",
        "ApprovalFormStatus",
        "ReviewReason",
        "MoldCodeReviewStatus",
        "AssignedMoldCode",
        "ReviewerNote",
    ]

    output = []
    for i, r in enumerate(selected, start=1):
        output.append({
            "ReviewID": f"MMCR-1405-{i:04d}",
            "RecordKey": clean(r.get("RecordKey")),
            "SourceSheet": clean(r.get("SourceSheet")),
            "SourceRowNumber": clean(r.get("SourceRowNumber")),
            "RecordID": clean(r.get("RecordID")),
            "AssetName": clean(r.get("AssetName")),
            "WorkType": clean(r.get("WorkType")),
            "RequestLetterNo": clean(r.get("RequestLetterNo")),
            "FailureDescriptionRaw": clean(r.get("FailureDescriptionRaw")),
            "OperationDescriptionRaw": clean(r.get("OperationDescriptionRaw")),
            "RelatedMachineCode": clean(r.get("RelatedMachineCode")),
            "MachineName": clean(r.get("MachineName")),
            "PartName": clean(r.get("PartName")),
            "PartCode": clean(r.get("PartCode")),
            "WorkDate": clean(r.get("WorkDate")),
            "WorkedHours": clean(r.get("WorkedHours")),
            "ProcessStatus": clean(r.get("ProcessStatus")),
            "RepairDeliveryOrProductionStartDate": clean(r.get("RepairDeliveryOrProductionStartDate")),
            "MoldDeliveryToProductionDate": clean(r.get("MoldDeliveryToProductionDate")),
            "ApprovalFormStatus": clean(r.get("ApprovalFormStatus")),
            "ReviewReason": "Repair mold record with blank MoldCode; automatic MoldCode assignment prohibited",
            "MoldCodeReviewStatus": "OPEN",
            "AssignedMoldCode": "",
            "ReviewerNote": "",
        })

    write_csv(OUTPUT / "missing_mold_code_queue.csv", output, fields)

    by_sheet = Counter(r["SourceSheet"] for r in output)
    by_request = Counter("HAS_REQUEST" if r["RequestLetterNo"] else "NO_REQUEST" for r in output)

    summary = {
        "version": "missing-mold-code-review-v1",
        "source": str(INPUT.relative_to(ROOT)).replace("\\", "/"),
        "generated_at_utc": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "record_count": len(output),
        "status": "REVIEW ONLY",
        "rule": "AssetType=قالب AND WorkType contains تعمیر AND MoldCodeNorm is blank",
        "no_auto_inference": True,
        "breakdown": {
            "by_source_sheet": dict(sorted(by_sheet.items())),
            "request_letter_presence": dict(sorted(by_request.items())),
        },
    }

    (OUTPUT / "missing_mold_code_queue_index.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
