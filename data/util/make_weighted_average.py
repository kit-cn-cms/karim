import pandas as pd
import sys
infiles = sys.argv[1:]

dfnew = pd.read_csv(infiles[0].split("=")[0])
columns = dfnew.columns
columns = [c for c in columns if not c == "factor"]
print(columns)
dfnew.set_index(columns, inplace = True)
print(dfnew)
dfnew["factor"] = 0.
weightSum = 0.
for f in infiles:
    df = pd.read_csv(f.split("=")[0], index_col = columns)
    print(df)

    dfnew["factor"]+= df["factor"]*float(f.split("=")[1])
    weightSum += float(f.split("=")[1])

dfnew["factor"]/= weightSum
dfnew.to_csv("weightedAverages.csv", index = True, columns = columns+["factor"])
print(dfnew)
