#!/usr/bin/env bash

opt=$1

if [ "$opt" = "TEST" ]; then
    echo "Publishing to TEST PyPi"
    if [ -d ./dist ]; then
      echo Publishing...
      twine upload --repository-url https://test.pypi.org/legacy/ dist/*
      echo install with:
      echo   pip install libcst inflect
      echo   pip install --index-url https://test.pypi.org/simple/ eve-utils
    else
      echo NOT PUBLISHING
    fi
elif [ "$opt" = "LOCAL" ]; then
    echo "Publishing to LOCAL"
else
    echo "Publishing to PROD"
fi

