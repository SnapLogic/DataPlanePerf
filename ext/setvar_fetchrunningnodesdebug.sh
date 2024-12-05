#!/bin/bash

export API_URL="https://cdn.canary.elastic.snaplogicdev.com/api/1/rest/slserver/snaplex_cc_details_with_info?subscriber_id=DpPerf"
export API_USERNAME="ashostak+dpperfsrv@snaplogic.com"
export API_PASSWORD="SnapLogic@12345"

echo "Environment variables set. Launching the Go application..."

go run runningnodesfetchdebug.go

if [ $? -eq 0 ]; then
  echo "Go application executed successfully."
else
  echo "Go application failed to execute." >&2
  exit 1
fi
