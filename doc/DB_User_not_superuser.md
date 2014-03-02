If the database user does not have superuser rights, it will be denied the usage of language plpython3u. The following commands might not be the safiest, use with care!

```sh
UPDATE pg_language SET lanpltrusted = true WHERE lanname LIKE 'plpython3u';
grant usage on language plpython3u to USER;
```
