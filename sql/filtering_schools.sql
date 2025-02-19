-- Create UNIQUESCHOOLID
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = '2024' 
        AND table_name = 'ga_school_contact_list' 
        AND column_name = 'UNIQUESCHOOLID'
    ) THEN
        ALTER TABLE "2024".ga_school_contact_list 
        ADD COLUMN "UNIQUESCHOOLID" TEXT;
    END IF;
END $$;
UPDATE "2024".ga_school_contact_list
SET "UNIQUESCHOOLID" = LPAD("District ID"::TEXT, 4, '0') || LPAD("School ID"::TEXT, 4, '0');

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = '2024' 
        AND table_name = 'fte2024-1_enroll-demog_sch' 
        AND column_name = 'UNIQUESCHOOLID'
    ) THEN
        ALTER TABLE "2024"."fte2024-1_enroll-demog_sch" 
        ADD COLUMN "UNIQUESCHOOLID" TEXT;
    END IF;
END $$;
UPDATE "2024"."fte2024-1_enroll-demog_sch"
SET "UNIQUESCHOOLID" = LPAD("SYSTEM_ID"::TEXT, 4, '0') || LPAD("SCHOOL_ID"::TEXT, 4, '0');


-- Filter schools by grade range
CREATE TABLE "2024".filtered_schools AS
SELECT * 
FROM "2024"."fte2024-1_enroll-demog_sch"
WHERE NOT EXISTS (
    SELECT 1
    FROM unnest(
        regexp_split_to_array(
            regexp_replace(
                regexp_replace("GRADE_RANGE", 'PK', '0', 'g'), 
                'KK', '0.5', 'g'
            ), '[,-]'
        )::TEXT[]
    ) AS extracted_grades
    WHERE extracted_grades ~ '^[0-9.]+$' 
          AND extracted_grades::FLOAT < 9
)
AND EXISTS (
    SELECT 1
    FROM unnest(
        regexp_split_to_array(
            regexp_replace(
                regexp_replace("GRADE_RANGE", 'PK', '0', 'g'), 
                'KK', '0.5', 'g'
            ), '[,-]'
        )::TEXT[]
    ) AS extracted_grades
    WHERE extracted_grades ~ '^[0-9.]+$' 
          AND extracted_grades::FLOAT BETWEEN 9 AND 12
);

-- Create a table for alternative_schools
CREATE TABLE "2024".alternative_schools AS
SELECT * FROM "2024".filtered_schools
where "SCHOOL_NAME" ILIKE ANY (ARRAY[
    '%Academy%', '%STEM%', '%Charter%', '%State Schools%', '%Virtual%', '%Institute%', 
    '%Foundry%', '%Transition%', '%Center%', '%Online%', '%Intervention%', '%S.T.E.M.%', 
    '%Treatment%', '%Youth%', '%Home%', '%Ministries%', '%Chance%', '%Comprehensive%', 
    '%Career%', '%Arts%', '%E-Learning%', '%Humanities%', '%ITU%'
]);

-- Remove alternative_schools from filtered_schools
DELETE FROM "2024".filtered_schools
WHERE "UNIQUESCHOOLID" IN (SELECT "UNIQUESCHOOLID" FROM "2024".alternative_schools);

-- Join coordinate data from ga_school_contact_list
CREATE TABLE "2024".tbl_approvedschools AS
SELECT fs.*, 
       gsc."School Address",
       gsc."School City", 
       gsc."State",
       gsc."lat",
       gsc."lon"
FROM "2024".filtered_schools fs
LEFT JOIN "2024".ga_school_contact_list gsc
ON fs."UNIQUESCHOOLID" = gsc."UNIQUESCHOOLID";

-- Create a geometry column for school locations
ALTER TABLE "2024".tbl_approvedschools ADD COLUMN schoolgeom geometry(Point, 102005);
UPDATE "2024".tbl_approvedschools 
SET schoolgeom = ST_Transform(ST_SetSRID(ST_MakePoint(lon, lat), 4269), 102005);
