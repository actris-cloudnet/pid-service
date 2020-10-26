# PID service
![](https://github.com/actris-cloudnet/pid-service/workflows/PID-service%20CI/badge.svg)

A gateway service for minting persistent identifiers with a handle.net server.

## Installation

    $ git clone git@github.com:actris-cloudnet/pid-service.git
    $ cd pid-service
    $ python3 -m venv venv
    $ source venv/bin/activate
    (venv) $ pip3 install --upgrade pip
    (venv) $ pip3 install .


## Configuration

`config/main.ini` contains the configuration for the service. Note that you will need a private key and certificate to use the handle.net service. Contact your handle.net service provider for these.

## Running the server

The server can be controlled via the `control` script at project root:
- `./control start`
- `./control stop`

## Minting PIDs

By default, the server listens to `localhost:5800`. To mint a PID, send a `POST` request to `http://localhost:5800/pid/`, with a JSON body containing the fields:
- `type`: either *uuid* or *collection*.
- `uuid`: UUID of the resource for which the PID is generated.

Example:
   
    $ curl -d '{"type":"file","uuid":"42092c00-161d-4ca2-a29d-628cf8e960f6"}' -H"content-type: application/json" http://localhost:5800/pid/
    {"pid":"https://hdl.handle.net/21.T12995/1.42092c00161d4ca2"}
    
Navigating to `https://hdl.handle.net/21.T12995/1.42092c00161d4ca2` will now redirect to `http://localhost:8080/file/42092c00-161d-4ca2-a29d-628cf8e960f6`, if using the default configuration.
