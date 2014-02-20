pep8 --ignore E501 --exclude=migrations opentavern tavern
pylint --rcfile=.pylintrc opentavern tavern accounts --ignore=migrations,config
