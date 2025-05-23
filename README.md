# nsf_cosea workflow

This repository contains SQL scripts and a Jupyter notebook used to process and analyze Georgia High School data

### Repository Structure

- `cosea_workbook.ipynb`: Main notebook with the analysis and data processing workflow
- `sql/`: Contains 4 SQL scripts that generate final outputs: `tbl_approvedschools` and `tbl_cbg_finalassignment`
- `old/`: Contains deprecated and unused materials (includes `data.zip` with needed CSVs)
- `docs/`: Documentation

---

### Workbook Summary
**output tables:** `census.gadoe2024` and `census.course_logic_2024`

The Jupyter notebook performs the following tasks:

- Defines approved CS courses
- Standardizes IDs, cleans certification data, and formats course titles
- Summarizes enrollment and demographics by school
- Combines approved schools, enrollment, and course data into one dataset
- Computes under-/over-representation of racial/gender groups in CS courses
- Logic Flags:
  - `LOGIC_CLASS`: Binary flags for in-person, virtual, and extra CS teachers
  - `LOGIC_CLASS_2`: Same logic using expanded list of CS-related courses

---

### SQL Scripts
**output tables:** `tbl_approvedschools` and `tbl_cbg_finalassignment`

**Files needed in database:**
- `fte2024-1_enroll-demog_sch.csv`
- `ga_school_contact_list.csv`
- `ncesdata2024.csv`
- `tl_2024_13_bg.zip` (named `2024.tbl_cbg` in our database)

#### 1. `filtering_schools.sql`
1. Creates `UNIQUESCHOOLID` in `ga_school_contact_list` and `fte2024-1_enroll-demog_sch`
2. Filters schools by grade range into `filtered_schools`
3. Creates a table for alternative schools `alternative_schools`
4. Removes `alternative_schools` from `filtered_schools`
5. Joins `School Address`, `School City`, `State`, `lat` and `lon` from `ga_school_contact_list` to the new table `tbl_approvedschools`
6. Creates a `schoolgeom` column  that contains the point geom derived from the coordinates in `tbl_approvedschools`

#### 2. `district_info.sql`
1. Extracts numeric portion of `State District ID` and store it as `district_id_clean` in `ncesdata2024`.
2. Joins the `Locale Code` from `ncesdata2024` to `tbl_approvedschools` using `SYSTEM_ID = district_id_clean`.
3. Converts `Locale Code` into simplified categories:  
   - **City** (`Locale Code` 11-19)  
   - **Suburb** (`Locale Code` 21-29)  
   - **Town** (`Locale Code` 31-39)  
   - **Rural** (`Locale Code` 41-49)  
4. Stores the locale type in the `Locale` column of `tbl_approvedschools`.

#### 3. `define_buffers.sql`
1. Creates `tbl_bufferlookup` to store buffer distances for different locale types.
2. Inserts predefined buffer distances:
   - **City** → 1 mile  
   - **Suburb** → 3 miles  
   - **Town** → 7 miles  
   - **Rural** → 18 miles  
3. Adds a `buffer_distance` column to `tbl_approvedschools`
4. Joins `buffer_distance` from `tbl_bufferlookup` to `tbl_approvedschools`

#### 4. `attendance_zones.sql`
1. Creates `cbgcentroidgeom` column in `tbl_cbg` and populates it with centroids
2. Assigns CBGs to schools using buffer distances (`ST_DWithin()`)
3. Computes distances between CBG centroids and schools
4. Assigns each CBG to the closest school within the buffer
5. Identifies unassigned CBGs and assigns them to the nearest school
6. Creates `tbl_cbg_finalassignment`, ensuring every CBG is assigned to exactly one school
7. Validation checks:
   - [x] All CBGs are assigned once (`tbl_cbg_finalassignment = tbl_cbg`)
   - [x] No duplicate assignments
   - [x] Every school has at least one assigned CBG
