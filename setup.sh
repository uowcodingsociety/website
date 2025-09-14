# add virtual environment if it doesn't already exist
if ! [[ -d venv ]]; then
    echo Adding virtual environment 
    python3 -m venv venv

    # create pip.conf if doesn't exist
    echo Creating venv/pip.conf
    ( cat <<'EOF'
[install]
user = false
EOF
    ) > vcwk/pip.conf

    source venv/bin/activate

    echo Setting up Flask requirements
    pip install -r requirements.txt
    deactivate
fi

