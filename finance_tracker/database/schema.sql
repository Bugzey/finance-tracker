/*
	Create a blank database file - tables, views, constraints
*/

create table test_table
(
	test_col int 
	, test_col2 varchar
	, CONSTRAINT pk_test_table PRIMARY KEY (test_col)
);
