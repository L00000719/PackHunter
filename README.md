# PackHunter: Recovering Missing Packages for C/C++ Projects

## Dataset
We choose the projects with missing package errors that are investigated in our empirical study (https://github.com/PackHunter-dataset/Empircal_Study).

## PackHunter
PackHunter is a tool that automates the recovery of missing packages in C/C++ projects.

### Dependencies
PackHunter analyze the source code by using [*srcML*](https://www.srcml.org/)

### Usage
run command:
```
cd packhunter
python3 packhunter.py --path=$poroject_directory
```

### Test
```tests``` directory contains several projects used to test PackHunter.