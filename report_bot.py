# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 16:42:05 2021

@author: beccamayers
"""
from selenium.webdriver.common.action_chains import ActionChains
from jinja2 import Environment as JinjaEnvironment
from report_variables import get_variables
from random import choice, randrange
from jinja2 import FileSystemLoader
from selenium import webdriver
from datetime import datetime
from PIL import Image
from glob import glob
import pandas as pd
import numpy as np
import pdfkit

def get_report():

    (current_month_readable,
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
    tiered_facilities,
    css_file,
    extended_css_file,
    base_folder_path) = get_variables()
    
    icon_integers = ['one', 'two', '3', '4']
    def green_icon(i):
        icon_path = '<i class="material-icons md-36 success">looks_{}</i>'.format(icon_integers[i])
        return icon_path
    
    def orange_icon(i):
        icon_path ='<i class="material-icons md-36 warning">looks_{}</i>'.format(icon_integers[i])
        return icon_path
    
    #%% initialize data points
    
    overall_los = round(this_fiscal_los_df['LOS'].sum()/this_fiscal_los_df['GMLOS'].sum(),2)
    overall_obs_rate = round(this_fiscal_obs_df['Obs_Cases'].sum()/(this_fiscal_obs_df['Obs_Cases'].sum() + this_fiscal_obs_df['Obs_Rate_Inp'].sum()),2)*100
    total_48_hrs = int(this_fiscal_obs_df['Obs_Hours_48'].sum())
    opp_days = int(this_fiscal_los_df['OppDays'].sum())
    
    data_points = {}
    
    data_points[0] = {}
    data_points[0]['metric'] = 'Length of Stay (LOS) Ratio'
    data_points[0]['value'] = overall_los
    data_points[0]['arena'] = '<b>' + current_month_readable + '</b>'
    data_points[0]['icon'] = '<i class="material-icons md-36">bed</i>'
    data_points[0]['class'] = '"card-header card-header-info card-header-icon"'
    data_points[0]['header_class'] = '"card-header card-header-info"'
    data_points[0]['icon_text'] = '"text-info"'
     
    data_points[1] = {}
    data_points[1]['metric'] = 'Opportunity Days'
    data_points[1]['value'] = f'{opp_days:,}'
    data_points[1]['arena'] = '<b>' + current_month_readable + '</b>' 
    data_points[1]['icon'] = '<i class="material-icons md-36">watch_later</i>'
    data_points[1]['class'] = '"card-header card-header-danger card-header-icon"'
    data_points[1]['header_class'] = '"card-header card-header-danger"'
    data_points[1]['icon_text'] = '"text-danger"'
       
    data_points[2] = {}
    data_points[2]['metric'] = 'Observation Rate' 
    data_points[2]['value'] = str(round(overall_obs_rate,3))+'%'
    data_points[2]['arena'] = '<b>' + current_month_readable + '</b>'  
    data_points[2]['icon'] = '<i class="material-icons md-36">remove_red_eye</i>'      
    data_points[2]['class'] = '"card-header card-header-success card-header-icon"'
    data_points[2]['header_class'] = '"card-header card-header-success"'
    data_points[2]['icon_text'] = '"text-success"'
      
    data_points[3] = {}
    data_points[3]['metric'] = 'Observation Cases > 48H'
    data_points[3]['value'] = f'{total_48_hrs:,}'
    data_points[3]['arena'] = '<b>' + current_month_readable + '</b>' 
    data_points[3]['icon'] = '<i class="material-icons md-36">hourglass_bottom</i>'
    data_points[3]['class'] = '"card-header card-header-primary card-header-icon"'
    data_points[3]['header_class'] = '"card-header card-header-primary"'
    data_points[3]['icon_text'] = '"text-primary"'
    
    
    #%% Tiers
    for key, value in tiers.items():
            
        data_points[0][key] = {}
        los_tier = this_fiscal_los_df.loc[this_fiscal_los_df['Facility'].isin(value)]
        los_ratio_tier_avg = round(los_tier['LOS'].sum()/los_tier['GMLOS'].sum(),2)
        data_points[0][key] = '<b>'+str(los_ratio_tier_avg)+'</b>'
    
        data_points[1][key] = {}
        days_tier = this_fiscal_los_df.loc[this_fiscal_los_df['Facility'].isin(value)]
        days_tier_avg = round(days_tier['OppDays'].mean(),2)
        data_points[1][key] = '<b>'+f'{days_tier_avg:,}'+'</b>'
        
        data_points[2][key] = {}
        obs_rates_tier = this_fiscal_obs_df.loc[this_fiscal_obs_df['Facility'].isin(value)]
        obs_rates_tier_avg = round(((obs_rates_tier['Obs_Cases'].sum()/(obs_rates_tier['Obs_Cases'].sum() + obs_rates_tier['Obs_Rate_Inp'].sum()))*100),1)
        data_points[2][key] = '<b>'+str(obs_rates_tier_avg)+'</b>'
    
        data_points[3][key] = {}
        obs_48_tier = this_fiscal_obs_df.loc[this_fiscal_obs_df['Facility'].isin(value)]
        obs_48_tier_avg = round(obs_48_tier['Obs_Hours_48'].mean(),2)
        data_points[3][key] = '<b>'+f'{obs_48_tier_avg:,}'+'</b>'
    
    #%% 1. LOS Ratio
                        
    total_current_fiscal_los = this_fiscal_los_df['LOS'].sum()
    total_current_fiscal_gmlos = this_fiscal_los_df['GMLOS'].sum()
    current_fiscal_los_ratio = round(total_current_fiscal_los/total_current_fiscal_gmlos,2)
    
    total_last_fiscal_los_df = last_fiscal_los_df['LOS'].sum()
    total_last_gmlos = last_fiscal_los_df['GMLOS'].sum()
    last_fiscal_los_ratio = round(total_last_fiscal_los_df/total_last_gmlos,2)
    
    fiscal_los_ratios = pd.Series([last_fiscal_los_ratio, current_fiscal_los_ratio])
    total_fiscal_los_ratio_change = fiscal_los_ratios.pct_change()[1]
    total_fiscal_los_ratio_change = round((total_fiscal_los_ratio_change*100),2)
    
    los_ratios = pd.Series([last_fiscal_los_ratio, overall_los])
    total_los_ratio_change = los_ratios.pct_change()[1]
    total_los_ratio_change = round((total_los_ratio_change*100),2)
    
    if total_fiscal_los_ratio_change < 0:
        fiscal_change_direction = 'decreased'
        fiscal_change_icon = arrow_down_white
    elif total_fiscal_los_ratio_change > 0:
        fiscal_change_direction = 'increased'
        fiscal_change_icon = arrow_up_white
    elif total_fiscal_los_ratio_change == 0:
        fiscal_change_direction = 'continued'
        fiscal_change_icon = arrow_right_white
    else:
        fiscal_change_direction = 'unknown'
        fiscal_change_icon = arrow_right_white
            
    if total_los_ratio_change < 0:
        los_ratio_change_type = 'decreased'
        metric1_icon = arrow_down_white
    elif total_los_ratio_change > 0:
        los_ratio_change_type = 'increased'
        metric1_icon = arrow_up_white      
    elif total_los_ratio_change == 0:
        los_ratio_change_type = 'stayed the same'
        metric1_icon = arrow_right_white   
    else:
        los_ratio_change_type = 'unknown'
        metric1_icon = arrow_right_white
    
    if total_los_ratio_change != 0:    
        metric1_summary = '''The overall LOS Ratio of {} {}
        {} FYTD ({}) by {} {}.'''.format(overall_los,
                                                 fiscal_change_direction,
                                                 last_month_readable,
                                                 last_fiscal_los_ratio,
                                                 fiscal_change_icon,
                                                 str(abs(total_fiscal_los_ratio_change)) + '%', #fiscal change %
    
                                                 )
    elif total_los_ratio_change == 0:
        metric1_summary = '''The overall LOS Ratio of {} {}
        the {} FYTD ({}) by {} {} and {} when compared 
        to {} ({}).'''.format(overall_los,
                            fiscal_change_direction,
                            last_month_readable,
                            last_fiscal_los_ratio,
                            fiscal_change_icon,
                            str(abs(total_fiscal_los_ratio_change)) + '%', #fiscal change %
                            los_ratio_change_type,  #month change direction 
                            last_month_readable,
                            round(last_fiscal_los_ratio,2))
    
    metric1_progress_dict = {'metric': metric1, 'summary': metric1_summary}
    
    # Top Performers #########################################################
    
    for facility in tiered_facilities:
    
        current_fiscal_ratio = tiered_this_fiscal_los_df.loc[tiered_this_fiscal_los_df['Facility'] == facility]['LOSRatio'].reset_index(drop=True)[0]
        last_fiscal_ratio = tiered_last_fiscal_los_df.loc[tiered_last_fiscal_los_df['Facility'] == facility]['LOSRatio'].reset_index(drop=True)[0]
    
        los_ratio_series = pd.Series([last_fiscal_ratio, current_fiscal_ratio])
        ratio_change = los_ratio_series.pct_change()[1]
        ratio_change = round(((ratio_change)*100),2)
        
        tiered_this_fiscal_los_df.loc[tiered_this_fiscal_los_df['Facility'] == facility, 'LOSRatioChange'] = ratio_change
        tiered_this_fiscal_los_df.loc[tiered_this_fiscal_los_df['Facility'] == facility, 'percentage_change'] = ratio_change
        
        if ratio_change < 0:
            tiered_this_fiscal_los_df.loc[tiered_this_fiscal_los_df['Facility'] == facility, 'percentage_change_direction'] = 'decrease'
           
        elif ratio_change > 0:
            tiered_this_fiscal_los_df.loc[tiered_this_fiscal_los_df['Facility'] == facility, 'percentage_change_direction'] = 'increase' 
           
        elif ratio_change == 0:    
            tiered_this_fiscal_los_df.loc[tiered_this_fiscal_los_df['Facility'] == facility, 'percentage_change_direction'] = 'change' 
           
        else:
            tiered_this_fiscal_los_df.loc[tiered_this_fiscal_los_df['Facility'] == facility, 'percentage_change_direction'] = 'unknown' 
           
        tiered_this_fiscal_los_df.loc[tiered_this_fiscal_los_df['Facility'] == facility, 'from_value'] = last_fiscal_ratio
        tiered_this_fiscal_los_df.loc[tiered_this_fiscal_los_df['Facility'] == facility, 'to_value'] = current_fiscal_ratio
    
    los_top = tiered_this_fiscal_los_df.sort_values(by='LOSRatio', ascending=True).reset_index().drop('index', axis=1)
    metric1_performer_dict = {}
    
    for i in range(0, 4): 
        
        metric1_performer_dict[i] = {}
        metric1_performer_dict[i]['top'] = {}  
        
        facility = los_top['Facility'][i]
        metric1_performer_dict[i]['top']['numeric_icon'] = green_icon(i)
        metric1_performer_dict[i]['top']['facility'] = '<b>'+facility+'</b>'
        metric1_performer_dict[i]['top']['class'] = '"text-success"'
        metric1_performer_dict[i]['top']['value'] = '<b>'+str(round(los_top['LOSRatio'][i],2))+'</b>'
        metric1_performer_dict[i]['top']['from_value'] = '<b>'+str(round(los_top['from_value'][i],2))+'</b>'
        metric1_performer_dict[i]['top']['percentage_change_direction'] = los_top['percentage_change_direction'][i]
        metric1_performer_dict[i]['top']['percentage_change'] = '<b>'+str(abs(los_top['percentage_change'][i]))+'%</b>'
        
        if los_top['percentage_change_direction'][i] == 'decrease':
            metric1_performer_dict[i]['top']['icon'] = arrow_down
        elif los_top['percentage_change_direction'][i] == 'increase':
            metric1_performer_dict[i]['top']['icon'] = arrow_up
        elif los_top['percentage_change_direction'][i] == 'change':
            metric1_performer_dict[i]['top']['icon'] = arrow_right
        else:   
            metric1_performer_dict[i]['top']['icon'] = question_mark
            
    los_bottom = tiered_this_fiscal_los_df.sort_values(by='LOSRatio', ascending=False).reset_index().drop('index', axis=1)                       
    
    for i in range(0, 4):
        metric1_performer_dict[i]['bottom'] = {}
        
        facility = los_bottom['Facility'][i]           
        metric1_performer_dict[i]['bottom']['numeric_icon'] = orange_icon(i)
        metric1_performer_dict[i]['bottom']['facility'] = '<b>'+facility+'</b>'
        metric1_performer_dict[i]['bottom']['class'] = '"text-warning"'
        metric1_performer_dict[i]['bottom']['value'] = '<b>'+str(round(los_bottom['LOSRatio'][i],2))+'</b>'
        metric1_performer_dict[i]['bottom']['from_value'] = '<b>'+str(round(los_bottom['from_value'][i],2))+'</b>'
        metric1_performer_dict[i]['bottom']['percentage_change_direction'] = los_bottom['percentage_change_direction'][i]
        metric1_performer_dict[i]['bottom']['percentage_change'] = '<b>'+str(abs(los_bottom['percentage_change'][i]))+'%</b>'
        
        if los_bottom['percentage_change_direction'][i] == 'decrease':
            metric1_performer_dict[i]['bottom']['icon'] = arrow_down
        elif los_bottom['percentage_change_direction'][i] == 'increase':
            metric1_performer_dict[i]['bottom']['icon'] = arrow_up
        elif los_bottom['percentage_change_direction'][i] == 'change':
            metric1_performer_dict[i]['bottom']['icon'] = arrow_right
        else:   
            metric1_performer_dict[i]['bottom']['icon'] = question_mark
            
    # Best/Worst Progress #########################################################
    
    for facility in tiered_facilities:
    
        current_fiscal_ratio = tiered_this_fiscal_los_df.loc[tiered_this_fiscal_los_df['Facility'] == facility]['LOSRatio'].reset_index(drop=True)[0]
        last_fiscal_ratio = tiered_last_fiscal_los_df.loc[tiered_last_fiscal_los_df['Facility'] == facility]['LOSRatio'].reset_index(drop=True)[0]
    
        los_ratio_series = pd.Series([last_fiscal_ratio, current_fiscal_ratio])
        ratio_change = los_ratio_series.pct_change()[1]
        ratio_change = round(((ratio_change)*100),2)
        
        tiered_this_fiscal_los_df.loc[tiered_this_fiscal_los_df['Facility'] == facility, 'LOSRatioChange'] = ratio_change
        tiered_this_fiscal_los_df.loc[tiered_this_fiscal_los_df['Facility'] == facility, 'percentage_change'] = ratio_change
        
        if ratio_change < 0:
            tiered_this_fiscal_los_df.loc[tiered_this_fiscal_los_df['Facility'] == facility, 'percentage_change_direction'] = 'decreased'
           
        elif ratio_change > 0:
            tiered_this_fiscal_los_df.loc[tiered_this_fiscal_los_df['Facility'] == facility, 'percentage_change_direction'] = 'increased' 
           
        elif ratio_change == 0:    
            tiered_this_fiscal_los_df.loc[tiered_this_fiscal_los_df['Facility'] == facility, 'percentage_change_direction'] = 'equated' 
           
        else:
            tiered_this_fiscal_los_df.loc[tiered_this_fiscal_los_df['Facility'] == facility, 'percentage_change_direction'] = 'unknown' 
           
        tiered_this_fiscal_los_df.loc[tiered_this_fiscal_los_df['Facility'] == facility, 'from_value'] = round(last_fiscal_ratio,2)
        tiered_this_fiscal_los_df.loc[tiered_this_fiscal_los_df['Facility'] == facility, 'to_value'] = round(current_fiscal_ratio,2)
    
    ranked_ratio_df = tiered_this_fiscal_los_df[['Facility','from_value', 'to_value', 'LOSRatioChange', 'percentage_change_direction']].drop_duplicates()
    ranked_ratio_df = ranked_ratio_df.sort_values(by='LOSRatioChange', ascending=True).reset_index().drop('index', axis=1)  
       
    for i in range(0, 4): 
    
        metric1_progress_dict[i] = {}
        metric1_progress_dict[i]['top'] = {}
    
        metric1_progress_dict[i]['top']['facility'] = '<b>'+ranked_ratio_df.iloc[i]['Facility']+'</b>' 
        metric1_progress_dict[i]['top']['from'] = '<b>'+str(ranked_ratio_df.iloc[i]['from_value'])+'</b>'
        metric1_progress_dict[i]['top']['to'] = '<b>'+str(ranked_ratio_df.iloc[i]['to_value'])+'</b>'
        metric1_progress_dict[i]['top']['trend_type'] = ranked_ratio_df.iloc[i]['percentage_change_direction']
        metric1_progress_dict[i]['top']['percentage_change'] = '<b>'+str(abs(ranked_ratio_df.iloc[i]['LOSRatioChange'])) + '%</b>'
        metric1_progress_dict[i]['top']['numeric_icon'] = green_icon(i)
        
        if ranked_ratio_df.iloc[i]['percentage_change_direction'] == 'decreased':
            metric1_progress_dict[i]['top']['class'] = '"text-success"'
            metric1_progress_dict[i]['top']['icon'] = arrow_down
            metric1_progress_dict[i]['top']['main_class'] = "material-icons md-36 success"
            metric1_progress_dict[i]['top']['main_icon'] = arrow_down
            
        elif ranked_ratio_df.iloc[i]['percentage_change_direction'] == 'increased':
            metric1_progress_dict[i]['top']['class'] = '"text-warning"'
            metric1_progress_dict[i]['top']['icon'] = arrow_up
            metric1_progress_dict[i]['top']['main_class'] = "material-icons md-36 warning"
            metric1_progress_dict[i]['top']['main_icon'] = arrow_up
            
        elif ranked_ratio_df.iloc[i]['percentage_change_direction'] == 'equaled':
            metric1_progress_dict[i]['top']['class'] = '"text-info"'
            metric1_progress_dict[i]['top']['icon'] = arrow_right
            metric1_progress_dict[i]['top']['main_class'] = "material-icons md-36 info"
            metric1_progress_dict[i]['top']['main_icon'] = arrow_right
            
        else:
            metric1_progress_dict[i]['top']['class'] = '"text-secondary"'
            metric1_progress_dict[i]['top']['icon'] = arrow_right
            metric1_progress_dict[i]['top']['main_class'] = "material-icons md-36 secondary"
            metric1_progress_dict[i]['top']['main_icon'] = arrow_right
    
    ranked_ratio_df = ranked_ratio_df.sort_values(by='LOSRatioChange', ascending=False).reset_index().drop('index', axis=1)  
       
    for i in range(0, 4): 
        metric1_progress_dict[i]['bottom'] = {}
        
        metric1_progress_dict[i]['bottom']['facility'] = '<b>'+ranked_ratio_df.iloc[i]['Facility']+'</b>' 
        metric1_progress_dict[i]['bottom']['from'] = '<b>'+str(ranked_ratio_df.iloc[i]['from_value'])+'</b>'
        metric1_progress_dict[i]['bottom']['to'] = '<b>'+str(ranked_ratio_df.iloc[i]['to_value'])+'</b>'
        metric1_progress_dict[i]['bottom']['trend_type'] = ranked_ratio_df.iloc[i]['percentage_change_direction']
        metric1_progress_dict[i]['bottom']['percentage_change'] = '<b>'+str(abs(ranked_ratio_df.iloc[i]['LOSRatioChange'])) + '%</b>'
        metric1_progress_dict[i]['bottom']['numeric_icon'] = orange_icon(i)
        
        if ranked_ratio_df.iloc[i]['percentage_change_direction'] == 'decreased':
            metric1_progress_dict[i]['bottom']['trend_type'] = 'decreased'
            metric1_progress_dict[i]['bottom']['class'] = '"text-success"'
            metric1_progress_dict[i]['bottom']['icon'] = arrow_down
            metric1_progress_dict[i]['bottom']['main_class'] = "material-icons md-36 success"
            metric1_progress_dict[i]['bottom']['main_icon'] = arrow_down
            
        elif ranked_ratio_df.iloc[i]['percentage_change_direction'] == 'increased':
            metric1_progress_dict[i]['bottom']['trend_type'] = 'increased'
            metric1_progress_dict[i]['bottom']['class'] = '"text-warning"'
            metric1_progress_dict[i]['bottom']['icon'] = arrow_up
            metric1_progress_dict[i]['bottom']['main_class'] = "material-icons md-36 warning"
            metric1_progress_dict[i]['bottom']['main_icon'] = arrow_up
            
        elif ranked_ratio_df.iloc[i]['percentage_change_direction'] == 'equaled':
            metric1_progress_dict[i]['bottom']['trend_type'] = '(no change)'
            metric1_progress_dict[i]['bottom']['class'] = '"text-info"'
            metric1_progress_dict[i]['bottom']['icon'] = arrow_right
            metric1_progress_dict[i]['bottom']['main_class'] = "material-icons md-36 info"
            metric1_progress_dict[i]['bottom']['main_icon'] = arrow_right
        
        else:
            metric1_progress_dict[i]['bottom']['class'] = '"text-secondary"'
            metric1_progress_dict[i]['bottom']['icon'] = arrow_right
            metric1_progress_dict[i]['bottom']['main_class'] = "material-icons md-36 secondary"
            metric1_progress_dict[i]['bottom']['main_icon'] = arrow_right
    
    metric1_progress_dict['summary_icon'] = metric1_icon
        
    #%% 2. Opportunity Days
    last_opp_days = last_fiscal_los_df['OppDays'].sum()
    current_opp_days = this_fiscal_los_df['OppDays'].sum()
    oppchange = round((((current_opp_days-last_opp_days)/last_opp_days)*100),2)
    
    if oppchange < 0:
        opp_days_change_type = 'decreased'
        opp_days_change_type_verb = 'reduction'
        opp_days_overall_percentage = str(abs(oppchange)) + '%'
        opp_days_change = round(last_opp_days-current_opp_days,3)
        opp_days_change = f'{opp_days_change:,}'
        metric2_trend_class = '"text-success"'
        metric2_icon = arrow_down_white
        
    elif oppchange > 0:
        opp_days_change_type = 'increased'
        opp_days_change_type_verb = 'increase'
        opp_days_overall_percentage = str(abs(oppchange)) + '%'
        opp_days_change = round(current_opp_days-last_opp_days,2)
        opp_days_change = f'{opp_days_change:,}'
        metric2_trend_class = '"text-warning"'
        metric2_icon = arrow_up_white
        
    elif oppchange == 0:
        opp_days_change_type = 'flatlined'
        opp_days_change_type_verb = 'change'
        opp_days_overall_percentage = '0.0%'
        opp_days_change = '0.0'
        metric2_trend_class = '"text-info"'
        metric2_icon = arrow_right_white
    
    else:
        opp_days_change_type = 'unknown'
        opp_days_change_type_verb = 'unknown'
        opp_days_overall_percentage = '?%'
        opp_days_change = '?%'
        metric2_trend_class = '"text-secondary"'
        metric2_main_class = "material-icons md-24 secondary"
        metric2_icon = arrow_right_white
        
    last_opp_days = round(last_opp_days,2)
    current_opp_days = round(current_opp_days,2)
    
    metric2_summary = '''Total Opportunity Days {}
    by {} <b>{}</b> from {} days in {} to {} days in {}, which represents a 
    <b>{} {}</b> in days.'''.format(opp_days_change_type,
                                    metric2_icon,
                                    opp_days_overall_percentage,
                                    f'{last_opp_days:,}',
                                    last_month_readable,
                                    f'{current_opp_days:,}',
                                    current_month_readable,
                                    opp_days_change,
                                    opp_days_change_type_verb)
    
    for facility in tiered_facilities:
        
        last_days = tiered_last_fiscal_los_df.loc[tiered_last_fiscal_los_df['Facility'] == facility]['OppDays'].reset_index(drop=True)[0]
        current_days = tiered_this_fiscal_los_df.loc[tiered_this_fiscal_los_df['Facility'] == facility]['OppDays'].reset_index(drop=True)[0]
        
        last_days = round(last_days,2) 
        current_days = round(current_days,2)
        oppdays_change = round((((current_days-last_days)/last_days)*100),2)
        
        tiered_this_fiscal_los_df.loc[tiered_this_fiscal_los_df['Facility'] == facility, 'from_value'] = last_days
        tiered_this_fiscal_los_df.loc[tiered_this_fiscal_los_df['Facility'] == facility, 'to_value'] = current_days
        tiered_this_fiscal_los_df.loc[tiered_this_fiscal_los_df['Facility'] == facility, 'OppDaysChange'] = oppdays_change
            
        if oppdays_change < 0:
            tiered_this_fiscal_los_df.loc[tiered_this_fiscal_los_df['Facility'] == facility, 'trend_type'] = 'decrease'
            
        elif oppdays_change > 0:
            tiered_this_fiscal_los_df.loc[tiered_this_fiscal_los_df['Facility'] == facility, 'trend_type'] = 'increase'
            
        elif last_days == current_days:
            tiered_this_fiscal_los_df.loc[tiered_this_fiscal_los_df['Facility'] == facility, 'trend_type'] = 'equal'
    
    # Top/Bottom Performers #####################################################
    metric2_performer_dict = {}
    opp_top = tiered_this_fiscal_los_df.sort_values(by='OppDays', ascending=True).reset_index().drop('index', axis=1)
    opp_top['OppDays'] = opp_top['OppDays'].astype(float).round(2)
    
    for i in range(0, 4): 
    
        metric2_performer_dict[i] = {}
        metric2_performer_dict[i]['top'] = {}
        
        facility = opp_top['Facility'][i]           
        metric2_performer_dict[i]['top']['numeric_icon'] = green_icon(i)
        metric2_performer_dict[i]['top']['facility'] = '<b>'+opp_top['Facility'][i]+'</b>'
        metric2_performer_dict[i]['top']['class'] = '"text-success"'
        
        top_value ='{:,}'.format(int(opp_top["OppDays"][i]))
        from_value = '{:,}'.format(int(opp_top["from_value"][i]))
    
        metric2_performer_dict[i]['top']['to_value'] = '<b>' + top_value + '</b>'
        metric2_performer_dict[i]['top']['from_value'] = '<b>' + from_value + '</b>'
        metric2_performer_dict[i]['top']['percentage_change_direction'] = opp_top['trend_type'][i] 
        metric2_performer_dict[i]['top']['percentage_change'] = '<b>' + str(abs(opp_top['OppDaysChange'][i])) + '%</b>'
    
        if opp_top['trend_type'][i] == 'decrease':
            metric2_performer_dict[i]['top']['icon'] = arrow_down
        elif opp_top['trend_type'][i] == 'increase':
            metric2_performer_dict[i]['top']['icon'] = arrow_up
        elif opp_top['trend_type'][i] == 'equal':
            metric2_performer_dict[i]['top']['icon'] = arrow_right
        else:   
            metric2_performer_dict[i]['top']['icon'] = question_mark
            
    opp_bottom = tiered_this_fiscal_los_df.sort_values(by='OppDays', ascending=False).reset_index().drop('index', axis=1)                       
    opp_bottom['OppDays'] = opp_bottom['OppDays'].round(3)
    
    for i in range(0, 4):
        
        bottom_value = '{:,}'.format(int(opp_bottom["OppDays"][i]))
        from_value = '{:,}'.format(int(opp_bottom["from_value"][i]))
        
        metric2_performer_dict[i]['bottom'] = {}
        facility = opp_bottom['Facility'][i]             
        metric2_performer_dict[i]['bottom']['numeric_icon'] = orange_icon(i)
        metric2_performer_dict[i]['bottom']['facility'] = '<b>'+opp_bottom['Facility'][i]+'</b>'
        metric2_performer_dict[i]['bottom']['class'] = '"text-warning"'
        metric2_performer_dict[i]['bottom']['to_value'] = '<b>' + bottom_value + '</b>'
        metric2_performer_dict[i]['bottom']['from_value'] = '<b>' + from_value + '</b>'
        metric2_performer_dict[i]['bottom']['percentage_change_direction'] = opp_bottom['trend_type'][i] 
        metric2_performer_dict[i]['bottom']['percentage_change'] = '<b>' + str(abs(opp_bottom['OppDaysChange'][i])) + '%</b>'
    
        if opp_bottom['trend_type'][i] == 'decrease':
            metric2_performer_dict[i]['bottom']['icon'] = arrow_down
        elif opp_bottom['trend_type'][i] == 'increase':
            metric2_performer_dict[i]['bottom']['icon'] = arrow_up
        elif opp_bottom['trend_type'][i] == 'equal':
            metric2_performer_dict[i]['bottom']['icon'] = arrow_right
        else:   
            metric2_performer_dict[i]['bottom']['icon'] = question_mark
        
    # Best/Worst Progress #######################################################
    metric2_progress_dict = {'metric': metric2, 'summary': metric2_summary}
       
    opp_days_dff = tiered_this_fiscal_los_df[['Facility', 'from_value', 'to_value', 'OppDaysChange', 'trend_type']].drop_duplicates()  
    opp_days_dff = opp_days_dff.dropna(subset=['OppDaysChange']).sort_values(by='OppDaysChange', ascending=True).reset_index().drop('index', axis=1)
         
    for i in range(0, 4): #n metrics
    
        negi =(i+1)*-1
        metric2_progress_dict[i] = {}
        metric2_progress_dict[i]['top'] = {}
        metric2_progress_dict[i]['bottom'] = {}
        
        from_val = int(opp_days_dff.iloc[i]['from_value'])
        to_val = int(opp_days_dff.iloc[i]['to_value'])
        
        bottom_from_val = int(opp_days_dff.iloc[-negi]['from_value'])
        bottom_to_val = int(opp_days_dff.iloc[-negi]['to_value'])
        
        metric2_progress_dict[i]['top']['facility'] = '<b>'+opp_days_dff.iloc[i]['Facility']+'</b>' 
        metric2_progress_dict[i]['top']['from'] = '<b>'+f'{from_val:,}'+'</b>'
        metric2_progress_dict[i]['top']['to'] = '<b>'+f'{to_val:,}'+'</b>'
        metric2_progress_dict[i]['top']['trend_type'] = opp_days_dff.iloc[i]['trend_type']
        metric2_progress_dict[i]['top']['percentage_change'] = '<b>'+str(abs(opp_days_dff.iloc[i]['OppDaysChange'])) + '%</b>' 
        metric2_progress_dict[i]['top']['numeric_icon'] = green_icon(i)
        
        if opp_days_dff.iloc[i]['trend_type'] == 'decrease':
            metric2_progress_dict[i]['top']['class'] = '"text-success"'
            metric2_progress_dict[i]['top']['icon'] = arrow_down
            metric2_progress_dict[i]['top']['main_class'] = "material-icons md-36 success"
            metric2_progress_dict[i]['top']['main_icon'] = arrow_down
            
        elif opp_days_dff.iloc[i]['trend_type'] == 'increase':
            metric2_progress_dict[i]['top']['class'] = '"text-warning"'
            metric2_progress_dict[i]['top']['icon'] = arrow_up
            metric2_progress_dict[i]['top']['main_class'] = "material-icons md-36 warning"
            metric2_progress_dict[i]['top']['main_icon'] = arrow_up
            
        elif opp_days_dff.iloc[i]['trend_type'] == 'equal':
            metric2_progress_dict[i]['top']['trend_type'] = '(no change)'
            metric2_progress_dict[i]['top']['class'] = '"text-info"'
            metric2_progress_dict[i]['top']['icon'] = arrow_right
            metric2_progress_dict[i]['top']['main_class'] = "material-icons md-36 info"
            metric2_progress_dict[i]['top']['main_icon'] = arrow_right
    
        metric2_progress_dict[i]['bottom']['facility'] = '<b>'+opp_days_dff.iloc[-negi]['Facility']+'</b>' 
        metric2_progress_dict[i]['bottom']['from'] = '<b>'+f'{bottom_from_val:,}'+'</b>'
        metric2_progress_dict[i]['bottom']['to'] = '<b>'+f'{bottom_to_val:,}'+'</b>'
        metric2_progress_dict[i]['bottom']['trend_type'] = opp_days_dff.iloc[-negi]['trend_type']
        metric2_progress_dict[i]['bottom']['percentage_change'] = '<b>'+str(abs(opp_days_dff.iloc[-negi]['OppDaysChange'])) + '%</b>' 
        metric2_progress_dict[i]['bottom']['numeric_icon'] = orange_icon(i)
        
        if opp_days_dff.iloc[-negi]['trend_type'] == 'decrease':
            metric2_progress_dict[i]['bottom']['class'] = '"text-success"'
            metric2_progress_dict[i]['bottom']['icon'] = arrow_down
            metric2_progress_dict[i]['bottom']['main_class'] = "material-icons md-36 success"
            metric2_progress_dict[i]['bottom']['main_icon'] = arrow_down
            
        elif opp_days_dff.iloc[-negi]['trend_type'] == 'increase':
            metric2_progress_dict[i]['bottom']['class'] = '"text-warning"'
            metric2_progress_dict[i]['bottom']['icon'] = arrow_up
            metric2_progress_dict[i]['bottom']['main_class'] = "material-icons md-36 warning"
            metric2_progress_dict[i]['bottom']['main_icon'] = arrow_up
            
        elif opp_days_dff.iloc[-negi]['trend_type'] == 'equal':
            metric2_progress_dict[i]['bottom']['class'] = '"text-info"'
            metric2_progress_dict[i]['bottom']['icon'] = arrow_right
            metric2_progress_dict[i]['bottom']['main_class'] = "material-icons md-36 info"
            metric2_progress_dict[i]['bottom']['main_icon'] = arrow_right
    
    metric2_progress_dict['summary_icon'] = metric2_icon
        
    #%% 2. Observation Rate
    
    last_fiscal_obs_cases = last_fiscal_obs_df['Obs_Cases'].sum()
    last_fiscal_obs_inp = round(last_fiscal_obs_df['Obs_Rate_Inp'].sum(),3)
    last_fiscal_obs_rates = last_fiscal_obs_cases/(last_fiscal_obs_cases + last_fiscal_obs_inp)
    last_fiscal_obs_rates = round(last_fiscal_obs_rates*100,1)
    
    current_obs_cases = this_fiscal_obs_df['Obs_Cases'].sum()
    current_obs_inp = round(this_fiscal_obs_df['Obs_Rate_Inp'].sum(),2)
    current_obs_rates = current_obs_cases/(current_obs_cases + current_obs_inp)
    current_obs_rates = round(current_obs_rates*100,1)
    
    obs_rates_series = pd.Series([last_fiscal_obs_rates, current_obs_rates])
    obs_rates_change = obs_rates_series.pct_change()[1]
    
    obs_rates_change = round((obs_rates_change*100),2)
        
    if obs_rates_change < 0:
        obs_rates_change_type = 'decreased'
        obs_rates_change_type_verb = 'reduction'
        obs_rates_overall_percentage = abs(obs_rates_change)
        metric3_trend_class = '"text-success"'
        metric3_icon = arrow_down_white
        
    elif obs_rates_change > 0:
        obs_rates_change_type = 'increased'
        obs_rates_change_type_verb = 'increase'
        obs_rates_overall_percentage = obs_rates_change
        metric3_trend_class = '"text-warning"'
        metric3_icon = arrow_up_white
        
    elif obs_rates_change == 0:
        obs_rates_change_type = 'flatlined'
        obs_rates_change_type_verb = 'consistency'
        obs_rates_overall_percentage = 0.0
        metric3_trend_class = '"text-info"'
        metric3_icon = arrow_right_white
       
    else:
        obs_rates_change_type = 'unknown'
        obs_rates_change_type_verb = 'unknown'
        obs_rates_overall_percentage = '?%'
        metric3_trend_class = '"text-secondary"'
        metric3_icon = arrow_right_white
        
    last_obs_cases = int(last_fiscal_obs_df['Obs_Cases'].sum())
    current_obs_cases = int(this_fiscal_obs_df['Obs_Cases'].sum())
    
    obs_cases = pd.Series([last_obs_cases, current_obs_cases])
    obs_cases_change = obs_cases.pct_change()[1]
    
    obs_cases_change = round(((obs_cases_change)*100),2)
    
    if obs_cases_change < 0:
        obs_change_type_verb = 'reduction' 
        obs_cases_change = int(last_obs_cases-current_obs_cases)
        obs_cases_change = f'{obs_cases_change:,}'
        
    elif obs_cases_change > 0:
        obs_change_type_verb = 'increase'
        obs_cases_change = int(current_obs_cases-last_obs_cases)
        obs_cases_change = f'{obs_cases_change:,}'
        
    elif obs_cases_change == 0:
        obs_change_type_verb = 'change'
        obs_cases_change = 0.0
    
    else:
        obs_change_type_verb = 'unknown'
        obs_cases_change = np.nan
        
    last_inp_obs_cases = int(last_fiscal_obs_df['Obs_Rate_Inp'].sum())
    current_inp_obs_cases = int(this_fiscal_obs_df['Obs_Rate_Inp'].sum())
    
    inp_obs_cases = pd.Series([last_inp_obs_cases, current_inp_obs_cases])
    inp_obs_cases_change = inp_obs_cases.pct_change()[1]
    
    inp_obs_cases_change = round(((inp_obs_cases_change)*100),2)
    
    if inp_obs_cases_change < 0:
        inp_obs_cases_change_type_verb = 'reduction' 
        inp_obs_cases_change = int(last_inp_obs_cases-current_inp_obs_cases)
        inp_obs_cases_change = f'{inp_obs_cases_change:,}'
        
    elif inp_obs_cases_change > 0:
        inp_obs_cases_change_type_verb = 'increase'
        inp_obs_cases_change = int(current_inp_obs_cases-last_inp_obs_cases)
        inp_obs_cases_change = f'{inp_obs_cases_change:,}'
        
    elif inp_obs_cases_change == 0:
        inp_obs_cases_change_type_verb = 'equal'
        inp_obs_cases_change = 0.0
    
    else:
        obs_change_type_verb = 'unknown'
        obs_cases_change = np.nan
        
    current_obs_rates = round((current_obs_rates*100),2)
    
    if inp_obs_cases_change_type_verb == 'equal':
        metric3_summary = '''CThe overall Observation Rate of {}
        {} the prior month's FYTD ({}) by {} <b>{}%</b> (<b>{}</b> in {} to 
        <b>{}</b> in {}). There was no change in observation cases or inpatient 
        observation cases.'''.format(round(overall_obs_rate,2),
                                    obs_rates_change_type,
                                    f'{last_fiscal_obs_rates:,}',
                                    metric3_icon,
                                    str(obs_rates_overall_percentage),
                                    round(overall_obs_rate,3),
                                    current_month_readable,
                                    f'{current_obs_rates:,}',
                                    last_month_readable)
    
    else:
        metric3_summary = '''The overall Observation Rate of {} {} {}'s FYTD ({}) 
        by {} <b>{}%</b>. This change resulted from a <b>{}</b> 
        observation case {} (<b>{}</b> to <b>{}</b>) and a <b>{}</b> inpatient 
        observation case {} (<b>{}</b> to <b>{}</b>).'''.format(round(overall_obs_rate,2),
                                                                obs_rates_change_type,
                                                                current_month_readable,
                                                                f'{last_fiscal_obs_rates:,}',
                                                                metric3_icon,
                                                                str(obs_rates_overall_percentage),
                                                                obs_cases_change,
                                                                obs_change_type_verb,
                                                                f'{last_obs_cases:,}',
                                                                f'{current_obs_cases:,}',
                                                                inp_obs_cases_change,
                                                                inp_obs_cases_change_type_verb,
                                                                f'{last_fiscal_obs_inp:,}',
                                                                f'{current_obs_inp:,}')
    
    for facility in tiered_facilities:
        
        last_fiscal_rate = tiered_last_fiscal_obs_df.loc[tiered_last_fiscal_obs_df['Facility'] == facility]['ObservationRates'].reset_index(drop=True)[0]
        current_fiscal_rate = tiered_this_fiscal_obs_df.loc[tiered_this_fiscal_obs_df['Facility'] == facility]['ObservationRates'].reset_index(drop=True)[0]
        
        last_fiscal_rate = round(last_fiscal_rate,1)
        current_fiscal_rate = round(current_fiscal_rate,1)
        
        tiered_this_fiscal_obs_df.loc[tiered_this_fiscal_obs_df['Facility'] == facility, 'from_value'] = f'{last_fiscal_rate:,}'
        tiered_this_fiscal_obs_df.loc[tiered_this_fiscal_obs_df['Facility'] == facility, 'to_value'] = f'{current_fiscal_rate:,}'
        
        fobs_rates = pd.Series([last_fiscal_rate, current_fiscal_rate])
        fobs_rates_change = fobs_rates.pct_change()[1]
        
        fobs_rate_change = round(((fobs_rates_change)*100),2)
        
        if fobs_rate_change < 0:
            tiered_this_fiscal_obs_df.loc[tiered_this_fiscal_obs_df['Facility'] == facility, 'ObsRateChange'] = fobs_rate_change
            tiered_this_fiscal_obs_df.loc[tiered_this_fiscal_obs_df['Facility'] == facility, 'trend_type'] = 'decrease'
                            
        elif fobs_rate_change > 0:
            tiered_this_fiscal_obs_df.loc[tiered_this_fiscal_obs_df['Facility'] == facility, 'ObsRateChange'] = fobs_rate_change
            tiered_this_fiscal_obs_df.loc[tiered_this_fiscal_obs_df['Facility'] == facility, 'trend_type'] = 'increase'
        
        elif fobs_rate_change == 0:
            tiered_this_fiscal_obs_df.loc[tiered_this_fiscal_obs_df['Facility'] == facility, 'trend_type'] = 'equal'
            tiered_this_fiscal_obs_df.loc[tiered_this_fiscal_obs_df['Facility'] == facility, 'ObsRateChange'] = 0.00
     
        else:
            tiered_this_fiscal_obs_df.loc[tiered_this_fiscal_obs_df['Facility'] == facility, 'trend_type'] = 'unknown'
            tiered_this_fiscal_obs_df.loc[tiered_this_fiscal_obs_df['Facility'] == facility, 'ObsRateChange'] = np.nan
            
    # Top/Bottom Performers ####################################################
    metric3_performer_dict = {}
    obs_rates_top = tiered_this_fiscal_obs_df.sort_values(by='ObservationRates', ascending=True).reset_index().drop('index', axis=1)
    
    for i in range(0, 4): 
        
        metric3_performer_dict[i] = {}
        metric3_performer_dict[i]['top'] = {}
    
        from_val = obs_rates_top['from_value'][i]
        to_val = obs_rates_top['ObservationRates'][i]
        
        facility = obs_rates_top['Facility'][i]            
        metric3_performer_dict[i]['top']['numeric_icon'] = green_icon(i)
        metric3_performer_dict[i]['top']['facility'] = '<b>'+obs_rates_top['Facility'][i]+'</b>'
        metric3_performer_dict[i]['top']['class'] = '"text-success"'
        metric3_performer_dict[i]['top']['to_value'] = '<b>'+str(to_val)+'</b>'
        metric3_performer_dict[i]['top']['from_value'] = '<b>'+str(from_val)+'</b>'
        metric3_performer_dict[i]['top']['percentage_change_direction'] = obs_rates_top['trend_type'][i] 
        metric3_performer_dict[i]['top']['percentage_change'] = '<b>' + str(abs(obs_rates_top['ObsRateChange'][i])) + '%</b>'
        
        if obs_rates_top['trend_type'][i] == 'decrease':
            metric3_performer_dict[i]['top']['icon'] = arrow_down
        elif obs_rates_top['trend_type'][i] == 'increase':
            metric3_performer_dict[i]['top']['icon'] = arrow_up
        elif obs_rates_top['trend_type'][i] == 'equal':
            metric3_performer_dict[i]['top']['icon'] = arrow_right
        else:   
            metric3_performer_dict[i]['top']['icon'] = question_mark
    
    obs_rate_bottom = tiered_this_fiscal_obs_df.sort_values(by='ObservationRates', ascending=False).reset_index().drop('index', axis=1)                       
    
    for i in range(0, 4): 
        metric3_performer_dict[i]['bottom'] = {}
        
        from_val = obs_rate_bottom['from_value'][i]
        to_val = obs_rate_bottom['ObservationRates'][i]
        facility = obs_rate_bottom['Facility'][i]
        metric3_performer_dict[i]['bottom']['numeric_icon'] = orange_icon(i)
        metric3_performer_dict[i]['bottom']['facility'] = '<b>'+obs_rate_bottom['Facility'][i]+'</b>'
        metric3_performer_dict[i]['bottom']['class'] = '"text-warning"'
        metric3_performer_dict[i]['bottom']['to_value'] = '<b>'+str(to_val)+'</b>'
        metric3_performer_dict[i]['bottom']['from_value'] = '<b>'+str(from_val)+'</b>'    
        metric3_performer_dict[i]['bottom']['percentage_change_direction'] = obs_rate_bottom['trend_type'][i] 
        metric3_performer_dict[i]['bottom']['percentage_change'] = '<b>' + str(abs(obs_rate_bottom['ObsRateChange'][i])) + '%</b>'
        
        if obs_rate_bottom['trend_type'][i] == 'decrease':
            metric3_performer_dict[i]['bottom']['icon'] = arrow_down
        elif obs_rate_bottom['trend_type'][i] == 'increase':
            metric3_performer_dict[i]['bottom']['icon'] = arrow_up
        elif obs_rate_bottom['trend_type'][i] == 'equal':
            metric3_performer_dict[i]['bottom']['icon'] = arrow_right
        else:   
            metric3_performer_dict[i]['bottom']['icon'] = question_mark
    
    # Best/Worst Progress ####################################################
    ranked_rates_df = tiered_this_fiscal_obs_df[['Facility', 'from_value', 'to_value', 'ObsRateChange', 'trend_type']].drop_duplicates()
    ranked_rates_df = ranked_rates_df.dropna(subset=['ObsRateChange']).sort_values(by='ObsRateChange', 
                                                                                   ascending=True).reset_index().drop('index', axis=1)
    
    metric3_progress_dict = {'metric': metric3, 'summary': metric3_summary}
                         
    for i in range(0, 4): #n metrics
        metric3_progress_dict[i] = {}
        metric3_progress_dict[i]['top'] = {}
        from_val = ranked_rates_df.iloc[i]['from_value']
        to_val = ranked_rates_df.iloc[i]['to_value']
        metric3_progress_dict[i]['top']['facility'] = '<b>'+ranked_rates_df.iloc[i]['Facility']+'</b>' 
        metric3_progress_dict[i]['top']['from'] = '<b>'+str(from_val)+'</b>'
        metric3_progress_dict[i]['top']['to'] = '<b>'+str(to_val)+'</b>'
        metric3_progress_dict[i]['top']['trend_type'] = ranked_rates_df.iloc[i]['trend_type']
        metric3_progress_dict[i]['top']['percentage_change'] ='<b>'+str(abs(ranked_rates_df.iloc[i]['ObsRateChange'])) + '%</b>' 
        metric3_progress_dict[i]['top']['numeric_icon'] = green_icon(i)
       
        if ranked_rates_df.iloc[i]['trend_type']  == 'decrease':
            metric3_progress_dict[i]['top']['main_class'] = "material-icons md-36 success"
            metric3_progress_dict[i]['top']['class'] = '"text-success"'
            metric3_progress_dict[i]['top']['main_icon'] = arrow_down
            metric3_progress_dict[i]['top']['icon'] = arrow_down
            
        elif ranked_rates_df.iloc[i]['trend_type'] == 'increase':
            metric3_progress_dict[i]['top']['main_class'] = "material-icons md-36 warning"
            metric3_progress_dict[i]['top']['class'] = '"text-warning"'
            metric3_progress_dict[i]['top']['main_icon'] = arrow_up
            metric3_progress_dict[i]['top']['icon'] = arrow_up
            
        elif ranked_rates_df.iloc[i]['trend_type'] == 'equal':
            metric3_progress_dict[i]['top']['main_class'] = "material-icons md-36 info"
            metric3_progress_dict[i]['top']['class'] = '"text-info"'
            metric3_progress_dict[i]['top']['main_icon'] = arrow_right
            metric3_progress_dict[i]['top']['icon'] = arrow_right
            
        else:
            metric3_progress_dict[i]['top']['main_class'] = "material-icons md-36 secondary"
            metric3_progress_dict[i]['top']['class'] = '"text-secondary"'
            metric3_progress_dict[i]['top']['main_icon'] = arrow_right
            metric3_progress_dict[i]['top']['icon'] = arrow_right
     
    ranked_rates_df = ranked_rates_df.dropna(subset=['ObsRateChange']).sort_values(by='ObsRateChange', 
                                                                                   ascending=False).reset_index().drop('index', axis=1)
    
    for i in range(0, 4): #n metrics
    
        metric3_progress_dict[i]['bottom'] = {}
        from_val = ranked_rates_df.iloc[i]['from_value']
        to_val = ranked_rates_df.iloc[i]['to_value']
        metric3_progress_dict[i]['bottom']['facility'] = '<b>'+ranked_rates_df.iloc[i]['Facility']+'</b>' 
        metric3_progress_dict[i]['bottom']['from'] = '<b>'+str(from_val)+'</b>'
        metric3_progress_dict[i]['bottom']['to'] = '<b>'+str(to_val)+'</b>'
        metric3_progress_dict[i]['bottom']['trend_type'] = ranked_rates_df.iloc[i]['trend_type']
        metric3_progress_dict[i]['bottom']['percentage_change'] = '<b>'+str(abs(ranked_rates_df.iloc[i]['ObsRateChange'])) + '%</b>'
        metric3_progress_dict[i]['bottom']['numeric_icon'] = orange_icon(i)
        
        if ranked_rates_df.iloc[i]['trend_type']  == 'decrease':
            metric3_progress_dict[i]['bottom']['main_class'] = "material-icons md-36 success"
            metric3_progress_dict[i]['bottom']['main_icon'] = arrow_down
            metric3_progress_dict[i]['bottom']['class'] = '"text-success"'
            metric3_progress_dict[i]['bottom']['icon'] = arrow_down
            
        elif ranked_rates_df.iloc[i]['trend_type'] == 'increase':
            metric3_progress_dict[i]['bottom']['main_class'] = "material-icons md-36 warning"
            metric3_progress_dict[i]['bottom']['main_icon'] = arrow_up
            metric3_progress_dict[i]['bottom']['class'] = '"text-warning"'
            metric3_progress_dict[i]['bottom']['icon'] = arrow_up
            
        elif ranked_rates_df.iloc[i]['trend_type'] == 'equal':
            metric3_progress_dict[i]['bottom']['class'] = '"text-info"'
            metric3_progress_dict[i]['bottom']['icon'] = arrow_right
            metric3_progress_dict[i]['bottom']['main_class'] = "material-icons md-36 info"
            metric3_progress_dict[i]['bottom']['main_icon'] = arrow_right
        
        else:
            metric3_progress_dict[i]['bottom']['class'] = '"text-secondary"'
            metric3_progress_dict[i]['bottom']['icon'] = arrow_right
            metric3_progress_dict[i]['bottom']['main_class'] = "material-icons md-36 secondary"
            metric3_progress_dict[i]['bottom']['main_icon'] = arrow_right
            
    metric3_progress_dict['summary_icon'] = metric3_icon
    
    #%%3. Observation Cases  > 48 Hrs
    
    last_48_cases = int(last_fiscal_obs_df['Obs_Hours_48'].sum())
    current_48_cases = int(this_fiscal_obs_df['Obs_Hours_48'].sum())
    
    cases_48 = pd.Series([last_48_cases, current_48_cases])
    cases_48_change = cases_48.pct_change()[1]
    
    obs_48_change = round(((cases_48_change)*100),2)
    
    if obs_48_change < 0:
        obs_cases_change_type = 'decreased'
        obs_cases_change_type_verb = 'reduction'
        obs_cases_overall_percentage = '<b>'+str(abs(obs_48_change)) + '%</b>'
        case_change = int(last_48_cases-current_48_cases)
        case_change = f'{case_change:,}'
        metric4_icon = arrow_down_white
        
    elif obs_48_change > 0:
        obs_cases_change_type = 'increase'
        obs_cases_change_type_verb = 'increase'
        obs_cases_overall_percentage = '<b>'+str(abs(obs_48_change)) + '%</b>'
        case_change = int(current_48_cases-last_48_cases)
        case_change = f'{case_change:,}'
        metric4_icon = arrow_up_white
        
    elif obs_48_change == 0:
        obs_cases_change_type = 'flatlined'
        obs_cases_change_type_verb = 'change'
        obs_cases_overall_percentage = 0.0
        metric4_icon = arrow_right_white
        case_change = 0.0
    
    else:
        obs_cases_change_type = 'unknown'
        obs_cases_change_type_verb = 'unknown'
        obs_cases_overall_percentage = '?%'
        metric3_icon = arrow_right_white
      
    metric4_summary = '''The overall Observation Cases > 48 Hours have {} 
    by {} <b>{}</b> from <b>{}</b> cases in {} to <b>{}</b> cases in {}, 
    representing a <b>{}</b> case {}.'''.format(obs_cases_change_type,
                                                    metric4_icon,
                                                    obs_cases_overall_percentage,
                                                    f'{last_48_cases:,}',
                                                    current_month_readable,
                                                    f'{current_48_cases:,}',
                                                    'FYTD',
                                                    case_change,
                                                    obs_cases_change_type_verb)
    
    facilities = tiered_this_fiscal_obs_df['Facility'].drop_duplicates().tolist()
    
    for facility in tiered_facilities:
        
        last_48 = tiered_last_fiscal_obs_df.loc[tiered_last_fiscal_obs_df['Facility'] == facility]['Obs_Hours_48'].reset_index(drop=True)[0]
        current_48 = tiered_this_fiscal_obs_df.loc[tiered_this_fiscal_obs_df['Facility'] == facility]['Obs_Hours_48'].reset_index(drop=True)[0]
        the_48s = pd.Series([last_48, current_48])
        change = the_48s.pct_change()[1]
        obs_48_change = round(((change)*100),2)
        tiered_this_fiscal_obs_df.loc[tiered_this_fiscal_obs_df['Facility'] == facility, 'Obs48Change'] = obs_48_change
        tiered_this_fiscal_obs_df.loc[tiered_this_fiscal_obs_df['Facility'] == facility, 'from_value'] = int(last_48)
        tiered_this_fiscal_obs_df.loc[tiered_this_fiscal_obs_df['Facility'] == facility, 'to_value'] = int(current_48)
     
        if obs_48_change < 0:
            tiered_this_fiscal_obs_df.loc[tiered_this_fiscal_obs_df['Facility'] == facility, 'trend_type'] = 'reduction'
            
        elif obs_48_change > 0:
            tiered_this_fiscal_obs_df.loc[tiered_this_fiscal_obs_df['Facility'] == facility, 'trend_type'] = 'increase'
        
        elif obs_48_change == 0:
            tiered_this_fiscal_obs_df.loc[tiered_this_fiscal_obs_df['Facility'] == facility, 'trend_type'] = 'change'
        
        elif obs_48_change.isna():
            tiered_this_fiscal_obs_df.loc[tiered_this_fiscal_obs_df['Facility'] == facility, 'trend_type'] = 'change'
    
        else:
            tiered_this_fiscal_obs_df.loc[tiered_this_fiscal_obs_df['Facility'] == facility, 'trend_type'] = 'unknown'
              
    # Top/Bottom Performers ##########################################################
    metric4_performer_dict = {}
    obs_48_top = tiered_this_fiscal_obs_df.sort_values(by='Obs_Hours_48', ascending=True).reset_index().drop('index', axis=1)
    
    for i in range(0, 4): 
        metric4_performer_dict[i] = {}
        metric4_performer_dict[i]['top'] = {}        
        facility = obs_48_top['Facility'][i]
        metric4_performer_dict[i]['top']['numeric_icon'] = green_icon(i)
        metric4_performer_dict[i]['top']['facility'] = '<b>'+obs_48_top['Facility'][i]+'</b>'
        metric4_performer_dict[i]['top']['class'] = '"text-success"'
        
        met4_value = int(obs_48_top['Obs_Hours_48'][i])
        met4_from_value = int(obs_48_top['from_value'][i])
        
        metric4_performer_dict[i]['top']['to_value'] = '<b>'+f'{met4_value:,}'+'</b>'
        metric4_performer_dict[i]['top']['from_value'] = '<b>'+f'{met4_from_value:,}'+'</b>'
        metric4_performer_dict[i]['top']['percentage_change_direction'] = obs_48_top['trend_type'][i] 
        metric4_performer_dict[i]['top']['percentage_change'] = '<b>' + str(abs(obs_48_top['Obs48Change'][i])) + '%</b>'
    
        if obs_48_top['trend_type'][i] == 'reduction':
            metric4_performer_dict[i]['top']['icon'] = arrow_down
        elif obs_48_top['trend_type'][i] == 'increase':
            metric4_performer_dict[i]['top']['icon'] = arrow_up
        elif obs_48_top['trend_type'][i] == 'change':
            metric4_performer_dict[i]['top']['icon'] = arrow_right
        else:   
            metric4_performer_dict[i]['top']['icon'] = question_mark
        
    obs_48_bottom = tiered_this_fiscal_obs_df.sort_values(by='Obs_Hours_48', ascending=False).reset_index().drop('index', axis=1)                       
    
    for i in range(0, 4): 
        metric4_performer_dict[i]['bottom'] = {}                   
        metric4_performer_dict[i]['bottom']['numeric_icon'] = orange_icon(i)
        metric4_performer_dict[i]['bottom']['facility'] = '<b>'+obs_48_bottom['Facility'][i]+'</b>'
        metric4_performer_dict[i]['bottom']['class'] = '"text-warning"'
        
        met4_value = int(obs_48_bottom['Obs_Hours_48'][i])
        met4_from_value = int(obs_48_bottom['from_value'][i])
        
        metric4_performer_dict[i]['bottom']['to_value'] = '<b>'+f'{met4_value:,}'+'</b>'    
        metric4_performer_dict[i]['bottom']['from_value'] = '<b>'+f'{met4_from_value:,}'+'</b>'
        metric4_performer_dict[i]['bottom']['percentage_change_direction'] = obs_48_bottom['trend_type'][i] 
        metric4_performer_dict[i]['bottom']['percentage_change'] = '<b>' + str(abs(obs_48_bottom['Obs48Change'][i])) + '%</b>'
    
        if obs_48_bottom['trend_type'][i] == 'reduction':
            metric4_performer_dict[i]['bottom']['icon'] = arrow_down
        elif obs_48_bottom['trend_type'][i] == 'increase':
            metric4_performer_dict[i]['bottom']['icon'] = arrow_up
        elif obs_48_bottom['trend_type'][i] == 'change':
            metric4_performer_dict[i]['bottom']['icon'] = arrow_right   
        else:   
            metric4_performer_dict[i]['bottom']['icon'] = question_mark
            
    # Best/Worst Progress ##########################################################
    ranked_48_df = tiered_this_fiscal_obs_df[['Facility', 'from_value', 'to_value', 'Obs48Change', 'trend_type']].drop_duplicates()
    ranked_48_df = ranked_48_df.dropna(subset=['Obs48Change']).sort_values(by='Obs48Change', ascending=True).reset_index().drop('index', axis=1)
    metric4_progress_dict = {'metric': metric4, 'summary': metric4_summary}
                      
    for i in range(0, 4): 
    
        metric4_progress_dict[i] = {}
        metric4_progress_dict[i]['top'] = {}
        from_val = int(ranked_48_df.iloc[i]['from_value'])
        to_val = int(ranked_48_df.iloc[i]['to_value'])
        metric4_progress_dict[i]['top']['facility'] = '<b>'+ranked_48_df.iloc[i]['Facility']+'</b>' #1 facility
        metric4_progress_dict[i]['top']['from'] = '<b>'+f'{from_val:,}'+'</b>'
        metric4_progress_dict[i]['top']['to'] = '<b>'+f'{to_val:,}'+'</b>'
        
        metric4_progress_dict[i]['top']['percentage_change'] = '<b>'+str(abs(ranked_48_df.iloc[i]['Obs48Change'])) + '%</b>'
        metric4_progress_dict[i]['top']['numeric_icon'] = green_icon(i)
        
        if ranked_48_df.iloc[i]['trend_type'] == 'reduction':
            metric4_progress_dict[i]['top']['trend_type'] = 'reduced'
            metric4_progress_dict[i]['top']['class'] = '"text-success"'
            metric4_progress_dict[i]['top']['icon'] = arrow_down
            metric4_progress_dict[i]['top']['main_class'] = "material-icons md-36 success"
            metric4_progress_dict[i]['top']['main_icon'] = arrow_down
            
        elif ranked_48_df.iloc[i]['trend_type'] == 'increase':
            metric4_progress_dict[i]['top']['trend_type'] = 'increased'
            metric4_progress_dict[i]['top']['class'] = '"text-warning"'
            metric4_progress_dict[i]['top']['icon'] = arrow_up
            metric4_progress_dict[i]['top']['main_class'] = "material-icons md-36 warning"
            metric4_progress_dict[i]['top']['main_icon'] = arrow_up
            
        elif ranked_48_df.iloc[i]['trend_type'] == 'equal':
            metric4_progress_dict[i]['top']['trend_type'] = 'equaled'
            metric4_progress_dict[i]['top']['class'] = '"text-info"'
            metric4_progress_dict[i]['top']['icon'] = arrow_right
            metric4_progress_dict[i]['top']['main_class'] = "material-icons md-36 info"
            metric4_progress_dict[i]['top']['main_icon'] = arrow_right
    
        else:
            metric4_progress_dict[i]['top']['trend_type'] = 'unknown'
            metric4_progress_dict[i]['top']['class'] = '"text-info"'
            metric4_progress_dict[i]['top']['icon'] = arrow_right
            metric4_progress_dict[i]['top']['main_class'] = "material-icons md-36 info"
            metric4_progress_dict[i]['top']['main_icon'] = arrow_right
            
    ranked_48_df = ranked_48_df.dropna(
        subset=['Obs48Change']).sort_values(
            by='Obs48Change', ascending=False).reset_index().drop('index', axis=1)
    ranked_48_df['from_value'] = ranked_48_df['from_value'].astype(int)
    ranked_48_df['to_value'] = ranked_48_df['to_value'].astype(int)
    
    for i in range(0, 4): 
    
        metric4_progress_dict[i]['bottom'] = {}
        from_val = ranked_48_df.iloc[i]['from_value']
        to_val = ranked_48_df.iloc[i]['to_value']
        metric4_progress_dict[i]['bottom']['facility'] = '<b>'+ranked_48_df.iloc[i]['Facility']+'</b>' #bottom 1 facility
        metric4_progress_dict[i]['bottom']['from'] = '<b>'+f'{from_val:,}'+'</b>'
        metric4_progress_dict[i]['bottom']['to'] = '<b>'+f'{to_val:,}'+'</b>'
        metric4_progress_dict[i]['bottom']['percentage_change'] = '<b>'+str(abs(ranked_48_df.iloc[i]['Obs48Change'])) + '%</b>' #bottom 1 value
        metric4_progress_dict[i]['bottom']['numeric_icon'] = orange_icon(i)
        
        if ranked_48_df.iloc[i]['trend_type'] == 'reduction':
            metric4_progress_dict[i]['bottom']['trend_type'] = 'reduced'
            metric4_progress_dict[i]['bottom']['class'] = '"text-success"'
            metric4_progress_dict[i]['bottom']['icon'] = arrow_down
            metric4_progress_dict[i]['bottom']['main_class'] = "material-icons md-36 success"
            metric4_progress_dict[i]['bottom']['main_icon'] = arrow_down
            
        elif ranked_48_df.iloc[i]['trend_type'] == 'increase':
            metric4_progress_dict[i]['bottom']['trend_type'] = 'increased'
            metric4_progress_dict[i]['bottom']['class'] = '"text-warning"'
            metric4_progress_dict[i]['bottom']['icon'] = arrow_up
            metric4_progress_dict[i]['bottom']['main_class'] = "material-icons md-36 warning"
            metric4_progress_dict[i]['bottom']['main_icon'] = arrow_up
            
        elif ranked_48_df.iloc[i]['trend_type'] == 'change':
            metric4_progress_dict[i]['bottom']['trend_type'] = 'equaled'
            metric4_progress_dict[i]['bottom']['class'] = '"text-info"'
            metric4_progress_dict[i]['bottom']['icon'] = arrow_right
            metric4_progress_dict[i]['bottom']['main_class'] = "material-icons md-36 info"
            metric4_progress_dict[i]['bottom']['main_icon'] = arrow_right
    
        else:
            metric4_progress_dict[i]['bottom']['trend_type'] = 'unknown'
            metric4_progress_dict[i]['bottom']['class'] = '"text-info"'
            metric4_progress_dict[i]['bottom']['icon'] = arrow_right
            metric4_progress_dict[i]['bottom']['main_class'] = "material-icons md-36 info"
            metric4_progress_dict[i]['bottom']['main_icon'] = arrow_right
    
    metric4_progress_dict['summary_icon'] = metric4_icon    
    
    data = [metric1_progress_dict,
            metric2_progress_dict,
            metric3_progress_dict,
            metric4_progress_dict]
    
    performers = [metric1_performer_dict,
                  metric2_performer_dict,
                  metric3_performer_dict,
                  metric4_performer_dict]
    
    #%% Recommendations
    
    recommendations = {}
    for i in range(0,8):
        recommendations[i] = {   'class': choice(icon_classes), 
                                  'icon': choice(icons),
                                  'area': choice(areas),
                                'action': choice(actions),
                            'percentage': randrange(1,100)}
    
    #%% render
    
    today = datetime.now().strftime('%b %d, %Y')
    env = JinjaEnvironment(loader=FileSystemLoader('templates/'))
    
    
    template = env.get_template('report_template.html')
    html = template.render(current_readable = current_month_readable,
                           last_readable = last_month_readable,
                            date = today,
                            data = data,
                            performers = performers,
                            data_points = data_points,
                            css_file = css_file,
                            extended_css_file = extended_css_file,
                            recommendations = recommendations)
    
    with open("html/report.html", "w") as h:
        h.write(html)
        h.close() 
    
    options = {
                           '--orientation': 'Landscape',
                'enable-local-file-access': ""
              }
    
    pdfkit.from_file("html/report.html", "pdfs/report.pdf", options=options)
