from weasyprint import HTML
from jinja2 import Template
from pathlib import Path
import os

# all the INPUT fields in the firebase document
# 
# firebase   >  corresponds to iun UI

# c_cel      >  %C_cel
# c_wood     >  %C_wood
# carbon     >  d13C_wood
# d13C_cel   >  d13C_cel
# d18O_cel   >  d18O_cel
# n_wood     >  %N_wood
# nitrogen   >  d15N_wood
# oxygen     >  d18O_wood

# c_wood = [val_m1, valm2...]

# all the INPUT fields in the reference doc https://docs.google.com/document/d/1AHSZKS7JgLpQoDQ59yOSamP_tI-G2gIRspWLs2S_-l8/edit?resourcekey=0-iZNziq3gmAg7OnqHGIJlKw
# sampl            δ13C δ13C δ15N δ18O
# point            wood cell wood cell
# 0                ?    ?    ?    ?
# 25               ?    ?    ?    ?
# 50               ?    ?    ?    ?
# 75               ?    ?    ?    ?
# 100              ?    ?    ?    ?
# sample mean      ?    ?    ?    ?
# sample variance  ?    ?    ?    ?

# validity
#   4.248069198730162e-9
# validity_details
#   p_value_carbon
#     0.00034070435105630674
#   p_value_nitrogen
#     0.010445452763826784
#   p_value_oxygen
#     0.001193676470473496

# open questions ->
#   are all these values actually used in the origin validation code?
#   why does it have to have 2 or more? do we enforce that in the frontend somewhere?
#   do we have the latest isoscapes in earth engine?
#   


jinja_html_template = """
<!doctype html>
<html>
<style>
    table {
    border-collapse: collapse;
        font-family: Tahoma, Geneva, sans-serif;
    }
    table td {
        padding: 15px;
    }
    table thead td {
        background-color: #54585d;
        color: #ffffff;
        font-weight: bold;
        font-size: 13px;
        border: 1px solid #54585d;
    }
    table tbody td {
        color: #636363;
        border: 1px solid #dddfe1;
    }
    table tbody tr {
        background-color: #f9fafb;
    }
    table tbody tr:nth-child(odd) {
        background-color: #ffffff;
    }
</style>
<body>
    <h1>Origin verification of test sample</h1>
    <h2>Inputs</h2>
    <p>Sample identifier: xxx</p>
    <p>Claimed Tree species: xxx xxx</p>
    <p>Claimed Latitude: xx.xxxxx</p>
    <p>Claimed Longitude: xx.xxxxx</p>
    <p>Date of harvesting:  xxx xx, xxxx</p>
    <h3>Isotope values of test sample:</h3>
    <table>
<thead>
<tr>
    <td>Sample Point</td>
    <td>δ<sup>13</sup>C<br/>Wood</td>
    <td>δ<sup>13</sup>13C<br/>Cellulose</td>
    <td>δ<sup>15</sup>13N<br/>Wood</td>
    <td>δ<sup>18</sup>13O<br/>Cellulose</td>
</tr>
</thead>
    <tbody>
        <tr>
        <td>1</td>
        <td>0.000000</td>
        <td>0.000000</td>
        <td>0.000000</td>
        <td>0.000000</td>
        </tr>
        <tr>
        <td>2</td>
        <td>0.000000</td>
        <td>0.000000</td>
        <td>0.000000</td>
        <td>0.000000</td>
        </tr>
        <tr>
        <td>3</td>
        <td>0.000000</td>
        <td>0.000000</td>
        <td>0.000000</td>
        <td>0.000000</td>
        </tr>
        <tr>
        <td>4</td>
        <td>0.000000</td>
        <td>0.000000</td>
        <td>0.000000</td>
        <td>0.000000</td>
        </tr>
    </tbody>
    </table>
</body>
</html>
"""

test_items = [
    0.000000,
    0.000000,
    0.000000,
    0.000000,
]

def makepdf(document_id):
    # TODO: Apply changes from  https://stackoverflow.com/questions/72591126/how-to-create-google-cloud-storage-access-token-programmatically-python/72597432#72597432
    # before uploading

    # download_dir = os.getcwd()
    # html_file = os.path.join(download_dir, f'{document_id}.html')

    document_id = "example"
    download_dir = os.getcwd()
    htmldoc = HTML(string=html, base_url="")
    file_pdf_bytes = htmldoc.write_pdf()


    Path(os.path.join(download_dir, f'{document_id}.pdf')).write_bytes(file_pdf_bytes)

    htmldoc = HTML(string=html, base_url="")


