# biodiversity neuchatel botanical garden

Project code: `bdbg`

This repository merges the reusable taxa workflow from `jbp-data` and the
QGIS/QField field project structure from `jbp-new`, adapted for biodiversity
neuchatel botanical garden.

## Project Metadata

- Nom du projet: biodiversity neuchatel botanical garden
- Code etiquette: bdbg
- Zone d'echantillonnage: Jardin botanique de Neuchatel
- Description: echantillonnage de 20 especes plantees dans des bacs au Jardin
  botanique. Dans certains bacs, les especes sont seules, dans d'autres elles
  sont en communautes. Environ 400 echantillons sont attendus.
- Observateurs: Emmanuel Defossez et Mazzarine Laboureau

## Main Files

- QGIS/QField project directory: `qgis/bdbg/`
- QGIS/QField project: `qgis/bdbg/bdbg.qgs`
- Active observation data: `qgis/bdbg/observations.gpkg`
- Species lookup: `qgis/bdbg/species_list.gpkg`
- Collector lookup: `qgis/bdbg/collector_list.gpkg`
- Observation subject lookup: `qgis/bdbg/observation_subject.gpkg`
- Offline map rasters: `qgis/bdbg/optimized_maps/`
- Source species spreadsheet: `List_manip_check.xlsx`
- Taxa workflow input: `data/taxa_list/input_taxa_list.csv`

## QGIS / QField Notes

- The observation layer is stored in `EPSG:4326`.
- The project CRS is `EPSG:2056` (`CH1903+ / LV95`) for Switzerland.
- The old JBP Prague raster map layers were removed. Neuchatel optimized map
  GeoPackages from the QField cloud folder are kept in `qgis/bdbg/optimized_maps/`.
- QField photo naming uses the `DCIM/bdbg/` folder and the `sample_id` field.
- `taxon_name` is the list-based taxon field.
- `name_proposition` is the manual-entry taxon field.
- `no_name_on_list` is used as the manual-entry mode switch.
- `MatchedCanonical` and `TaxonId` are lookup-derived fields from
  `species_list`; `TaxonId` remains empty until taxa are resolved with
  `gnverifier`.

## Rebuild Lookups From Excel

```bash
python3 scripts/build_bdbg_from_excel.py
ogr2ogr -f GPKG qgis/bdbg/species_list.gpkg qgis/bdbg/species_list.csv -nln species_list -nlt NONE -oo EMPTY_STRING_AS_NULL=YES
ogr2ogr -f GPKG qgis/bdbg/collector_list.gpkg qgis/bdbg/collector_list.csv -nln collector_list -nlt NONE -oo EMPTY_STRING_AS_NULL=YES
```

## Resolve Taxa

The repository includes a CLI script to resolve taxa names with `gnverifier`.

Prerequisite:

- Install `gnverifier` and make sure it is available on your `PATH`.

Extract the names and refresh RO-Crate metadata without running `gnverifier`:

```bash
python3 scripts/resolve_taxa.py --skip-gnverifier --force --header taxon_name
```

Run full taxon resolution:

```bash
python3 scripts/resolve_taxa.py --force --header taxon_name --dedupe-input
python3 scripts/build_bdbg_from_excel.py --resolved data/taxa_list/input_taxa_list_resolved.csv
ogr2ogr -f GPKG qgis/bdbg/species_list.gpkg qgis/bdbg/species_list.csv -nln species_list -nlt NONE -oo EMPTY_STRING_AS_NULL=YES
```

That command reads `data/taxa_list/input_taxa_list.csv` and writes:

- `data/taxa_list/input_taxa_list_names.txt`
- `data/taxa_list/input_taxa_list_gnverifier.csv`
- `data/taxa_list/input_taxa_list_resolved.csv`
- `ro-crate-metadata.json`

The resolved CSV keeps all original columns from `List_manip_check.xlsx`
alongside the taxonomic resolution columns, so fields such as `CHECK`,
`famille`, `phytochemical_diversity_full`, `div_group`, `Aternative`, and
`comm` remain available in the final species lookup.
