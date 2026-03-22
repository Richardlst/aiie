input=$1

if [ -z "$input" ]; then
    echo "Please provide a migration name"
    exit 1
fi

alembic revision --autogenerate -m "$input"