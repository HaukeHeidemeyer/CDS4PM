#!/bin/bash

# Ask the user for the resource type
echo "Enter the FHIR resource you want to download (e.g., Patient, Observation):"
read resourceType

# Ask the user for the download folder
echo "Enter the full path of the folder where you want to save the file:"
read folderPath

# Ask the user for the filename without the extension
echo "Enter the filename for the download (extension will be added automatically):"
read fileName

# Check if the filename ends with .ndjson, if not append it
if [[ $fileName != *".ndjson" ]]; then
    fileName="${fileName}.ndjson"
fi

# Construct the full path
fullPath="${folderPath}/${fileName}"

# Execute the blazectl command
blazectl --server http://localhost:8085/fhir download "${resourceType}" --output-file "${fullPath}"

echo "Download completed. File saved to ${fullPath}"
