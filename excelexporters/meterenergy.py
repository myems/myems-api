import base64
from openpyxl.chart import (
        PieChart,
        BarChart,
        ProjectedPieChart,
        Reference,
        label
    )
from openpyxl.chart.series import DataPoint
from openpyxl.styles import PatternFill, Border, Side, Alignment, Protection, Font
from openpyxl.drawing.image import Image
import json
from openpyxl import Workbook
from openpyxl.chart.label import DataLabelList
from openpyxl.drawing.text import Paragraph, ParagraphProperties, CharacterProperties

####################################################################################################################
# PROCEDURES
# Step 1: Validate the report data
# Step 2: Generate excelexporters file
# Step 3: Encode the excelexporters file to Base64
####################################################################################################################


def export(report_data, name, start, end, period):
    ####################################################################################################################
    # Step 1: Validate the report data
    ####################################################################################################################
    pass
    ####################################################################################################################
    # Step 2: Generate excel exporters file from the report data
    ####################################################################################################################
    export_name = generate_excel(report_data, name, start, end, period)

    ####################################################################################################################
    # Step 3: Encode the excel exporters file to Base64
    ####################################################################################################################
    data = open(export_name, 'rb').read()
    base64_encoded = base64.b64encode(data).decode('UTF-8')
    # todo: replace the demo string

    return base64_encoded


def generate_excel(data, name, start, end, period):

    """
    parameter:
    name,
    data,
    start, end
    period
    """
    # For test
    # start = "2021-01-01"
    # end = "2021-01-05"
    # period = 'day'
    # name = "AHc01进线柜正向有功Wp"
    #
    # with open('test.json', 'r') as fr:
    #     json_data = fr.read()
    #     data = json.loads(json_data)

    wb = Workbook()
    ws = wb.active

    # Row height
    ws.row_dimensions[1].height = 118
    for i in range(2, 11 + 1):
        ws.row_dimensions[i].height = 30

    for i in range(12, 43 + 1):
        ws.row_dimensions[i].height = 15

    # Col width
    ws.column_dimensions['A'].width = 1.5

    for i in range(ord('B'), ord('I')):
        ws.column_dimensions[chr(i)].width = 15.0

    # Font
    name_font = Font(name='Constantia', size=15, bold=True)
    title_font = Font(name='宋体', size=15, bold=True)
    data_font = Font(name='Franklin Gothic Book', size=11)

    table_fill = PatternFill(fill_type='solid', fgColor='1F497D')
    f_border = Border(left=Side(border_style='medium', color='00000000'),
                      right=Side(border_style='medium', color='00000000'),
                      bottom=Side(border_style='medium', color='00000000'),
                      top=Side(border_style='medium', color='00000000')
                      )
    b_border = Border(
        bottom=Side(border_style='medium', color='00000000'),
    )

    b_c_alignment = Alignment(vertical='bottom',
                              horizontal='center',
                              text_rotation=0,
                              wrap_text=False,
                              shrink_to_fit=False,
                              indent=0)
    c_c_alignment = Alignment(vertical='center',
                              horizontal='center',
                              text_rotation=0,
                              wrap_text=False,
                              shrink_to_fit=False,
                              indent=0)
    b_r_alignment = Alignment(vertical='bottom',
                              horizontal='right',
                              text_rotation=0,
                              wrap_text=False,
                              shrink_to_fit=False,
                              indent=0)
    c_r_alignment = Alignment(vertical='bottom',
                              horizontal='center',
                              text_rotation=0,
                              wrap_text=False,
                              shrink_to_fit=False,
                              indent=0)
    # Img
    img = Image("myems.png")
    ws.add_image(img, 'B1')

    # Title
    ws['B3'].font = name_font
    ws['B3'].alignment = b_r_alignment
    ws['B3'] = 'Name:'
    ws['C3'].border = b_border
    ws['C3'].alignment = b_c_alignment
    ws['C3'].font = name_font
    ws['C3'] = name

    ws['D3'].font = name_font
    ws['D3'].alignment = b_r_alignment
    ws['D3'] = 'Period:'
    ws['E3'].border = b_border
    ws['E3'].alignment = b_c_alignment
    ws['E3'].font = name_font
    ws['E3'] = period

    ws['F3'].font = name_font
    ws['F3'].alignment = b_r_alignment
    ws['F3'] = 'Date:'
    ws['G3'].border = b_border
    ws['G3'].alignment = b_c_alignment
    ws['G3'].font = name_font
    ws['G3'] = start + "__" + end
    ws.merge_cells("G3:H3")

    #################################################
    # First: 能耗分析
    # 6: title
    # 7: table title
    # 8~9 table_data
    #################################################

    ws['B6'].font = title_font
    ws['B6'] = name + '能耗分析'

    report = data['reporting_period']
    # print(report)
    category = data['meter']['energy_category_name']
    ca_len = len(category)

    ws['B7'].fill = table_fill

    ws['B8'].font = title_font
    ws['B8'].alignment = c_c_alignment
    ws['B8'] = '能耗'
    ws['B8'].border = f_border

    ws['B9'].font = title_font
    ws['B9'].alignment = c_c_alignment
    ws['B9'] = '环比'
    ws['B9'].border = f_border

    for i in range(0, ca_len):
        col = chr(ord('C') + i)
        row = '7'
        cell = col + row
        ws[col + '7'].fill = table_fill
        ws[col + '7'].font = name_font
        ws[col + '7'].alignment = c_c_alignment
        ws[col + '7'] = data['meter']['energy_category_name'] + " (" + data['meter']['unit_of_measure'] + ")"
        ws[col + '7'].border = f_border

        ws[col + '8'].font = name_font
        ws[col + '8'].alignment = c_c_alignment
        ws[col + '8'] = round(report['total_in_category'], 0)
        ws[col + '8'].border = f_border

        ws[col + '9'].font = name_font
        ws[col + '9'].alignment = c_c_alignment
        ws[col + '9'] = str(round(report['increment_rate'] * 100, 2)) + "%"
        ws[col + '9'].border = f_border

    # TCE TCO2E
    end_col = col
    # TCE
    tce_col = chr(ord(end_col) + 1)
    ws[tce_col + '7'].fill = table_fill
    ws[tce_col + '7'].font = name_font
    ws[tce_col + '7'].alignment = c_c_alignment
    ws[tce_col + '7'] = "TCE"
    ws[tce_col + '7'].border = f_border

    ws[tce_col + '8'].font = name_font
    ws[tce_col + '8'].alignment = c_c_alignment
    ws[tce_col + '8'] = round(report['total_in_category'], 0)
    ws[tce_col + '8'].border = f_border

    ws[tce_col + '9'].font = name_font
    ws[tce_col + '9'].alignment = c_c_alignment
    ws[tce_col + '9'] = str(round(report['increment_rate'] * 100, 2)) + "%"
    ws[tce_col + '9'].border = f_border

    # TCO2E
    tco2e_col = chr(ord(end_col) + 2)
    ws[tco2e_col + '7'].fill = table_fill
    ws[tco2e_col + '7'].font = name_font
    ws[tco2e_col + '7'].alignment = c_c_alignment
    ws[tco2e_col + '7'] = "TCO2E"
    ws[tco2e_col + '7'].border = f_border

    ws[tco2e_col + '8'].font = name_font
    ws[tco2e_col + '8'].alignment = c_c_alignment
    ws[tco2e_col + '8'] = round(report['total_in_kgco2e'], 0)
    ws[tco2e_col + '8'].border = f_border

    ws[tco2e_col + '9'].font = name_font
    ws[tco2e_col + '9'].alignment = c_c_alignment
    ws[tco2e_col + '9'] = str(round(report['increment_rate'] * 100, 2)) + "%"
    ws[tco2e_col + '9'].border = f_border
    #################################################
    # Second: 电耗详情
    # 11: title
    # 12: table title
    # 13~43: table_data
    #################################################
    report = data['reporting_period']
    times = report['timestamps']

    ws['B11'].font = title_font
    ws['B11'] = name + '电耗详情'

    ws['B12'].fill = table_fill
    ws['B12'].border = f_border
    ws['B12'].alignment = c_c_alignment
    ws['B12'] = '时间'
    time = times
    has_data = False
    max_row = 0
    if len(time) > 0:
        has_data = True
        max_row = 12 + len(time)

    if has_data:
        for i in range(0, len(time)):
            col = 'B'
            row = str(13 + i)
            # col = chr(ord('B') + i)
            ws[col + row].font = title_font
            ws[col + row].alignment = c_c_alignment
            ws[col + row] = time[i]
            ws[col + row].border = f_border

        for i in range(0, ca_len):
            # 12 title
            col = chr(ord('C') + i)

            ws[col + '12'].fill = table_fill
            ws[col + '12'].font = title_font
            ws[col + '12'].alignment = c_c_alignment
            ws[col + '12'] = data['meter']['energy_category_name'] + " (" + data['meter']['unit_of_measure'] + ")"
            ws[col + '12'].border = f_border

            # 13 data
            time = times
            time_len = len(time)

            for j in range(0, time_len):
                row = str(13 + j)
                # col = chr(ord('B') + i)
                ws[col + row].font = title_font
                ws[col + row].alignment = c_c_alignment
                ws[col + row] = round(report['values'][j], 0)
                ws[col + row].border = f_border
            # bar
            # 13~: bar
            bar = BarChart()
            labels = Reference(ws, min_col=2, min_row=13, max_row=max_row + 1)
            bar_data = Reference(ws, min_col=3 + i, min_row=12, max_row=max_row + 1)  # openpyxl bug
            bar.add_data(bar_data, titles_from_data=True)
            bar.set_categories(labels)
            bar.height = 5.25  # cm 1.05*5 1.05cm = 30 pt
            bar.width = 18
            # pie.title = "Pies sold by category"
            bar.dLbls = DataLabelList()
            bar.dLbls.showCatName = True  # 标签显示
            bar.dLbls.showVal = True  # 数量显示
            bar.dLbls.showPercent = True  # 百分比显示
            # s1 = CharacterProperties(sz=1800)     # 图表中字体大小 *100
            chart_col = chr(ord('B') + 2 * i)
            chart_cell = chart_col + str(max_row + 2)
            ws.add_chart(bar, chart_cell)

    export_name = "meter.xlsx"
    wb.save(export_name)

    return export_name


# Test Data
"""
parameter:
    data,
    start, end
    period
"""
with open('test.json', 'r') as fr:
    json_data = fr.read()
    report_data = json.loads(json_data)
start = "2021-01-01"
end = "2021-01-05"
period = 'day'
name = "AHc01进线柜正向有功Wp"
base64_encoded = export(report_data, name, start, end, period)
print(base64_encoded)