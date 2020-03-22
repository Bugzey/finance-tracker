/*
	Create a blank database file - tables, views, constraints
*/

/*	Category table, indices and triggers	*/
create table category
(
	category_id int not null
	, historic_category_name varchar not null collate nocase
	, current_category_name varchar not null collate nocase
	, created_time varchar default current_timestamp not null
	, valid_to_time varchar default null
	, constraint pk_category PRIMARY KEY (category_id)
	, constraint unique_category_name unique (current_category_name, historic_category_name)
);

/* Subcategory table, indices and triggers */
create table subcategory
(
	subcategory_id int not null
	, category_id int not null
	, current_subcategory_name varchar not null collate nocase
	, historic_subcategory_name varchar not null collate nocase
	, created_time varchar default current_timestamp not null
	, valid_to_time varchar default null
	, constraint pk_subcategory PRIMARY KEY (subcategory_id)
	, constraint unique_subcategory_name unique (current_subcategory_name, historic_subcategory_name)
	, constraint fk_subcategory_category foreign key (category_id)
	references category (category_id)
);


/*	ledger table, indices and triggers */
create table ledger
(
	ledger_id int not null
	, category_id int not null
	, subcategory_id int not null
	, created_time varchar default current_timestamp not null
	, accounting_date varchar not null
	, transaction_time varchar not null
	, ledger_amount float not null
	, constraint pk_ledger primary key (ledger_id)
	, constraint fk_ledger_category foreign key (category_id)
	references category (category_id)
	, constraint fk_ledger_subcategory foreign key (subcategory_id)
	references subcategory (subcategory_id)
);

create index idx_ledger_categories on ledger (category_id, subcategory_id);

create index idx_ledger_dates on ledger (accounting_date, transaction_time, created_time);

