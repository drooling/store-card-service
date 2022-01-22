# Store Card Service

## Install

```
git clone https://github.com/9sv/store-card-service/
cd store-card-service

pip install git+https://github.com/Pycord-Development/pycord
pip install python-dotenv
pip install pymysql
pip install selenium
```

## Setup

### YOU WILL NEED A MYSQL SERVER !!
#### You can host one on your own or use [XAMMP](https://www.apachefriends.org/download.html)

Once you have access to a MySQL server you need to create the table and database

```sql
CREATE DATABASE IF NOT EXISTS `tragedy`;
USE `tragedy`;

CREATE TABLE `amazon` (
    `user` BIGINT(18) NOT NULL UNIQUE,
    `premium` BOOLEAN NOT NULL,
    `plan_expiration` DATETIME NOT NULL
);
```

After this you can create the .env file with the following variables:

```
mysqlServer=#Address of MySQL server or localhost
mysqlPassword=#Password of root user
token=#Discord bot token
```

And finally run the bot with

```
python src/init.py
```
