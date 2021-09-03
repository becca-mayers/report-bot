# -*- coding: utf-8 -*-
"""
Created on Thu Jul  1 11:43:42 2021

@author: beccamayers
"""

from data_generator import generate_data
from datetime import datetime
import pandas as pd
import pathlib

def get_variables():
    
    #paths
    base_folder_path = str(pathlib.Path(__file__).parent.absolute())
    
    #determine if this is an odd or an even month
    current_month = datetime.today().month
    
    los_df, obs_df, tiers, facilities, tiered_locations = generate_data()
    
    los_df = los_df.rename(columns={'Reporting Month':'StrDate'})
    obs_df = obs_df.rename(columns={'Reporting Month':'StrDate'})
    
    los_df['Reporting Month'] = pd.to_datetime(los_df['StrDate'])
    obs_df['Reporting Month'] = pd.to_datetime(obs_df['StrDate'])
    
    ''' dates '''
    current_month = max(los_df['Reporting Month'])
    current_month_month = current_month.month
    current_month_year = current_month.year
    current_month_readable = current_month.strftime('%B %Y')
    
    last_month = datetime(current_month_year, current_month_month-1, 1)
    last_month_readable = last_month.strftime('%B %Y')
    
    los_dfff = los_df.groupby(['Facility', 'Fiscal Year', 'Tiers'], as_index=False).agg({'LOS':'sum', 'GMLOS':'sum', 'OppDays':'sum'})    
    obs_dfff = obs_df.groupby(['Facility', 'Fiscal Year', 'Tiers'], as_index=False).agg({'Obs_Cases':'sum', 'Obs_Hours_48':'sum', 'Obs_Rate_Inp':'sum'})
    
    tiered_this_fiscal_los_df = los_dfff.loc[los_dfff['Tiers'].isin(['B','C'])]
    tiered_this_fiscal_obs_df = obs_dfff.loc[obs_dfff['Tiers'].isin(['B','C'])]
    
    ''' fiscal '''
    last_fiscal_los_df = los_dfff.loc[los_dfff['Fiscal Year'] == 'FY2020']
    last_fiscal_obs_df = obs_dfff.loc[obs_dfff['Fiscal Year'] == 'FY2020']
    this_fiscal_los_df = los_dfff.loc[los_dfff['Fiscal Year'] == 'FY2021']
    this_fiscal_obs_df = obs_dfff.loc[obs_dfff['Fiscal Year'] == 'FY2021']
    tiered_last_fiscal_los_df = tiered_this_fiscal_los_df.loc[tiered_this_fiscal_los_df['Fiscal Year'] == 'FY2020']   
    tiered_last_fiscal_obs_df = tiered_this_fiscal_obs_df.loc[tiered_this_fiscal_obs_df['Fiscal Year'] == 'FY2020'] 
    tiered_this_fiscal_obs_df = tiered_this_fiscal_obs_df.loc[tiered_this_fiscal_obs_df['Fiscal Year'] == 'FY2021']
    tiered_this_fiscal_los_df = tiered_this_fiscal_los_df.loc[tiered_this_fiscal_los_df['Fiscal Year'] == 'FY2021']
       
    #make LOS Ratio
    this_fiscal_los_df['LOSRatio'] = round(this_fiscal_los_df['LOS']/this_fiscal_los_df['GMLOS'])
    last_fiscal_los_df['LOSRatio'] = round(last_fiscal_los_df['LOS']/last_fiscal_los_df['GMLOS'])
    tiered_this_fiscal_los_df['LOSRatio'] = round(tiered_this_fiscal_los_df['LOS']/tiered_this_fiscal_los_df['GMLOS'])
    tiered_last_fiscal_los_df['LOSRatio'] = round(tiered_last_fiscal_los_df['LOS']/tiered_last_fiscal_los_df['GMLOS'])
    
    #Make Observation Rates
    this_fiscal_obs_df['ObservationRates'] = round((this_fiscal_obs_df['Obs_Cases']/(this_fiscal_obs_df['Obs_Cases'] + this_fiscal_obs_df['Obs_Rate_Inp']))*100)  
    last_fiscal_obs_df['ObservationRates'] = round((last_fiscal_obs_df['Obs_Cases']/(last_fiscal_obs_df['Obs_Cases'] + last_fiscal_obs_df['Obs_Rate_Inp']))*100)
    tiered_this_fiscal_obs_df['ObservationRates'] = round((tiered_this_fiscal_obs_df['Obs_Cases']/(tiered_this_fiscal_obs_df['Obs_Cases'] + tiered_this_fiscal_obs_df['Obs_Rate_Inp']))*100)                                  
    tiered_last_fiscal_obs_df['ObservationRates'] = round((tiered_last_fiscal_obs_df['Obs_Cases']/(tiered_last_fiscal_obs_df['Obs_Cases'] + tiered_last_fiscal_obs_df['Obs_Rate_Inp']))*100)
        
    metric1 = 'LOS Ratio'
    metric2 = 'opportunity days'
    metric3 = 'observation rate'
    metric4 = 'observation cases > 48 hours'    
    areas = [metric1, metric2, metric3, metric4]
    actions = ['Increase', 'Decrease', 'Review', 'Replace']
    
    #visuals   
    icon_classes = ['"material-icons md-48 success"', '"material-icons md-48 secondary"', '"material-icons md-48 info"', '"material-icons md-48 primary"'] 
    icons = ['healing', 'self_improvement', 'health_and_safety', 'hourglass_empty', 'find_replace', 'child_friendly', 'spa', 'monitor_weight']    
    arrow_up = '<i class="material-icons md-36 warning">trending_up</i>' #arrow_upward
    arrow_down = '<i class="material-icons md-36 success">trending_down</i>' #arrow_downward
    arrow_right = '<i class="material-icons md-36 info">trending_flat</i>'#arrow_forward
    arrow_up_white = '<i class="material-icons md-36 white">trending_up</i>'
    arrow_down_white = '<i class="material-icons md-36 white">trending_down</i>'
    arrow_right_white = '<i class="material-icons md-36 white">trending_flat</i>'
    question_mark = '<i class="material-icons-outlined md-36">help</i>'   
    css_file = base_folder_path + '/templates/material-dashboard.css'
    extended_css_file = base_folder_path + '/templates/extended.css'

    return (current_month_readable,
            last_month_readable,
            this_fiscal_los_df,
            this_fiscal_obs_df,
            last_fiscal_los_df,
            last_fiscal_obs_df, 
            tiered_this_fiscal_los_df,
            tiered_last_fiscal_los_df,
            tiered_this_fiscal_obs_df, 
            tiered_last_fiscal_obs_df, 
            metric1, metric2, metric3, metric4,
            arrow_up,
            arrow_down,
            arrow_right,
            question_mark,
            arrow_up_white,
            arrow_down_white,
            arrow_right_white,  
            icon_classes, icons, areas, actions,   
            tiers,
            facilities,
            tiered_locations,
            css_file,
            extended_css_file,
            base_folder_path)
    
