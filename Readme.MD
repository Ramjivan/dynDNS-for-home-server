## About

> detect change in IP and update domain entry managed by AWS lightsail

## how to use?

- in ~~config.json~~ put domain and subdomain
- attach iam policy to aws user
- make sure AWS credentials files is accessiable

* check DEFINNE section on ~~auto_update_domain_entry_lightsail.py~~

  > schedule script with cron

## Possible problem

- if server does not connect to internet for long time there could be multiple instances of script invoked by CRON stuck in a infinite loop to grab IP, which can result in unexpected things.
