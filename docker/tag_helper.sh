#!/usr/bin/env bash
# Generate a deterministic docker tag
# based on the git tag and the short hash

GIT_SHORT_HASH=$(git log -1 --pretty=format:%h)

git describe --exact-match > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "$(git describe --exact-match --abbrev=0)-$GIT_SHORT_HASH"
else
    echo "$GIT_SHORT_HASH"
fi
