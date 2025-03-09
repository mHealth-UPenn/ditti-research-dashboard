#!/bin/bash
echo "Building the frontend..."
cd ../aws_portal/frontend
npm run build

if [ $? -ne 0 ]; then
  echo "Frontend build failed."
  exit 1
else
  echo "Frontend build succeeded."
fi
