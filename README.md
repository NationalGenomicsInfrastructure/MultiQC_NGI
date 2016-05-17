# [<img src="https://raw.githubusercontent.com/ewels/MultiQC/master/multiqc/templates/default/assets/img/MultiQC_logo.png" width="250" title="MultiQC">](https://github.com/ewels/MultiQC) [<img src="multiqc_ngi/templates/ngi/assets/img/NGI-final-small.png" width="250" title="MultiQC">](http://www.scilifelab.se/platforms/ngi/)

**MultiQC_NGI is a plugin for MultiQC, providing additional tools which are
specific to the National Genomics Infrastructure at the Science for Life
Laboratory in Stockholm, Sweden.**

[![Build Status](https://travis-ci.org/ewels/MultiQC_NGI.svg?branch=master)](https://travis-ci.org/ewels/MultiQC_NGI)

For more information about NGI, see http://www.scilifelab.se/platforms/ngi/

For more information about MultiQC, see http://multiqc.info

## Contents
This plugin provides two extra templates - `ngi` and `genstat`. `ngi` is a
stand-alone template, much like the default MultiQC template but with additional
branding. `genstat` produces a template suitable for `tornado`, allowing reports
to be directly integrated into our internal sample tracking website,
[Genomics Status](https://github.com/SciLifeLab/genomics-status).

## Installation
To run this tool, you must have MultiQC installed. You can install both
MultiQC and this package with the following command:

```
pip install multiqc git+ssh://git@github.com:ewels/MultiQC_NGI.git
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

## Configuration
The MultiQC_NGI plugin has some configuration options which you can add to the main
MultiQC config files (`inst_dir/multiqc_config.yaml`, `~/.multiqc_config.yaml` and `./multiqc_config.yaml`).
They are (with default values):
```yaml
disable_ngi: False          # Disable the MultiQC_NGI hooks
push_statusdb: False        # Enable pushing to StatusDB by default.
```

## Development
If you're developing this code, you'll want to clone it locally and install
it manually instead of using `pip`:

```
git clone git@github.com:ewels/MultiQC_NGI.git
cd MultiQC_NGI
python setup.py develop
```

### Changelog
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
