# nsf_cosea workflow
## SQL Scripts
<details>
<summary><strong>View SQL Script Details</strong></summary>

### 1. `filtering_schools.sql`
1. Creates `UNIQUESCHOOLID` in `ga_school_contact_list` and `fte2024-1_enroll-demog_sch`
2. Filters schools by grade range into `filtered_schools`
3. Creates a table for alternative schools `alternative_schools`
4. Removes `alternative_schools` from `filtered_schools`
5. Joins `School Address`, `School City`, `State`, `lat` and `lon` from `ga_school_contact_list` to the new table `tbl_approvedschools`
6. Creates a `schoolgeom` column  that contains the point geom derived from the coordinates in `tbl_approvedschools`

---

### 2. `district_info.sql`
1. Extracts numeric portion of `State District ID` and store it as `district_id_clean` in `ncesdata2024`.
2. Joins the `Locale Code` from `ncesdata2024` to `tbl_approvedschools` using `SYSTEM_ID = district_id_clean`.
3. Converts `Locale Code` into simplified categories:  
   - **City** (`Locale Code` 11-19)  
   - **Suburb** (`Locale Code` 21-29)  
   - **Town** (`Locale Code` 31-39)  
   - **Rural** (`Locale Code` 41-49)  
4. Stores the locale type in the `Locale` column of `tbl_approvedschools`.  

---

### 3. `define_buffers.sql`
1. Creates `tbl_bufferlookup` to store buffer distances for different locale types.
2. Inserts predefined buffer distances:
   - **City** → 1 mile  
   - **Suburb** → 3 miles  
   - **Town** → 7 miles  
   - **Rural** → 18 miles  
3. Adds a `buffer_distance` column to `tbl_approvedschools`
4. Joins `buffer_distance` from `tbl_bufferlookup` to `tbl_approvedschools`

---

### 4. `attendance_zones.sql`

</details>

---

## Final Data Description
### `table_name`
- **Column_Name**: Description of columnn

Last updated: 02/18/2025 by Linn