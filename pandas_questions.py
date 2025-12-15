"""Plotting referendum results in pandas.
In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

def load_data():
    """Load data from the CSV files referundum/regions/departments.
     referendum = pd.DataFrame({})
    regions = pd.DataFrame({})
    departments = pd.DataFrame({})
    """
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")
    return referendum, regions, departments

def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.
    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged = departments.merge(
        regions,
        left_on="region_code",
        right_on="code",
        how="inner",
        suffixes=("_dep", "_reg"),
    )
    # select and rename columns
    merged = merged.rename(
        columns={
            "code_reg": "code_reg",
            "name_reg": "name_reg",
            "code_dep": "code_dep",
            "name_dep": "name_dep",
        }
    )
    return merged[["code_reg", "name_reg", "code_dep", "name_dep"]]
    # return pd.DataFrame({})

def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.
    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.
    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    # 1.copy and avoid SettingWithCopy
    referendum = referendum.copy()
    # 2. Department codes should be formatted 
    # as strings and padded with two digits
    referendum["Department code"] = (
        referendum["Department code"]
        .astype(str)
        .str.zfill(2)
    )
    # 3. Delete DOM-TOM / abroad (starting with Z)
    referendum = referendum[
        ~referendum["Department code"].str.startswith("Z")
    ]
    # 4. inner merge（won't generate NaN）
    merged = referendum.merge(
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="inner",
    )
    return merged
    # return pd.DataFrame({})

def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.
    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    # sum numeric results by region
    grouped = referendum_and_areas.groupby("code_reg").sum(numeric_only=True)
    # keep region name
    grouped["name_reg"] = (
        referendum_and_areas.groupby("code_reg")["name_reg"].first()
        )
    # select and order columns
    grouped = grouped[
        ["name_reg", "Registered", "Abstentions", "Null", "Choice A", "Choice B"]
        ]
    return grouped
    # return pd.DataFrame({})

def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.
    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # load geographic data
    gdf_regions = gpd.read_file("data/regions.geojson", engine="pyogrio")
    # transfer index to column for merge
    results = referendum_result_by_regions.reset_index()
    # merge geographic data with referendum results
    gdf = gdf_regions.merge(
        results,
        left_on="code",
        right_on="code_reg",
        how="left",
    )
    # compute ratio of Choice A over expressed ballots
    gdf["ratio"] = gdf["Choice A"] / (gdf["Choice A"] + gdf["Choice B"])
    # plot
    gdf.plot(column="ratio", legend=True)
    return gdf
    # return gpd.GeoDataFrame({})

if __name__ == "__main__":
    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)
    plot_referendum_map(referendum_results)
    plt.show()
