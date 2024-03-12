create schema chatbot;
use chatbot;

-- laptop table
create table laptop(
	lapNO int not null,
	lapID varchar(100) not null,
	lapPrice int not null,
	lapCPU varchar(100),
	lapGPU varchar(100),
	lapRAM varchar(100),
	lapDisk varchar(100),
	lapWarranty varchar(30),
	lapImage varchar(100),
    lapBrand varchar(20),
	primary key(lapNO));
SHOW COLUMNS FROM laptop;

-- userID
create table users(
	userID varchar(100) not null,
	primary key(userID));
SHOW COLUMNS FROM users;

-- disprice
create table discount(
	disNO int not null,
	disPrice int not null,
	disStart date,
	disEnd date,
	constraint PK primary key(disNO,disPrice),
	foreign key(disNO) references laptop(lapNO));
SHOW COLUMNS FROM discount;

-- attention
create table attention(
	att_NO int not null,
	att_userID varchar(100) not null,
	constraint PK primary key(att_NO,att_userID),
	foreign key(att_NO) references laptop(lapNO),
	foreign key(att_userID) references users(userID));
SHOW COLUMNS FROM attention;

-- show all
select * from laptop;
select * from users;
select * from discount;
select * from attention; 

-- alter constrain change 
alter table attention drop foreign key attention_ibfk_1;
alter table attention drop foreign key attention_ibfk_2;
-- modify  
alter table users modify userID varchar(100);
alter table attention modify att_userID varchar(100);
-- add constrain 
alter table attention add constraint userFK foreign key(att_userID) references users(userID);
alter table attention add constraint lapFK foreign key(att_NO) references laptop(lapNO);
-- alter constrain change 
alter table attention drop foreign key userFK;
alter table attention drop foreign key lapFK;

-- insert 
insert into discount select lapNO,(lapprice - 5000),"2019-12-01","2020-1-26" from laptop where lapprice < 30000; 

-- !!!!!!!!!!!!!!!!! delete all table data !!!!!!!!!!!!!!!!!!!
-- truncate table users; -- 
-- truncate table attention; -- 

-- !!!!!!!!!!!!!!!!!!!!!!! delete database !!!!!!!!!!!!!!!!!!!!!!!!
-- drop database pratices; -- 