import os
import csv
from pyproj import Proj, transform
from re import sub

inProj = Proj(init='EPSG:25832')
outProj = Proj(init='epsg:4326')

headers_cykelstativ = {'id':'INT',
               'bydel':'VARCHAR(100)',
               'stativ_placering':'VARCHAR(100)',
               'vejnavn': 'VARCHAR(100)',
               'wkb_geometry':'GEOMETRY NOT NULL SRID 4326'}

headers_tungvognsnet = {
    'id': 'VARCHAR(100)',
    'wkb_geometry': 'GEOMETRY NOT NULL SRID 4326',
    'vej': 'VARCHAR(100)'
}

headers_gadetraer = {
    'id': 'INT',
    'traeart': 'VARCHAR(100)',
    'wkb_geometry': 'GEOMETRY NOT NULL SRID 4326'
}

headers_f_udsatte_byomraader = {
    'id': 'INT',
    'byomraade': 'VARCHAR(100)',
    'wkb_geometry': 'GEOMETRY NOT NULL SRID 4326'
}

def transformer(x,y):
    # point is on the form "722942.66 6173097.7"
    ll = transform(inProj, outProj, x,y)
    return str(ll[0])+' '+str(ll[1])


def geom_transformer(geom):
    reg_ex="([0-9.]+) ([0-9.]+)" # pick out two numbers with a space inbetween
    return sub(reg_ex, lambda m: transformer(m.group(1), m.group(2)), geom)

def makeInsertStatements(name, headers, infile, outfile):
    print("Writing inserts ",end='')
    headerline = infile.readline()
    csv_headers = headerline.rstrip().split(",")
    headerIndex = { h : csv_headers.index(h) for h in headers.keys()}
    sql = ""
    csv_in = csv.reader(infile, delimiter=',', quotechar='"')
    for row in csv_in:
        print('.',end='')
        if row[-1] != "": # some positions are missing
            sql_values = [valueOf(row[headerIndex[k]], headers[k]) for k in headers.keys()]
            values_combined = ','.join(sql_values)
            columns = ','.join(headers.keys())
            sql += f"INSERT INTO {name} ( {columns} ) VALUES ({values_combined});\n"
    return sql

def valueOf(v, sql_type):
    if sql_type == "INT":
        return v
    if sql_type[0:8] == "GEOMETRY":
        c = geom_transformer(v) # This is where I convert from EPSG:25832' to 'epsg:4326'
        return f'ST_GeomFromText("{c}", 4326)'
    v = v.replace("'", "")
    return f'"{v}"'

def createTable(name, headers):
    sql = f"drop table if exists {name};\n"
    sql += f"create table {name} (\n"
    sql += ", \n".join([f"\t{header} {sql_type}" for header,sql_type in headers.items()])
    sql += f",\n\tprimary key({list(headers.keys())[0]})\n);\n"
    print(f'created table {name}')
    return sql

def makeSQLFile(file_name, headers):
    cwd = os.getcwd() # current working directory
    inputfile = open(f"{cwd}/{file_name}.csv","r")
    outputfile = open(f"{cwd}/{file_name}.sql", "w+")
    table = createTable(file_name, headers)
    inserts = makeInsertStatements(file_name, headers, inputfile, outputfile)
    outputfile.write(table)
    outputfile.write(inserts)
    outputfile.close()

# makeSQLFile("cykelstativ", headers_cykelstativ)
# makeSQLFile("tungvognsnet", headers_tungvognsnet)
makeSQLFile("gadetraer", headers_gadetraer)
makeSQLFile("f_udsatte_byomraader", headers_f_udsatte_byomraader)
