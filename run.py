from flask import Flask, request, render_template, redirect,url_for
import pandas as pd
import os
import numpy as np

app = Flask(__name__ , template_folder='Templates')
UPLOAD_FOLDER = 'Uploaded File'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST']) 
def upload_file():
        
     if 'file' not in request.files:
        return redirect(request.url)
    
     file = request.files['file']
     if file.filename == '':
        return redirect(request.url)

     if file:
          filename = file.filename
          file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
          file.save(file_path)
          return redirect(url_for('show_csv', filename=filename))
     
@app.route('/Upload/<filename>')
def show_csv(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = pd.read_csv(file_path,encoding= 'unicode_escape' )

    count = len(df['CallerId'])
    
    def transform_tariff_description(tariff):
        if tariff in ['USA toll free', 'USA-Toll free', 'USTollfree']:
            return 'Tollfree'
        else:
            return 'Non-Toll free'
        

    df['Tariff'] = df['Tariff'].apply(lambda x: x if x.startswith(('PTT', 'PulsePTT')) else None)


    df['TariffDescription'] = df['TariffDescription'].apply(transform_tariff_description)

    df['Minutes'] = df['Duration'].astype(int)
    df['Minutes'] = (df['Duration']*(1440/60))

    df['Total_min'] = df['Minutes']

    df['Total_cost'] = df['Cost']

    negative_bal= (df['ClientCost'])-(df['Cost']*83)
    df['Negative'] = negative_bal.round(4)

    df['Route'] = df['Route'].astype(str)
    df.loc[df['Route'].str.startswith(('4', '5', '8', '7')), 'Route'] = 'Incoming'

    grp = df.groupby('TariffDescription')['Total_min'].sum()
    tarriff = grp.index.to_list()
    total_min2 = grp.values.tolist()

    grp1 = df.groupby('TariffDescription')['Total_cost'].sum()
    total_cost3 = grp1.values.tolist()
    new_df3 = pd.DataFrame({'tarriff': tarriff, 'total_min2': total_min2, 'total_cost3': total_cost3})
    data_list3 = new_df3.to_dict(orient='records')

    grouped_dff = df.groupby(['Route', 'Login', 'TariffPrefix', 'Tariff']).agg({'Negative': 'sum'}).reset_index()
    route31 = grouped_dff['Route'].tolist()
    Login31 = grouped_dff['Login'].tolist()
    TariffPrefix31 = grouped_dff['TariffPrefix'].tolist()
    Tariff31 = grouped_dff['Tariff'].tolist()
    neg31 = grouped_dff['Negative'].tolist()
    new_df31 = pd.DataFrame({'route31': route31, 'neg31': neg31, 'Login31': Login31,'Tariff31':Tariff31, 'TariffPrefix31': TariffPrefix31})
    new_df41 = new_df31[new_df31['neg31'].lt(0) ].round(3)
    data_list31 = new_df41.to_dict(orient='records')

    grouped_df1 = df.groupby('Route')['Total_min'].sum()
    grouped_df1 = np.round(grouped_df1,4)
    Route1 = grouped_df1.index.to_list()
    Total_min1 = grouped_df1.values.tolist()

    grouped_df2 = df.groupby('Route')['Total_cost'].sum()
    grouped_df2 = np.round(grouped_df2,4)
    total_cost = grouped_df2.values.tolist() 
    new_df = pd.DataFrame({'Route1': Route1, 'Total_min1': Total_min1,'total_cost' : total_cost})
    data_list = new_df.to_dict(orient='records')

    """Negative Balance Route wise"""
    
    # grouped_df3 = df.groupby('Route')['Negative'].sum().reset_index()
    # route3 = grouped_df3['Route'].to_list()
    # neg = grouped_df3['Negative'].tolist()
    # new_df2 = pd.DataFrame({'route3':route3, 'neg1': neg})
    # negative_balances_df = new_df2[new_df2['neg1'] < 0].round(4)
    # data_list2 = negative_balances_df.to_dict(orient='records')

    """Negative Balance Login wise"""

    # grouped_df6 = df.groupby('Login')['Negative'].sum()
    # grouped_df7 = grouped_df6.reset_index()
    # grouped_df7.columns = ['Login', 'Negative']
    # negative_balances_df1 = grouped_df7[grouped_df7['Negative'] < 0].round(4)

    # neg_login= [f"{row['Login']} {row['Negative']}" for _, row in negative_balances_df1.iterrows()]

    """Negative Balance TariffPrefix wise"""

    # grouped_df8 = df.groupby('TariffPrefix')['Negative'].sum()
    # grouped_df9 = grouped_df8.reset_index()
    # grouped_df9.columns = ['TariffPrefix', 'Negative']
    # negative_balances_df2 = grouped_df9[grouped_df9['Negative'] < 0].round(4)
    # neg_tarrif = [f"{row['TariffPrefix']} {row['Negative']}" for _, row in negative_balances_df2.iterrows()]


    grouped_df = df.groupby(['Route']).agg({
      'Total_cost': 'sum',
      'Total_min': 'sum',
      'Negative' : 'sum'
      }).reset_index()
   
    grand_total_cost = grouped_df['Total_cost'].sum()
    grand_total_cost = np.round(grand_total_cost,4)
    grand_total_min = grouped_df['Total_min'].sum()
    grand_total_min = np.round(grand_total_min,4)
    grand_total_neg = grouped_df['Negative'].sum()
    grand_total_neg = np.round(grand_total_neg,4)
                 
    return render_template('display.html',
                           count = count,
                           new_df1=data_list3,
                           new_df=data_list,
                           grand_total_cost=grand_total_cost, 
                           grand_total_min=grand_total_min,
                           grand_total_neg = grand_total_neg,
                           tot = data_list31
                           )
      
if __name__ == "__main__":
    app.run(host='0.0.0.0' ,port = 80)
