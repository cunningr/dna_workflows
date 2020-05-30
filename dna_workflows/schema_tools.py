import sdtables
from openpyxl import Workbook
from openpyxl.styles import Color, PatternFill, Font, Alignment
from openpyxl.styles.differential import DifferentialStyle
from openpyxl.formatting import Rule

# manifest = 'manifest.yml'
# xl_out = 'example.xlsx'


def create_new_workbook():
    _wb = Workbook()
    _ws = _wb.active
    _wb.remove(_ws)

    return _wb


def load_xl_wf_db(excel_db, flatten=False):
    _data = sdtables.load_xl_db(excel_db, flatten=flatten)

    return _data


def build_module_schema(_wb, _schema):
    """ Builds Excel tables from schema based on module manifest.

    :param _wb: (object) An openpyxl workbook object
    :param _schema: (dict) Dictionary describing the project modules loaded from schema.yml

    :returns: an updated openpyxl workbook object """

    for module in _schema['manifest']:
        exec_str = 'import {}'.format(module)
        exec(exec_str)
        exec_str = '{}.get_module_definition()'.format(module)
        module_doc = eval(exec_str)

        ws = _wb.create_sheet(module)
        ws.sheet_properties.tabColor = "009900"

        if 'description' in module_doc['module'].keys():
            ws.append({2: module_doc['module']['description']})
            ws['B1'].fill = PatternFill("solid", fgColor="b6e5eb")
            ws['B1'].alignment = Alignment(wrapText=True, vertical='top')
            ws.merge_cells(start_row=1, start_column=2, end_row=1, end_column=11)

        for module_schema in module_doc['module']['schemas'].keys():
            module_name = module_doc['module']['name']
            name = '{}.{}.{}'.format(module_schema, 'schema', module_name)
            schema_doc = module_doc['module']['schemas'][module_schema]
            if 'data' in module_doc['module']:
                if module_schema in module_doc['module']['data'].keys():
                    data = module_doc['module']['data'][module_schema]
                    sdtables.add_schema_table_to_worksheet(ws, name, schema_doc, data=data, table_style='TableStyleMedium2')
                else:
                    sdtables.add_schema_table_to_worksheet(ws, name, schema_doc, table_style='TableStyleMedium2')
            else:
                sdtables.add_schema_table_to_worksheet(ws, name, schema_doc, table_style='TableStyleMedium2')

    return _wb


def build_workflow_task_sheet(_wb, _schema):
    """ Builds the workflows cover sheet with a table containing available tasks
    based on the project manifest loaded from schema.yml.

    :param _wb: (object) An openpyxl workbook object
    :param _schema: (dict) Dictionary describing the project modules loaded from schema.yml

    :returns: an updated openpyxl workbook object """

    # Build a list of modules and tasks based on the manifest
    methods = []
    for module in _schema['manifest']:
        exec_str = 'import {}'.format(module)
        exec(exec_str)
        exec_str = '{}.get_module_definition()'.format(module)
        module_doc = eval(exec_str)

        for m in module_doc['module']['methods']:
            methods.append(m)

    _ws = _wb.create_sheet("workflows", 0)
    _ws.sheet_properties.tabColor = "0080FF"
    from dna_workflows import wf_engine
    wf_doc = wf_engine.get_module_definition()
    wf_schema = wf_doc['module']['schemas']['workflow']
    sdtables.add_schema_table_to_worksheet(_ws, 'workflow', wf_schema, data=methods, table_style='TableStyleLight14')

    # Add conditional formatting to workflow worksheet
    for table in _ws._tables:
        if 'workflow' == table.name:
            _tdef = table.ref
            red_fill = PatternFill(bgColor="9da19e")
            dxf = DifferentialStyle(fill=red_fill)
            r = Rule(type="expression", dxf=dxf, stopIfTrue=True)
            _formula = '${}="disabled"'.format(_tdef.split(':')[0])
            r.formula = [_formula]
            _ws.conditional_formatting.add(_tdef, r)

    return _wb


# if __name__ == "__main__":
#     schema = yaml.load(open(manifest, 'r'), Loader=yaml.SafeLoader)
#     wb = create_new_workbook()
#     wb = build_module_schema(wb, schema)
#     wb = build_workflow_task_sheet(wb, schema)
#     wb.save(xl_out)
