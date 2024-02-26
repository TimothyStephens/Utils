#!/usr/bin/env bash

if [ $# -eq 0 ]
  then
    echo -e "\nNo arguments supplied:\n\n$0 URL {URL URL ..]\n"
    exit 1
fi

RED='\e[1;91m%s\e[0m\n'
GREEN='\e[1;92m%s\e[0m\n'

for URL in "$@";
do
	ping -c 1 -q "$URL" > /dev/null 2>&1
	if [ "$?" -eq 0 ]; then
		#printf "$GREEN" "[ CONNECTION AVAILABLE ]    ${URL}"
		printf "$GREEN" "${URL}"
	else
		#printf "$RED" "[  HOST DISCONNECTED   ]    ${URL}"
		printf "$RED" "${URL}"
	fi
done

