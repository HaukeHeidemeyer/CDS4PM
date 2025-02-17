#!/bin/bash

# Set the base URL for the Blaze FHIR instance
FHIR_SERVER_URL="http://localhost:8080/fhir"

# Test connection using a GET request to the /metadata endpoint
response=$(curl --silent --write-out "%{http_code}" --output /dev/null "$FHIR_SERVER_URL/metadata")

# Check the HTTP status code
if [ "$response" -ne 200 ]; then
  echo "Blaze FHIR server is not running or not reachable at $FHIR_SERVER_URL"
  echo "Received HTTP status code: $response"
  exit 1
fi

# Retrieve all FHIR resource types available
echo "Fetching all FHIR resources available on the Blaze instance..."

resource_types=$(curl --silent "$FHIR_SERVER_URL/metadata" | jq -r '.rest[0].resource[].type' 2>/dev/null)

# Check if jq is installed and if parsing was successful
if [ $? -ne 0 ]; then
  echo "Error: 'jq' is required for parsing JSON. Please install jq and try again."
  exit 1
fi

if [ -z "$resource_types" ]; then
  echo "No FHIR resources found or an error occurred."
else
  # Initialize the total resource count
  total_resources=0

  echo "Available FHIR resources and their counts:"
  
  # Loop through each resource type and fetch the count
  while IFS= read -r resource_type; do
    # Fetch the total count of each resource type
    resource_count=$(curl --silent "$FHIR_SERVER_URL/$resource_type?_summary=count" | jq -r '.total' 2>/dev/null)
    
    # Check if the request was successful and resource_count is a number
    if [[ "$resource_count" =~ ^[0-9]+$ ]]; then
      echo "$resource_type: $resource_count"
      total_resources=$((total_resources + resource_count))
    else
      echo "$resource_type: Unable to retrieve count"
    fi
  done <<< "$resource_types"
  
  echo "Total resources across all types: $total_resources"
fi

