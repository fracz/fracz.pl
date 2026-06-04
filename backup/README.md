# MariaDB Backup Container

## Konfiguracja

```bash
cp config.yml.example config.yml
```

## rclone

Na hoscie:

```bash
rclone config --config ./rclone/rclone.conf
chmod 600 ./rclone.conf
```

## Budowanie

```bash
docker compose build
```

## Test

```bash
docker compose run --rm mariadb-backup
```

## Cron

```cron
30 2 * * * cd /opt/mariadb-backups && docker compose run --rm mariadb-backup >> /var/log/mariadb-backups.log 2>&1
```

## SQL user

```sql
CREATE USER 'backup_user'@'%'
IDENTIFIED BY 'XXX';

GRANT SELECT,
      SHOW VIEW,
      TRIGGER,
      EVENT,
      EXECUTE
ON *.* TO 'backup_user'@'%';

FLUSH PRIVILEGES;
```
