from pathlib import Path
from shiny import ui, render, reactive, App
import shinyswatch
import rpu_calculations


css_path = Path(__file__).parent / "www" / "calculator-theme.css"
MAX_SIZE_FILE = 50000
currency = "€"
factor_projection = 1


"""
Main Shiny app for the RPU frequentist A/B-test Calculator
I have based the UI and the information about what statistical test to perform from the RPU calculator
developed by BLAST (https://www.blastanalytics.com/rpv-calculator) that I have been using for long.
Wanted to understand and develop the calculator on my own (and in python) to learn and check result output were the same, which are :) 
"""
app_ui = ui.page_fluid(
    #https://bootswatch.com/
    shinyswatch.theme.pulse(),
    ui.head_content(ui.HTML("""
      <!-- Google tag (gtag.js) -->
      <script async src="https://www.googletagmanager.com/gtag/js?id=G-EE3R9DZV33"></script>
      <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-EE3R9DZV33');
      </script>""")),
    ui.include_css(css_path),
    ui.output_ui("head_html"),
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.tags.div(
               ui.tags.div(ui.input_numeric("test_duration", "Test duration in days", min=1, max=100, value=14), class_="form-group col-md-6 col-xs-12"),
               ui.tags.div(ui.input_numeric("percent_traffic_in_test", "Percentage of traffic", value=100, min=1, max=100), class_="form-group col-md-6 col-xs-12"),
              class_="row"
            ),            
            ui.tags.div(
              ui.tags.div(ui.input_switch("currency_switch", "$/€", True), class_="form-group col-md-4 col-xs-12"),
              ui.tags.div(ui.input_switch("year_assessment_switch", "6/12 months projection", True), class_="form-group col-md-8 col-xs-12"),
              class_="row"
            ),
            ui.input_radio_buttons(
                "conf_level",
                "Choose desired Confidence Level:",
                {
                    "0.90": "90%",
                    "0.95": "95%",
                    "0.98": "98%",
                },
                selected="0.95",
            ),
            ui.tags.div(
            ui.input_file("file1", ui.div("Choose a file to upload", ui.tooltip(bs_info_icon("format of csv file to upload"), 
            f'''CSV file with two columns for revenue (Control Revenue and Variation Revenue), where each row
              represents one user/clientId and their revenue, which can be 0 if there was no purchase. 
              The delimiter must be a comma and if there is decimal numbers, the decimal separator must be a period.'''),),
              multiple=False, accept="text/csv"),
            ui.download_button("download", "Download sample csv")),
            ui.input_action_button("compute", "Calculate", class_="btn-primary")
        ),
        ui.panel_main(   
            ui.output_ui("main_result"),  
            ui.output_ui("data_distributions_plots"), 
            #ui.output_text_verbatim("file_content")
        ),
    ),
)

"""
Generates an HTML the info icon.
"""
def bs_info_icon(title: str):
    return ui.HTML(f'''
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" class="bi bi-info-circle"
             style="height:1em;width:1em;fill:currentColor;" aria-hidden="true" role="img">
          <title>{title}</title>
          <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"></path>
          <path d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"></path>
        </svg>
    ''')

def server(input, output, session):
    """
    This function defines the shiny server with multiple reactive effects and output functions. 
    It takes input, output, and session as parameters.
    """

    r = rpu_calculations.rpuCalculations()

    @reactive.Effect
    @reactive.event(input.compute)
    def _():
        """
        A "side effect" function that is called when the "Calculate" button is clicked. 
        It calculates the RPU probs and handles ValueError exceptions.
        """
        global currency
        global factor_projection

        if input.currency_switch():
            currency = "€"
        else:
            currency = "$"

        if input.year_assessment_switch():
            factor_projection = 2
        else:
            factor_projection = 1

        try:
          csv_file = input.file1()[0]["datapath"]
          if not csv_file:
              return
          r.read_csv(csv_file)
          r.calculate_frequentist_result(float(input.percent_traffic_in_test()), int(input.test_duration()))

        except ValueError:
            m = ui.modal(
            "An error occured, please check the test data input and try again.",
            title="",
            easy_close=True,
            footer=None)
            ui.modal_show(m)
            
    @output
    @render.ui
    def head_html():
        """
        A function that generates the HTML content for the header section of the web page.
        """
        head_html_info = """
        <header>
        <div class="row">
          <div class="col-md-12">
            <h1 id="title">Revenue per Visitor Statistical Significance Calculator</h1> 
            <h2 class="header">This app is based on the <a href="https://www.blastanalytics.com/rpv-calculator" target="_blank">revenue per visitor calculator</a> by Blast. 
            The calculations are implemented with Python and the interface and deployment with Shiny for Python.  Developed by <a href="https://www.linkedin.com/in/fernandomaquedano/" target="_blank">Fer Maquedano</a>.
            </h2>
          </div>
        </div>
        </header>"""
        return ui.HTML(head_html_info)
    
    @session.download(filename="sample_revenue_example.csv")
    def download():
        """
        Download the file "sample_revenue_example.csv" 
        """
        file_path = Path(__file__).parent / "www" / "SampleRevenueExample.csv"
        f = open(file_path, "r")
        yield f.read()
        f.close()
        
    @output
    @render.ui
    @reactive.event(input.compute)
    def main_result():
        """
        This function generates the main result information for the UI. 
        It constructs HTML elements based on the statistical significance of the observed increase in RPU (Revenue Per User)
        on the variant (B) compared to the control (A). It also includes a table with the number of users, revenue per user,
        standard deviation, RPU uplift, P-value, and test confidence level for both A and B. 
        It returns the main result information in HTML format.
        """
        
        significant_looser_html = """<div class="contribution negative-contribution">
                        <div class="contribution-amount">RPU decrease is statistically significant</div>
                    </div>"""
        significant_html = """<div class="contribution">
                                <div class="contribution-amount">RPU uplift is statistically significant</div>
                            </div>"""
        not_significant_html = """<div class="contribution negative-contribution">
                                <div class="contribution-amount">Not statistically significant</div>
                              </div>"""
        projection_html = """<p class="table-caption">Based on """ + f"{r.uplift:.2%}" + """ RPU uplift and """ + f"{6 * factor_projection}" + """ months time, the projected extra revenue is expected to be """ + currency + f"{r.contribution * factor_projection:,.0f}" + """</p>"""
        
        significant_text = not_significant_html if r.conf_level <= float(input.conf_level()) else (significant_html if r.uplift > 0 else significant_looser_html)
        projection_text  = "" if r.conf_level <= float(input.conf_level()) or r.uplift <= 0 else projection_html

        main_result_info = """
        <div class="block">
            <h3>Test result</h3>
            <h4>Determining the statistical significance of the observed increase in RPU (Revenue Per User) on the variant (B) compared to the control (A)</h4>
            <h2>""" + significant_text + """</h2>
            <table class="table">
              <thead>
                <tr>
                  <th>#</th>
                  <th class="align-right">Number of users</th>
                  <th class="align-right">Revenue per user</th>
                  <th class="align-right">Std dev</th>
                  <th class="align-right">RPU uplift</th>
                  <th class="align-right">P-value</th>
                  <th class="align-right move-tds">Test confidence level</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>A</td>
                  <td class="align-right">""" + f"{r.users_A:,}" + """</td>
                  <td class="align-right">""" + f"{r.RPU_A:.2f}" + """</td>
                  <td class="align-right">""" + f"{r.std_B:.2f}" + """</td>
                  <td></td>
                  <td></td>
                  <td></td>
                  <td></td>
                </tr>
                <tr>
                  <td>B</td>
                  <td class="align-right">""" + f"{r.users_B:,}" + """</td>
                  <td class="align-right">""" + f"{r.RPU_B:.2f}" + """</td>
                  <td class="align-right">""" + f"{r.std_B:.2f}" + """</td>
                  <td class="align-right">""" + f"{r.uplift:.2%}" + """</td>
                  <td class="align-right">""" + f"{r.p_value:.5f}" + """</td>
                  <td class="align-right move-tds">""" + f"{r.conf_level:.2%}" + """</td>
                </tr>
              </tbody>
            </table>
            <br>""" + projection_text + """
        </div>"""
        return ui.HTML(main_result_info)
        
    @output
    @render.ui
    @reactive.event(input.compute)
    def data_distributions_plots():
        """
        Plots the data distributions of A and B embeded in a div with explanation and returns the HTML content.
        """
        data_distributions_html = """
        <div class="block">
            <h3>Data distributions</h3>
            <div id="test-results-chart" class="">""" + str(ui.output_plot("plot_1")) + """</div>
        </div>"""
        return ui.HTML(data_distributions_html)   
    
    @output
    @render.plot
    @reactive.event(input.compute)
    def plot_1():
        return r.plot_data_distributions()
    
    @output
    @render.text
    @reactive.event(input.compute)
    def file_content():
        """
        file_content function to process file information and return a formatted string of its contents.
        Not used at the moment, only during the development. But could be useful in a new tab, showing the
        contents of the uploaded file, so the user can verify that the file uploaded for calculations is the correct one.
        """
        file_infos = input.file1()
        if not file_infos:
            return

        # file_infos is a list of dicts; each dict represents one file. Example:
        # [
        #   {
        #     'name': 'data.csv',
        #     'size': 2601,
        #     'datapath': '/tmp/fileupload-1wnx_7c2/tmpga4x9mps/0.csv'
        #   }
        # ]
        out_str = ""
        for file_info in file_infos:
            out_str += (
                "=" * 47
                + "\n"
                + file_info["name"]
                + "\nSize: "
                + str(file_info["size"])
            )
            if file_info["size"] > MAX_SIZE_FILE:
                out_str += f"\nTruncating at {MAX_SIZE_FILE} bytes."

            out_str += "\n" + "=" * 47 + "\n"

            with open(file_info["datapath"], "r") as f:
                out_str += f.read(MAX_SIZE_FILE)

        return out_str

app = App(app_ui, server, debug=False)


