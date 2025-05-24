import psycopg2
import pandas as pd
import geopandas as gpd
import folium
from folium import Choropleth, CircleMarker
from folium.plugins import Fullscreen
conn = psycopg2.connect(
    dbname="cosea_db",
    user="cosea_user",
    password="CoSeaIndex",
    host="pgsql.dataconn.net",
    port="5432"
)
school_query = """
SELECT 
    ST_X(ST_GeomFromWKB(decode("schoolgeom", 'hex'), 4326)) AS lon,
    ST_Y(ST_GeomFromWKB(decode("schoolgeom", 'hex'), 4326)) AS lat,
    "DI_Asian"
FROM "2024"."tbl_approvedschools"
"""
school_df = pd.read_sql(school_query, conn)
school_df['asian_disparity'] = pd.to_numeric(school_df['DI_Asian'], errors='coerce')
school_df.dropna(subset=['lon', 'lat', 'asian_disparity'], inplace=True)
pop_query = """
SELECT 
    "Geo_FIPS",
    "SE_A04001_006",
    "SE_A04001_001"
FROM "census"."population_race_ethnicity"
"""
pop_df = pd.read_sql(pop_query, conn)
pop_df['asian_ratio'] = pop_df["SE_A04001_006"] / pop_df["SE_A04001_001"]
pop_df['Geo_FIPS'] = pop_df['Geo_FIPS'].astype(str).str.zfill(12)
block_groups_query = """
SELECT 
    "GEOID",
    ST_AsGeoJSON(ST_Transform(cbgpolygeom, 4326)) AS geometry
FROM "2024"."tbl_cbg"
"""
block_df = pd.read_sql(block_groups_query, conn)
block_df['GEOID'] = block_df['GEOID'].astype(str).str.zfill(12)
merged_df = block_df.merge(pop_df[['Geo_FIPS', 'asian_ratio']],
                           left_on='GEOID', right_on='Geo_FIPS', how='left')
merged_df.dropna(subset=['asian_ratio'], inplace=True)
merged_df['asian_ratio_class'] = pd.qcut(
    merged_df['asian_ratio'],
    5,
    labels=False,
    duplicates='drop'
)
blue_shades = ['#c6dbef', '#9ecae1', '#6baed6', '#3182bd', '#08519c']
merged_df['fill_color'] = merged_df['asian_ratio_class'].apply(lambda x: blue_shades[int(x)] if pd.notnull(x) else 'gray')
m = folium.Map(location=[32.5, -83.5], zoom_start=7, tiles='CartoDB positron')
for _, row in merged_df.iterrows():
    geojson = {
        "type": "Feature",
        "geometry": eval(row['geometry']),
        "properties": {
            "fillColor": row['fill_color'],
            "color": "black",
            "weight": 0.2,
            "fillOpacity": 0.85
        }
    }
    folium.GeoJson(
        geojson,
        style_function=lambda feature: {
            'fillColor': feature['properties']['fillColor'],
            'color': feature['properties']['color'],
            'weight': feature['properties']['weight'],
            'fillOpacity': feature['properties']['fillOpacity']
        }
    ).add_to(m)
def get_color(val):
    if pd.isnull(val):
        return 'gray'
    elif val <= -0.050279:
        return 'pink'
    elif -0.050278 <= val <= 0.049733:
        return 'white'
    elif 0.049734 <= val <= 0.083157:
        return 'lightgreen'
    elif 0.083158 <= val <= 0.138494:
        return 'mediumseagreen'
    else:
        return 'darkgreen'
for _, row in school_df.iterrows():
    color = get_color(row['asian_disparity'])
    folium.CircleMarker(
        location=(row['lat'], row['lon']),
        radius=3,
        color='black',
        weight=0.3,
        fill=True,
        fill_color=color,
        fill_opacity=0.85,
        line_opacity=0,
    line_color='white',
        popup=folium.Popup(f"DI_Asian: {round(row['asian_disparity'], 4)}", max_width=250)
    ).add_to(m)
legend_html = """
<div style="
    position: fixed; 
    bottom: 50px; right: 10px; 
    z-index:9999; 
    background-color: white;
    border:2px solid grey;
    padding: 10px;
    font-size: 13px;
    box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
">
<b>Legend</b><br>
<b>Asian Ratio (Underlay)</b><br>
<div style='background:#c6dbef; width:20px; height:10px; display:inline-block'></div> Lowest 20%<br>
<div style='background:#9ecae1; width:20px; height:10px; display:inline-block'></div> 20-40%<br>
<div style='background:#6baed6; width:20px; height:10px; display:inline-block'></div> 40-60%<br>
<div style='background:#3182bd; width:20px; height:10px; display:inline-block'></div> 60-80%<br>
<div style='background:#08519c; width:20px; height:10px; display:inline-block'></div> Highest 20%<br><br>

<b>Asian Disparity (Schools)</b><br>
<div style='background:pink; width:20px; height:10px; display:inline-block'></div> ≤ -0.050279<br>
<div style='background:white; width:20px; height:10px; display:inline-block; border:1px solid black'></div> -0.050278 to 0.049733<br>
<div style='background:lightgreen; width:20px; height:10px; display:inline-block'></div> 0.049734 to 0.083157<br>
<div style='background:mediumseagreen; width:20px; height:10px; display:inline-block'></div> 0.083158 to 0.138494<br>
<div style='background:darkgreen; width:20px; height:10px; display:inline-block'></div> ≥ 0.138495
</div>
"""

m.get_root().html.add_child(folium.Element(legend_html))

Fullscreen().add_to(m)
m.save("map4_interactive_updated.html")