# Author: Do Ngoc Duc and Sashankh Chengavalli Kumar
BUILD_FILE="build_test_LM.py"
README="README.txt"
REQUIRED_FILES=2

echo -e "Initialising CS3245 script..."
echo -e "Setting up..."
mkdir evaluation
submittedFiles=0
echo -e "Set up completed!"
echo -e ""

echo -n "Enter zip file (A0123456X.zip) > "
read zipfile

echo -e "Processing zipfile..."
studentNumber="$(basename "${zipfile%.*}")"
if unzip -B $zipfile -d evaluation/$studentNumber/; then

    echo -e ""
    # Check for submisison files
    echo -e "Finding $README, $BUILD_FILE"
    path=evaluation/$studentNumber/$studentNumber
    echo -e "\t Attempting to find in $path"
    if [ ! -d $path ]
    then
        altpath=evaluation/$studentNumber
        echo -e "\t $path does not exist, re-attempting in $altpath"
        path=$altpath
    fi

    # Checking for README.txt
    if [ -f $path/$README ]
    then
        let "submittedFiles=submittedFiles+1"
        echo -e "\t\t Found $README"
    else
        echo -e "\t\t Unable to find $studentNumber's $README"
    fi

    # Checking if BUILD_file exists
    if [ -f $path/$BUILD_FILE ]
    then
        let "submittedFiles=submittedFiles+1"
        echo -e "\t\t Found $BUILD_FILE"
    else
        echo -e "\t\t Unable to find $studentNumber's $BUILD_FILE"
    fi

else
    echo -e "Please enter the correct zipfile!"
fi

echo -e "Cleaning up ..."
rm -rf evaluation
echo -e "Clean up completed!"

echo -e ""
echo -e "Number of files submitted = $submittedFiles/$REQUIRED_FILES"
if [ "$submittedFiles" -eq "$REQUIRED_FILES" ]; then
    echo -e "You have submitted all files.\nPlease proceed on to submit to LumiNUS."
else
    echo -e "You have not submitted all the required files.\nPlease double check the required missing files"
fi
