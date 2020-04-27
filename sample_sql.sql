-- schema for new_project
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

create table user_base (
    uid text DEFAULT CONVERT(text, uuid_generate_v4()) not null,
    first_name text not null,
    surname text not null,
    phone_number text not null,
    password_hash text not null,
    confirmed_account int DEFAULT 0 not null
    primary key (uid)
);

CREATE TABLE confirmation_keys (
    phone_number text PRIMARY KEY,
    code text NOT NULL,
    expiry TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   
);



CREATE TRIGGER  delete_confirmation
    AFTER UPDATE ON user_base
    REFERENCING OLD ROW AS old_row
    FOR EACH ROW
    WHEN(old_row.confirmed_account = 0)
    DELETE from confirmation_keys
        where phone_number = old_row.phone_number

     