# Week 4 — Postgres and RDS
I learned a lot about RDS - PSQL database this week. I connected to psql via CLI. Created tables and inserted data into the table by running some of the bash scripts. 

Created the same connection in both the environments Dev and Prod. Then, I installed the Postgres container from my `docker-compose.yml` file.

```
 db:
    image: postgres:13-alpine
    restart: always
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=<enteryourpassword>
    ports:
      - '5432:5432'
    volumes: 
      - db:/var/lib/postgresql/data

volumes:
  db:
    driver: local
```

I connect to psql in my terminal by running `psql -U postgres -localhost` and it asks me for the password then I am connected to Postgres. I had also set the env vars in Gitpod for the `Connection URL` and `Prod Connection URL`. 

As mentioned above we have certain bash scripts to create, drop and insert data into tables. 

### `./bin/db-connect` to connect to the psql 
```
#! /usr/bin/bash
if [ "$1" = "prod" ]; then
  echo "Running in production mode"
  URL=$PROD_CONNECTION_URL
else
  URL=$CONNECTION_URL
fi

psql $URL
```

### `./bin/db-create` to create a new table 'cruddur'

```
#!  /usr/bin/bash

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-create"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

NO_DB_CONNECTION_URL=$(sed 's/\/cruddur//g' <<< "$CONNECTION_URL")
psql $NO_DB_CONNECTION_URL -c "create database cruddur;"
```

### `./bin/db-drop` to drop, if the table is existing

```
#!  /usr/bin/bash

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-drop"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

NO_DB_CONNECTION_URL=$(sed 's/\/cruddur//g' <<< "$CONNECTION_URL")
psql $NO_DB_CONNECTION_URL -c "drop database cruddur;"
```

### `./bin/db-schema-load` to load the schema, giving the contents and setting its' constraints.

```
#! /usr/bin/bash

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-schema-load"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

schema_path="$(realpath .)/db/schema.sql"
echo $schema_path

if [ "$1" = "prod" ]; then
  echo "Running in production mode"
  URL=$PROD_CONNECTION_URL
else
  URL=$CONNECTION_URL
fi

psql $URL cruddur < $schema_path
```

### `./bin/db-seed` to insert the data into the schema loaded

```
#! /usr/bin/bash

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-seed"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

seed_path="$(realpath .)/db/seed.sql"
echo $seed_path

if [ "$1" = "prod" ]; then
  echo "Running in production mode"
  URL=$PROD_CONNECTION_URL
else
  URL=$CONNECTION_URL
fi

psql $URL cruddur < $seed_path

```

To connect to the PROD environment, you can suffix the command with PROD. `./bin/db-connect prod`

## RDS Instance
I also created a Database instance in Amazon RDS Service. Since it costs us money, I stopped it temporarily for a week and started it only when required. I took the endpoint ARN of that instance for the connection URL; security group ID and security group rules ID and added those in my `rds-update-sg-rules` shell script. Also, had the Inbound rules set as Postgres: port 5432 to Custom : (My Gitpod IP).

Provisioning of RDS (We need to wait for around 10 mins to get it activated)

```
aws rds create-db-instance \
  --db-instance-identifier cruddur-db-instance \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version  14.6 \
  --master-username root \
  --master-user-password huEE33z2Qvl383 \
  --allocated-storage 20 \
  --availability-zone ca-central-1a \
  --backup-retention-period 0 \
  --port 5432 \
  --no-multi-az \
  --db-name cruddur \
  --storage-type gp2 \
  --publicly-accessible \
  --storage-encrypted \
  --enable-performance-insights \
  --performance-insights-retention-period 7 \
  --no-deletion-protection
```

All these tasks helped us to get the IP from which we were creating the database/ inserting data. We also used `psycopg3` driver.

## AWS Lambda
**Post Confirmation Lambda**: I added some code to record the logs as I sign in to the cruddur app. Created a Lambda Function using psycopg3 lib. 

`https://pypi.org/project/psycopg2-binary/#files`

Lambda function
```
import json
import psycopg2

def lambda_handler(event, context):
    user = event['request']['userAttributes']
    try:
        conn = psycopg2.connect(
            host=(os.getenv('PG_HOSTNAME')),
            database=(os.getenv('PG_DATABASE')),
            user=(os.getenv('PG_USERNAME')),
            password=(os.getenv('PG_SECRET'))
        )
        cur = conn.cursor()
        cur.execute("INSERT INTO users (display_name, handle, cognito_user_id) VALUES(%s, %s, %s)", (user['name'], user['email'], user['sub']))
        conn.commit() 

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        
    finally:
        if conn is not None:
            cur.close()
            conn.close()
            print('Database connection closed.')

    return event
    ```
