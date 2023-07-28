# The East India Company's Shipping in Data

This is the repository for the MA thesis "The East India Company's Shipping in Data", submitted by Maximilian Henning for the Digital Humanities MA at the University of Groningen in 2023. The thesis digitised two books (Farrington, Anthony: A Biographical Index of East India Company Maritime Service Officers 1600-1834, London 1999; Farrington, Anthony: Catalogue of East India Company Ships’ Journals and Logs 1600-1834, London 1999) to create a new dataset and then analysed it.

The repository is structured as follows:

- Output: The finished datasets, ready for use.
- Analysis: The analysis of these datasets, mainly in Jupyter Notebooks but also in QGIS.
- Combined: Complete .txt and .csv versions of the books scanned to create the datasets, without any wrangling. Mostly for finding the sources of errors.
- Geocoding: Everything used for geocoding locations, mostly the external Geonames dataset and the manual annotations file.
- Processing: All other processing. Only change things in the \_text folder - everything else will be erased when the scripts are run.
- Scripts: The Python scripts used for wrangling the scanned files.

If you found an error that you want to fix, change it in the corresponding file in the \_text folder and rerun the scripts by running script.py. This will output a new version of the datasets, taking your change into account. Any changes made in other files, apart from the manual geocoding annotation file, will be erased by this.