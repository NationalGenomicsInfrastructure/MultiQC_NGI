# MultiQC_NGI

MultiQC_NGI is a plugin for MultiQC, providing additional tools which are
specific to the National Genomics Infrastructure at the Science for Life
Laboratory in Stockholm, Sweden.

For more information about NGI, see http://www.scilifelab.se/platforms/ngi/

For more information about MultiQC, see http://multiqc.info

[<img src="https://raw.githubusercontent.com/ewels/MultiQC/master/multiqc/templates/default/assets/img/MultiQC_logo.png" width="200" title="MultiQC">](https://github.com/ewels/MultiQC) [<img src="https://portal.scilifelab.se/genomics/sites/default/files/NGI-logo-white-background.png" width="200" title="MultiQC">](http://www.scilifelab.se/platforms/ngi/)

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

_(No need to clone the repo if you're just using it and not developing,
`pip` can install directly from GitHub)_

## Usage
To use the new templates, specify their name with the `-t` flag in MultiQC:

```
multiqc -t ngi .
```

## Development
If you're developing this code, you'll want to clone it locally and install
it manually instead of using `pip`:

```
git clone git@github.com:ewels/MultiQC_NGI.git --recursive
cd MultiQC_NGI
python setup.py develop
```

### Changelog
#### v0.1dev
* Initial release.