# Data formats




## Expenses

Expenses are defined by:

- An integer `id` field, which does not need to be specified at
  construction.
- A date `date` field, the date in which the expense has been
  performed. Dates should be submitted in the `yyyy-mm-dd`
  format.
- A character `field` type, identifying the type of the
  expense. Should be a single character (e.g., `N`, `R`).
- A numeric `amount` type, the amount of the expense.
- A string `justification` type, the motivation of the expense.
  Should be of max length 100.




## CSV format

CSV files for importing expenses should be formatted as

```
(<id>,)<date>,<type>,<amount>,<justification>
```

- The `<id>` field is optional (if missing, a new one will be
  assigned by the database).
- `<date>` should be in the `yyyy-mm-dd` format.
