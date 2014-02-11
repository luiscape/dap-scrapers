#!/bin/bash
source ~/libs
STATUS="ok"
MSG=" failed"
rm ocha.db
for PYFILE in m49.py acled.py echo.py emdat.py esa.py faosec.py faostat.py hdr-disaster.py hdrstats.py mdg.py unicef.py unterm.py weather.py wikipedia.py worldbank-lendinggroups.py worldbank.py worldaerodata.py reliefweb-api.py hdr_new.py
do
    echo $PYFILE
    python $PYFILE > log1/$PYFILE.txt 2> log2/$PYFILE.txt
    EXIT=$?
    echo EXIT: $EXIT
    if [ $EXIT != "0" ]
        then
            STATUS="error"
            MSG=$PYFILE:$MSG
    fi
done

# todo: upload to CKAN

if [ $STATUS == "ok" ]
    then
        MSG=
fi
curl https://scraperwiki.com/api/status --data "type=$STATUS&message=$MSG"


# todo: reliefweb-api
# tood: sanity
