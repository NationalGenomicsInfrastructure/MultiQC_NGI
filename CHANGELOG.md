### MultiQC_NGI

#### v0.5dev
* More updates to match syntax changes in core MultiQC v1.0

#### [v0.4](https://github.com/ewels/MultiQC_NGI/releases/tag/v0.4) - 2017-03-28
* Updated code to work with new import styles in MultiQC v1.0dev
* Whitespace cleanup
* Fetch Reference Genome from statusdb
  * Print at the top of the report
  * Show just underneath the FastQ Screen plot

#### [v0.3.1](https://github.com/ewels/MultiQC_NGI/releases/tag/v0.3.1) - 2016-11-25
* Stopped DupRadar section from displaying even when there were no DupRadar reports
* Gave featureCounts biotype a unique ID so that nav links work
* Made featureCounts biotype have consistent key order in plot
* New script to run DupRadar with appropriate output files for MultiQC_NGI

#### [v0.3](https://github.com/ewels/MultiQC_NGI/releases/tag/v0.3) - 2016-09-27
* New dupRadar module
  * Takes output from dupRadar script in the [NGI-RNAseq](https://github.com/SciLifeLab/NGI-RNAseq/) pipeline
* New featureCounts biotype plot / rRNA in General Stats table
  * Takes output from the [NGI-RNAseq](https://github.com/SciLifeLab/NGI-RNAseq/) pipeline
    where featureCounts sums the counts for each biotype and plots this
* Reports now handle multiple projects
  * No header is added to the top of the report, but other fuctions (eg. sample name swapping) now works
* Added functionality to copy reports to an external server via `scp` on report completion
* New General Stats table column - NGI name
* New command line flag `--disable-ngi`

#### [v0.2.2](https://github.com/ewels/MultiQC_NGI/releases/tag/v0.2.2) - 2016-07-08
* Another bugfix release to handle even more missing information in statusdb

#### [v0.2.1](https://github.com/ewels/MultiQC_NGI/releases/tag/v0.2.1) - 2016-07-06
* Minor bugfix release to handle missing information in statusdb

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
