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
      width: 200px;
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
    .no-results {
        display: none;
        color: #888;
        font-size: 14px;
        text-align: center;
        padding: 10px 0;
    }
  </style>
  <body>
  <form id="searchForm" class="parent-container">

"""
START_FACET_PANEL = """
    <div class="container">
    <input
          type="search"
          id="REPLACE"
          class="search-box"
          placeholder="Search items..."
        />
    <div class="scroll-panel">
"""
END_FACET_PANEL = """
    <div id="noResults_REPLACE" class="no-results">No matching items found</div>
    </div>
    <script>
        const searchBar_REPLACE = document.getElementById('REPLACE');
        searchBar_REPLACE.addEventListener('input', function() {
            searchbar_listener('REPLACE');
      })
      </script>
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
        let other_filters = {};
        let catears = [];
        for (const key of Object.keys(dataObject)){
          if (key.slice(-2) == ',c'){
            catears.push(key);
          }
          else if (key.slice(-2) in other_filters ){ other_filters[key.slice(-2)].append(key);}
          else {other_filters[key.slice(-2)] = [key];}
        }
        let toDisplay = new Set();
        console.log(other_filters);
        if (Object.keys(other_filters).length > 0){
            for (const key of Object.keys(other_filters)){
                let temp = new Set();
                other_filters[key].forEach(value => temp = temp.union(new Set(facet_map[value])));
                if (toDisplay.size == 0) {toDisplay = temp;}
                else {toDisplay = toDisplay.intersection(temp);}
            }
        }
        else if (catears.length > 0){toDisplay = toDisplay.union(new Set(facet_map[catears[0]]));}
        if (catears.length > 0){catears.forEach(value => toDisplay = toDisplay.intersection(new Set(facet_map[value])));};
        console.log(toDisplay);
        let htmlString = ''
        toDisplay.forEach(value => {
          d = data[value];
          htmlString += REPLACE;
        })
        tbody.innerHTML = htmlString;
      });
      function searchbar_listener(facetName){
            const searchBar = document.getElementById(facetName);
            const checkboxItems = document.querySelectorAll('.' + facetName);
            const noResults = document.getElementById('noResults_'+facetName);
            const filter = searchBar.value.toLowerCase();
            let hasMatches = false;
            
            checkboxItems.forEach(item => {
                const text = item.textContent.trim().toLowerCase();

                if (text.includes(filter)) {
                    item.style.display = 'flex';
                    hasMatches = true;
                } else {
                    item.style.display = 'none';
                }
            });

        // Show fallback text if nothing matches the query
        noResults.style.display = hasMatches ? 'none' : 'block';
        }
    </script>
  </body>
</html>

"""
TABLE_STRING = """</td><td>' + d['etd_data']['chyron_data']['name_normalized'] + '</td><td>' + d['cataloger'] + '</td></tr>' """


dataImport = f"""
    <script src="./catout_table.js"></script>
    <script src="./facet_map.js"></script>"""

class html_file:
    def __init__(self, image_dir:str) -> None:
        self.html_str = ""
        self.facet_map = {}

    def write_html(self, file_name:str) -> None:
        self.html_str = ""
        self.html_str += START_HTML
        for facet in self.facet_map:
            self.html_str += START_FACET_PANEL.replace('REPLACE', facet)
            for item in self.facet_map[facet]:
                self.html_str += f'<label class="{facet}"><p><input type="checkbox" id="{item}" name="{item}" value="{item}"> {item[:-2]}</p></label>';
            self.html_str += END_FACET_PANEL.replace('REPLACE', facet)
        self.html_str += dataImport
        self.html_str += END_HTML.replace('REPLACE', """'<tr><td><img src="' + d['img_path'] + '"></img>""" + TABLE_STRING)
        with open(file_name, "w") as f:
            f.write(self.html_str)

    def addFacet(self, facetName, facet):
        if facet not in self.facet_map:
            self.facet_map[facet] = [facetName]
        else:
            self.facet_map[facet].append(facetName)