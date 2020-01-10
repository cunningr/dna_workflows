import tables
import json
import yaml


excel_tables_db = 'example_parse_xlsx.xlsx'

excel_to_dict = tables.load_xl_db(excel_tables_db)

# Dump raw Python dict
print(excel_to_dict)

# Dump to YAML
# print(yaml.dump(excel_to_dict))

# Dump to JSON
print(json.dumps(excel_to_dict, indent=4))
