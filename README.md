# sem
`sem` (Simple Expense Manager) is a simple Python utility for
the management of domestic expenses.

A streamlined Qt graphical interface allows straightforward
management of multi-user data stored in encrypted SQLite
databases and transfered via Pandas dataframes.



## Current capabilities

- Multiple-user, secure management via SQLite databases
  password-encrypted using the
  [SQLCipher](https://www.zetetic.net/sqlcipher/) library
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
- [SQLCipher](https://www.zetetic.net/sqlcipher/) (encrypted
  database management)
- [Pandas](https://pandas.pydata.org/) (data manipulation and
  transfer)



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

`sem` has been designed to allow multiple users to store their
data side-by-side on the same machine, requiring protection of
each user's data from other users' direct access. At the same
time, the design philosophy of `sem` is to aim for the maximum
possible data security: as such, the designation of
administrator-level users, with access and permission
granting/revoking rights to other users' data, is actively
avoided.

To comply with both these design principles, `sem` distributes
the data of different users into separate databases, each
password-encrypted at the moment of its creation. This solution
allows the maximum level of protection to each user's data, as
well as ease of backup and data transfer while maintaining
encryption.

Furthermore, each password is directly forwarded to its
database at the moment of login. As such, each database stores
its own password, eliminating the need for password storage at
the level of the program itself. The *SQLCipher* library, with
the (default) settings employed in `sem`, employs strong
encryption and key hashing algorithms (more information
[here](https://www.zetetic.net/sqlcipher/design/)). These,
together with industry-standard practices (e.g., large number
of hash iterations, password salting) allow safe storage of
user credentials and data.

It is important to note that, due to these design choices,
`sem` *cannot recover forgotten passwords*.



## To Do

- [ ] Add documentation (underway)
- [ ] Streamline packaging
