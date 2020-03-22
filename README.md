#	Finance tracker
Personal monthly finance tracker inspired by a free well-structured, but hard to summarise spreadsheet template.

##	Features
- Transactional backend with a user-friendly balance mode
- Import from / export to a free compatible spreadsheet template
- CLI input
- Interactive TUI input
- SQLite backend
- Visual reporting

##	Features
- [X] Project structure
- [ ] Main function with docopt command line handling
- [ ] Set up, read from and write to SQLite file
- [ ] Import / export functions (export need not have functional spreadsheet formulas at this time)
- [ ] Config file with optional database path
- [ ] Transactional backend with an optional balance mode that creates phantom transactions
- [ ] Prebuit HTML / PDF reports
- [ ] Transaction accounts - specify entities such as shops or institutions
- [ ] Time series forecasting
- [ ] Report builder - select from preset measures and graphs

##	Tasks
SQLite

- create category, subcategory, transaction tables
- procedures to add, modify or cancel a transaction
- procedures to add, modify or cancel a balance item via fictional transactions
- assure transactions are never deleted via triggers
- allow categories and subcategories to be modified using current and historic names
- disallow deletion of categories and subcategories via triggers
