#!/usr/bin/env bash
ininit="/init.src"
outinit="/init.sql"
dd if=/dev/urandom count=1 2> /dev/null | uuencode -m - | sed -ne 2p | tr -d '@' | cut -c-12 > /db_pass
chown postgres /db_pass
chmod 660 /db_pass
rpg_admin=$(dd if=/dev/urandom count=1 2> /dev/null | uuencode -m - | sed -ne 2p |tr -d '@' | cut -c-12)
app=$(dd if=/dev/urandom count=1 2> /dev/null | uuencode -m - | sed -ne 2p |tr -d '@' | cut -c-12)
echo "*************************************************"
echo "** Save these db user passwords                **"
echo "*************************************************"
echo "rpg_admin = $rpg_admin"
echo "app       = $app"
sed --expression "s@\@\@rpg_admin\@\@@$rpg_admin@g; s@\@\@app\@\@@$app@g" $ininit  > $outinit
cp $outinit /docker-entrypoint-initdb.d/
