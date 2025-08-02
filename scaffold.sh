cp "$1.py" "$2.py"
cp "templates/$1.py" "templates/$2.py"
cp "templates/$1/" "templates/$2/" -r
echo "add this : "

echo "from . import $2"
echo "app.add_url_rule(\"/$2\", endpoint=\"$2.index\")"
echo "to : "
grep -r -i "from . import db"
