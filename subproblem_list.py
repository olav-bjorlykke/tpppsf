import numpy as np
import pandas as pd
from input_data import InputData
from site_class import Site
from scenarios import Scenarios
from model import Model
import configs


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
    init_biomass=907 * 1000,
    init_avg_weight=2410,
    init_biomass_months_deployed=8,
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
    init_biomass=378 * 1000,
    init_avg_weight=695,
    init_biomass_months_deployed=4,
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
    init_biomass=661 * 1000,
    init_avg_weight=1634,
    init_biomass_months_deployed=6,
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
    init_biomass=661 * 1000,
    init_avg_weight=1634,
    init_biomass_months_deployed=6,
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
    init_biomass=1312 * 1000,
    init_avg_weight=2458,
    init_biomass_months_deployed=12,
    site_name="HOLAND"
)
site_11 = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc[area_senja_string],
    MAB_capacity=4680*1000,
    init_biomass=4296 * 1000,
    init_avg_weight=5464,
    init_biomass_months_deployed=17,
    site_name="LAVIKA"
)

site_12 = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc[area_senja_string],
    MAB_capacity=3600*1000,
    init_biomass=3536 * 1000,
    init_avg_weight=6536,
    init_biomass_months_deployed=18,
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
    init_biomass=961 * 1000,
    init_avg_weight=1411,
    init_biomass_months_deployed=7,
    site_name="RUSSELVA"
)
site_16 = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc[area_nordtroms_string],
    MAB_capacity=5000*1000,
    site_name="HAUKØYA Ø",
)


sites_list = [site_1, site_2, site_3, site_4, site_5, site_6,
              site_7, site_8, site_9, site_10, site_11, site_12,
              site_13, site_14, site_15, site_16]

medium_sites_list = [site_3, site_4, site_6, site_7, site_8,
                site_9, site_10, site_15]

short_sites_list = [site_4, site_6,  site_15]


sub_problem_list = [Model(site_objects=site) for site in sites_list]
medium_sub_problem_list = [Model(site_objects=site) for site in medium_sites_list]
short_sub_problem_list = [Model(site_objects=site) for site in short_sites_list]


short_node_init_list = [[2,0]]
medium_node_init_list = [[0,0],[4,0],[6,0],[7,0]]
long_node_init_list = [[0,0], [2,0], [4,0], [7,0], [9,0],[10,0], [11,0], [14,0]]

NODE_INIT_LIST = short_node_init_list
SUB_PROBLEM_LIST = short_sub_problem_list
SITE_LIST = short_sites_list

if configs.INSTANCE == "SMALL":
    NODE_INIT_LIST = short_node_init_list
    SUB_PROBLEM_LIST = short_sub_problem_list
    SITE_LIST = short_sites_list


elif configs.INSTANCE == "MEDIUM":
    NODE_INIT_LIST = medium_node_init_list
    SUB_PROBLEM_LIST = medium_sub_problem_list
    SITE_LIST = medium_sites_list

elif configs.INSTANCE == "LARGE":
    NODE_INIT_LIST = long_node_init_list
    SUB_PROBLEM_LIST = sub_problem_list
    SITE_LIST = sites_list

else:
    print("Instance set does not match any, set to default")
