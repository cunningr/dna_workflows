# coding: utf-8


"""
    xlTables - Load table data from Excel
    into python dictionary structures

    cunningr@cisco.com - 2019

    Requires openpyxl >= 2.6.2


"""

import openpyxl


def load_xl_db(_db_file):
    wb = openpyxl.load_workbook(filename=_db_file)

    _sheets = wb.sheetnames
    _workbook_dict = {}

    # Iterate over the sheets->tables in the workbook
    for _sheet in _sheets:
        _sheet_name = wb[_sheet].title
        _workbook_dict.update({_sheet_name: {}})
        for _table in wb[_sheet]._tables:

            # Get the cell range of the table
            _table_range = _table.ref

            _keys = []

            for _column in _table.tableColumns:
                _keys.append(_column.name)

            _table_dict = _build_dict_from_table(wb[_sheet], _table.name, _table_range, _keys)

            _workbook_dict[_sheet_name].update(_table_dict)

    return _workbook_dict


def _build_dict_from_table(_work_sheet, _table_name, _table_range, _keys):
    _num_columns = len(_keys)
    _row_width = len(_work_sheet[_table_range][0])
    if _num_columns != _row_width:
        print('ERROR: Key count and row elements are not equal' + _num_columns, _row_width)

    _new_dict = {_table_name: {}}
    _rows_list = []

    for _row in _work_sheet[_table_range]:
        _row_dict = {}
        for _cell, _key in zip(_row, _keys):
            if _cell.value == _key:
                # Pass over headers where cell.value equal key
                pass
            else:
                _row_dict.update({_key:_cell.value})

        if bool(_row_dict):
            _rows_list.append(_row_dict)

    _new_dict[_table_name] = _rows_list

    return _new_dict
