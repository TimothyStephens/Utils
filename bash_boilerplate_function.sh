#!/usr/bin/env bash

VERSION=0.1

## Useage information
usage() {
echo -e "##
## $(basename ${0}) v${VERSION}
##

<<<DESCRIPTION>>>

Usage:
$(basename $0) XXXX > YYYY
*OR*
cat XXXX | $(basename $0) > YYYY

Options (all optional):
-v, --version              Script version (v${VERSION})
-h, --help                 This help message
--debug                    Run debug mode
" 1>&2
exit 1
}

# See https://stackoverflow.com/questions/192249/how-do-i-parse-command-line-arguments-in-bash
POSITIONAL=()
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    -h|--help)
      usage
      exit 1;
      ;;
    -v|--version)
      echo "v${VERSION}"
      exit 0;
      ;;
    --debug)
      set -x
      shift # past argument
      ;;
    *) # unknown option
      POSITIONAL+=("$1") # save it in an array for later
      shift # past argument
      ;;
  esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters

# View as columns
if [ -z "${1}" ]; then
  # No file given, use stdin
  FILE=/dev/stdin
else
  # Use file given
  FILE="${1}"
fi

cat $FILE | XXXX | YYYY

