-- Creates full-text search index and trigger to update a tf_vector column

-- CREATE INDEX idx_fts_script_vec ON usc_script USING gin(script_vector)

-- CREATE FUNCTION update_script_vec() RETURNS trigger
-- 	LANGUAGE 'plpgsql' VOLATILE NOT LEAKPROOF
-- AS $BODY$
-- BEGIN
-- 	NEW.script_vector :=
-- 		setweight(to_tsvector('pg_catalog.english',
-- 			coalesce(NEW.title,'')), 'A') ||
-- 		setweight(to_tsvector('pg_catalog.english',
-- 			coalesce(NEW.script,'')), 'D');
-- 	RETURN NEW;
-- END
-- $BODY$;

-- CREATE TRIGGER update_script_vec
-- 	BEFORE INSERT OR UPDATE ON usc_script
-- 	FOR EACH ROW EXECUTE PROCEDURE update_script_vec()


-- Migrate scripts from the migration/upload db to the prod db

-- INSERT INTO search_script (title, script_type, year, season, episode, episode_title, script_content)
-- (SELECT
--   title,
--   script_type,
--   CASE
--     WHEN year_text IS NOT NULL AND year_text <> '' THEN
--       CAST(year_text AS INTEGER)
--     ELSE
--       NULL
--     END AS year_text,
--   CASE
--     WHEN season_text IS NOT NULL AND season_text <> '' THEN
--       CAST(season_text AS INTEGER)
--     ELSE
--       NULL
--     END AS season_text,
--   episode_text,
--   episode_title,
--   script_content 
-- FROM search_scriptmigration)


-- Example search query

-- SELECT
-- 	id,
-- 	title,
-- 	year,
-- 	script_type,
-- 	ts_rank("search_content", plainto_tsquery('hello')) as "rank",
-- 	ts_headline(script_content,
-- 			   	plainto_tsquery('hello'),
-- 			   	'StartSel=*,StopSel=*,MaxFragments=10,' ||
-- 			   	'FragmentDelimiter=||||,MaxWords=10,MinWords=1') as "headline"
-- FROM
-- 	search_script
-- WHERE
-- 	search_content @@ plainto_tsquery('hello')
-- ORDER BY rank DESC LIMIT 20 OFFSET 0
