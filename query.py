from scripts.query_parser import query_tool

if __name__ == "__main__":
    get = query_tool(fl = "/Users/christossynodinos/Documents/regex-query-tool/patterns.csv", pattern = "None")
    get.query()