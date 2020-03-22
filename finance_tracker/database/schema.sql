/*
	Create a blank database file - tables, views, constraints
*/

/*	Category table, indices and triggers	*/
create table category
(
	category_id integer primary key autoincrement
	, historic_category_name text not null collate nocase
	, current_category_name text not null collate nocase
	, created_time text default current_timestamp not null
	, valid_to_time text default null
	, constraint unique_category_name unique (current_category_name, historic_category_name)
);

/* Subcategory table, indices and triggers */
create table subcategory
(
	subcategory_id integer primary key autoincrement
	, category_id integer not null
	, current_subcategory_name text not null collate nocase
	, historic_subcategory_name text not null collate nocase
	, created_time text default current_timestamp not null
	, valid_to_time text default null
	, constraint unique_subcategory_name unique (current_subcategory_name, historic_subcategory_name)
	, constraint fk_subcategory_category foreign key (category_id)
	references category (category_id)
);


/*	ledger table, indices and triggers */
create table ledger
(
	ledger_id integer primary key autoincrement
	, category_id integer not null
	, subcategory_id integer not null
	, created_time text default current_timestamp not null
	, accounting_date text not null
	, transaction_time text not null
	, ledger_amount real not null
	, constraint fk_ledger_category foreign key (category_id)
	references category (category_id)
	, constraint fk_ledger_subcategory foreign key (subcategory_id)
	references subcategory (subcategory_id)
);

create index idx_ledger_categories on ledger (category_id, subcategory_id);

create index idx_ledger_dates on ledger (accounting_date, transaction_time, created_time);

