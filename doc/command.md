# Command

## To Manager

### envelop

```json
{
    "target": "manager",
    "client": "null",
    "commands": [
        // Details here
    ]
}
```

### command detail

- operate client

The `action` support `start` `stop` `restart`

```json
{
    "type": "operate_client",
    "target": "wxext",
    "action": "start"
}
```