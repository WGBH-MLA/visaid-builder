# I need a persistent variable for a bunch of functions, and a class is kinda designed for that

HTML_EXT_SCRIPTS = """
<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
<script src="https://cdn.datatables.net/2.0.0/js/dataTables.js"></script>

<script src="https://cdn.datatables.net/searchpanes/2.3.0/js/dataTables.searchPanes.js"></script>
<script src="https://cdn.datatables.net/searchpanes/2.3.0/js/searchPanes.dataTables.js"></script>
<script src="https://cdn.datatables.net/select/2.0.0/js/dataTables.select.js"></script>
"""
from ..html_tables import *

HTML_CSS = """
<link rel="stylesheet" href="https://cdn.datatables.net/2.0.0/css/dataTables.dataTables.css">
<link rel="stylesheet" href="https://cdn.datatables.net/searchpanes/2.3.0/css/searchPanes.dataTables.css">
<link rel="stylesheet" href="https://cdn.datatables.net/select/2.0.0/css/select.dataTables.css">
<style>
    body{padding: 20px; font-family: sans-serif;}
    table{background-color: #E8E8E8;}
    td{border: 1px solid black;}
    th{border: 1px solid black;}
    .small{font-size: 0.7em;}
    div.fdata{width: 400px;}
    pre{white-space: pre-wrap; width: 300px;}
    img{height: 180px;}
    #catdoor{ max-width: 1200px; margin: 0 auto; content-visibility: auto;}
</style>
"""
class html_file:
    def __init__(self):
        self.html_str = f"<!DOCTYPE html>\n<html lang='en'>\n<head>\n<title>cat door</title>\n{HTML_CSS}\n</head>\n<body>\n"
        #used for error handling(trying to add a row before calling writeField, etc.)
        self.phase = 0

    def write_html(self, file_name):
        if self.phase == 0: raise Exception(f"Called write_html out of phase, phase should be 1 or 2, phase is {self.phase}")
        if self.phase == 1:
            self.phase = 2
            self.html_str += "</tbody></table>"
            self.html_str += HTML_EXT_SCRIPTS + """
    <script>
        $(document).ready(function() {
            $('#catdoor').DataTable({
                pageLength: 100,
                // layout: defines where the facets (searchPanes) appear
                layout: {
                    top1: {
                        searchPanes: {
                            // Set to false so it only shows what we explicitly ask for in columnDefs
                            show: false
                        }
                    }
                },
                // configures the faceting behavior
                columnDefs: [
                    {
                        searchPanes: {
                            show: true
                        },
                        targets: [0, 1, 5, 7, 9]
                    },
                    {
                        searchPanes: {
                            show: false
                        },
                        targets: '_all' // Hide everything else explicitly
                    }
                ]
            });
        });
    </script>
    """
            self.html_str += "\n\n</body></html>"
        with open(file_name, "w") as f:
            f.write(self.html_str)

    #must be called before adding rows
    def writeFields(self, fields=None):
        if fields is None:
            fields = ["asset ID", "cataloger", "export date", "time", "still image", "etd type", "etd text", "cat ears",
                      "cat ear data", "to attend to", "message", ]

        if not self.phase == 0 : raise Exception(f"Called writeFields out of phase, phase should be 0, phase is {self.phase}")
        self.phase = 1
        self.html_str += "<table id='catdoor'><thead><tr>\n"
        for f in fields:
            self.html_str += f"<th>{f}</th>"
        self.html_str += "\n</tr></thead>\n<tbody>"

    def addRow(self, row, image_path):
        if not (self.phase == 1): raise Exception(f"Called addRow out of phase, phase should be 1, phase is {self.phase}")
        self.html_str += "\n<tr>\n"
        self.html_str += f"<td class='small'>{row['asset_id']}</td>"
        self.html_str += f"<td>{row['cataloger']}</td>"
        self.html_str += f"<td class='small'>{row['export_date']}</td>"
        self.html_str += f"<td>{aapb_html_link(row['asset_id'], row['tp_time'])}</td>"
        self.html_str += f"<td><img src='{image_path}' loading=\"lazy\" height=180px width=240px></td>"
        self.html_str += f"<td>{row['etd_data']['etd_type']}</td>"
        self.html_str += f"<td><pre>{row['etd_text']}</pre></td>"
        self.html_str += f"<td>{stringify_keys(row['etd_data']['catear_data'])}</td>"
        self.html_str += f"<td>{htmlify_catear_data(row['etd_data']['catear_data'])}</td>"
        self.html_str += f"<td>{htmlify_attention(row['etd_data'])}</td>"
        self.html_str += f"<td class='small'>{htmlify_messages(row['etd_data'])}</td>"
        self.html_str += "\n</tr>\n"