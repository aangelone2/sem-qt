# sem
`sem` (Simple Expense Manager) is a basic utility for the
management of domestic expenses.

Current features allow:

- Multiple-user, secure management via `SQLite` databases
  password-encrypted via the
  [SQLCipher][https://www.zetetic.net/sqlcipher/] library
- Manual addition of single expenses or bulk importing from CSV
  files
- Reviewing and summarizing of expenses by date and type
- Expense deletion via graphical interface
- Exporting and backup of user databases to CSV files



## Imported libraries

The following external libraries are imported in `sem`, and
required for its operation:

- PyQt6 (GUI toolkit, [link][https://www.riverbankcomputing.com/software/pyqt/])
- SQLCipher (encrypted database management, [link][https://www.zetetic.net/sqlcipher/])
- Pandas (data manipulation and transfer, [link][https://pandas.pydata.org/])



## Dependencies and Setup

`sem` requires the following packages to be installed in the
Python 3 environment:

- `PyQt6`
- `pysqlcipher3`
- `pandas`

The main executable is launched as

```
  > python sem.py
```



## Security

To guarantee secure access to multiple users without the need
for an administrator-level user to set up database(s) and
permissions, `sem` distributes the data of different users into
separate databases, each password-encrypted at the moment of
its creation. This solution allows the maximum level of
protection to each users' data, as well as ease of backup and
data transfer while maintaining encryption.

Furthermore, each passwords is directly forwarded to its
databases, encrypted via `SQLCipher`, at the moment of login.
As such, each database stores its own password, eliminating the
need for password storage at the level of the program itself.
The `SQLCipher` library, with the (default) settings employed
in `sem`, employs strong encryption and key hashing
algorithms (more information
[here][https://www.zetetic.net/sqlcipher/design/]). These,
together with industry-standard practices (e.g., large number
of hash iterations, password salting) allow safe storage of
user credentials and data.

It is important to note that, due to these design choices,
`sem` *cannot recover forgotten passwords*.



## To Do

- [ ] Streamline packaging
- [ ] Add documentation (underway)
