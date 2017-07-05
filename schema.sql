create table if not exists snippets (
keyword text primary key,
message text not null default ''
);

alter table snippets
add column if not exists
hidden bool default false;