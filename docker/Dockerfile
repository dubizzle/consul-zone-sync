FROM dubizzledotcom/base-image-python3.4:latest

ENV APP_NAME consul-zone-sync

ENV REPO_DIR $DBZ_USER_DIR/$APP_NAME

RUN mkdir $REPO_DIR


# Copy the archive and grant permissions
ADD docker/archive.tar.gz $REPO_DIR
ONBUILD RUN chown -R $DBZ_USER:$DBZ_GROUP $REPO_DIR

RUN DEBIAN_FRONTEND=noninteractive set -e \
    apt-get update -y \
    apt-get install -y python-dev

RUN su $DBZ_USER -l -c "pip install virtualenv" \
    su $DBZ_USER -l -c "virtualenv venv && . venv/bin/activate"; \
    su $DBZ_USER -l -c "$VENV_DIR/bin/pip install -r $REPO_DIR/requirements/requirements.txt"
