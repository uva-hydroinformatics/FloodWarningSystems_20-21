import run.http_get, run.parser

data = run.http_get.get_data()
transformed_data = run.parser.parse_data(data)

print(data)
print("done")