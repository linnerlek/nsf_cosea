-- Extract numeric portion of district ID
ALTER TABLE "2024".ncesdata2024 ADD COLUMN IF NOT EXISTS district_id_clean TEXT;

UPDATE "2024".ncesdata2024
SET district_id_clean = SPLIT_PART("State District ID", '-', 2);

-- Add missing columns from "2024".ncesdata2024 to "2024".tbl_approvedschools
DO $$ 
DECLARE 
    col_record RECORD;
BEGIN
    FOR col_record IN 
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_schema = '2024'  
        AND table_name = 'ncesdata2024' 
        AND column_name NOT IN ( -- Exclude duplicates
            'district_id_clean',
            'ZIP',
            'ZIP 4-digit',       
            'State District ID',  
            'Street Address', -- we do not need the district address
            'Students', -- students in entire district not per school
            'Teachers', -- teachers in entire district not per school
            'Student Teacher Ratio', -- ratio is for entire district not per school
            'City',
            'State',
            'Phone',
            'Schools'
        )
        AND column_name NOT IN (
            SELECT column_name FROM information_schema.columns 
            WHERE table_schema = '2024' 
            AND table_name = 'tbl_approvedschools'
        )
    LOOP
        EXECUTE format('ALTER TABLE "2024".tbl_approvedschools ADD COLUMN IF NOT EXISTS %I TEXT;', col_record.column_name);
    END LOOP;
END $$;

DO $$ 
DECLARE 
    column_list TEXT;
BEGIN
    SELECT STRING_AGG(format('%I = n.%I', col.column_name, col.column_name), ', ')
    INTO column_list
    FROM information_schema.columns col
    WHERE col.table_schema = '2024' 
    AND col.table_name = 'ncesdata2024'
    AND col.column_name NOT IN (
		'district_id_clean',
            'ZIP',
            'ZIP 4-digit',       
            'State District ID',  
            'Street Address',
            'Students', 
            'Teachers',
            'Student Teacher Ratio',
            'City',
            'State',
            'Phone',
            'Schools'
        );
    EXECUTE format(
        'UPDATE "2024".tbl_approvedschools AS a
         SET %s
         FROM "2024".ncesdata2024 AS n
         WHERE a."SYSTEM_ID" = n.district_id_clean::INTEGER;', 
        column_list
    );
END $$;
