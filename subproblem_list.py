import numpy as np
import pandas as pd
from parameters import GlobalParameters
from input_data import InputData
from site_class import Site
from scenarios import Scenarios
from sub_problem_class import SubProblem
from master_problem import MasterProblem


input_test =InputData()
scenarios_test = Scenarios(input_test.temperatures_df)

area_vesteralen_string = "Vesteralen"
area_nordtroms_string = "Nord-Troms"
area_senja_string = "Senja"

"""
Sites
"""
site_1 = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc[area_vesteralen_string],
    MAB_capacity=3120 * 1000,
    init_biomass=1500 * 1000,
    init_avg_weight=2000,
    init_biomass_months_deployed=11,
    site_name="INNERBROKLØYSA"
)

site_2 = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc[area_vesteralen_string],
    MAB_capacity=2340 * 1000,
    site_name="SANDAN SØ"
)

site_3 = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc[area_vesteralen_string],
    MAB_capacity=3120*1000,
    site_name="TROLLØYA SV"
)

site_4 = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc[area_vesteralen_string],
    MAB_capacity=3120*1000,
    site_name="KUNESET"
)

site_5 = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc[area_vesteralen_string],
    MAB_capacity=3120*1000,
    site_name="STRETARNESET"
)
site_6 = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc[area_vesteralen_string],
    MAB_capacity=3120*1000,
    site_name="DALJORDA"
)
site_7 = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc[area_vesteralen_string],
    MAB_capacity=5500*1000,
    site_name="REINSNESØYA"
)
site_8 = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc[area_vesteralen_string],
    MAB_capacity=3120*1000,
    site_name="LANGHOLMEN N"
)
site_9 = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc[area_vesteralen_string],
    MAB_capacity=3900*1000,
    site_name="BREMNESØYA"
)
site_10 = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc[area_vesteralen_string],
    MAB_capacity=2340*1000,
    site_name="Holand"
)
site_11 = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc[area_senja_string],
    MAB_capacity=4680*1000,
    site_name="LAVIKA"
)
site_12 = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc[area_senja_string],
    MAB_capacity=3600*1000,
    init_biomass=100 * 1000,
    init_avg_weight=3200,
    init_biomass_months_deployed=15,
    site_name="FLESEN"
)
site_13 = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc[area_senja_string],
    MAB_capacity=3900*1000,
    site_name="KVENBUKTA V"
)
site_14 = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc[area_nordtroms_string],
    MAB_capacity=3600*1000,
    site_name="HAGEBERGAN"
)
site_15 = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc[area_nordtroms_string],
    MAB_capacity=3500*1000,
    site_name="RUSSELVA"
)
site_16 = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc[area_nordtroms_string],
    MAB_capacity=5000*1000,
    site_name="HAUKØYA Ø",
    init_biomass=200 * 1000,
    init_avg_weight=3200,
    init_biomass_months_deployed=16,
)


sites_list = [site_1, site_2, site_3, site_4, site_5, site_6,
              site_7, site_8, site_9, site_10, site_11, site_12,
              site_13, site_14, site_15, site_16]

medium_sites_list = [site_1, site_2, site_3, site_4, site_5, site_6,
              site_7, site_8,]

short_sites_list = [site_1, site_12, site_16]


sub_problem_list = [SubProblem(site_obj=site) for site in sites_list]
medium_sub_problem_list = [SubProblem(site_obj=site) for site in medium_sites_list]
short_sub_problem_list = [SubProblem(site_obj=site) for site in short_sites_list]
