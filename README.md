# [<img src="https://raw.githubusercontent.com/ewels/MultiQC/master/multiqc/templates/default/assets/img/MultiQC_logo.png" width="250" title="MultiQC">](https://github.com/ewels/MultiQC) [<img src="multiqc_ngi/templates/ngi/assets/img/NGI-final-small.png" width="250" title="MultiQC">](http://www.scilifelab.se/platforms/ngi/)

**MultiQC_NGI is a plugin for MultiQC, providing additional tools which are
specific to the National Genomics Infrastructure at the Science for Life
Laboratory in Stockholm, Sweden.**

[![Build Status](https://travis-ci.org/ewels/MultiQC_NGI.svg?branch=master)](https://travis-ci.org/ewels/MultiQC_NGI)

For more information about NGI, see http://www.scilifelab.se/platforms/ngi/

For more information about MultiQC, see http://multiqc.info

## Description
### Templates
This plugin provides two extra templates - `ngi` and `genstat`. `ngi` is a
stand-alone template, much like the default MultiQC template but with additional
branding. `genstat` produces a template suitable for `tornado`, allowing reports
to be directly integrated into our internal sample tracking website,
[Genomics Status](https://github.com/SciLifeLab/genomics-status). Both are able
to print data specific to this plugin (see below).

### Modules
#### ngi_rnaseq
This module reads data files produced by our [RNA pipeline](https://github.com/SciLifeLab/NGI-RNAseq)
in a custom R script (`process sample_correlation`). It plots a heatmap of sample
similarity distances and an MDS plot.

#### featureCounts_biotype
This module picks up summary statistics from featureCounts about the overlap
counts of different gene biotypes (including rRNA). These files are generated
by our [RNA pipeline](https://github.com/SciLifeLab/NGI-RNAseq).

### Pulling from StatusDB
This plugin connects MultiQC to our internal sample tracking database,
[statusdb](https://github.com/SciLifeLab/statusdb).

Firstly, it retrieves information from statusdb to put into the report:

1. Looks at sample names in the General Stats table for something that looks like
   an NGI project number (_eg._ `P1234`). Bails if none or more than one are found.
2. Connects to statusdb and searches projects for this. Bails if not found.
3. Retrieves project level information to be printed at the top of the report
   (`ngi` template only).
4. Goes through general stats table looking for sample identifiers (`P1234_001`)
5. Searches statusdb for each of these and tries to pull interesting fields if possible:
  * Initial QC RIN score
  * Amount of sample taken for library prep
  * Concentration of prepared library
    * _NB:_ These are skipped if multiple library preps are found.

### Pushing to StatusDB
As well as retrieving data, MultiQC_NGI can push data back to statusdb. This is helpful
as it allows us to do cross-project meta analyses, tracking the bioinformatics
statistics across everything we run.

1. If pulling data has worked, we already know the project and sample IDs
2. Either pushes or updates records in the `analysis` database, using data saved
   by all MultiQC modules available in `report.saved_raw_data`

This is dependent on either `--push` or `config.push_statusdb` being `true`, so
doesn't run by default.

### Saving reports to a server
Once the MultiQC report is complete and has been saved to disk, MultiQC_NGI can
transfer the report to a remote server by using the `scp` command. We use this
to store reports in a central backed up location. Once there, we are able to
integrate them into our sample tracking website.

## Installation
To run this tool, you must have MultiQC installed. You can install both
MultiQC and this package with the following command:

```
pip install multiqc git+https://github.com/ewels/MultiQC_NGI.git
```

## Usage
To use the new templates, specify their name with the `-t` flag in MultiQC:

```
multiqc -t ngi .
```

There are two new command line flags introduced by the plugin:

* `--project`
  * Specify a Project ID number, instead of automatically searching for one in sample names
* `--push/--no-push`
  * Override the config file default for whether to push results to StatusDB.
* `--test-db`
  * Specify a JSON file to use for testing instead of StatusDB. For example,
  [this one](https://github.com/ewels/MultiQC_TestData/blob/master/data/ngi/ngi_db_data.json)
* `--disable-ngi`
  * Disable the MultiQC_NGI plugin for this run

## Configuration
The MultiQC_NGI plugin has some configuration options which you can add to the main
MultiQC config files (`inst_dir/multiqc_config.yaml`, `~/.multiqc_config.yaml` and 
`./multiqc_config.yaml`).

The available config options with some suggested values can be found in
[`multiqc_ngi_config.yaml`](multiqc_ngi_config.yaml)

## Code structure
The new modules and templates are held in `multiqc_ngi/`. The code that interacts
with statusdb is in `multiqc_ngi/multiqc_ngi.py` and the new command line options
are defined in `multiqc_ngi/cli.py`.

The way that all of these plugin functions work is defined in `setup.py`, in the
`entry_points` section.

## Development
If you're developing this code, you'll want to clone it locally and install
it manually instead of using `pip`:

```
git clone git@github.com:ewels/MultiQC_NGI.git
cd MultiQC_NGI
python setup.py develop
```

### Changelog
### v0.3dev
* New featureCounts biotype plot / rRNA in General Stats table
* Reports now able to send to a remote server
* Metadata for samples still retrieved when multiple project IDs found


#### [v0.2](https://github.com/ewels/MultiQC_NGI/releases/tag/v0.2) - 2016-07-05
* Ability to test using a static JSON file instead of statusdb
* Compatability with new MultiQC features (eg. ENV vars)
* WGS-specific cleaning of reports (remove FastQC and FastQ Screen from general stats table)
* Got the RNA-seq MDS plot to work
* Made code more tolerant of missing statusdb values
* Lots of minor bug fixes

#### [v0.1](https://github.com/ewels/MultiQC_NGI/releases/tag/v0.1) - 2016-05-17
Initial release.
* Module for NextFlow RNA-Seq BP pipeline
  * Heatmap of sample correlations
  * MDS plot
* Automatically find Project ID from report, or specify with `--project`
* Pull project and sample metadata from StatusDB
  * `NGI` template shows project metadata at head of report, plus NGI logo
  * General Stats columns added for `RIN`, `Library Concentration` and `Library Amount Taken`
* Push MultiQC report data to StatusDB
  * `config.push_statusdb` or `--push`/`--no-push`
* Ability to disable StatusDB interactions with `config.disable_ngi`
* `genstat` barebones template started, but not complete.
