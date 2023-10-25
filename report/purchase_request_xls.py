import base64
# import csv
# from io import StringIO
#
# def export_to_excel(self):
#     output = StringIO()
#     writer = csv.writer(output)
#     writer.writerow(['Sản phẩm', 'Số lượng', 'Đơn vị tính'])
#
#     for line in self:
#         writer.writerow([line.product_id.name, line.quantity, line.uom_id.name])
#
#     # Chuyển dữ liệu vào tệp CSV
#     attachment = self.env['ir.attachment'].create({
#         'name': 'purchase_request_lines.csv',
#         'datas': base64.b64encode(output.getvalue().encode()),
#         'datas_fname': 'purchase_request_lines.csv',
#         'res_model': self._name,
#         'res_id': self.id,
#     })
#     output.close()
#
#     # Trả về tệp đính kèm
#     return {
#         'type': 'ir.actions.act_url',
#         'url': "web/content/?model=ir.attachment&id=" + str(attachment.id) + "&filename_field=name&field=datas&download=true&filename=" + attachment.name,
#         'target': 'new',
#     }

import csv
import io
from odoo import api
