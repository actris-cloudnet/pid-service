# PID service
![](https://github.com/actris-cloudnet/pid-service/workflows/Test%20and%20lint/badge.svg)

A gateway service for minting persistent identifiers with a handle.net server.

## Installation

As a requirement, docker must be installed. Once docker is running, you may
issue:

    docker build -t pid-service --target prod .

## Configuration

The service is configured with environment variables, see `.env` for more
information. Note that you will need a private key and certificate to use the
handle.net service. Contact your handle.net service provider for these.

## Running the server

    docker run -p 5800:5800 pid-service

## Minting PIDs

By default, the server listens to http://localhost:5800. To mint a PID, send a
`POST` request to http://localhost:5800/pid/, with a JSON body containing the
fields:

- `type`: either *file*, *collection* or *instrument*.
- `uuid`: UUID of the resource for which the PID is generated.
- `url`: landing page where the PID should resolve to
- `data`: extra data to store in the PID, an array of objects with following properties:
    - `type`: data type, usually another PID.
    - `value`: value as a string.

Example:

    $ curl -d '{"type":"file","uuid":"42092c00-161d-4ca2-a29d-628cf8e960f6","url":"http://localhost:8000/file/42092c00-161d-4ca2-a29d-628cf8e960f6"}' \
           -H 'Content-Type: application/json' \
           http://localhost:5800/pid/
    {"pid":"https://hdl.handle.net/21.T12995/1.42092c00161d4ca2"}

Navigating to https://hdl.handle.net/21.T12995/1.42092c00161d4ca2 will now
redirect to http://localhost:8080/file/42092c00-161d-4ca2-a29d-628cf8e960f6
(may take couple of seconds to work).

## License

MIT
