# I need a persistent variable for a bunch of functions, and a class is kinda designed for that
START_HTML = """<!doctype html>
<html lang="en">
  <head>
    <title>cat door</title>
  </head>
  <style>
    body {
      padding: 20px;
      font-family: sans-serif;
    }
    table {
      background-color: #e8e8e8;
    }
    td {
      border: 1px solid black;
    }
    th {
      border: 1px solid black;
    }
    .small {
      font-size: 0.7em;
    }
    .scroll-panel {
      width: 300px;
      height: 150px;
      overflow: auto; /* Adds scrollbars only when content exceeds the box dimensions */
      border: 1px solid #ccc;
      padding: 10px;
    }
    .parent-container {
      display: flex; /* Aligns children horizontally */
      gap: 20px; /* Adds space between the two divs */
    }
    div.fdata {
      width: 400px;
    }
    pre {
      white-space: pre-wrap;
      width: 300px;
    }
    img {
      height: 180px;
    }
    #catdoor {
      max-width: 1200px;
      margin: 0 auto;
      content-visibility: auto;
    }
  </style>
  <body>
  <form id="searchForm" class="parent-container">

"""
START_FACET_PANEL = """
    <div class="scroll-panel">
"""
END_FACET_PANEL = """
    </div>
"""

END_HTML = """
<button type="submit">Search</button>
    </form>
    <table id="table">
      <tbody id="tableBody"></tbody>
    </table>
    <script>
      const form = document.getElementById("searchForm");

      const tbody = document.getElementById('tableBody');

      form.addEventListener("submit", function (event) {
        // Prevent page from refreshing
        event.preventDefault();

        // Create a FormData object from the form
        const formData = new FormData(form);
        const dataObject = Object.fromEntries(formData);
        console.log("Plain Object:", dataObject);
        let names = [];
        let catears = [];
        for (const key of Object.keys(dataObject)){
          if (key.slice(-2) == ',c'){
            catears.push(key);
          }
          if (key.slice(-2) == ',n'){
            names.push(key);
          }
        }
        let toDisplay = new Set()
        if (names.length > 0){names.forEach(value => toDisplay = toDisplay.union(new Set(facet_map[value])));}
        else if (catears.length > 0){toDisplay = toDisplay.union(new Set(facet_map[catears[0]]));}
        if (catears.length > 0){catears.forEach(value => toDisplay = toDisplay.intersection(new Set(facet_map[value])));};
        console.log(toDisplay);
        let htmlString = ''
        toDisplay.forEach(value => {
          d = data[value];
          htmlString += '<tr><td><img src="' + d['img_path'] + '"></img></td><td>' + d['etd_data']['chyron_data']['name_normalized'] + '</td></tr>';
        })
        tbody.innerHTML = htmlString;
      });
    </script>
  </body>
</html>

"""
class html_file:
    def __init__(self, image_dir:str) -> None:
        self.html_str = ""
        self.name_html = []
        self.catears_html = []
        # this relies on the fact that python defaults to shallow copies,
        # meaning I can edit name_html & catears_html and html_arr will change
        dataImport = f"""
            <script src="./{image_dir}/catout_table.js"></script>
            <script src="./{image_dir}/facet_map.js"></script>"""
        self.html_arr = [START_HTML, START_FACET_PANEL, self.name_html ,END_FACET_PANEL, START_FACET_PANEL, self.catears_html, dataImport, END_FACET_PANEL, END_HTML]

    def write_html(self, file_name:str) -> None:
        for i in self.html_arr:
            if type(i) == str:
                self.html_str += i
            if type(i) == list:
                for j in i:
                    self.html_str += j

        with open(file_name, "w") as f:
            f.write(self.html_str)


    def addNameFacet(self, facetName:str) -> None:
        self.name_html.append(f'<p><input type="checkbox" id="{facetName}" name="{facetName}"> {facetName[:-2]}</p>')

    def addCatearsFacet(self, facetName:str) -> None:
        self.catears_html.append(f'<p><input type="checkbox" id="{facetName}" name="{facetName}"> {facetName[:-2]}</p>')