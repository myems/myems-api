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


def export(report_data, start, end, period):
    ####################################################################################################################
    # Step 1: Validate the report data
    ####################################################################################################################
    # 可能不需要验证数据了,因为数据是从spaceenergycategory.py的api里面调用的,也就是之前已经验证过了
    # 所以应该不需要重复验证
    pass
    ####################################################################################################################
    # Step 2: Generate excel exporters file from the report data
    ####################################################################################################################
    export_name = generate_excel(report_data, start, end, period)

    ####################################################################################################################
    # Step 3: Encode the excelexporters file to Base64
    ####################################################################################################################
    data = open(export_name, 'rb').read()
    base64_encoded = base64.b64encode(data).decode('UTF-8')
    # todo: replace the demo string
    # base64_encoded = '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'
    return base64_encoded


def generate_excel(data, start, end, period):

    """
    parameter:
    data,
    start, end
    period
    """
    # start = "2021-01-01"
    # end = "2021-01-05"
    # period = 'day'

    # For test
    # with open('test.json', 'r') as fr:
    #     json_data = fr.read()
    #     data = json.loads(json_data)

    wb = Workbook()
    ws = wb.active

    # Row height
    ws.row_dimensions[1].height = 118
    for i in range(2, 37 + 1):
        ws.row_dimensions[i].height = 30

    for i in range(37, 69 + 1):
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
    ws['C3'] = data['space']['name']

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
    # 8~11 table_data
    #################################################

    ws['B6'].font = title_font
    ws['B6'] = '远洋太古里 能耗分析'

    report = data['reporting_period']
    print(report)
    category = report['names']
    ca_len = len(category)

    ws['B7'].fill = table_fill

    ws['B8'].font = title_font
    ws['B8'].alignment = c_c_alignment
    ws['B8'] = '能耗'
    ws['B8'].border = f_border

    ws['B9'].font = title_font
    ws['B9'].alignment = c_c_alignment
    ws['B9'] = '单位面积能耗'
    ws['B9'].border = f_border

    ws['B10'].font = title_font
    ws['B10'].alignment = c_c_alignment
    ws['B10'] = '环比'
    ws['B10'].border = f_border

    for i in range(0, ca_len):
        col = chr(ord('C') + i)
        row = '7'
        cell = col + row
        ws[col + '7'].fill = table_fill
        ws[col + '7'].font = name_font
        ws[col + '7'].alignment = c_c_alignment
        ws[col + '7'] = report['names'][i] + " (" + report['units'][i] + ")"
        ws[col + '7'].border = f_border

        ws[col + '8'].font = name_font
        ws[col + '8'].alignment = c_c_alignment
        ws[col + '8'] = round(report['subtotals'][i], 0)
        ws[col + '8'].border = f_border

        ws[col + '9'].font = name_font
        ws[col + '9'].alignment = c_c_alignment
        ws[col + '9'] = round(report['subtotals_per_unit_area'][i], 2)
        ws[col + '9'].border = f_border

        ws[col + '10'].font = name_font
        ws[col + '10'].alignment = c_c_alignment
        ws[col + '10'] = str(round(report['increment_rates'][i] * 100, 2)) + "%"
        ws[col + '10'].border = f_border

    #################################################
    # Second: 分时电耗
    # 12: title
    # 13: table title
    # 14~17 table_data
    #################################################
    ws['B12'].font = title_font
    ws['B12'] = '远洋太古里 分时电耗'

    ws['B13'].fill = table_fill
    ws['B13'].font = name_font
    ws['B13'].alignment = c_c_alignment
    ws['B13'].border = f_border

    ws['C13'].fill = table_fill
    ws['C13'].font = name_font
    ws['C13'].alignment = c_c_alignment
    ws['C13'].border = f_border
    ws['C13'] = '分时电耗'

    ws['B14'].font = title_font
    ws['B14'].alignment = c_c_alignment
    ws['B14'] = '尖'
    ws['B14'].border = f_border

    ws['C14'].font = title_font
    ws['C14'].alignment = c_c_alignment
    ws['C14'].border = f_border
    ws['C14'] = round(report['toppeaks'][0], 0)

    ws['B15'].font = title_font
    ws['B15'].alignment = c_c_alignment
    ws['B15'] = '峰'
    ws['B15'].border = f_border

    ws['C15'].font = title_font
    ws['C15'].alignment = c_c_alignment
    ws['C15'].border = f_border
    ws['C15'] = round(report['onpeaks'][0], 0)

    ws['B16'].font = title_font
    ws['B16'].alignment = c_c_alignment
    ws['B16'] = '平'
    ws['B16'].border = f_border

    ws['C16'].font = title_font
    ws['C16'].alignment = c_c_alignment
    ws['C16'].border = f_border
    ws['C16'] = round(report['midpeaks'][0], 0)

    ws['B17'].font = title_font
    ws['B17'].alignment = c_c_alignment
    ws['B17'] = '谷'
    ws['B17'].border = f_border

    ws['C17'].font = title_font
    ws['C17'].alignment = c_c_alignment
    ws['C17'].border = f_border
    ws['C17'] = round(report['offpeaks'][0], 0)

    pie = PieChart()
    labels = Reference(ws, min_col=2, min_row=14, max_row=17)
    pie_data = Reference(ws, min_col=3, min_row=14, max_row=17)
    pie.add_data(pie_data, titles_from_data=True)
    pie.set_categories(labels)
    pie.height = 5.25  # cm 1.05*5 1.05cm = 30 pt
    pie.width = 9
    # pie.title = "Pies sold by category"
    s1 = pie.series[0]
    s1.dLbls = DataLabelList()
    s1.dLbls.showCatName = True  # 标签显示
    s1.dLbls.showVal = True  # 数量显示
    s1.dLbls.showPercent = True  # 百分比显示
    # s1 = CharacterProperties(sz=1800)     # 图表中字体大小 *100

    ws.add_chart(pie, "D13")

    #################################################
    # Third: 子空间能耗
    # 19: title
    # 20: table title
    # 21~24 table_data
    #################################################
    child = data['child_space']
    child_spaces = child['child_space_names_array'][0]
    child_subtotals = child['subtotals_array'][0]

    ws['B19'].font = title_font
    ws['B19'] = '远洋太古里 子空间能耗'

    ws['B20'].fill = table_fill
    ws['B20'].border = f_border

    ws['C20'].fill = table_fill
    ws['C20'].font = title_font
    ws['C20'].alignment = c_c_alignment
    ws['C20'].border = f_border
    ws['C20'] = child['energy_category_names'][0]

    ca_len = len(child['energy_category_names'])
    space_len = len(child['child_space_names_array'][0])
    for i in range(0, space_len):
        row = str(i + 21)

        ws['B' + row].font = name_font
        ws['B' + row].alignment = c_c_alignment
        ws['B' + row] = child['child_space_names_array'][0][i]
        ws['B' + row].border = f_border

        for j in range(0, ca_len):
            col = chr(ord('C') + j)
            ws[col + row].font = name_font
            ws[col + row].alignment = c_c_alignment
            ws[col + row] = child['subtotals_array'][0][i]
            ws[col + row].border = f_border
            # pie
            # 25~30: pie
            pie = PieChart()
            labels = Reference(ws, min_col=2, min_row=21, max_row=23)
            pie_data = Reference(ws, min_col=3 + j, min_row=21, max_row=23)
            pie.add_data(pie_data, titles_from_data=True)
            pie.set_categories(labels)
            pie.height = 5.25  # cm 1.05*5 1.05cm = 30 pt
            pie.width = 8
            # pie.title = "Pies sold by category"
            s1 = pie.series[0]
            s1.dLbls = DataLabelList()
            s1.dLbls.showCatName = True  # 标签显示
            s1.dLbls.showVal = True  # 数量显示
            s1.dLbls.showPercent = True  # 百分比显示
            # s1 = CharacterProperties(sz=1800)     # 图表中字体大小 *100
            chart_col = chr(ord('B') + 2 * j)
            chart_cell = chart_col + '26'
            ws.add_chart(pie, chart_cell)

    #################################################
    # Third: 电耗详情
    # 37: title
    # 38: table title
    # 39~69: table_data
    #################################################
    report = data['reporting_period']
    times = report['timestamps']

    ws['B37'].font = title_font
    ws['B37'] = '远洋太古里 电耗详情'

    ws['B38'].fill = table_fill
    ws['B38'].border = f_border
    ws['B38'].alignment = c_c_alignment
    ws['B38'] = '时间'
    time = times[0]
    has_data = False
    max_row = 0
    if len(time) > 0:
        has_data = True
        max_row = 38 + len(time)
        print("max_row", max_row)

    if has_data:
        for i in range(0, len(time)):
            col = 'B'
            row = str(39 + i)
            # col = chr(ord('B') + i)
            ws[col + row].font = title_font
            ws[col + row].alignment = c_c_alignment
            ws[col + row] = time[i]
            ws[col + row].border = f_border

        for i in range(0, ca_len):
            # 38 title
            col = chr(ord('C') + i)

            ws[col + '38'].fill = table_fill
            ws[col + '38'].font = title_font
            ws[col + '38'].alignment = c_c_alignment
            ws[col + '38'] = report['names'][i] + " (" + report['units'][i] + ")"
            ws[col + '38'].border = f_border

            # 39 data
            time = times[i]
            time_len = len(time)

            for j in range(0, time_len):
                row = str(39 + j)
                # col = chr(ord('B') + i)
                ws[col + row].font = title_font
                ws[col + row].alignment = c_c_alignment
                ws[col + row] = round(report['values'][i][j], 0)
                ws[col + row].border = f_border
            # bar
            # 25~30: bar
            bar = BarChart()
            labels = Reference(ws, min_col=2, min_row=39, max_row=max_row + 1)
            bar_data = Reference(ws, min_col=3 + i, min_row=38, max_row=max_row + 1)  # openpyxl bug
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

    export_name = "energy.xlsx"
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
base64_encoded = export(report_data, start, end, period)
print(base64_encoded)