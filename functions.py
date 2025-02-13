import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from openai import OpenAI
from datetime import datetime
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import plotly.express as px
import os
from io import StringIO


def prepare_prompt(user_prompt,history_info):
    '''收入多少，各类型支出多少，'''
    df=history_info
    df['timestamp'] = df['timestamp'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))
    df["month"]=df["timestamp"].apply(lambda x:x.month)
    df_spend = df.groupby(["month","income_or_spending"],as_index=False).agg({"amount":"sum"}).query("""income_or_spending==0""")
    df_income= df.groupby(["month","income_or_spending"],as_index=False).agg({"amount":"sum"}).query("""income_or_spending==1""")
    
    text_all=""  #每月支出和收入
    for i in range(df_income.shape[0]):
        income=df_income.iloc[i,:]
        spend=df_spend.iloc[i,:]
        text_unit=f"In month {i+1}, the spending is {spend[-1]} and the income is {income[-1]}. "
        text_all += text_unit
    
    df_income_type = df.groupby(["income_or_spending","type"],as_index=False).agg({"amount":"sum"}).query("""income_or_spending==1""")
    df_spend_type = df.groupby(["income_or_spending","type"],as_index=False).agg({"amount":"sum"}).query("""income_or_spending==0""")

    income_type_info='' #不同收入类型
    for i in range(df_income_type.shape[0]):
        info=df_income_type.iloc[i,:]
        type=f'The income type is {info[-2]}, the amount is {info[-1]}.'
        income_type_info+=type

    spend_type_info='' #不同支出类型
    for i in range(df_spend_type.shape[0]):
        info=df_spend_type.iloc[i,:]
        type=f'The spending type is {info[-2]}, the amount is {info[-1]}.'
        spend_type_info+=type

    
    prompt = "here is my monthly income and spending information:" + "\n" + text_all + "\n" + "here is my income type information" + income_type_info + "here is my spend type information" + spend_type_info
    prompt = "here is my goal: " + user_prompt
    return prompt




def chat_with_gpt(user_input):
    
    '''
    description: 
        this function call openai api to make users able to interact with chatgpt within this website

    parameters:
        None
    
    output:
        print the response from chat-gpt

    '''
    client = OpenAI(
    api_key=os.getenv("api_key"),
    )
    conversation = [{"role": "system", "content": "You are a helpful assistant. And you need to give the user detailed financial plan to achieve his goal."}]
    try:
        conversation.append({"role": "user", "content": user_input})
        chat_completion = client.chat.completions.create(
            messages=conversation,
            model="gpt-4o-mini",
                    )
        assistant_reply = chat_completion.choices[0].message.content
        conversation.append({"role": "assistant", "content": assistant_reply})
        return assistant_reply

    except TimeoutError:
        print("error")



def load_data():
    data_sample = """
timestamp,income_or_spending,type,amount
2024-01-01,0,Healthcare,1806.08
2024-01-02,1,Bonus,2773.64
2024-01-03,0,Transport,1654.65
2024-01-04,0,Shopping,646.9
2024-01-05,0,Rent,1792.09
2024-01-06,1,Gift,2251.41
2024-01-07,0,Food,31.57
2024-01-08,0,Shopping,1811.71
2024-01-09,0,Shopping,191.66
2024-01-10,1,Salary,1936.91
2024-01-11,0,Rent,1900.62
2024-01-12,0,Food,1901.71
2024-01-13,0,Healthcare,1151.14
2024-01-14,0,Shopping,1267.36
2024-01-15,1,Salary,2518.0
2024-01-16,0,Entertainment,593.49
2024-01-17,1,Gift,1978.99
2024-01-18,1,Investment,3526.33
2024-01-19,1,Investment,3885.69
2024-01-20,0,Food,1585.24
2024-01-21,1,Salary,4053.28
2024-01-22,0,Transport,191.5
2024-01-23,1,Investment,2724.89
2024-01-24,1,Gift,759.01
2024-01-25,1,Gift,2972.88
2024-01-26,1,Investment,2486.89
2024-01-27,1,Gift,4494.67
2024-01-28,1,Gift,2079.12
2024-01-29,1,Bonus,1026.8
2024-01-30,1,Gift,1143.46
2024-01-31,0,Food,1525.41
2024-02-01,0,Shopping,1240.25
2024-02-02,1,Investment,955.05
2024-02-03,1,Salary,878.48
2024-02-04,1,Gift,3654.36
2024-02-05,0,Shopping,154.8
2024-02-06,1,Bonus,4198.37
2024-02-07,0,Shopping,1415.42
2024-02-08,0,Healthcare,171.88
2024-02-09,0,Transport,178.83
2024-02-10,0,Healthcare,1973.41
2024-02-11,0,Food,754.8
2024-02-12,1,Investment,2167.89
2024-02-13,1,Salary,4157.6
2024-02-14,1,Salary,4762.62
2024-02-15,1,Bonus,4937.0
2024-02-16,1,Gift,3890.2
2024-02-17,0,Healthcare,758.76
2024-02-18,1,Bonus,875.75
2024-02-19,1,Bonus,3997.16
2024-02-20,0,Healthcare,1121.22
2024-02-21,1,Investment,2409.0
2024-02-22,0,Entertainment,1813.65
2024-02-23,1,Salary,1000.39
2024-02-24,0,Shopping,990.32
2024-02-25,1,Salary,551.09
2024-02-26,1,Gift,2608.97
2024-02-27,0,Food,122.04
2024-02-28,0,Healthcare,246.45
2024-02-29,0,Entertainment,243.88
2024-03-01,0,Shopping,1301.93
2024-03-02,0,Transport,1494.63
2024-03-03,0,Food,1170.9
2024-03-04,0,Food,1924.72
2024-03-05,0,Shopping,755.99
2024-03-06,1,Investment,1785.7
2024-03-07,1,Investment,4408.7
2024-03-08,0,Healthcare,454.96
2024-03-09,1,Investment,4834.5
2024-03-10,1,Bonus,554.7
2024-03-11,1,Bonus,4864.45
2024-03-12,1,Bonus,694.22
2024-03-13,0,Healthcare,1783.37
2024-03-14,1,Bonus,2874.65
2024-03-15,0,Entertainment,1986.0
2024-03-16,1,Investment,832.08
2024-03-17,1,Bonus,2992.34
2024-03-18,1,Gift,4861.86
2024-03-19,0,Transport,1050.96
2024-03-20,1,Investment,3332.29
2024-03-21,0,Rent,1394.54
2024-03-22,1,Salary,2545.43
2024-03-23,0,Healthcare,1258.84
2024-03-24,1,Salary,3129.41
2024-03-25,0,Shopping,1803.3
2024-03-26,0,Food,100.44
2024-03-27,1,Salary,1764.33
2024-03-28,0,Shopping,1901.32
2024-03-29,1,Salary,4506.19
2024-03-30,1,Gift,2550.46
2024-03-31,1,Investment,3290.6
2024-04-01,1,Gift,1748.22
2024-04-02,1,Investment,1346.55
2024-04-03,1,Gift,2586.64
2024-04-04,1,Salary,2090.09
2024-04-05,1,Gift,3126.45
2024-04-06,1,Salary,849.81
2024-04-07,1,Gift,4884.78
2024-04-08,1,Gift,4937.95
2024-04-09,0,Healthcare,1399.34
2024-04-10,0,Entertainment,1076.83
2024-04-11,1,Bonus,1892.87
2024-04-12,1,Salary,4162.08
2024-04-13,1,Bonus,3581.29
2024-04-14,1,Investment,1231.78
2024-04-15,1,Gift,4599.17
2024-04-16,1,Salary,4201.42
2024-04-17,1,Salary,4774.1
2024-04-18,1,Gift,3765.74
2024-04-19,0,Entertainment,1230.7
2024-04-20,1,Salary,2382.09
2024-04-21,0,Healthcare,1866.13
2024-04-22,1,Salary,4397.29
2024-04-23,1,Investment,703.48
2024-04-24,0,Transport,62.47
2024-04-25,1,Gift,2194.09
2024-04-26,0,Food,1623.0
2024-04-27,1,Gift,4942.74
2024-04-28,1,Investment,1176.88
2024-04-29,0,Entertainment,1192.32
2024-04-30,1,Salary,2214.01
2024-05-01,0,Food,1940.13
2024-05-02,1,Gift,4289.54
2024-05-03,0,Transport,1678.27
2024-05-04,0,Rent,942.7
2024-05-05,1,Salary,2366.69
2024-05-06,1,Bonus,1730.33
2024-05-07,0,Healthcare,122.19
2024-05-08,1,Bonus,4391.25
2024-05-09,1,Investment,4158.05
2024-05-10,1,Gift,4998.73
2024-05-11,0,Healthcare,1993.31
2024-05-12,0,Rent,1115.31
2024-05-13,0,Healthcare,1540.28
2024-05-14,0,Rent,1890.08
2024-05-15,0,Transport,1700.8
2024-05-16,0,Rent,502.22
2024-05-17,0,Rent,906.58
2024-05-18,0,Rent,267.03
2024-05-19,0,Food,1908.56
2024-05-20,1,Gift,3227.79
2024-05-21,0,Food,465.0
2024-05-22,1,Salary,3522.65
2024-05-23,1,Investment,3281.58
2024-05-24,1,Bonus,2111.73
2024-05-25,0,Entertainment,235.98
2024-05-26,0,Rent,1346.43
2024-05-27,0,Rent,1045.41
2024-05-28,0,Transport,1546.91
2024-05-29,1,Bonus,2840.74
2024-05-30,0,Food,1705.84
2024-05-31,0,Entertainment,1108.29
2024-06-01,0,Shopping,1126.27
2024-06-02,0,Rent,1754.54
2024-06-03,0,Food,812.93
2024-06-04,1,Gift,1103.07
2024-06-05,0,Entertainment,67.28
2024-06-06,1,Gift,3898.12
2024-06-07,0,Food,1244.42
2024-06-08,1,Gift,3668.36
2024-06-09,0,Healthcare,433.8
2024-06-10,0,Healthcare,281.38
2024-06-11,1,Gift,565.45
2024-06-12,1,Investment,2077.64
2024-06-13,1,Investment,3154.63
2024-06-14,0,Shopping,790.57
2024-06-15,1,Bonus,2468.64
2024-06-16,0,Rent,1809.28
2024-06-17,0,Healthcare,703.03
2024-06-18,1,Investment,2812.95
2024-06-19,1,Salary,4026.44
2024-06-20,0,Rent,799.12
2024-06-21,0,Healthcare,1247.95
2024-06-22,1,Salary,4380.64
2024-06-23,1,Bonus,4772.84
2024-06-24,1,Bonus,1161.83
2024-06-25,0,Rent,1853.91
2024-06-26,0,Healthcare,989.31
2024-06-27,0,Food,523.91
2024-06-28,0,Shopping,923.68
2024-06-29,0,Rent,1960.26
2024-06-30,0,Healthcare,990.31
2024-07-01,1,Investment,1979.38
2024-07-02,0,Healthcare,1270.47
2024-07-03,0,Transport,487.89
2024-07-04,0,Shopping,160.97
2024-07-05,1,Salary,1079.96
2024-07-06,0,Food,264.81
2024-07-07,0,Entertainment,312.29
2024-07-08,1,Gift,1124.72
2024-07-09,0,Shopping,1285.34
2024-07-10,0,Shopping,371.94
2024-07-11,0,Entertainment,697.88
2024-07-12,0,Shopping,1794.61
2024-07-13,0,Healthcare,953.18
2024-07-14,1,Salary,3504.01
2024-07-15,1,Gift,1275.44
2024-07-16,1,Gift,1365.3
2024-07-17,0,Healthcare,91.33
2024-07-18,0,Transport,346.18
2024-07-19,0,Shopping,564.39
2024-07-20,1,Gift,1296.55
2024-07-21,0,Entertainment,186.52
2024-07-22,0,Rent,250.07
2024-07-23,1,Gift,2573.5
2024-07-24,0,Rent,420.6
2024-07-25,1,Bonus,2139.21
2024-07-26,1,Investment,2765.38
2024-07-27,1,Salary,3606.78
2024-07-28,0,Transport,88.23
2024-07-29,0,Shopping,1600.83
2024-07-30,0,Rent,1259.52
2024-07-31,0,Rent,172.7
2024-08-01,0,Entertainment,1748.42
2024-08-02,0,Rent,1842.54
2024-08-03,0,Entertainment,131.55
2024-08-04,1,Bonus,1745.95
2024-08-05,0,Food,1614.34
2024-08-06,1,Gift,3867.17
2024-08-07,0,Entertainment,377.2
2024-08-08,0,Food,426.61
2024-08-09,0,Rent,747.24
2024-08-10,1,Bonus,2680.35
2024-08-11,1,Salary,3282.15
2024-08-12,1,Investment,2160.11
2024-08-13,1,Bonus,2581.41
2024-08-14,0,Healthcare,1497.47
2024-08-15,1,Bonus,665.07
2024-08-16,0,Food,512.35
2024-08-17,0,Entertainment,1429.57
2024-08-18,1,Salary,4528.43
2024-08-19,1,Salary,2802.55
2024-08-20,1,Gift,2894.51
2024-08-21,1,Salary,982.27
2024-08-22,1,Investment,2513.36
2024-08-23,1,Gift,2896.78
2024-08-24,1,Investment,1591.12
2024-08-25,1,Salary,1711.59
2024-08-26,0,Healthcare,760.8
2024-08-27,1,Salary,590.32
2024-08-28,1,Investment,1949.36
2024-08-29,0,Transport,430.78
2024-08-30,1,Gift,1973.74
2024-08-31,0,Rent,248.33
2024-09-01,0,Transport,1782.15
2024-09-02,1,Salary,3171.17
2024-09-03,0,Healthcare,1361.41
2024-09-04,0,Food,1580.45
2024-09-05,0,Entertainment,1001.9
2024-09-06,0,Healthcare,182.97
2024-09-07,1,Gift,2916.98
2024-09-08,0,Entertainment,1177.81
2024-09-09,1,Investment,3854.48
2024-09-10,0,Food,869.0
2024-09-11,0,Healthcare,263.88
2024-09-12,0,Healthcare,574.71
2024-09-13,0,Healthcare,732.53
2024-09-14,1,Gift,3406.63
2024-09-15,1,Salary,3068.5
2024-09-16,0,Shopping,718.63
2024-09-17,0,Rent,1973.17
2024-09-18,1,Bonus,3225.99
2024-09-19,0,Entertainment,482.08
2024-09-20,0,Shopping,212.55
2024-09-21,0,Food,314.19
2024-09-22,1,Bonus,1606.81
2024-09-23,1,Bonus,1223.07
2024-09-24,1,Salary,1339.55
2024-09-25,0,Rent,577.34
2024-09-26,0,Rent,355.01
2024-09-27,1,Bonus,4535.44
2024-09-28,1,Salary,861.05
2024-09-29,1,Gift,2860.3
2024-09-30,1,Bonus,2346.79
2024-10-01,0,Shopping,1964.93
2024-10-02,1,Investment,1004.18
2024-10-03,0,Rent,801.73
2024-10-04,1,Bonus,4862.62
2024-10-05,0,Transport,1732.36
2024-10-06,1,Bonus,4176.82
2024-10-07,1,Gift,1660.56
2024-10-08,1,Salary,1268.99
2024-10-09,1,Gift,3508.89
2024-10-10,0,Entertainment,1859.46
2024-10-11,1,Salary,3005.43
2024-10-12,0,Shopping,1147.51
2024-10-13,0,Rent,567.16
2024-10-14,0,Food,1541.29
2024-10-15,0,Shopping,382.22
2024-10-16,1,Gift,1956.56
2024-10-17,0,Transport,856.62
2024-10-18,0,Shopping,1020.14
2024-10-19,0,Shopping,492.4
2024-10-20,1,Bonus,1016.77
2024-10-21,1,Investment,3247.79
2024-10-22,1,Gift,1798.84
2024-10-23,1,Salary,3115.57
2024-10-24,0,Food,317.18
2024-10-25,0,Entertainment,967.47
2024-10-26,1,Investment,2896.65
2024-10-27,0,Transport,113.13
2024-10-28,0,Entertainment,679.84
2024-10-29,0,Shopping,277.49
2024-10-30,1,Investment,785.19
2024-10-31,1,Salary,4954.82
2024-11-01,0,Food,651.48
2024-11-02,1,Gift,4144.44
2024-11-03,1,Bonus,1645.88
2024-11-04,1,Investment,3566.76
2024-11-05,1,Gift,3921.03
2024-11-06,1,Salary,3180.37
2024-11-07,0,Entertainment,948.44
2024-11-08,1,Gift,2353.28
2024-11-09,0,Healthcare,704.25
2024-11-10,0,Rent,1859.76
2024-11-11,1,Salary,4237.79
2024-11-12,0,Transport,1930.4
2024-11-13,0,Rent,257.35
2024-11-14,0,Transport,1464.43
2024-11-15,1,Investment,4722.53
2024-11-16,1,Salary,1315.55
2024-11-17,0,Rent,142.33
2024-11-18,1,Gift,3835.04
2024-11-19,1,Salary,3085.13
2024-11-20,1,Bonus,4288.23
2024-11-21,1,Bonus,1128.98
2024-11-22,0,Rent,1592.58
2024-11-23,0,Healthcare,411.24
2024-11-24,1,Bonus,1236.45
2024-11-25,1,Investment,1239.2
2024-11-26,0,Food,1631.0
2024-11-27,0,Shopping,1333.74
2024-11-28,1,Bonus,2853.79
2024-11-29,0,Entertainment,724.07
2024-11-30,1,Bonus,4447.4
2024-12-01,1,Salary,2266.0
2024-12-02,0,Transport,1635.03
2024-12-03,0,Entertainment,883.88
2024-12-04,1,Gift,2196.25
2024-12-05,1,Gift,2582.06
2024-12-06,0,Food,609.74
2024-12-07,1,Salary,3864.24
2024-12-08,0,Entertainment,1010.41
2024-12-09,1,Salary,1544.96
2024-12-10,0,Shopping,1800.15
2024-12-11,0,Rent,773.94
2024-12-12,0,Entertainment,1091.67
2024-12-13,1,Salary,4579.12
2024-12-14,1,Gift,3309.07
2024-12-15,0,Transport,242.63
2024-12-16,1,Salary,4729.24
2024-12-17,0,Transport,1259.14
2024-12-18,0,Shopping,676.46
2024-12-19,1,Bonus,1126.72
2024-12-20,1,Salary,4073.11
2024-12-21,0,Healthcare,1243.94
2024-12-22,1,Gift,2900.57
2024-12-23,1,Salary,4522.52
2024-12-24,0,Shopping,1579.31
2024-12-25,0,Food,311.83
2024-12-26,1,Investment,1902.75
2024-12-27,0,Entertainment,504.49
2024-12-28,0,Food,1490.45
2024-12-29,1,Investment,650.9
2024-12-30,0,Food,1144.08
2024-12-31,0,Healthcare,1527.29
"""
    df = pd.read_csv(StringIO(data_sample))
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['month'] = df['timestamp'].dt.month
    return df

def get_monthly_summary(df):
    income = df[df.income_or_spending == 1].groupby('month').amount.sum().rename('income')
    spending = df[df.income_or_spending == 0].groupby('month').amount.sum().rename('spending')
    return pd.concat([income, spending], axis=1).reset_index().fillna(0)

def get_month_type_data(df, month, category):
    filtered = df[(df.month == month) & (df.income_or_spending == category)]
    return filtered.groupby('type', as_index=False).amount.sum()