create role rpg_admin with login superuser password 'cCl52yUQ4pTRBp0';
create role app with login password '1wm4iMSfX9hzehT';
alter database rpg owner to rpg_admin;
create schema dnd_5e;
grant usage on schema dnd_5e to rpg_admin;
grant usage on schema dnd_5e to app;
alter database rpg set search_path = dnd_5e, "$user", public;

grant select on all sequences in schema dnd_5e to app;
grant select on all tables in schema dnd_5e to app;
grant usage on all sequences in schema dnd_5e to app;
ALTER DEFAULT PRIVILEGES FOR USER rpg_admin IN SCHEMA dnd_5e GRANT EXECUTE ON FUNCTIONS TO app;
GRANT SELECT ON ALL TABLES IN SCHEMA dnd_5e TO app;
ALTER DEFAULT PRIVILEGES FOR USER rpg_admin IN SCHEMA dnd_5e GRANT SELECT ON TABLES TO app;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA dnd_5e TO app;
ALTER DEFAULT PRIVILEGES FOR USER rpg_admin IN SCHEMA dnd_5e GRANT SELECT ON SEQUENCES TO app;

