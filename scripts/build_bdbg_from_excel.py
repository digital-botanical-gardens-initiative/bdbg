#!/usr/bin/env python3
"""Build bdbg taxa and lookup CSV files from List_manip_check.xlsx."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import openpyxl


PROJECT_NAME = "biodiversity neuchatel botanical garden"
PROJECT_CODE = "bdbg"
SAMPLING_AREA = "Jardin botanique de Neuchatel"
OBSERVERS = [
    {
        "fullname": "Emmanuel Defossez",
        "firstname": "Emmanuel",
        "lastname": "Defossez",
        "laboratory": "Jardin botanique de Neuchatel",
        "ORCID": "",
        "iNat_username": "",
    },
    {
        "fullname": "Mazzarine Laboureau",
        "firstname": "Mazzarine",
        "lastname": "Laboureau",
        "laboratory": "Jardin botanique de Neuchatel",
        "ORCID": "",
        "iNat_username": "",
    },
]

SPECIES_LOOKUP_FIELDS = [
    "taxon_name_original",
    "Kind",
    "SortScore",
    "MatchType",
    "EditDistance",
    "ScientificName",
    "MatchedName",
    "MatchedCanonical",
    "TaxonId",
    "CurrentName",
    "Synonym",
    "DataSourceId",
    "DataSourceTitle",
    "ClassificationPath",
    "Error",
    "CHECK",
    "species",
    "famille",
    "genre",
    "espece",
    "phytochemical_diversity_full",
    "div_group",
    "Aternative",
    "comm",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def read_excel_rows(path: Path) -> list[dict[str, str]]:
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    worksheet = workbook.active
    rows = worksheet.iter_rows(values_only=True)
    headers = [clean(value) for value in next(rows)]
    result: list[dict[str, str]] = []
    for row in rows:
        record = {header: clean(value) for header, value in zip(headers, row, strict=False)}
        if not any(record.values()):
            continue
        if not record.get("taxon_name"):
            continue
        result.append(record)
    return result


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def build(excel_path: Path, output_dir: Path) -> None:
    rows = read_excel_rows(excel_path)
    qgis_dir = output_dir / "qgis/bdbg"

    taxa_rows = [
        {
            "taxon_name_original": row["taxon_name"],
            **row,
        }
        for row in rows
    ]
    write_csv(output_dir / "data/taxa_list/input_taxa_list.csv", list(taxa_rows[0]), taxa_rows)

    names_rows = [{"taxon_name_original": row["taxon_name"]} for row in rows]
    write_csv(output_dir / "data/taxa_list/input_taxa_list_names.csv", ["taxon_name_original"], names_rows)
    (output_dir / "data/taxa_list/input_taxa_list_names.txt").write_text(
        "\n".join(row["taxon_name"] for row in rows) + "\n",
        encoding="utf-8",
    )

    species_rows = []
    for row in rows:
        species_rows.append(
            {
                "taxon_name_original": row["taxon_name"],
                "Kind": "Input",
                "SortScore": "",
                "MatchType": "Unresolved",
                "EditDistance": "",
                "ScientificName": row["taxon_name"],
                "MatchedName": row["taxon_name"],
                "MatchedCanonical": row["taxon_name"],
                "TaxonId": "",
                "CurrentName": "",
                "Synonym": "",
                "DataSourceId": "",
                "DataSourceTitle": "List_manip_check.xlsx",
                "ClassificationPath": "",
                "Error": "",
                **row,
            }
        )
    write_csv(qgis_dir / "species_list.csv", SPECIES_LOOKUP_FIELDS, species_rows)

    write_csv(qgis_dir / "collector_list.csv", list(OBSERVERS[0]), OBSERVERS)


def build_species_lookup_from_resolved(resolved_path: Path, output_dir: Path) -> None:
    rows = read_csv(resolved_path)
    if not rows:
        raise ValueError(f"No rows found in {resolved_path}")

    fieldnames = list(rows[0])
    write_csv(output_dir / "qgis/bdbg/species_list.csv", fieldnames, rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--excel", type=Path, default=Path("List_manip_check.xlsx"))
    parser.add_argument(
        "--resolved",
        type=Path,
        help=(
            "Resolved taxa CSV to use for qgis/species_list.csv. "
            "Use this after running scripts/resolve_taxa.py."
        ),
    )
    parser.add_argument("--output-dir", type=Path, default=Path("."))
    args = parser.parse_args()
    if args.resolved:
        build_species_lookup_from_resolved(args.resolved, args.output_dir)
    else:
        build(args.excel, args.output_dir)


if __name__ == "__main__":
    main()
