create table user(
user_id integer primary key autoincrement,
username text not null,
email text not null,
pw_hash text not null,
timezone text not null
);
create table conversation(
conversation_id integer primary key autoincrement,
user1_id integer not null,
user2_id integer not null,
title text not null,
post_day integer not null,
post_time integer not null
);
create table message(
message_id integer primary key autoincrement,
conversation_id integer not null,
sender_id integer not null,
receiver_id integer not null,
message_text text not null,
message_timestamp integer not null,
is_draft integer not null
);
