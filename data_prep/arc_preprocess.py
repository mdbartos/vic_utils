import arcpy

#Clip raster
#Clip_management (in_raster, rectangle, out_raster, {in_template_dataset}, {nodata_value}, {clipping_geometry})

#Add Field
#AddField_management (in_table, field_name, field_type, {field_precision}, {field_scale}, {field_length}, {field_alias}, {field_is_nullable}, {field_is_required}, {field_domain})

#Create Fishnet
#CreateFishnet_management (out_feature_class, origin_coord, y_axis_coord, cell_width, cell_height, number_rows, number_columns, {corner_coord}, {labels}, {template}, {geometry_type})

#Intersect
#Intersect_analysis (in_features, out_feature_class, {join_attributes}, {cluster_tolerance}, {output_type})

poly_list = { \
"davis" : "abv_davis_c_a_clipped.shp",
"gc" : "abv_gc_poly_clipped.shp",
"imperial" : "abv_imp_c_a_clipped.shp",
"hoover" : "abv_hoover_c_a_clipped.shp",
"parker" : "abv_park_c_a_clipped.shp",
"billw" : "billw_c_a_poly.shp",
"gila_imp" : "gila_imp_poly.shp",
"little_col" : "little_co_contrib_area_poly.shp",
"paria" : "paria_c_a_poly.shp",
"virgin" : "virgin_c_a_poly.shp",
"lees_f" : "lees_f_c_a_poly.shp",
"castaic" : "castaic_poly.shp",
"corona" : "corona.shp",
"cottonwood" : "cottonwood_poly.shp",
"coyotecr" : "coyotecr_poly.shp",
"kern" : "kern_poly.shp",
"pitt" : "pitt_poly.shp",
"redmtn" : "redmtn_poly.shp",
"riohondo" : "riohondo_poly.shp",
"rushcr" : "rushcr_poly.shp",
"tulare" : "tulare_poly.shp",
"colstrip" : "colstrip_poly.shp",
"comanche" : "comanche_poly.shp",
"eaglept" : "eaglept_poly.shp",
"guer" : "guernsey_poly.shp",
"irongate" : "irongate_poly.shp",
"pawnee" : "pawnee_poly.shp",
"peck" : "peck_poly.shp",
"sodasprings" : "sodasprings_poly.shp",
"wauna" : "wauna_poly.shp",
"brigham" : "brigham_poly.shp",
"intermtn" : "intermtn_poly.shp",
"salton" : "salton_poly.shp",
"wabuska" : "wabuska_poly.shp",
"lahontan" : "lahontan_poly.shp",
"yelm" : "yelm_poly.shp",
"hmjack" : "hmjack_poly.shp",
"baker" : "baker_poly.shp",
"elwha" : "elwha_poly.shp",
"paper" : "paper_poly.shp",
"glenn" : "glenns_poly.shp"}

#Clip 16d grid
for i, k in poly_list.items():
	arcpy.Clip_management("flowdir_16d.asc", "#" , "e:/MBartos/source_GIS/other/grid_16d/dir/%s_d" % (i), k)
	arcpy.RasterToASCII_conversion ("%s_d" % (i), "e:/MBartos/source_GIS/other/grid_16d/dir/ascii/%s_d.asc" % (i))


#Intersect fishnet & make frac file
int_d = {}
for i, k in poly_list.items():
	arcpy.Intersect_analysis([k.split('.')[0], "grid_16d"], "e:/MBartos/source_GIS/other/grid_16d/int/%s_int.shp" % (i))
	int_d.update({i : "%s_int.shp" % (i)})
	int_db = "%s_int" % (i)
	arcpy.AddField_management(int_db, "int_area", "FLOAT")
	exp = "!SHAPE.AREA@SQUAREMETERS!"
	arcpy.CalculateField_management(int_db, "int_area", exp, "PYTHON_9.3")
	arcpy.AddField_management(int_db, "frac", "FLOAT")
	exp2 = "!int_area!/!calc_area!"
	arcpy.CalculateField_management(int_db, "frac", exp2, "PYTHON_9.3")
	arcpy.AddJoin_management("grid_16d", "Id", int_db, "Id_1", "KEEP_COMMON")
	arcpy.CopyFeatures_management("grid_16d", "e:/MBartos/source_GIS/other/grid_16d/ri/%s_ri.shp" % (i))
	arcpy.RemoveJoin_management("grid_16d")

for i in poly_list.keys():
	fname = arcpy.ListFields("%s_ri" % (i))[-1].name
	arcpy.PolygonToRaster_conversion ("%s_ri" % (i), fname, "e:/MBartos/source_GIS/other/grid_16d/frac/%s_f" % (i), "CELL_CENTER", "#", 0.0625)
	arcpy.RasterToASCII_conversion ("%s_f" % (i), "e:/MBartos/source_GIS/other/grid_16d/dir/ascii/%s_f.asc" % (i))
