
if [ $# -ne 1 ]
  then
    echo -e "No arguments supplied:\n\n$0 username\n"
    exit 1
fi
username=$1

su - -c "
echo -e 'Adding user $username\n'

adduser $username
adduser $username DBlab
usermod -g DBlab $username

mkdir /scratch/$username
chown $username /scratch/$username
chmod o-rwx /scratch/$username /home/$username

echo -e '\nFinish adding $username'
"
