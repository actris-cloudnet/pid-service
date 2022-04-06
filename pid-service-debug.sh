#!/bin/bash

PID_SERVER=https://epic-pid.storage.surfsara.nl:8004/api/handles

#### modify following lines. assuming 310:<PREFIX>/USER01 for authentication
INDEX=310
PREFIX=21.12132
MY_PATH=./config/private/
PRIVKEY=${MY_PATH}/${PREFIX}_USER01_${INDEX}_privkey.pem
CERTIFICATE=${MY_PATH}/${PREFIX}_USER01_${INDEX}_certificate_only.pem
#### end modify lines
SUFFIX=`uuidgen`

DATA=`cat <<EOF
{"values":[\
{"index":1,"type":"URL","data":{"format":"string","value":"https://cloudnet.fmi.fi"}},\
{"index":100,"type":"HS_ADMIN","data":{"format":"admin",\
"value":{"handle":"0.NA/$PREFIX","index":200,"permissions":"011111110011"}}}\
]}
EOF
`

curl -i -v -k --key $PRIVKEY --cert $CERTIFICATE \
    -H "Content-Type: application/json" \
    -H 'Authorization: Handle clientCert="true"' \
    -X PUT --data $DATA \
    $PID_SERVER/$PREFIX/$SUFFIX
