-- drop table if exists entries;
/* block comment */
/* drop table if exists time_entry;
/* drop table if exists project;
/* drop table if exists contact;
*/
drop table if exists time_entry;
create table time_entry (
  id integer primary key autoincrement,
  project_id integer not null,
  start text not null,
  stop text,
  delta real,
  invoice_line_id integer,
  billed integer
);

create table project (
  id integer primary key autoincrement,
  name text not null,
  contact_id text not null,
  notes text
);

create table contact (
  id integer primary key autoincrement,
  name text,
  email text,
  notes text
);

create table invoice (
  id integer primary key autoincrement,
  invoice_date text,
  contact_id text,
  recipient_note text,
  subtotal text,
  total integer,
  invoice_history_id text,
  paid text
);

create table invoice_line (
  id integer primary key autoincrement,
  invoice_id integer,
  description text,
  quantity text,
  unit_price text,
  amount text
);