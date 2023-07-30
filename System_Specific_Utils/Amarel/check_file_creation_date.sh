#!/bin/bash
#######################################
# Update creation dates for old files #
#######################################
set -o pipefail
MAX_FILE_AGE=60 #days
BASE_USER_DIRECTORY=$PWD
DATE_OF_LAST_CHECK_FILE=.files_last_checked
DATE_OF_LAST_CHECK_DIR=/scratch/$USER/$DATE_OF_LAST_CHECK_FILE
MAX_DAYS_SINCE_LAST_TOUCH=14

CHECK_DATE_OF_LAST_TOUCH=0
LIST_OLD_FILES=0
LIST_FILE_AGES=0
TOUCH_OLD_FILES=0

usage() {
    echo -e "Usage: $(basename "$0") [OPTIONS...]
Options:
-m|--max_file_age           <days> max age of file before we touch them (default: $MAX_FILE_AGE) 
-M|--max_last_touch         <days> since we last touched file ages, affects --check (default: $MAX_DAYS_SINCE_LAST_TOUCH) 
-b|--base_user_directory    <base dir to search> (default is PWD: $BASE_USER_DIRECTORY) 
-l|--list                   list only files older then -m 
-L|--list_all_files         list all files and their ages 
-t|--touch                  touch old files 
-c|--check                  check how long it has been since we last touched some files (print warning if longer then --max_last_touch) 
-v|--verbose                print extra info while running 
-h|--help|-u|--usage        this help message" 1>&2
    exit 1
}


# Parse arguments
while [[ $# > 0 ]]
do
    key="$1"

    case $key in
	-m|--max_file_age)
	    MAX_FILE_AGE="$2"
	    shift
	    ;;
	-M|--max_last_touch)
	    MAX_DAYS_SINCE_LAST_TOUCH="$2"
	    shift
	    ;;
	-b|--base_user_directory)
	    BASE_USER_DIRECTORY="$2"
	    shift
	    ;;
	-l|--list)
	    LIST_OLD_FILES=1 
	    ;;
        -L|--list_all_files)
            LIST_FILE_AGES=1
            ;;
	-t|--touch)
	    TOUCH_OLD_FILES=1
	    ;;
	-c|--check)
	    CHECK_DATE_OF_LAST_TOUCH=1
	    ;;
	-v|--verbose)
	    set -x
	    ;;    
	-h|--help|-u|--usage)
	    usage
	    ;;
	*)
	    echo "Unknown option $1"
	    usage
	    ;;
    esac
    shift
done


# List how old files are (in days)
list_file_age_in_days()
{
        local BASE_USER_DIRECTORY=$1
        # Seach base dir and list each files age in days
	FILES_SEEN=0
	while IFS= read -r -d '' FILE; do
		FILES_SEEN=$((FILES_SEEN+1))
		FILE_AGE=$((($(date +%s) - $(date +%s -r "$FILE")) / 86400))
		echo "$FILE_AGE days - $FILE"
	done < <(find "$BASE_USER_DIRECTORY" -type f -print0)
	
	echo "Files seen: $FILES_SEEN"
}


# List files >$MAX_FILE_AGE days of age
list_old_files()
{
	local MAX_FILE_AGE=$(($1))
	local BASE_USER_DIRECTORY=$2
	# Seach base dir and list each files age in days
	FILES_SEEN=0
	OLD_FILES=0
        while IFS= read -r -d '' FILE; do
                FILES_SEEN=$((FILES_SEEN+1))
                FILE_AGE=$((($(date +%s) - $(date +%s -r "$FILE")) / 86400))
		
		if [ $FILE_AGE -gt $MAX_FILE_AGE ]; then
			OLD_FILES=$((OLD_FILES+1))
			echo "$FILE_AGE days - $FILE"
		fi
		
        done < <(find "$BASE_USER_DIRECTORY" -type f -print0)
	
        echo "Files seen: $FILES_SEEN"
	echo print "Old files: $OLD_FILES"
}


# Tocuh old files
touch_old_files()
{
	local MAX_FILE_AGE=$1
	local BASE_USER_DIRECTORY=$2
	local DATE_OF_LAST_CHECK_DIR=$3
	# Get files onder then $MAX_FILE_AGE
	FILES_SEEN=0
        FILES_TOUCHED=0
        while IFS= read -r -d '' FILE; do
                FILES_SEEN=$((FILES_SEEN+1))
                FILE_AGE=$((($(date +%s) - $(date +%s -r "$FILE")) / 86400))

                if [ $FILE_AGE -gt $MAX_FILE_AGE ]; then
			#echo "touching $FILE"
                        FILES_TOUCHED=$((FILES_TOUCHED+1))
                        touch -c "$FILE"
                fi

        done < <(find "$BASE_USER_DIRECTORY" -type f -print0)

        echo "Files seen: $FILES_SEEN"
	echo "Files touched: $FILES_TOUCHED"
}


#######################
## END AUTO CHECKING ##
#######################

# Update date of last touch
update_date_of_last_touch()
{
	local DATE_OF_LAST_CHECK_DIR=$1
	local BASE_USER_DIRECTORY=$2
        #update $DATE_OF_LAST_CHECK_DIR if we are searching the base dir.
        #we dont want to update this if we arent checking this dir. 
        if [ "$BASE_USER_DIRECTORY" = "/scratch/ts942" ];
        then
		date > $DATE_OF_LAST_CHECK_DIR
	fi
}

# Check when we last touched old files
check_date_of_last_touch()
{
        local DATE_OF_LAST_CHECK_DIR=$1
	local BASE_USER_DIRECTORY=$2
        local MAX_DAYS_SINCE_LAST_TOUCH=$3
	if [ ! -s $DATE_OF_LAST_CHECK_DIR ];
	then
		echo "ERROR: $DATE_OF_LAST_CHECK_DIR file does not exist or is empty. Cannot check date of last touch."
		exit 1
	fi
	
	local DATE_OF_LAST_TOUCH=`cat $DATE_OF_LAST_CHECK_DIR`
	local DAYS_SINCE_LAST_TOUCH=$((($(date +%s) - $(date --date="$DATE_OF_LAST_TOUCH" +%s)) / 86400))  
	#if [ $? -ne 0 ];
	#then
	#	echo "ERROR: Invalid date in $DATE_OF_LAST_CHECK_DIR." && exit 1
	#fi
	
	if [ $DAYS_SINCE_LAST_TOUCH -gt $MAX_DAYS_SINCE_LAST_TOUCH ];
	then
		echo "#########################"
		echo "######## WARNING ########"
		echo "#########################"
		echo "# "
		echo "# "
		echo "# $BASE_USER_DIRECTORY was checked $DAYS_SINCE_LAST_TOUCH days ago (>$MAX_DAYS_SINCE_LAST_TOUCH day max!!)"
		echo "# "
		echo "# Run 'check_file_creation_date.sh -t'"
		echo "# "
		echo "# "
		echo "#########################"
		echo "######## WARNING ########"
		echo "#########################"
	else
		echo "$BASE_USER_DIRECTORY was touched $DAYS_SINCE_LAST_TOUCH days ago (<=$MAX_DAYS_SINCE_LAST_TOUCH day max). All is good!!"
	fi
}
#########################
## START AUTO CHECKING ##
#########################



#list
if [ $LIST_FILE_AGES -eq 1 ];
then
	list_file_age_in_days $BASE_USER_DIRECTORY
fi
#list old files
if [ $LIST_OLD_FILES -eq 1 ];
then
	list_old_files $MAX_FILE_AGE $BASE_USER_DIRECTORY
fi

#touch
if [ $TOUCH_OLD_FILES -eq 1 ];
then
	touch_old_files $MAX_FILE_AGE $BASE_USER_DIRECTORY $DATE_OF_LAST_CHECK_DIR
	#update $DATE_OF_LAST_CHECK_DIR if we are searching the base dir.      ## AUTO CHECKING
	update_date_of_last_touch $DATE_OF_LAST_CHECK_DIR $BASE_USER_DIRECTORY ## AUTO CHECKING
fi
#check
if [ $CHECK_DATE_OF_LAST_TOUCH -eq 1 ];
then
	check_date_of_last_touch $DATE_OF_LAST_CHECK_DIR $BASE_USER_DIRECTORY $MAX_DAYS_SINCE_LAST_TOUCH
fi
