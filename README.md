# sem
`sem` (Simple Expense Manager) is a simple Python utility for
the management of domestic expenses.

A streamlined Qt graphical interface allows straightforward
management and analysis of expense data stored in SQLite databases.



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
  (GUI toolkit and Model/View interfaces)



## Dependencies and Setup

`sem` requires the following packages to be installed in the
Python 3 environment:

- `PyQt6`

The main executable is launched as

```
  > python sem.py
```



## To Do

- [ ] Update documentation
- [ ] Robust error management

- [ ] Add filter-by-justification functionality
- [ ] Status bar
