# sem
`sem` (Simple Expense Manager) is a basic utility for the
management of domestic expenses. Current features allow:

- Multiple-user, secure management via user-specific,
  password-protected `sqlite` databases
- Manual addition of single expenses or bulk importing from CSV
  files
- Reviewing and summarizing of expenses by date and type
- Expense deletion via a graphical interface
- Exporting and backup of user databases to CSV files



## Installation process

`sem` requires the following Python 3 packages to be installed
on the target system:

- `PyQt6` (GUI toolkit)
- `pysqlcipher3` (encrypted database management)
- `pandas` (data manipulation and transfer)

The main executable is launched as

```
  > python sem.py
```



## Security

*Add section here*



## To Do

- [ ] Streamline packaging
- [ ] Add documentation (underway)
