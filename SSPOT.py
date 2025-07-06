print("Comienzo ejecución")
import TOOLKIT
from datetime import datetime, timedelta
import pandas as pd 
print("Librerias instaladas")
try:
    print("Inicializando clases")
    sspot = TOOLKIT.SSPOT()
    midway = TOOLKIT.midway(False)


    fcName = "HAJ1"
    startDate = datetime.now()

    print("Función de SSPOT")
    df = sspot.pullScheduleFCApi(fcName=fcName, 
                        cookies=midway.cookieDict, 
                        export= True)

    print(df)
    df.to_csv("pullScheduleFCApi.csv")

except Exception as error:
    print(f"Error: {error}")

finally: 
    input("Pulsa enter para terminar...")