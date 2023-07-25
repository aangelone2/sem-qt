# sem
`sem` (Simple Expense Manager) is a simple Python utility for
the management of domestic expenses.

A streamlined Qt graphical interface allows straightforward
management of multi-user data stored in SQLite databases and
transfered via Pandas dataframes.



## Current capabilities

- Expense data management via SQLite database
- Manual addition of single expenses or bulk importing from CSV
  files
- Reviewing and summarizing of expenses by date and type
- Expense deletion via graphical interface
- Exporting and backup of user databases to CSV files



## Imported libraries

The following external libraries are imported in `sem`, and
required for its operation:

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
  (GUI toolkit)
- [Pandas](https://pandas.pydata.org/) (data manipulation and
  transfer)



## Dependencies and Setup

`sem` requires the following packages to be installed in the
Python 3 environment:

- `PyQt6`
- `pandas`

The main executable is launched as

```
  > python sem.py
```



## To Do

- [ ] Add flexibility for date format to CSV importing
- [ ] Add search functionality
- [ ] Fully implement MVC design pattern
- [ ] Clear custom appearance
- [ ] Allow to modify records ?

- [ ] Add documentation
- [ ] Streamline packaging
