#!/bin/bash
echo "Installing PigSpy dependencies..."
echo

pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo
    echo "Error installing dependencies. Please check your Python installation."
    exit 1
fi

echo
echo "Dependencies installed successfully!"
echo
echo "To run PigSpy:"
echo "python3 main.py"
echo