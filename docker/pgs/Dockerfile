FROM library/postgres:12
RUN apt-get update && apt-get install -y sharutils
ADD scripts/set_passes.sh /
COPY sql/init.src /
RUN bash -c "chmod 700 /set_passes.sh ; /set_passes.sh"
