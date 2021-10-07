#!/usr/bin/env bash

opt=$1

if [ "$opt" = "TEST" ]; then
    echo "Publishing to TEST PyPi"
    if [ -d ./dist ]; then
      twine upload --repository-url https://test.pypi.org/legacy/ dist/*
      echo install with:
      echo   pip install libcst inflect
      echo   pip install --index-url https://test.pypi.org/simple/ eve-utils
    else
      echo NOT PUBLISHING
      # TODO: build first
    fi
elif [ "$opt" = "LOCAL" ]; then
    echo "Publishing to LOCAL"
    echo "NOT YET IMPLEMENTED"
else
    echo "Publishing to PROD"
    if [ -d ./dist ]; then
      twine upload dist/*
      echo install with:
      echo   pip install eve_utils
      echo upgrade with:
      echo   pip install --upgrade eve-utils
    fi
fi
