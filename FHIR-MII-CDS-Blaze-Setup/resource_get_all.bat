@echo off

REM Ask the user for the resource type
set /p resourceType="Enter the FHIR resource you want to download (e.g., Patient, Observation): "

REM Ask the user for the download folder
set /p folderPath="Enter the full path of the folder where you want to save the file: "

REM Ask the user for the filename without the extension
set /p fileName="Enter the filename for the download (extension will be added automatically): "

REM Check if the filename ends with .ndjson, if not append it
if not "%fileName:~-6%"==".ndjson" set "fileName=%fileName%.ndjson"

REM Construct the full path
set "fullPath=%folderPath%\%fileName%"

REM Execute the blazectl command
blazectl --server http://localhost:8080/fhir download "%resourceType%" --output-file "%fullPath%"

echo Download completed. File saved to %fullPath%